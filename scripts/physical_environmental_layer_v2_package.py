"""Build the complete candidate-only Physical / Environmental Layer V2 package."""

from __future__ import annotations

from collections import Counter, defaultdict

from physical_environmental_layer_v2 import DATA, DOCS, PROGRAM_ID, read, write, write_doc, validate_protection

S = lambda n: f"SRC-CAND-ENV-LAYER-{n:03d}"
PREFIX = "**ADVISORY - HUMAN DECISION REQUIRED. New GOVERNED = 0 and ACTIVE = 0.**\n\n"

SOURCES = [
 ("29538664","10.1093/abm/kax043","The Built Environment as a Determinant of Physical Activity: A Systematic Review of Longitudinal Studies and Natural Experiments.",2018),
 ("29373567","10.3390/ijerph15020217","Do Natural Experiments of Changes in Neighborhood Built Environment Impact Physical Activity and Diet? A Systematic Review.",2018),
 ("36104757","10.1186/s12966-022-01352-7","Objectively measuring the association between the built environment and physical activity: a systematic review and reporting framework.",2022),
 ("27471026","10.1016/j.ypmed.2016.07.019","Does the built environment moderate the relationship between having a disability and lower levels of physical activity? A systematic review.",2017),
 ("34649047","10.1016/j.envint.2021.106905","Noise pollution and human cognition: An updated systematic review and meta-analysis of recent evidence.",2022),
 ("29414890","10.3390/ijerph15020285","WHO Environmental Noise Guidelines for the European Region: A Systematic Review on Environmental Noise and Cognition.",2018),
 ("25913554","10.4103/1463-1741.155845","The impact of road traffic noise on cognitive performance in attention-based tasks depends on noise level even within moderate-level ranges.",2015),
 ("41724797","10.1038/s41598-026-41251-6","Impact of thermal-acoustic exposure on human performance of healthy adults: simulation of traffic noise and thermal conditions in the urban environment.",2026),
 ("37107857","10.3390/ijerph20085576","Meta-Analysis of the Effect of Ventilation on Intellectual Productivity.",2023),
 ("36861764","10.13075/ijomeh.1896.02032","The effect of air quality on sleep and cognitive performance in school children aged 10-12 years: a double-blinded, placebo-controlled, crossover trial.",2023),
 ("26502459","10.1289/ehp.1510037","Associations of Cognitive Function Scores with Carbon Dioxide, Ventilation, and Volatile Organic Compound Exposures in Office Workers: A Controlled Exposure Study of Green and Conventional Office Environments.",2016),
 ("38130656","10.1080/23328940.2022.2157645","The effectiveness of heat preparation and alleviation strategies for cognitive performance: A systematic review.",2023),
 ("28633613","10.1080/02656736.2017.1345013","Thermal effects on cognition: a new quantitative synthesis.",2018),
 ("39516236","10.1038/s41598-024-78508-x","The influence of a walk in nature on human resting brain activity: a randomized controlled trial.",2024),
 ("38250104","10.3389/fpsyg.2023.1258378","Walking in nature may improve affect but not cognition.",2023),
 ("35726335","10.3389/fnbeh.2022.901491","Effects of Outdoor Walking on Positive and Negative Affect: Nature Contact Makes a Big Difference.",2022),
 ("34900906","10.3389/fpubh.2021.758457","Impact of Exposure to Natural and Built Environments on Positive and Negative Affect: A Systematic Review and Meta-Analysis.",2021),
 ("33066853","10.1016/j.ctim.2020.102514","Effect of nature exposure on perceived and physiologic stress: A systematic review.",2020),
]

