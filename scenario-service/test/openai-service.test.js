import test from "node:test";
import assert from "node:assert/strict";
import { createCatalog } from "../src/catalog.js";
import { createOperationalizer, ScenarioServiceError } from "../src/openai-service.js";
import { fixtureData, validRequest, validResponse } from "./fixtures.js";

function setup(outputs) {
  const calls = [];
  const client = {
    responses: {
      async create(parameters) {
        calls.push(parameters);
        const output = outputs[calls.length - 1];
        if (output instanceof Error) throw output;
        return output;
      },
    },
  };
  const data = fixtureData();
  const request = validRequest(data);
  const context = createCatalog(data.drivers, data.families, data.plainLanguage).resolve(request);
  const operationalize = createOperationalizer({
    client,
    model: "configured-model",
    timeoutMs: 1000,
    maxOutputTokens: 1800,
  });
  return { calls, context, operationalize, request };
}

test("Responses API request is stateless, schema-strict, and server controlled", async () => {
  const expected = validResponse();
  const testCase = setup([{ status: "completed", output_text: JSON.stringify(expected) }]);
  const generated = await testCase.operationalize(testCase.context, testCase.request);
  assert.deepEqual(generated.result, expected);
  assert.equal(generated.attempts, 1);
  assert.equal(testCase.calls[0].model, "configured-model");
  assert.equal(testCase.calls[0].store, false);
  assert.deepEqual(testCase.calls[0].tools, []);
  assert.equal(testCase.calls[0].text.format.type, "json_schema");
  assert.equal(testCase.calls[0].text.format.strict, true);
  assert.equal(Object.hasOwn(testCase.calls[0], "prompt"), false);
});

test("malformed structured output is retried once", async () => {
  const expected = validResponse();
  const testCase = setup([
    { status: "completed", output_text: "not json" },
    { status: "completed", output_text: JSON.stringify(expected) },
  ]);
  const generated = await testCase.operationalize(testCase.context, testCase.request);
  assert.equal(generated.attempts, 2);
  assert.equal(testCase.calls.length, 2);
});

test("API failures are not retried", async () => {
  const testCase = setup([new Error("upstream failure")]);
  await assert.rejects(
    () => testCase.operationalize(testCase.context, testCase.request),
    ScenarioServiceError
  );
  assert.equal(testCase.calls.length, 1);
});

test("a second malformed output fails without a third attempt", async () => {
  const testCase = setup([
    { status: "completed", output_text: "{" },
    { status: "completed", output_text: "{" },
  ]);
  await assert.rejects(
    () => testCase.operationalize(testCase.context, testCase.request),
    (error) => error instanceof ScenarioServiceError && error.code === "INVALID_MODEL_OUTPUT"
  );
  assert.equal(testCase.calls.length, 2);
});
