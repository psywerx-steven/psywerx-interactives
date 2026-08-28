export const REQUEST_KEYS = Object.freeze([
  "actor",
  "behaviorObjective",
  "context",
  "clarificationAnswer",
  "driver",
]);

export const DRIVER_SNAPSHOT_KEYS = Object.freeze([
  "id",
  "name",
  "definition",
  "plainLanguageExplanation",
  "analyticQuestion",
  "whatThisDoesNotMean",
  "layer",
  "family",
  "familyDefinition",
  "familyIncludes",
  "familyExclusions",
  "mechanism",
  "moderatorsBoundaryConditions",
  "indicators",
  "measurementAssessmentMethods",
  "observability",
  "measurementCaveats",
  "dataType",
  "timeScaleOfChange",
  "onsetCausalLag",
  "commonMisinterpretations",
  "evidenceNotes",
]);

export const RESPONSE_KEYS = Object.freeze([
  "driverId",
  "scenarioMeaning",
  "operationalizationExamples",
  "importantCaveat",
  "inputSufficiency",
  "clarificationQuestion",
]);

export const EXAMPLE_KEYS = Object.freeze([
  "title",
  "operationalization",
  "whatToLookFor",
  "questionToAsk",
]);

export const INPUT_SUFFICIENCY_VALUES = Object.freeze([
  "SUFFICIENT",
  "PARTIALLY_SUFFICIENT",
  "INSUFFICIENT",
]);

const PRIVATE_PATH_PATTERN =
  /(?:\b[A-Za-z]:[\\/]|file:\/\/|\/(?:Users|home)\/|source-data[\\/]|(?:^|\s)\\\\[^\s]+)/i;

export class ContractError extends Error {
  constructor(message, code = "INVALID_CONTRACT") {
    super(message);
    this.name = "ContractError";
    this.code = code;
  }
}