LANDSCAPES = {
 "ENV-F01":("Proximity, travel distance, route directness, connectivity, land-use mix and remoteness are distinct objective properties.","Spatial configuration can constrain route choice and opportunity without determining use.","Infrastructure or access changes are usually natural experiments rather than blinded manipulations.","GIS exposure, network distance and realized travel differ.","Accessibility is not utilization; proximity is not a Social relationship.",[1,2,3,4]),
 "ENV-F02":("Walking, cycling, transit, parking, traffic, speed, congestion and route redundancy describe different transport conditions.","Infrastructure changes opportunity and safety while travel behavior depends on uptake.","Built-environment natural experiments have selection and concurrent-policy limits.","Objective infrastructure, perceived safety and observed use require separate measures.","A facility's presence does not establish exposure or behavior.",[1,2,3]),
 "ENV-F03":("Layout, sightline, entrance/exit, circulation, seating, enclosure and openness are physical configuration properties.","Configuration can affect visibility and movement paths.","Room redesigns typically alter several components together.","Geometry and subjective openness/privacy are different levels.","Package redesign cannot identify one component effect.",[3,4]),
 "ENV-F04":("Landmarks, signage, legibility, option visibility, proximity, availability and barriers are distinct.","Information and geometry can support navigation conditional on perception and ability.","Signage placement is a message/environment operation, not attention itself.","Objective visibility differs from noticed or understood guidance.","Barrier-free design may moderate disability constraints but does not guarantee use.",[4]),
 "ENV-F05":("Objective density, physical proximity, privacy, bottlenecks and queues differ from perceived crowding.","Occupancy and flow constraints can alter movement and exposure.","Density manipulations often co-vary with noise, delay and interaction.","Persons per area is not subjective crowding or stress.","Physical proximity does not entail cohesion, trust or interaction.",[3]),
 "ENV-F06":("Ambient level, intermittency, intelligibility, vibration, illuminance, spectrum, daylight, glare and clutter require exact physical specification.","Acoustic and optical exposures depend on dose, timing, spectrum and task.","Noise playback and controlled lighting are plausible operations.","Objective exposure must be separated from annoyance, attention and performance.","Noise evidence varies by source, task and population; bright-light identity is already governed in BIO-F01.",[5,6,7]),
 "ENV-F07":("Heat, cold, humidity, wind, precipitation, weather, daylight duration, variability and radiant load differ.","Achieved physiological strain depends on dose, clothing, activity, acclimation and baseline.","Climate-chamber exposure can isolate selected factors; field weather cannot.","Temperature is not thermal comfort or body strain.","Thermal-cognitive response is task-, dose- and time-dependent.",[8,12,13]),
 "ENV-F08":("Ventilation, CO2, particulates, gases, VOCs, radiation, pathogens, water contaminants, dampness, mould, odor and cleanliness are distinct.","Ventilation can alter several indoor contaminants simultaneously.","Controlled chambers may vary CO2 alone or bundled ventilation/chemical conditions.","Room concentration is not personal dose received.","Ventilation/productivity evidence mixes school and office tasks and bundled exposures.",[9,10,11]),
 "ENV-F09":("Green availability, accessibility, quality, canopy, views, blue space, biodiversity and realized dose differ.","Natural-setting exposure may alter immediate affect while exercise, expectation and multisensory packages contribute.","Matched walking-route experiments are plausible but cannot isolate each green component.","Availability/accessibility are not realized exposure; affect is not cognition.","Affective findings are more consistent than cognitive transfer and remain heterogeneous.",[14,15,16,17,18]),
 "ENV-F10":("Slope, ruggedness, oxygen availability and water-barrier permeability are physical constraints.","Terrain can change effort and route feasibility; oxygen exposure differs from achieved physiology.","Field terrain packages are difficult to isolate.","Terrain is not physical capacity; oxygen availability is not tissue oxygenation.","No exact novel operation-to-Driver route survived preliminary triage.",[3]),
 "ENV-F11":("Illumination, observability, access control, hazards, exits, shelter, flood, wildfire and structural integrity differ.","Physical hazard and egress conditions constrain safety responses.","Hazard simulations often bundle information, urgency and physical constraints.","Hazard presence is not perceived risk; shelter availability is not use.","No broad hazard-to-psychology causal claim is inferred.",[3]),
 "ENV-F12":("Food, water, sanitation, housing, tools, electricity, fuel, medical material and supply continuity are resource conditions.","Availability and proximity create opportunity conditional on access and uptake.","Resource provision packages mix physical and institutional changes.","Availability is not consumption or benefit.","Existing cross-Layer water and supply reviews are reused.",[1,2]),
 "ENV-F13":("Infrastructure functionality, blockage, debris and utility redundancy concern system condition.","Damage and redundancy can affect continuity through network-specific mechanisms.","Infrastructure restoration is a package rather than one universal component.","Functionality is not Institutional capacity.","No new Network State or derived environmental variable is required.",[2,3]),
}

RETYPE={"REL-ENV-001","REL-ENV-014","REL-ENV-023","REL-ENV-035"}
RESEARCH={"REL-ENV-010","REL-ENV-017","REL-ENV-025","REL-ENV-027","REL-ENV-029","REL-ENV-031","REL-ENV-042","REL-INS-056"}
RETYPE_REASON={
 "REL-ENV-001":"Destination proximity and travel distance are inverse representations that may be semantic/derivational rather than an independent causal pair.",
 "REL-ENV-014":"Noise intermittency and ambient level are distinct acoustic dimensions; intermittency does not universally cause a higher level under an unspecified aggregation window.",
 "REL-ENV-023":"Green-space availability and accessibility may be nested opportunity dimensions; causal typing needs an explicit access mechanism.",
 "REL-ENV-035":"Point-of-use proximity and physical option availability overlap in the current definitions; causal versus compositional typing needs review.",
}


def sf(i,src,claim,design,pop,exposure,target,result,disp,limits,overlap=None):
 return {"id":f"SF-ENV-LAYER-{i:03d}","sourceId":S(src),"claimId":claim,"locator":"PubMed abstract; identity verified through NCBI Eutilities","accessDepth":"PUBMED_ABSTRACT","design":design,"population":pop,"exposure":exposure,"target":target,"result":result,"disposition":disp,"limitations":limits,"datasetGroup":f"PMID_{SOURCES[src-1][0]}","reviewOverlap":overlap or []}


def render(name,body):
 write_doc(DOCS/f"PHYSICAL_ENVIRONMENTAL_LAYER_{name}.md",f"# Physical / Environmental Layer {name.replace('_',' ').lower()}\n\n{PREFIX}{body}")


