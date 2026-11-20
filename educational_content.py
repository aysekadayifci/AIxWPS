SCENARIO = """The Republic of Ardin is a fictional conflict-affected state. Camp 17 houses 8,000 displaced people near an urban service corridor. Disrupted transport, damaged electrical and communications infrastructure, strained public services, registration backlogs and contested security claims create interdependent humanitarian dilemmas. This is proposed scenario background for teaching, not verified history or empirical field evidence. Decision-makers operate under incomplete information, time pressure and institutional competition."""
ROLE_PROFILES = {
'humanitarian':'Coordinate impartial assistance and protection while negotiating access, maintaining confidentiality and managing scarce operational capacity.',
'government':'Preserve administrative authority, public legitimacy and service delivery while responding to security and political pressure.',
'women':'Advocate meaningful decision authority, equitable eligibility and protection, including for undocumented and otherwise excluded households.',
'military':'Protect civilians and prevent armed threats while managing contested intelligence and operational security priorities.',
'technology':'Maintain reliable registration systems, address performance gaps and respond to contractual and reputational incentives.',
'community':'Represent diverse residents, contest exclusion, protect autonomy and seek reliable access to essential services.'}
PILLARS={
'Participation':'Women’s meaningful and equal participation in peace and security decisions. In Ardin, examine whether affected residents, especially marginalized women, influence registration design, data governance and crisis response. Also examine representation and exclusion among men, youth, people with disabilities and other groups.',
'Protection':'Protection of rights and safety in conflict. In Ardin, examine civilian security, discriminatory profiling, confidentiality, digital exclusion, GBV risks and barriers to safe services. Protection experiences vary by gender and intersecting characteristics.',
'Prevention':'Preventing conflict and violence through inclusive institutions, early warning, accountability and attention to grievances. In Ardin, examine unverified security alerts, tensions, community trust and the risks of restrictive responses.',
'Relief & Recovery':'Equitable humanitarian relief, recovery and access to essential services. In Ardin, compare aggregate aid throughput with distributional outcomes, damaged critical infrastructure, documentation barriers and the recovery needs of different households.'}
ISSUE_LENSES={
'Privacy & data governance':'Assess data minimization, consent, retention, independent review, sharing with security actors and potential surveillance harms. A privacy score change is a fictional proxy, not a legal compliance determination.',
'Critical infrastructure':'Trace dependencies between electricity, water, clinics, telecommunications, transport and registration. Distinguish immediate service effects from delayed, cascading risks; the current engine does not numerically simulate these dependencies.',
'Humanitarian access':'Ask whose access improves, which routes and eligibility rules create barriers, and whether speed trades off against inclusion. A change of −2 points is not two percent or two fewer beneficiaries.',
'Intersectional inclusion':'Analyze differences across gender, age, disability, documentation, livelihood, digital access and household roles. Existing modeled group outcomes are limited; do not invent quantitative subgroup results.',
'Civilian security':'Examine threats to residents, possible profiling, movement restrictions, independent verification and security actors’ incentives.',
'Community trust':'Examine legitimacy, participation, transparent communication, appeals and the delayed impact of unresolved grievances.',
'AI accountability':'Examine vendor accuracy claims, subgroup validation, oversight, human review, appeal rights and institutional responsibility.'}
SECTORS={'A':{'population':2100,'focus':'Registration/documentation barriers; temporary shelter pressure'},'B':{'population':1900,'focus':'Uneven connectivity and digital literacy'},'C':{'population':2200,'focus':'Distribution queues, mobility and access'},'D':{'population':1800,'focus':'Unverified route bottlenecks and infrastructure repairs'}}
FRAMEWORKS={
'UN Security Council Resolution 1325 and WPS agenda':'Participation, protection, prevention and relief/recovery. Specific subsequent resolutions and national action plans should be retrieved and cited for real-world scenario use.',
'International humanitarian law':'Relevant principles include civilian protection and restrictions on attacks affecting civilian objects; applicability depends on conflict classification and circumstances.',
'UNESCO Recommendation on the Ethics of Artificial Intelligence':'Global ethics instrument addressing human rights, governance, fairness and gender equality; not equivalent to binding domestic law.',
'EU Artificial Intelligence Act':'Regional regulatory framework; applicability and obligations depend on actor, system, jurisdiction and implementation dates.',
'Humanitarian data protection and protection standards':'Operational guidance on responsible data processing, safeguarding, protection mainstreaming and humanitarian principles; specific instruments should be cited in a future retrieval-enabled library.'}

# Illustrative demographics: disjoint age/sex categories sum to the synthetic 8,000.
DEMOGRAPHICS = {
    "Adult women": 2400, "Adult men": 2000,
    "Girls (under 18)": 1800, "Boys (under 18)": 1800,
}
DEMOGRAPHIC_NOTE = ("Synthetic planning assumptions, not census data. Age and sex categories "
    "do not establish gender identity, disability, documentation status or vulnerability. "
    "Those characteristics intersect and should not be added as disjoint groups.")
