import {
  ContractError,
  SCENARIO_RESPONSE_SCHEMA,
  validateOperationalizationResponse,
} from "./contracts.js";
import { buildModelInput, SYSTEM_INSTRUCTIONS } from "./prompt.js";

export class ScenarioServiceError extends Error {
  constructor(code, publicMessage, status = 502) {
    super(publicMessage);
    this.name = "ScenarioServiceError";
    this.code = code;
    this.publicMessage = publicMessage;
    this.status = status;
  }
}

function isRefusal(response) {
  return Array.isArray(response && response.output) && response.output.some(
    (item) =>
      Array.isArray(item && item.content) &&
      item.content.some((content) => content && content.type === "refusal")
  );
}

async function createWithTimeout(client, parameters, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await client.responses.create(parameters, { signal: controller.signal });
  } catch (error) {
    if (controller.signal.aborted || (error && error.name === "AbortError")) {
      throw new ScenarioServiceError(
        "UPSTREAM_TIMEOUT",
        "Scenario operationalization timed out. Please try again.",
        504
      );
    }
    throw new ScenarioServiceError(
      "UPSTREAM_UNAVAILABLE",
      "Scenario operationalization is temporarily unavailable. Please try again.",
      502
    );
  } finally {
    clearTimeout(timer);
  }
}

function parseAndValidate(response, driverId) {
  if (isRefusal(response)) {
    throw new ScenarioServiceError(
      "MODEL_REFUSAL",
      "The scenario could not be operationalized from the supplied information.",
      422
    );
  }
  if (!response || response.status !== "completed") {
    throw new ScenarioServiceError(
      "UPSTREAM_INCOMPLETE",
      "Scenario operationalization did not complete. Please try again.",
      502
    );
  }
  if (typeof response.output_text !== "string" || !response.output_text.trim()) {
    throw new ContractError("The model returned no structured output.", "INVALID_MODEL_OUTPUT");
  }
  let parsed;
  try {
    parsed = JSON.parse(response.output_text);
  } catch {
    throw new ContractError("The model returned malformed JSON.", "INVALID_MODEL_OUTPUT");
  }
  return validateOperationalizationResponse(parsed, driverId);
}

export function createOperationalizer({
  client,
  model,
  timeoutMs,
  maxOutputTokens,
}) {
  if (!client || !client.responses || typeof client.responses.create !== "function") {
    throw new TypeError("An OpenAI Responses client is required.");
  }
  return async function operationalize(context, request) {
    for (let attempt = 1; attempt <= 2; attempt += 1) {
      const response = await createWithTimeout(
        client,
        {
          model,
          instructions: SYSTEM_INSTRUCTIONS,
          input: [
            {
              role: "user",
              content: [
                {
                  type: "input_text",
                  text: buildModelInput(context, request, attempt),
                },
              ],
            },
          ],
          text: {
            format: {
              type: "json_schema",
              name: "psywerx_scenario_operationalization_v1",
              strict: true,
              schema: SCENARIO_RESPONSE_SCHEMA,
            },
          },
          tools: [],
          max_output_tokens: maxOutputTokens,
          store: false,
        },
        timeoutMs
      );
      try {
        return { result: parseAndValidate(response, context.driver.id), attempts: attempt };
      } catch (error) {
        const malformed = error instanceof ContractError;
        if (!malformed || attempt === 2) {
          if (malformed) {
            throw new ScenarioServiceError(
              "INVALID_MODEL_OUTPUT",
              "Scenario operationalization returned an invalid result. Please try again.",
              502
            );
          }
          throw error;
        }
      }
    }
    throw new ScenarioServiceError(
      "INVALID_MODEL_OUTPUT",
      "Scenario operationalization returned an invalid result. Please try again.",
      502
    );
  };
}