def build():
 validate_protection(); base=read(DATA/"baseline.json")
 entities={x["frozenRecord"]["id"]:{**x["frozenRecord"],"familyId":x["mechanical"]["familyId"]} for x in base["entities"]}
 canonical=read(DATA.parents[2]/"relationship-intervention-v1/source-register.json")["sources"]+read(DATA.parents[2]/"sources.json")["sources"]
 sources={S(i):{"id":S(i),"pmid":p,"doi":d.lower(),"title":t,"year":y,"accessDepth":"PUBMED_ABSTRACT","verificationRoute":"NCBI_EUTILITIES_PUBMED_ESUMMARY","canonicalExactMatch":next((x["id"] for x in canonical if x.get("pmid")==p or (x.get("doi") and x["doi"].lower()==d.lower())),None),"registrationStatus":"CANDIDATE_ONLY_UNREGISTERED"} for i,(p,d,t,y) in enumerate(SOURCES,1)}
 write(DATA/"candidate-source-registry.json",sources)
 landscapes={}
 for fid,v in LANDSCAPES.items():
  members=[x for x in entities.values() if x["familyId"]==fid]
  existing=sorted({s for x in members for s in x.get("keySources",[])})
  landscapes[fid]={"constructs":v[0],"mechanisms":v[1],"operations":v[2],"measurement":v[3],"boundaries":v[4],"candidateSourceIds":[S(n) for n in v[5]],"existingCanonicalSourceIds":existing,"researchDepth":"FAMILY_LANDSCAPE_ONLY"}
 write(DATA/"family-landscapes.json",{"schemaVersion":"1.0.0","programId":PROGRAM_ID,"method":"Bounded Family landscapes; existing canonical ontology sources reused and deep sources PubMed-verified.","families":landscapes})

 prior={}
 for layer in ["PSYCHOLOGICAL_LAYER","BIOLOGICAL_LAYER"]:
  prior.update({k:(layer,v) for k,v in read(DATA.parent/f"{layer}/relationship-review-registry.json").items()})
 reviews={}
 for row in base["incidentRelationships"]:
  rid,e=row["id"],row["edge"]; reused=None
  if rid in prior:
   layer,p=prior[rid]; disposition=p.get("disposition") or p.get("primaryDisposition")
   reason="Prior completed-Layer review reused: "+(p.get("rationale") or p.get("review",{}).get("rationale","")); reused=layer
  elif rid in RETYPE: disposition,reason="RETYPE_CANDIDATE",RETYPE_REASON[rid]
  elif rid in RESEARCH: disposition,reason="RESEARCH_NEEDED","Exact physical exposure, received dose, mechanism, timing or target alignment is insufficient for the stated causal direction."
  else: disposition,reason="RETAIN_V1_INCOMPLETE","Plausible bounded physical mechanism; retain the unchanged production proposition while exact dose, timing and evidence metadata remain V1-incomplete."
  reviews[rid]={"id":rid,"ownerFamilyId":row["ownerFamilyId"],"consultedFamilyIds":row["consultedFamilyIds"],"scope":row["scope"],"semanticType":e["semanticType"],"sourceId":e["source"],"targetId":e["target"],"disposition":disposition,"rationale":reason,"priorDecisionOrReview":reused,"v1IncompleteFields":row["v1IncompleteFields"],"productionChangeAuthorized":False}
 assert len(reviews)==47
 write(DATA/"relationship-review-registry.json",reviews)

 by_entity=defaultdict(list)
 for row in base["incidentRelationships"]:
  for eid in (row["edge"]["source"],row["edge"]["target"]):
   if eid in entities: by_entity[eid].append(row["id"])
 deep_targets={"ENV-039","ENV-047","ENV-056","ENV-073"}
 coverage={}
 for eid,ent in sorted(entities.items()):
  sufficient=any(reviews[r]["disposition"] in {"RETAIN_AS_IS","RETAIN_V1_INCOMPLETE"} for r in by_entity[eid])
  coverage[eid]={"id":eid,"familyId":ent["familyId"],"entityType":"DRIVER","relationshipStatus":"EXISTING_PROPOSITION_SUFFICIENT" if sufficient else "INSUFFICIENT_PRELIMINARY_SIGNAL","actionsEventsStatus":"CANDIDATE_RESEARCHED" if eid in deep_targets else "INSUFFICIENT_PRELIMINARY_SIGNAL","incidentCausalRelationshipIds":sorted(by_entity[eid]),"existingCanonicalSourceIds":landscapes[ent["familyId"]]["existingCanonicalSourceIds"],"reason":"Exact operation route received deep research." if eid in deep_targets else "Family landscape found no exact operation-to-Driver proposition requiring deep research; this is not a null finding."}
 write(DATA/"negative-coverage-registry.json",coverage); write(DATA/"rds-review.json",[])

 triage_spec=[
  ("ENV-F01","Destination proximity directly causes destination use","REJECT_CATEGORY_ERROR",[1,2,3]),
  ("ENV-F02","Infrastructure availability guarantees active travel","INSUFFICIENT_PRELIMINARY_SIGNAL",[1,2,3]),
  ("ENV-F03","Workspace openness universally improves cognition","INSUFFICIENT_PRELIMINARY_SIGNAL",[3]),
  ("ENV-F04","Signage placement is equivalent to attention or comprehension","REJECT_CATEGORY_ERROR",[4]),
  ("ENV-F05","Objective occupancy density is perceived crowding","REJECT_CATEGORY_ERROR",[3]),
  ("ENV-F06","Controlled road-traffic-noise playback increases PSY-057 cognitive load","DEEP_RESEARCHED_RESEARCH_NEEDED",[5,6,7]),
  ("ENV-F07","Heat and traffic-noise exposure reduces broad attentional capacity","DEEP_RESEARCHED_RESEARCH_NEEDED",[8,12,13]),
  ("ENV-F08","Higher room CO2 or lower ventilation reduces broad cognitive capacity","DEEP_RESEARCHED_RESEARCH_NEEDED",[9,10,11]),
  ("ENV-F09","A specified nature walk increases immediate PSY-050 mood valence versus an urban walk","FORMAL_CANDIDATE_REVIEW_READY",[14,15,16,17,18]),
  ("ENV-F10","Terrain ruggedness is biological physical capacity","REJECT_CATEGORY_ERROR",[3]),
  ("ENV-F11","Objective hazard presence is perceived risk","REJECT_CATEGORY_ERROR",[3]),
  ("ENV-F12","Resource accessibility establishes resource use","REJECT_CATEGORY_ERROR",[1,2]),
  ("ENV-F13","Infrastructure functionality is Institutional capacity","REJECT_CATEGORY_ERROR",[2,3]),
 ]
 triage=[{"id":f"HYP-ENV-LAYER-{i:03d}" if i!=9 else "EA-CAND-ENV-LAYER-0001","familyId":f,"proposition":p,"semanticType":"CAUSAL","outcome":o,"reason":"Construct substitution rejected." if o=="REJECT_CATEGORY_ERROR" else "Preliminary signal did not isolate an exact causal endpoint." if o=="INSUFFICIENT_PRELIMINARY_SIGNAL" else "Proposition-level evidence reviewed with exact boundaries.","sourceIds":[S(n) for n in nums]} for i,(f,p,o,nums) in enumerate(triage_spec,1)]
 write(DATA/"triage-hypotheses.json",triage)
 deep=[
  {"id":"DEEP-ENV-001","familyId":"ENV-F06","hypothesisId":"HYP-ENV-LAYER-006","question":"Road-traffic-noise playback to PSY-057 cognitive load","sourceIds":[S(n) for n in (5,6,7)],"outcome":"RESEARCH_NEEDED","stopReason":"Task performance and annoyance vary by level, task and source; neither is an exact cognitive-load measure."},
  {"id":"DEEP-ENV-002","familyId":"ENV-F07","hypothesisId":"HYP-ENV-LAYER-007","question":"Combined heat/noise exposure to attentional capacity","sourceIds":[S(n) for n in (8,12,13)],"outcome":"RESEARCH_NEEDED","stopReason":"The experiment bundles heat and noise; syntheses show task, dose and adaptation dependence, blocking a broad component effect."},
  {"id":"DEEP-ENV-003","familyId":"ENV-F08","hypothesisId":"HYP-ENV-LAYER-008","question":"Indoor CO2/ventilation to broad cognitive capacity","sourceIds":[S(n) for n in (9,10,11)],"outcome":"RESEARCH_NEEDED","stopReason":"Ventilation, VOCs and CO2 are partly bundled; task productivity is not a broad latent capacity and a controlled child trial reports a next-day cognition null."},
  {"id":"DEEP-ENV-004","familyId":"ENV-F09","hypothesisId":"EA-CAND-ENV-LAYER-0001","question":"Matched low-intensity natural versus urban walk to immediate PSY-050 mood valence","sourceIds":[S(n) for n in (14,15,16,17,18)],"outcome":"REVIEW_READY_BOUNDED_MIXED","stopReason":"Immediate positive-affect signal survives, but setting packages, young-adult samples and high synthesis heterogeneity prohibit broader mood, cognition or clinical claims."},
 ]
 write(DATA/"deep-research-ledger.json",deep)
 findings=[
  sf(1,7,"HYP-ENV-LAYER-006","Three controlled experiments","Healthy adults in small laboratory samples","Recorded road-traffic noise at 50, 60 or 70 dB(A)","Stroop, arithmetic and serial-recall performance plus annoyance","Performance effects depended on task and level; the most detrimental acoustic condition differed across tasks.","MIXED_TASK_DEPENDENT","Task performance and annoyance are not PSY-057; small samples."),
  sf(2,5,"HYP-ENV-LAYER-006","Systematic review and meta-analysis","Children and middle-to-older adults across epidemiological studies","Environmental noise estimates","Multiple cognitive outcomes","Support varied by population and endpoint; some executive-function evidence was against association and other evidence was low quality.","MIXED_ASSOCIATIONAL","Predominantly observational; review may include evidence summarized by source 006.",[S(6)]),
  sf(3,6,"HYP-ENV-LAYER-006","Systematic review","Child populations in 34 quantitative non-experimental papers","Aircraft, road and railway noise","Reading, memory, attention and executive function","Moderate evidence for selected aircraft-noise reading/memory outcomes and no effect for several other outcomes.","MIXED_WITH_NULL","Mostly cross-sectional; not an adult controlled cognitive-load effect."),
  sf(4,8,"HYP-ENV-LAYER-007","Randomized crossover experiment","80 healthy young adults","75 dB(A) traffic noise, heat, combined heat/noise, and comfort control","Physiology, Stroop and n-back performance","Combined exposure produced the most pronounced reported physiological and cognitive alterations.","SUPPORTS_BUNDLED","Heat and noise components cannot be assigned independent effects from the combined contrast."),
  sf(5,12,"HYP-ENV-LAYER-007","Systematic review","Studies of active/passive heat exposure and mitigation","Heat exposure with acclimation, cooling or hydration strategies","Task-specific cognitive performance","Mitigation findings were task- and strategy-dependent and sometimes ambiguous.","MIXED_SYNTHESIS","Intervention review does not identify one universal heat effect."),
  sf(6,13,"HYP-ENV-LAYER-007","Quantitative synthesis","Experimental thermal-load studies","Thermal stress across time/temperature combinations","Task-specific cognitive performance","Performance decrement functions varied by task and thermal dose.","MIXED_NONLINEAR","Task performance is not broad capacity; model does not identify noise interaction."),
  sf(7,11,"HYP-ENV-LAYER-008","Controlled office exposure study","Office workers in simulated office conditions","CO2, ventilation and VOC condition packages","Cognitive function test scores","Scores varied across green/conventional office exposure conditions.","MIXED_BUNDLED","CO2, ventilation and VOC contrasts are not all independently identified; task score is not latent capacity."),
  sf(8,10,"HYP-ENV-LAYER-008","Double-blind crossover trial","36 children aged 10-12","Overnight 700 versus 2000-3000 ppm CO2 under high/reduced ventilation","Next-morning cognitive performance","No effect of CO2 during sleep on next-day cognition was found.","NULL_BOUNDED","Child overnight setting; favorable baseline air quality and small sample limit transfer."),
  sf(9,9,"HYP-ENV-LAYER-008","Meta-analysis of five studies","3679 school/office participants","Higher ventilation rates","Task speed and error rate","Small average improvement in task speed and near-zero error-rate estimate with higher ventilation.","MIXED_SYNTHESIS","Heterogeneous productivity tasks; underlying studies are not independent from the synthesis."),
  sf(10,14,"EA-CAND-ENV-LAYER-0001","Randomized controlled trial","92 adults","40-minute low-intensity natural versus urban walk matched on time and distance","Self-reported affect and frontal midline theta","Both groups improved affect, with greater positive-affect improvement after the nature walk; neural measure differed by route.","SUPPORTS_BOUNDED_AFFECT","Setting package not one green component; immediate outcome and adult sample only."),
  sf(11,15,"EA-CAND-ENV-LAYER-0001","Three-environment experiment","188 undergraduates","Outdoor nature, outdoor urban or indoor treadmill walk","Positive/negative affect and several cognitive tasks","Nature condition had greatest affect improvement, while no location effect appeared on cognitive measures.","SUPPORTS_AFFECT_NULL_COGNITION","Undergraduate sample; cognitive null blocks transfer to attention/memory claims."),
  sf(12,16,"EA-CAND-ENV-LAYER-0001","Randomized three-arm field study","150 students","Green walk, urban walk or no-exercise control","Positive and negative affect","Both walking groups reduced negative affect; natural contact showed differential positive/negative-affect patterns reported by the study.","MIXED_COMPARATOR","Exercise contributes; young student sample and immediate report."),
  sf(13,17,"EA-CAND-ENV-LAYER-0001","Systematic review and meta-analysis","20 natural-versus-built exposure studies","Natural versus built environment exposure","Positive and negative affect","Pooled positive affect increased and negative affect decreased, with extreme heterogeneity and high risk of bias.","MIXED_SUPPORTIVE_SYNTHESIS","Review overlaps experimental paradigms and cannot be counted as independent replication.",[S(14),S(15),S(16)]),
 ]
 write(DATA/"source-findings.json",findings)
 identity={"id":"HT-CAND-ENV-LAYER-0001","originFamilyId":"ENV-F09","name":"Specified low-intensity walk in a natural outdoor setting","identity":"A bounded low-intensity walk of specified duration and route through a defined natural outdoor setting, with pace, distance and material environmental conditions recorded.","intentionality":"DELIBERATE_EXPERIMENTAL_OR_PROGRAM_OPERATION","efficacyImplied":False,"status":"REVIEW_READY","lifecycleStatus":"CANDIDATE","activationStatus":"NOT_ELIGIBLE","duplicateReview":"Distinct from controlled timed bright-light exposure and all existing Psychological, Informational, Biological and Cultural identities; walking route is the operation and does not imply an effect.","sourceIds":[S(14),S(15),S(16)]}
 write(DATA/"actions-events-identity-registry.json",{identity["id"]:identity})
 effect={"id":"EA-CAND-ENV-LAYER-0001","originFamilyId":"ENV-F09","happeningTypeId":identity["id"],"targetKind":"DRIVER","targetId":"PSY-050","property":"LEVEL","direction":"CONTEXT_DEPENDENT_POSITIVE","timing":"Immediate post-walk self-report in the studied session.","population":"Healthy adult and predominantly young-adult/student samples in specified field settings.","operation":"Specified low-intensity natural outdoor walk compared with a time/distance-matched urban or built-setting walk.","scope":"Immediate self-reported positive affect or mood-valence component only.","limitations":"No enduring mood, clinical benefit, cognition, attention, stress physiology, behavior, dose-response, practitioner recommendation or universal setting transfer. The natural route is a multisensory package.","status":"REVIEW_READY","activationStatus":"NOT_ELIGIBLE","lifecycleStatus":"CANDIDATE","sourceFindingIds":[f"SF-ENV-LAYER-{i:03d}" for i in range(10,14)],"evidenceAssessmentId":"EVA-AE-CAND-ENV-LAYER-0001"}
 ae=[effect,
  {"id":"HYP-ENV-LAYER-AE-002","originFamilyId":"ENV-F06","targetKind":"DRIVER","targetId":"PSY-057","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":[f"SF-ENV-LAYER-{i:03d}" for i in range(1,4)],"reason":deep[0]["stopReason"]},
  {"id":"HYP-ENV-LAYER-AE-003","originFamilyId":"ENV-F07","targetKind":"DRIVER","targetId":"PSY-080","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":[f"SF-ENV-LAYER-{i:03d}" for i in range(4,7)],"reason":deep[1]["stopReason"]},
  {"id":"HYP-ENV-LAYER-AE-004","originFamilyId":"ENV-F08","targetKind":"DRIVER","targetId":"PSY-080","property":"LEVEL","status":"RESEARCH_NEEDED","sourceFindingIds":[f"SF-ENV-LAYER-{i:03d}" for i in range(7,10)],"reason":deep[2]["stopReason"]}]
 write(DATA/"actions-events-hypotheses.json",ae); write(DATA/"candidate-proposition-registry.json",{effect["id"]:effect})
 eva={"id":"EVA-AE-CAND-ENV-LAYER-0001","assertionId":effect["id"],"basis":"RANDOMIZED_NATURAL_VERSUS_BUILT_WALK_EXPERIMENTS_AND_OVERLAPPING_SYNTHESIS","productionMethod":"CURATED_SOURCE_FINDING_SYNTHESIS","disposition":"MIXED_SUPPORTS_BOUNDED","strength":"MODERATE_FOR_IMMEDIATE_POSITIVE_AFFECT","confidence":"MODERATE_WITH_SETTING_HETEROGENEITY","sourceFindingIds":effect["sourceFindingIds"],"nullContrary":"Cognitive outcomes were null in PMID 38250104; both natural and urban walks reduced negative affect in some comparisons. These findings limit the claim to immediate positive mood valence.","overlap":"PMID 34900906 synthesizes experimental paradigms and is not independent replication.","lifecycleStatus":"CANDIDATE","activationStatus":"NOT_ELIGIBLE","use":"REVIEW_READY_BOUNDED"}
 write(DATA/"evidence-assessments.json",[eva])
 write(DATA/"source-overlap-registry.json",[
  {"id":"OV-ENV-001","sources":[S(5),S(6),S(7)],"issue":"Noise reviews overlap primary literatures; reviews and included studies are not independent replications."},
  {"id":"OV-ENV-002","sources":[S(9),S(10),S(11)],"issue":"Ventilation meta-analysis and controlled studies differ in population, exposure package and task; possible included-study overlap must remain explicit."},
  {"id":"OV-ENV-003","sources":[S(12),S(13),S(8)],"issue":"Thermal syntheses and combined-exposure experiment do not isolate the same contrast."},
  {"id":"OV-ENV-004","sources":[S(14),S(15),S(16),S(17),S(18)],"issue":"Nature reviews overlap experimental paradigms; walking, setting and expectation components vary."}])
 skeptical=[
  {"id":"SK-ENV-001","claimId":"HYP-ENV-LAYER-006","attemptedFalsification":["Performance is not cognitive load","Task and source heterogeneity","Selected null outcomes"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[0]["stopReason"]},
  {"id":"SK-ENV-002","claimId":"HYP-ENV-LAYER-007","attemptedFalsification":["Bundled heat/noise","Nonlinear dose","Task transfer"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[1]["stopReason"]},
  {"id":"SK-ENV-003","claimId":"HYP-ENV-LAYER-008","attemptedFalsification":["CO2/ventilation/VOC bundling","Child null","Task score versus latent capacity"],"result":"KEEP_RESEARCH_NEEDED","reason":deep[2]["stopReason"]},
  {"id":"SK-ENV-004","claimId":"EA-CAND-ENV-LAYER-0001","attemptedFalsification":["Walking/exercise contribution","Setting package","Cognition null","High synthesis heterogeneity","Young-adult transfer"],"result":"MODIFY_AND_RETAIN_REVIEW_READY","reason":"Immediate positive affect remains supported under exact natural-versus-urban walking semantics; all broader outcomes and transfer are excluded."}]
 write(DATA/"skeptical-review.json",skeptical)
 write(DATA/"cross-family-issues.json",[
  {"id":"XF-ENV-001","families":["ENV-F01","ENV-F02","ENV-F04"],"issue":"Availability, proximity, accessibility and realized use form a pathway but are not interchangeable."},
  {"id":"XF-ENV-002","families":["ENV-F05","ENV-F06"],"issue":"Density, proximity, noise and privacy co-vary; objective properties and appraisal remain distinct."},
  {"id":"XF-ENV-003","families":["ENV-F06","ENV-F07","ENV-F08"],"issue":"Indoor acoustic, thermal and air-quality packages can be bundled; component efficacy is not inferred."},
  {"id":"XF-ENV-004","families":["ENV-F09","ENV-F01"],"issue":"Green-space availability/accessibility differs from realized nature-exposure dose and walking behavior."}])
 write(DATA/"cross-layer-findings.json",[
  {"id":"XL-ENV-001","relationshipIds":["REL-ENV-039","REL-ENV-040","REL-ENV-041","REL-V1-BIO-F01-004"],"reusedFrom":"BIOLOGICAL_LAYER and BIO-F01","issue":"Exact heat, noise/light and water routes reused; Biological science not reopened."},
  {"id":"XL-ENV-002","relationshipIds":["REL-ENV-044","REL-ENV-045"],"reusedFrom":"PSYCHOLOGICAL_LAYER","issue":"Supply/control and noise/load reviews reused; Psychological science not reopened."},
  {"id":"XL-ENV-003","relationshipIds":["REL-ENV-042","REL-INS-056"],"issue":"Infrastructure and Institutional capacity remain externally owned and research-needed."}])
 write(DATA/"architecture-escalations.json",[]); write(DATA/"astra-escalation-queue.json",[])

 groups=[
  {"id":"GRP-ENV-001","recommendation":"APPROVE_RETAIN_V1_INCOMPLETE","recordIds":[k for k,v in reviews.items() if v["disposition"]=="RETAIN_V1_INCOMPLETE" and not v["priorDecisionOrReview"]],"rationale":"Twenty-nine bounded physical mechanisms may remain unchanged with V1-incomplete dose, timing or evidence metadata."},
  {"id":"GRP-ENV-002","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[k for k,v in reviews.items() if v["disposition"]=="RESEARCH_NEEDED" and not v["priorDecisionOrReview"]],"rationale":"Eight existing propositions lack exact exposure, mechanism or endpoint identification."},
  {"id":"GRP-ENV-003","recommendation":"ACCEPT_CATEGORY_ERROR_REJECTIONS","recordIds":[x["id"] for x in triage if x["outcome"]=="REJECT_CATEGORY_ERROR"],"rationale":"Physical condition is not perceived state, behavior, use, capacity or Institutional condition."},
  {"id":"GRP-ENV-004","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":[x["id"] for x in triage if x["outcome"]=="INSUFFICIENT_PRELIMINARY_SIGNAL"],"rationale":"Two broad package claims terminated at cheap triage."}]
 individual=[{"id":f"DEC-ENV-RETYPE-{i:02d}","recommendation":"APPROVE_RETYPE_REVIEW_ONLY","recordIds":[rid],"rationale":RETYPE_REASON[rid]} for i,rid in enumerate(sorted(RETYPE),1)]
 individual += [
  {"id":"DEC-ENV-NOISE","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["HYP-ENV-LAYER-006","HYP-ENV-LAYER-AE-002"],"rationale":deep[0]["stopReason"]},
  {"id":"DEC-ENV-THERMAL-ACOUSTIC","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["HYP-ENV-LAYER-007","HYP-ENV-LAYER-AE-003"],"rationale":deep[1]["stopReason"]},
  {"id":"DEC-ENV-CO2-VENTILATION","recommendation":"KEEP_RESEARCH_NEEDED","recordIds":["HYP-ENV-LAYER-008","HYP-ENV-LAYER-AE-004"],"rationale":deep[2]["stopReason"]},
  {"id":"DEC-ENV-NATURE-IDENTITY","recommendation":"GOVERN_INACTIVE_IDENTITY","recordIds":[identity["id"]],"rationale":"The specified low-intensity natural-setting walk is a coherent reusable operation identity; identity implies no mood effect, recommendation, feasibility or activation."},
  {"id":"DEC-ENV-NATURE-EFFECT","recommendation":"MODIFY_AND_GOVERN_INACTIVE","recordIds":[effect["id"],eva["id"]],"rationale":"Approve only the immediate positive mood-valence contrast under matched natural-versus-urban walking semantics; MIXED stays mixed and all broader cognition, stress, clinical, behavior and durability claims are excluded."}]
 decision_for={}
 for unit in groups+individual:
  for rid in unit["recordIds"]: assert rid not in decision_for,rid; decision_for[rid]=unit["id"]
 regs=["relationship-review-registry","negative-coverage-registry","triage-hypotheses","deep-research-ledger","candidate-source-registry","source-findings","source-overlap-registry","actions-events-identity-registry","actions-events-hypotheses","evidence-assessments","cross-family-issues","cross-layer-findings","skeptical-review"]
 index=[]
 for name in regs:
  obj=read(DATA/f"{name}.json"); seq=list(obj.values()) if isinstance(obj,dict) else obj; keys=list(obj) if isinstance(obj,dict) else None
  for j,val in enumerate(seq):
   rid=keys[j] if keys is not None else val["id"]; prior_ref=val.get("priorDecisionOrReview") if isinstance(val,dict) else None; dec=decision_for.get(rid)
   if name=="relationship-review-registry" and not dec: assert prior_ref,rid
   index.append({"rowId":f"GI-ENV-LAYER-{len(index)+1:04d}","registry":name,"recordId":rid,"decisionId":dec,"rowClass":"SCIENTIFIC_VOTE_REFERENCE" if dec else "NONVOTING_ACKNOWLEDGEMENT","priorDecisionOrReview":prior_ref})
 write(DATA/"governance-index.json",index)
 required={S(n) for n in (14,15,16,17)}
 write(DATA/"source-registration-recommendations.json",{sid:{"candidateSourceId":sid,"canonicalExactMatch":row["canonicalExactMatch"],"recommendation":"REQUIRED_IF_NATURE_IDENTITY_AND_EFFECT_APPROVED" if sid in required else "RESEARCH_NEEDED_OR_LANDSCAPE_ONLY","dependencyIds":[identity["id"],effect["id"],eva["id"]] if sid in required else [],"registrationNowAuthorized":False} for sid,row in sources.items()})
 gov={"schemaVersion":"1.0.0","programId":PROGRAM_ID,"advisory":"ADVISORY - HUMAN DECISION REQUIRED","originalGovernanceRows":len(index),"distinctScientificDecisions":len(groups)+len(individual)+sum(bool(v["priorDecisionOrReview"]) for v in reviews.values()),"groupedHumanDecisions":groups,"individualScientificDecisions":individual,"blockedDecisions":[],"nonVotingAcknowledgements":sum(x["rowClass"]=="NONVOTING_ACKNOWLEDGEMENT" for x in index),"priorScientificPropositionsReused":sum(bool(v["priorDecisionOrReview"]) for v in reviews.values()),"futureMaterializationRecommendations":{"Relationships":0,"HappeningTypes":1,"EffectAssertions":1,"EvidenceAssessments":1},"newGoverned":0,"newActive":0,"consequentialHumanStopRequired":True}
 write(DATA/"governance-recommendations.json",gov)
 progress=read(DATA/"progress.json");progress["families"]={f:"COMPLETE" for f in progress["families"]};write(DATA/"progress.json",progress)
 write_doc(DOCS/"PHYSICAL_ENVIRONMENTAL_LAYER_PROGRESS.md","# Physical / Environmental Layer progress\n\n"+PREFIX+"| Family | Stage |\n|---|---|\n"+"\n".join(f"| {f} | COMPLETE |" for f in progress["families"])+"\n")
 canonical_reused={s for row in landscapes.values() for s in row["existingCanonicalSourceIds"]}
 write(DATA/"resource-telemetry.json",{"driversCovered":109,"rdsReviewed":0,"cheapNegativeAERoutes":105,"hypothesisRoutesGenerated":13,"propositionsEnteringDeepResearch":4,"formalRelationshipsRetained":0,"formalEffectAssertionsRetained":1,"sourceFindings":13,"evidenceAssessments":1,"priorLayerRelationshipReviewsReused":6,"existingCanonicalSourcesReused":len(canonical_reused),"newCandidateSources":18,"crossFamilyDuplicateVotesPrevented":4,"happeningTypeIdentitiesReused":1,"newHappeningTypeIdentities":1,"astraEscalations":0,"creditSavings":"NOT_MEASURED","tokenSavings":"NOT_MEASURED","timeSavings":"NOT_MEASURED"})

 counts=Counter(x["disposition"] for x in reviews.values())
 render("RELATIONSHIP_SUMMARY","All 47 incident causal Relationships were reviewed exactly once: 21 within-Family, 18 same-Layer cross-Family, one incoming and seven outgoing.\n\n| Disposition | Count |\n|---|---:|\n"+"\n".join(f"| {k} | {v} |" for k,v in sorted(counts.items()))+"\n\nSix exact Biological/Psychological reviews are reused. Four retype proposals are review-only. No production edge changes.\n")
 render("CONSTRUCT_BOUNDARIES","Objective condition remains separate from perceived condition, presence from received dose, exposure from attention, setting from psychological state, noise level from intermittency, light from circadian effect, temperature from comfort, density from crowding, proximity from relationship, accessibility from use, and hazard from risk perception. No ontology content changes.\n")
 render("CROSS_FAMILY_ISSUES","Four shared issues are reconciled once: access pathways, density/noise/privacy, bundled indoor exposure, and green availability versus realized nature dose. No duplicate proposition is created.\n")
 render("CROSS_LAYER_FINDINGS","Four exact Biological/BIO-F01 and two Psychological reviews are reused. Institutional infrastructure edges retain external ownership. Completed Layers are not reopened.\n")
 render("ACTIONS_EVENTS_SUMMARY","All 109 Drivers have coverage. Four routes entered deep research. Noise, combined thermal-acoustic exposure and CO2/ventilation remain research-needed. One natural-setting walk identity and one bounded immediate mood-valence effect remain REVIEW_READY recommendations. Timed bright-light exposure reuses the governed BIO-F01 intervention identity. No RDS or RelationalState target exists.\n")
 fc=Counter("SUPPORT" if x["disposition"].startswith("SUPPORTS") else "NULL" if x["disposition"].startswith("NULL") else "MIXED" for x in findings)
 render("EVIDENCE_SUMMARY",f"The candidate bibliography has 18 PubMed-verified sources and 13 sourceFindings: {fc['SUPPORT']} bounded support, {fc['MIXED']} mixed and {fc['NULL']} bounded null rows. One candidate EvidenceAssessment is `MIXED_SUPPORTS_BOUNDED`; approval would not upgrade it. Review/included-study overlap and the cognition null in the nature-walk literature remain explicit.\n")
 render("REJECTIONS","Seven category-error hypotheses reject only the stated substitution of physical condition for behavior, perception, capacity or Institutional state. Two cheap-triage package claims remain research-needed.\n")
 render("ARCHITECTURE_ESCALATIONS","No RDS, Network State binding, architecture change or Astra escalation is required. The audit explicitly declines to create a derived environmental state merely to summarize exposure.\n")
 fam=[f"| {fid} | {sum(x['familyId']==fid for x in coverage.values())} | COMPLETE | {landscapes[fid]['boundaries']} |" for fid in sorted(landscapes)]
 render("COMPLETENESS_REPORT","All 13 Families completed membership, landscape, edge review, Driver/A&E coverage, triage, deep research where warranted, evidence reconciliation, skeptical review and deduplication.\n\n| Family | Drivers | Stage | Principal boundary |\n|---|---:|---|---|\n"+"\n".join(fam)+"\n")
 individual_rows="\n".join(
  f"| `{unit['id']}` | {', '.join(f'`{rid}`' for rid in unit['recordIds'])} | `{unit['recommendation']}` | {unit['rationale']} |"
  for unit in individual
 )
 source_rows="\n".join(
  f"| `{sid}` | PMID {sources[sid]['pmid']} | DOI `{sources[sid]['doi']}` |"
  for sid in sorted(required)
 )
 recommendations=f"""## Executive summary

The {len(index)} governance rows reduce to **{len(groups)} grouped decisions + {len(individual)} individual scientific decisions + 0 blocked decisions**. Six prior reviews are acknowledgements rather than new votes; {gov['nonVotingAcknowledgements']} rows are workflow/evidence acknowledgements. New GOVERNED = 0; new ACTIVE = 0.

## Grouped approvals recommended

`GRP-ENV-001` retains 29 new-to-this-audit V1-incomplete physical mechanisms without semantic change.

## Grouped rejection recommendations

`GRP-ENV-003` accepts seven exact category-error rejections.

## Grouped research-needed recommendations

`GRP-ENV-002` keeps eight existing edges research-needed. `GRP-ENV-004` keeps two broad package claims at cheap triage.

## Existing Relationship proposals

The complete disposition is 1 `RETAIN_AS_IS`, 31 `RETAIN_V1_INCOMPLETE`, 2 prior `REVISION_CANDIDATE`, 4 `RETYPE_CANDIDATE`, and 9 `RESEARCH_NEEDED`. Four retype proposals are review-only. Six completed-Layer decisions are reused. No production Relationship changes.

## Individual scientific decisions

| Decision | Records | Recommendation | Scientific boundary |
|---|---|---|---|
{individual_rows}

## New Relationship candidates

None.

## HappeningType identities

Recommend `GOVERN_INACTIVE_IDENTITY` for `HT-CAND-ENV-LAYER-0001`, a specified low-intensity walk through a defined natural outdoor route. Identity does not imply efficacy, feasibility, recommendation or activation.

## EffectAssertions

Recommend `MODIFY_AND_GOVERN_INACTIVE` for `EA-CAND-ENV-LAYER-0001` only under exact semantics: a specified low-intensity natural outdoor walk, compared with a time/distance-matched urban walk, may increase immediate self-reported positive affect/mood valence in studied adult settings. No lasting mood, cognition, attention, stress, clinical, behavior, dose-response or universal transfer claim.

Noise, thermal-acoustic and CO2/ventilation effects remain research-needed.

## EvidenceAssessment dependencies

Recommend future inactive governance of `EVA-AE-CAND-ENV-LAYER-0001` as `MIXED_SUPPORTS_BOUNDED`. Null cognition, comparator improvement, setting packages, overlap and heterogeneity remain explicit.

## Construct/ontology questions

No ontology change is recommended. Physical/perceived, exposure/dose, access/use and density/crowding boundaries remain claim constraints.

## Architecture blockers

None. No RDS or Network State addition is proposed.

## Future source registrations

Only the following candidate sources would be required if the human approves the identity/effect/evidence bundle. Register none now.

| Candidate source | Authoritative identity | DOI |
|---|---|---|
{source_rows}

## Proposed future materialization set

Relationships **0**; HappeningTypes **1**; EffectAssertions **1**; EvidenceAssessments **1**. These are recommendations only.

## Explicit exclusions

No production proposition, existing lifecycle, source registry, ontology, architecture, Network State or completed Layer changes.

## Activation boundary

NO ACTIVATION is recommended or authorized. Because a new EffectAssertion and EvidenceAssessment are recommended, explicit human governance is required before any materialization.
"""
 render("GOVERNANCE_RECOMMENDATIONS",recommendations)
 render("GOVERNANCE_REVIEW_SUMMARY",f"From **{len(index)} rows**, the package proposes **{len(groups)} grouped + {len(individual)} individual + 0 blocked** decisions. **{gov['nonVotingAcknowledgements']}** rows are non-voting acknowledgements and six prior reviews are reused. The human should read the natural-walk identity/effect/evidence bundle, four retype proposals, and three deep research-needed routes most closely.\n")
 render("HANDOFF",f"Program `{PROGRAM_ID}` completed all 13 Physical / Environmental Families against main `{base['baseCommit']}`. Candidate science remains non-governed and inactive. The bounded nature-walk mood bundle crosses the consequential stop rule and requires explicit human scientific governance. The PR must remain open and unmerged.\n")
 manifest={"schemaVersion":"1.0.0","programId":PROGRAM_ID,"baseCommit":base["baseCommit"],"familiesComplete":13,"driversCovered":109,"rdsReviewed":0,"entitiesReviewed":109,"relationshipReviews":47,"protectedScienceHashFile":"protected-baseline.json","governanceRows":len(index),"groupedVotes":len(groups),"individualVotes":len(individual),"blockedVotes":0,"nonVotingAcknowledgements":gov["nonVotingAcknowledgements"],"newGoverned":0,"newActive":0,"status":"ADVISORY_HUMAN_DECISION_REQUIRED"}
 write(DOCS/"PHYSICAL_ENVIRONMENTAL_LAYER_AUDIT_MANIFEST.json",manifest)
 print("Physical / Environmental package",len(reviews),"relationships",len(index),"governance rows",len(findings),"findings")


if __name__=="__main__": build()
