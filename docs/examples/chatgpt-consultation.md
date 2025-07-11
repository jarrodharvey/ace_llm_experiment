# ChatGPT Consultation Command Examples

## Phase 2A: Investigation Obstacles

```bash
source venv/bin/activate && python scripts/chatgpt_consultant.py "You are designing investigation obstacles for an Ace Attorney case. Provide a detailed JSON structure with specific obstacles for each character.

CASE BACKBONE: [Insert detailed case summary with victim, client, real killer, motive, evidence chain]

DESIGN REQUIREMENTS:
1. Make witnesses hostile/uncooperative without breaking logical knowledge
2. Hide evidence behind realistic challenges (bureaucracy, personal conflicts)
3. Create misdirection without contradicting established facts
4. Make client appear MORE guilty initially
5. Force player to work hard for every piece of information
6. Design Psyche-Lock scenarios requiring specific evidence combinations
7. Create story-driven evidence presentation gates

FORMAT YOUR RESPONSE AS DETAILED JSON WITH THESE SECTIONS:
- hostile_witnesses: {character_name: {reason_for_hostility, cooperation_requirements, misdirection_tactics}}
- hidden_evidence: {evidence_name: {hiding_method, access_requirements, bureaucratic_obstacles}}
- psyche_lock_scenarios: {character_name: {locked_secret, evidence_combination_required, unlock_trigger}}
- evidence_presentation_gates: {gate_name: {evidence_required, character_target, story_progression}}

EXCITEMENT CHECK: Rate investigation 1-10 for drama and suggest improvements." --case-dir {case_name} -o obstacles/chatgpt_obstacles_v1.json
```

**Note:** The `--case-dir` parameter ensures outputs are saved to the correct case directory regardless of working directory. ChatGPT may return an API response wrapper - extract the content and convert to proper JSON structure manually.

## Phase 2B: Trial Fabrications (THEATRICAL PROMPTING)

```bash
source venv/bin/activate && python scripts/chatgpt_consultant.py "You are designing an Ace Attorney courtroom battle. Embrace authentic AA zaniness!

TRUE TESTIMONIES: [Insert witness_testimonies.json summary]
EVIDENCE LIST: [Insert evidence_chain.json summary]

CRITICAL REQUIREMENT: This trial MUST happen regardless of pre-trial evidence discovery.

CREATE STRUCTURED JSON OUTPUT WITH THESE SECTIONS:
- prosecutor_[name]: {signature_quirk, dramatic_flair, impossible_habit, weakness}
- fabricated_testimonies: {witness_name_lies: {theatrical_lie, evidence_contradiction, breakdown_trigger, breakdown_style}}
- zany_elements: {spirit_medium_twist, impossible_but_logical, judge_absurdity}
- gallery_reactions: {character_groups and their reactions}
- evidence_anchors: {evidence_name: how_it_contradicts_lies}
- trial_enforcement: {prosecution_persistence, witness_perjury, dramatic_necessity}

AUTHENTIC ACE ATTORNEY FLAIR REQUIREMENTS:
1. THEATRICAL LIES: Add dramatic lies/contradictions with over-the-top confidence
2. EVIDENCE ANCHORS: Each lie must be contradictable by specific evidence
3. PROSECUTION RESISTANCE: Prosecutor fights even when evidence contradicts their case
4. WITNESS PERJURY: Witnesses lie in court despite pre-trial revelations
5. DRAMATIC BREAKDOWNS: Spectacular witness meltdowns when lies exposed
6. ZANY PROSECUTOR: Design prosecutor with impossible quirks who never gives up
7. IMPOSSIBLE BUT LOGICAL: Elements that seem impossible but have logical explanations
8. GALLERY REACTIONS: Colorful characters reacting dramatically
9. JUDGE CHAOS: Judge missing obvious absurdities while focusing on trivial details

REFERENCE ACE ATTORNEY SOURCE MATERIAL: Spirit channeling, time travel evidence, impossible crime scenes.

EXCITEMENT CHECK: Rate trial 1-10 for AUTHENTIC AA DRAMA and suggest improvements." --case-dir {case_name} -o obstacles/trial_fabrications.json -t 0.8
```

**Note:** The `--case-dir` parameter ensures outputs are saved to the correct case directory regardless of working directory. ChatGPT may return an API response wrapper - extract the content and convert to proper JSON structure manually.

*Last updated: 2025-07-10*