TECH_CONTEXT = (
    "The proposed aid platform links identity checks, household registration and allocation queues. "
    "Its vendor advertises 88% overall accuracy, without explaining the evaluation sample, error "
    "definition, subgroup performance, or whether people without documents were tested. "
    "False rejections could prevent eligible households from entering the aid queue; false matches "
    "could compromise records or eligibility. Camp connectivity is intermittent, some residents "
    "share devices, and staff must decide whether manual registration and appeals remain available. "
    "The system depends on electricity, telecommunications, secure data storage and trained staff. "
    "The humanitarian coordinator must assess whether speed gains justify introducing an "
    "unverified system, who bears errors, who can contest them, and whether sensitive records "
    "might later be requested by security institutions."
)
ROUND_NARRATIVES = [
    ("A backlog at the registration center is delaying assistance. The ministry wants visible "
     "progress before the next distribution cycle, while residents without identity papers fear "
     "being turned away. The technology provider offers an AI-assisted intake system; it has "
     "not shown that its reported accuracy applies to undocumented households or to women, men "
     "and children facing different barriers. Your immediate goal is to reduce the queue without "
     "creating a new class of excluded residents."),
    ("Following the registration decision, local volunteers and the women's coalition identify "
     "households absent from the official database. Some lack documents; others have limited "
     "connectivity, mobility or digital literacy. Your goal is to decide who has authority to "
     "change eligibility and appeals, balancing immediate distribution speed against equitable access."),
    ("Security command receives an AI-assisted warning based on imagery that is three days old. "
     "A proposed restriction could delay aid vehicles, medical transfers and residents seeking "
     "services. Your goal is to protect civilians while deciding whether and how to verify the "
     "warning without giving uncertain model output the status of established intelligence."),
    ("The government minister's office requests named beneficiary records—including identity "
     "and household information—from the humanitarian registration database for security screening. "
     "The ministry argues this will identify threats and facilitate movement permissions; "
     "residents and protection staff fear profiling, surveillance and loss of confidentiality. "
     "Your goal is to respond to a concrete interagency data request: establish purpose, "
     "necessity, authority, minimum data needed, oversight and safeguards while keeping aid accessible."),
    ("Journalists and community groups publish conflicting accounts of the registration system. "
     "Some claims are inaccurate, but complaints about missing households are real. "
     "Your goal is to restore accountable communication without concealing errors or exposing "
     "individuals whose records may be sensitive."),
    ("A final aid convoy must be authorized under pressure from government and security institutions. "
     "Residents demand predictable access and an appeals route; the women's coalition seeks "
     "meaningful oversight, and transport delays threaten supplies. Your goal is to choose "
     "a delivery and protection arrangement that can withstand scrutiny beyond this final round.")
]

HUMANITARIAN_CHOICE_CONTEXTS = [
[
"Authorize the vendor to register households immediately. This may reduce queues before the next distribution, but the 88% accuracy claim is unvalidated for undocumented residents, older people, disability access or shared devices. Decide who can appeal errors and who is accountable for wrongful exclusion.",
"Run a limited pilot in selected registration points while keeping staffed paper/manual alternatives and an appeals route. This requires additional personnel and coordination but gives residents a way to challenge algorithmic outcomes before full rollout.",
"Delay deployment for an independent technical and protection review. Ask for disaggregated error testing, privacy safeguards and a fallback process. The cost is additional backlog pressure on households awaiting essential assistance."
],
[
"Give women-led organizations genuine authority over eligibility criteria and appeals, with participation from other marginalized groups. This may correct invisible exclusions but takes time and requires the ministry to share decision power.",
"Keep the existing central eligibility rules to preserve throughput during the aid cycle. The risk is that households without documents, connectivity or access to the database remain unregistered, and community grievances accumulate.",
"Send mixed mobile registration teams to reach residents who cannot attend fixed points. This may improve access quickly, but does not resolve who controls the eligibility rules or long-term oversight."
],
[
"Immediately restrict routes around Camp 17 in response to the dated AI alert. This might reduce exposure to a credible threat but also blocks aid, medical movement and livelihoods, and risks profiling young men or undocumented residents.",
"Request fresh imagery, local civilian testimony and independent security review before imposing proportionate restrictions. Verification takes time; the aim is to avoid treating a confidence score as proof of an imminent attack.",
"Continue operations without investigating the warning. This preserves access in the short term but leaves staff and residents without a documented contingency plan if the threat is credible."
],
[
"Transfer named beneficiary and household records to the government for screening. This could support government security operations, but humanitarian records may be reused for surveillance or profiling and residents may stop seeking aid.",
"Negotiate a narrowly defined protocol with purpose limits, independent review, data minimization and complaint mechanisms. Legal and operational negotiation may temporarily slow deliveries, but reduces the risk of uncontrolled secondary use.",
"Refuse transfer of humanitarian records. This protects confidentiality but may trigger permit disputes or pressure on aid operations; prepare an institutional negotiation and continuity plan."
],
[
"Release independently reviewed evidence on system performance, known exclusions and appeals, and hold accessible briefings. This may temporarily divert staff from distribution but gives residents a basis to evaluate claims and demand corrections.",
"Provide a short reassurance from the agency without disclosing a detailed audit. This is fast and may protect operational throughput, but does not address documented registration failures or explain contested claims.",
"Seek emergency controls on disputed reporting. This may limit some false claims but risks censorship, loss of trust and suppression of legitimate testimony from affected households."
],
[
"Negotiate joint convoy management with community oversight, access safeguards and independent monitoring. The goal is sustainable access for registered and unregistered households, though coordination can take longer.",
"Put the final delivery under centralized security command for rapid dispatch. This can improve immediate throughput and route control, but may sideline humanitarian independence and residents without recognized registration.",
"Pause final operations until enforceable political and security guarantees are secured. This may protect institutional principles but risks acute service delays for households relying on the convoy."
]]