function isPlainObject(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function sameKeys(value, expected) {
  if (!isPlainObject(value)) return false;
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  return actual.length === wanted.length && actual.every((key, index) => key === wanted[index]);
}

function text(value, field, minimum, maximum, options = {}) {
  if (typeof value !== "string") {
    throw new ContractError(`${field} must be a string.`);
  }
  if (value !== value.trim()) {
    throw new ContractError(`${field} cannot have surrounding whitespace.`);
  }
  if (value.length < minimum || value.length > maximum) {
    throw new ContractError(
      `${field} must contain between ${minimum} and ${maximum} characters.`
    );
  }
  if (options.question) {
    const questionMarks = (value.match(/\?/g) || []).length;
    if (!value.endsWith("?") || questionMarks !== 1) {
      throw new ContractError(`${field} must contain exactly one question.`);
    }
  }
  if (PRIVATE_PATH_PATTERN.test(value)) {
    throw new ContractError(`${field} contains prohibited private-path text.`);
  }
  return value;
}

function nullableText(value, field, minimum, maximum, options = {}) {
  if (value === null) return null;
  return text(value, field, minimum, maximum, options);
}

function stringArray(value, field, minimumItems, maximumItems, maximumLength = 500) {
  if (!Array.isArray(value) || value.length < minimumItems || value.length > maximumItems) {
    throw new ContractError(
      `${field} must contain between ${minimumItems} and ${maximumItems} items.`
    );
  }
  value.forEach((item, index) =>
    text(item, `${field}[${index}]`, 1, maximumLength)
  );
  return value;
}

export function validateOperationalizationRequest(value) {
  if (!sameKeys(value, REQUEST_KEYS)) {
    throw new ContractError("The request has an unexpected shape.", "INVALID_REQUEST");
  }
  text(value.actor, "actor", 1, 200);
  text(value.behaviorObjective, "behaviorObjective", 1, 400);
  text(value.context, "context", 1, 800);
  nullableText(value.clarificationAnswer, "clarificationAnswer", 1, 400);
  if (!sameKeys(value.driver, DRIVER_SNAPSHOT_KEYS)) {
    throw new ContractError(
      "The Driver snapshot has an unexpected shape.",
      "INVALID_REQUEST"
    );
  }
  const driver = value.driver;
  text(driver.id, "driver.id", 7, 32);
  if (!/^[A-Z]{3}-\d{3}$/.test(driver.id)) {
    throw new ContractError("driver.id has an invalid format.", "INVALID_REQUEST");
  }
  [
    "name",
    "definition",
    "layer",
    "family",
    "mechanism",
    "moderatorsBoundaryConditions",
    "measurementAssessmentMethods",
    "observability",
    "measurementCaveats",
    "dataType",
    "commonMisinterpretations",
    "evidenceNotes",
  ].forEach((field) => text(driver[field], `driver.${field}`, 1, 8000));
  ["plainLanguageExplanation", "analyticQuestion"].forEach((field) =>
    nullableText(driver[field], `driver.${field}`, 1, 4000)
  );
  nullableText(driver.whatThisDoesNotMean, "driver.whatThisDoesNotMean", 1, 2000);
  ["familyDefinition", "familyIncludes", "familyExclusions"].forEach((field) =>
    nullableText(driver[field], `driver.${field}`, 1, 8000)
  );
  stringArray(driver.indicators, "driver.indicators", 0, 64, 1000);
  stringArray(driver.timeScaleOfChange, "driver.timeScaleOfChange", 1, 9, 100);
  stringArray(driver.onsetCausalLag, "driver.onsetCausalLag", 1, 8, 100);
  return value;
}

export function validateOperationalizationResponse(value, expectedDriverId) {
  if (!sameKeys(value, RESPONSE_KEYS)) {
    throw new ContractError("The model response has an unexpected shape.", "INVALID_MODEL_OUTPUT");
  }
  if (value.driverId !== expectedDriverId) {
    throw new ContractError("The model response has the wrong Driver ID.", "INVALID_MODEL_OUTPUT");
  }
  text(value.scenarioMeaning, "scenarioMeaning", 40, 900);
  text(value.importantCaveat, "importantCaveat", 20, 500);
  if (!Array.isArray(value.operationalizationExamples) || value.operationalizationExamples.length !== 3) {
    throw new ContractError(
      "The model response must contain exactly three operationalization examples.",
      "INVALID_MODEL_OUTPUT"
    );
  }
  value.operationalizationExamples.forEach((example, index) => {
    if (!sameKeys(example, EXAMPLE_KEYS)) {
      throw new ContractError(
        `operationalizationExamples[${index}] has an unexpected shape.`,
        "INVALID_MODEL_OUTPUT"
      );
    }
    text(example.title, `operationalizationExamples[${index}].title`, 3, 100);
    text(
      example.operationalization,
      `operationalizationExamples[${index}].operationalization`,
      30,
      700
    );
    stringArray(
      example.whatToLookFor,
      `operationalizationExamples[${index}].whatToLookFor`,
      2,
      4,
      200
    );
    text(
      example.questionToAsk,
      `operationalizationExamples[${index}].questionToAsk`,
      8,
      300,
      { question: true }
    );
  });
  if (!INPUT_SUFFICIENCY_VALUES.includes(value.inputSufficiency)) {
    throw new ContractError("inputSufficiency is invalid.", "INVALID_MODEL_OUTPUT");
  }
  if (value.inputSufficiency === "SUFFICIENT") {
    if (value.clarificationQuestion !== null) {
      throw new ContractError(
        "A sufficient response cannot request clarification.",
        "INVALID_MODEL_OUTPUT"
      );
    }
  } else {
    text(value.clarificationQuestion, "clarificationQuestion", 8, 300, {
      question: true,
    });
  }
  return value;
}

export const SCENARIO_RESPONSE_SCHEMA = Object.freeze({
  type: "object",
  additionalProperties: false,
  properties: {
    driverId: { type: "string", pattern: "^[A-Z]{3}-[0-9]{3}$" },
    scenarioMeaning: { type: "string", minLength: 40, maxLength: 900 },
    operationalizationExamples: {
      type: "array",
      minItems: 3,
      maxItems: 3,
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          title: { type: "string", minLength: 3, maxLength: 100 },
          operationalization: { type: "string", minLength: 30, maxLength: 700 },
          whatToLookFor: {
            type: "array",
            minItems: 2,
            maxItems: 4,
            items: { type: "string", minLength: 1, maxLength: 200 },
          },
          questionToAsk: { type: "string", minLength: 8, maxLength: 300 },
        },
        required: ["title", "operationalization", "whatToLookFor", "questionToAsk"],
      },
    },
    importantCaveat: { type: "string", minLength: 20, maxLength: 500 },
    inputSufficiency: { type: "string", enum: INPUT_SUFFICIENCY_VALUES },
    clarificationQuestion: {
      type: ["string", "null"],
      minLength: 8,
      maxLength: 300,
    },
  },
  required: RESPONSE_KEYS,
});

export function containsPrivatePath(value) {
  return typeof value === "string" && PRIVATE_PATH_PATTERN.test(value);
}
