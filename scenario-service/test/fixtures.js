export function fixtureData({ includePlainLanguage = true } = {}) {
  const driver = {
    id: "BIO-001",
    entityType: "DRIVER",
    entitySubtype: null,
    name: "Sleep Quantity",
    definition: "The amount of sleep obtained over a defined interval relative to physiological sleep need.",
    layer: "Biological",
    family: "Sleep & Circadian Regulation",
    dataType: "Duration",
    mechanism: "Sleep pressure and circadian timing shape available sleep and waking function.",
    moderatorsBoundaryConditions: "Interpret relative to individual need and a stated time period.",
    indicators: ["Sleep diary", "Actigraphy"],
    measurementAssessmentMethods: "Use an appropriate sleep measure for the stated period.",
    observability: "High",
    measurementCaveats: "Reported hours and physiological need are not interchangeable.",
    timeScaleOfChange: ["Hours–Days"],
    onsetCausalLag: ["Hours–Days"],
    commonMisinterpretations: "Sleep quantity is not sleep quality.",
    evidenceNotes: "Interpret effects in relation to task and individual susceptibility.",
    constituentSpecifications: [],
    derivationType: null,
    derivationLogic: null,
    scopeRequirements: null,
    directManipulability: null,
    recalculationBehavior: null,
    uncertaintyPropagation: null,
    compositeSpecification: null,
    differenceSpecification: null,
    networkMetricSpecification: null,
    ratioSpecification: null,
    temporalSpecification: null,
  };
  const family = {
    id: "BIO-F01",
    name: driver.family,
    layer: driver.layer,
    definition: "Sleep amount, timing, continuity, and circadian regulation.",
    includes: "States that describe sleep or circadian regulation.",
    exclusions: "Do not substitute fatigue or task performance.",
  };
  const plain = {
    driverId: driver.id,
    plainLanguageLabel: "Amount of sleep relative to need",
    plainLanguageExplanation: "How much sleep a person gets during a stated period compared with how much their body needs.",
    analyticQuestion: "How much sleep is the person obtaining relative to current physiological need?",
    whatThisDoesNotMean: "It is not the same as sleep quality.",
  };
  return {
    drivers: [driver],
    families: { schemaVersion: "1.0", families: [family] },
    plainLanguage: {
      schemaVersion: "1.0",
      drivers: includePlainLanguage ? [plain] : [],
    },
    driver,
    family,
    plain: includePlainLanguage ? plain : null,
  };
}

export function validRequest(data = fixtureData()) {
  const { driver, family, plain } = data;
  return {
    actor: "Residents in a coastal county",
    behaviorObjective: "Deciding whether and when to evacuate",
    context: "A fast-moving storm with uneven access to transportation",
    clarificationAnswer: null,
    driver: {
      id: driver.id,
      entityType: driver.entityType,
      entitySubtype: driver.entitySubtype,
      name: driver.name,
      definition: driver.definition,
      plainLanguageExplanation: plain ? plain.plainLanguageExplanation : null,
      analyticQuestion: plain ? plain.analyticQuestion : null,
      whatThisDoesNotMean: plain ? plain.whatThisDoesNotMean : null,
      layer: driver.layer,
      family: driver.family,
      familyDefinition: family.definition,
      familyIncludes: family.includes,
      familyExclusions: family.exclusions,
      mechanism: driver.mechanism,
      moderatorsBoundaryConditions: driver.moderatorsBoundaryConditions,
      indicators: [...driver.indicators],
      measurementAssessmentMethods: driver.measurementAssessmentMethods,
      observability: driver.observability,
      measurementCaveats: driver.measurementCaveats,
      dataType: driver.dataType,
      timeScaleOfChange: [...driver.timeScaleOfChange],
      onsetCausalLag: [...driver.onsetCausalLag],
      commonMisinterpretations: driver.commonMisinterpretations,
      evidenceNotes: driver.evidenceNotes,
      constituentSpecifications: [...driver.constituentSpecifications],
      derivationType: driver.derivationType,
      derivationLogic: driver.derivationLogic,
      scopeRequirements: driver.scopeRequirements,
      directManipulability: driver.directManipulability,
      recalculationBehavior: driver.recalculationBehavior,
      uncertaintyPropagation: driver.uncertaintyPropagation,
      compositeSpecification: driver.compositeSpecification,
      differenceSpecification: driver.differenceSpecification,
      networkMetricSpecification: driver.networkMetricSpecification,
      ratioSpecification: driver.ratioSpecification,
      temporalSpecification: driver.temporalSpecification,
    },
  };
}

export function rdsFixtureData() {
  const data = fixtureData({ includePlainLanguage: false });
  Object.assign(data.driver, {
    id: "RDS-0001",
    entityType: "RELATIONAL_DERIVED_STATE",
    entitySubtype: "RELATIONAL_DERIVED_STATE",
    name: "Message Cohesion",
    definition: "The derived coherence of a message from governed message constituents.",
    mechanism: null,
    moderatorsBoundaryConditions: null,
    indicators: [],
    measurementAssessmentMethods: null,
    observability: null,
    measurementCaveats: null,
    timeScaleOfChange: [],
    onsetCausalLag: [],
    commonMisinterpretations: null,
    evidenceNotes: null,
    constituentSpecifications: [{
      entityId: "INF-013",
      externalParameterType: null,
      role: "CONSTITUENT_OR_INPUT",
      required: true,
      unitScaleExpectations: "Aligned with derivation logic",
      alignmentRequirements: "Match analytic level, scope, and time window",
    }],
    derivationType: "COMPOSITE",
    derivationLogic: "Derive cohesion from the governed message constituents.",
    scopeRequirements: "Use the same message and observation window.",
    directManipulability: "VIA_CONSTITUENTS",
    recalculationBehavior: "Recalculate when a constituent changes.",
    uncertaintyPropagation: "Preserve constituent uncertainty.",
  });
  return data;
}

export function validResponse() {
  const examples = ["Recorded sleep period", "Repeated sleep measure", "Comparison to need"].map(
    (title, index) => ({
      title,
      operationalization:
        `Define sleep quantity for the stated actor and period using bounded measure ${index + 1}, without treating it as an observed cause.`,
      whatToLookFor: ["Hours slept in the stated period", "Comparison with stated sleep need"],
      questionToAsk: `How does measure ${index + 1} compare observed sleep with the stated physiological need?`,
    })
  );
  return {
    driverId: "BIO-001",
    scenarioMeaning:
      "In this scenario, sleep quantity means the amount of sleep obtained by the stated actor during a defined period relative to physiological need.",
    operationalizationExamples: examples,
    importantCaveat:
      "Observed sleep duration does not by itself establish sleep quality, impairment, or a causal effect on behavior.",
    inputSufficiency: "SUFFICIENT",
    clarificationQuestion: null,
  };
}
