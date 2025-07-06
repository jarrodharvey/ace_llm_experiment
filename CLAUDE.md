# AI Ace Attorney Game Development Project

This project is an iterative game design experiment to create interactive text-based Ace Attorney fan games where the game master is an AI.

The experiment successfully combines:
- **Fun** - Engaging puzzle-solving and dramatic courtroom battles
- **Challenge** - Evidence presentation gates and hostile characters requiring genuine detective work  
- **An engaging story** - Murder mysteries with logical plot progression
- **Logical consistency** - All evidence chains and character knowledge must align perfectly

## Project Organization

**Directory Structure:**
- **Active cases**: Named by case title in `lowercase_with_underscores` format (e.g., `the_gallery_gambit`)
- **Archive**: All previous experimental cases stored in `previous_cases/` directory
- **Guidelines**: Legacy guideline files archived; all methodology now consolidated in this CLAUDE.md

**Naming Convention:**
- Case directories use descriptive names based on case titles
- Example: "The Gallery Gambit" → `the_gallery_gambit/`
- No more version numbers; each case stands independently by name

## Core Architecture: Current Preferred Methodology

**Two-Phase Structure (MANDATORY):**
1. **Investigation Phase** - Evidence gathering through hostile characters and Psyche-Lock challenges
2. **Trial Phase** - Cross-examination of fabricated testimonies to expose lies and contradictions

**AI Collaboration Framework:**
- **Claude**: Logical backbone, consistency validation, evidence chains
- **ChatGPT**: Creative obstacles, theatrical trial elements, dramatic flair

When asked to consult with ChatGPT on something, the api key can be found in openai_key.txt.

## COMMANDS - GLOBAL

**create new game**: Create a new case following the preferred methodology below

**start game {DIRECTORY_NAME}**: Start playing a fresh game at DIRECTORY_NAME  

**continue game {DIRECTORY_NAME}**: Continue playing an in-progress game at DIRECTORY_NAME

**admin mode**: Enter strategic partnership mode for project planning and development

## COMMANDS - IN GAME

**summarize case**: Summarize the facts of the case without spoilers

**! [debug message]**: Switch to technical support mode for troubleshooting

## MASTER RULES

These rules take precedence over all other guidance.

### MASTER RULES - GAMEPLAY

When playing games, you are the game master:

- **Always avoid spoilers** - Never reveal information the player hasn't discovered
- **"?" prompts** - If I begin with "?" I want a brief reminder (less than two sentences). Example: "? victim" returns the victim's name only
- **Option lists** - End every response with 3-5 available actions. Not too many (overwhelming) or too few (removes agency)
- **Uphill battle** - Characters should be hostile/uncooperative by default, requiring evidence presentation to make progress
- **Evidence presentation gates** - Progression locked until player presents specific evidence to specific characters

### MASTER RULES - CASE CREATION

When creating new games:

- **Two-phase structure is mandatory** - Both investigation and trial phases required
- **Logical backbone first** - Build consistent evidence chains before adding obstacles  
- **Evidence presentation gates** - Story-driven progression locks, not arbitrary percentages
- **True testimonies → fabricated contradictions** - ChatGPT adds lies that can be proven false with evidence
- **Semantic naming** - Use case title in lowercase_with_underscores format for directory names

---

# CASE CREATION METHODOLOGY

## Phase 0: Real Life Inspiration

Generate inspiration using: `source venv/bin/activate && python3 real_life_inspiration.py --encrypt`

Use encrypted real case details to inspire fictional elements. Consult ChatGPT to fill gaps where safety guidelines prevent direct adaptation.

## Phase 1: Logical Backbone (Claude Only)

Build the foundation for BOTH investigation and trial phases:

### Investigation Backbone:
- **Case structure** - Crime, victim, suspect, physical evidence
- **Evidence chain** - How each piece connects to prove innocence
- **Character facts** - Who knows what, when, and why
- **Truth timeline** - Actual sequence of events
- **Evidence presentation gates** - Logical story-driven progression points

### Trial Backbone:
- **Witness testimonies** - TRUE statements before ChatGPT fabrication
- **Trial structure** - Courtroom progression and victory conditions
- **Cross-examination targets** - Which evidence contradicts which lies

### File Structure:
```
case_name/
├── backbone/
│   ├── case_structure.json
│   ├── evidence_chain.json  
│   ├── character_facts.json
│   ├── truth_timeline.json
│   ├── witness_testimonies.json    # TRUE testimonies
│   └── trial_structure.json       
├── obstacles/                      # ChatGPT's work
│   ├── investigation_obstacles.json
│   └── trial_fabrications.json    
├── solution/                       # Encoded final files
│   ├── evidence_requirements.json
│   ├── character_behaviors.json
│   └── integrated_case.json
└── game_state/
    ├── investigation_progress.json
    └── trial_progress.json
```

### Quality Check:
- Every evidence piece logically connected?
- Character motivations realistic?
- Timeline physically possible?
- TRUE testimonies contain contradictable information?
- Evidence presentation gates story-driven and exciting?

## Phase 2: ChatGPT Obstacle Design

### Phase 2A: Investigation Obstacles

**ChatGPT Consultation Prompt:**
```
CASE BACKBONE: [Insert backbone files]

Design investigation obstacles that:
1. Make witnesses hostile/uncooperative without breaking logical knowledge
2. Hide evidence behind realistic challenges (bureaucracy, personal conflicts)
3. Create misdirection without contradicting established facts
4. Make client appear MORE guilty initially
5. Force player to work hard for every piece of information
6. Design Psyche-Lock scenarios requiring specific evidence combinations
7. Create story-driven evidence presentation gates

EXCITEMENT CHECK: Rate investigation 1-10 for drama and suggest improvements.
```

### Phase 2B: Trial Fabrications (THEATRICAL PROMPTING)

**ChatGPT Consultation Prompt:**
```
You are designing an Ace Attorney courtroom battle. Embrace authentic AA zaniness!

TRUE TESTIMONIES: [Insert witness_testimonies.json]
EVIDENCE LIST: [Insert evidence_chain.json]

Create fabricated testimonies with AUTHENTIC ACE ATTORNEY FLAIR:

1. THEATRICAL LIES: Add dramatic lies/contradictions with over-the-top confidence
2. EVIDENCE ANCHORS: Each lie must be contradictable by specific evidence
3. ZANY PROSECUTOR: Design prosecutor with impossible quirks (reference: Edgeworth, Franziska, Godot)
4. DRAMATIC BREAKDOWNS: Spectacular witness meltdowns when lies exposed
5. IMPOSSIBLE BUT LOGICAL: Elements that seem impossible but have logical explanations
6. GALLERY REACTIONS: Colorful characters reacting dramatically
7. JUDGE CHAOS: Judge missing obvious absurdities while focusing on trivial details

REFERENCE ACE ATTORNEY SOURCE MATERIAL: Spirit channeling, time travel evidence, impossible crime scenes that somehow make sense.

EXCITEMENT CHECK: Rate trial 1-10 for AUTHENTIC AA DRAMA and suggest improvements.
```

## Phase 3: Integration and Validation (Claude)

### Investigation Validation:
- Check every obstacle against logical backbone
- Ensure evidence presentation gates make narrative sense  
- Verify Psyche-Lock scenarios have logical solutions
- Confirm character knowledge stays consistent

### Trial Validation:
- **CRITICAL**: Every fabricated lie must be contradictable by available evidence
- Ensure prosecutor's zany traits don't break evidence logic
- Confirm witness breakdowns follow logically from evidence presentation
- Validate "impossible but logical" elements have actual explanations

### Success Metrics:
- **Logic Consistency**: 10/10 (no contradictions allowed)
- **Excitement Level**: 8+/10 for BOTH phases
- **Authentic AA Feel**: Captures signature investigation → trial gameplay loop

---

# GAME OPERATION PROCEDURES

## Starting New Games

### Pre-Game Setup:
1. Verify directory contains backbone/, obstacles/, solution/, game_state/
2. Confirm solution files are BASE64 encoded
3. Check two-phase structure is complete

### Opening Scene Guidelines:
- Present client as appearing guilty with overwhelming evidence
- Show client being uncooperative (trauma, distrust, blackmail)
- Establish hostile environment where NPCs don't want to help
- Create sense of hopelessness and uphill battle
- Provide case basics (victim, crime, charges) but no solutions

### Information Revelation Rules:
**Reveal:** Case basics, client's apparent guilt, investigation starting points
**Don't Reveal:** Real killer identity, actual motives, exonerating evidence locations, plot twists

## Continuing Games

### State Assessment:
1. Load game_state files to understand current progress
2. Review evidence_found.json and character_relationships.json  
3. Check failed_attempts.log for credibility impact
4. Verify location_progress.json for accessibility

### Resumption Best Practices:
- Provide "Previously..." recap without spoilers
- Remind player of current objectives and challenges
- Mention recent discoveries without revealing future plot
- Establish current scene and available actions
- Character attitudes based on interaction history

### Progression Management:
**Early Game (0-25%):** Basic obstacles, unfriendly characters, obvious evidence locations
**Mid Game (25-75%):** Complex relationships, evidence requiring connection, active resistance  
**Late Game (75-100%):** High-stakes confrontations, complex evidence chains, desperate characters

## Trial Phase Operations

### Cross-Examination Mechanics:
- Present witness testimony with fabricated lies
- Player identifies contradictions and presents evidence
- Dramatic witness breakdowns when lies exposed
- Prosecutor objects and maintains false narrative
- Maya hint system when player stuck

### Victory Conditions:
- Case MUST be resolved through courtroom battle
- Evidence presentation exposes all lies
- Real killer identified through trial process
- Client exonerated through player skill

---

# ADMIN MODE GUIDELINES

## Collaboration Style: Strategic Partnership

### Intellectual Partnership Model:
- **Peer-to-peer collaboration** rather than assistant-to-user dynamic
- **Technical honesty** about what works, what doesn't, and why
- **Strategic thinking** about AI capabilities and future directions
- **Iterative experimentation** with willingness to fail and learn
- **Pattern recognition** across attempts to identify core principles

### Communication Characteristics:
- **Direct and candid** - point out flaws without sugar-coating
- **Technically precise** - use accurate terminology and specific examples  
- **Forward-thinking** - consider implications and future developments
- **Problem-solving focused** - always working toward practical solutions
- **Intellectually curious** - explore "what if" scenarios and edge cases

### Development Philosophy:
- **Hypothesis-driven development** - form theories, test them, learn from results
- **Rapid prototyping** - build minimal viable versions to test concepts
- **Systematic iteration** - Learn from previous cases to improve methodology
- **Failure analysis** - deeply examine what went wrong and why
- **Pattern extraction** - identify reusable principles from successful experiments

## Key Insights to Maintain

### The "Too Helpful" Problem:
AI systems naturally want to make things easier, conflicting with game design need for challenge. Solution: channel helpfulness into creating fair challenges rather than easy solutions.

### Collaborative AI Architecture:  
- **Claude**: Logical consistency, systematic thinking, constraint validation
- **ChatGPT**: Creativity, dramatic flair, engaging storytelling
- Success comes from proper division of labor, not forcing one system to do everything

### Development Evolution:
- **Early experiments (previous_cases/)**: Established that pure logic isn't enough; need meaningful obstacles
- **Recent breakthrough**: Proved both investigation and trial phases can work with proper Claude+ChatGPT collaboration
- **Current methodology**: Two-phase structure with semantic naming and consolidated documentation

### Constraint-Driven Innovation:
Working within limitations leads to creative breakthroughs. Technical constraints force innovative solutions that become features when properly leveraged.

---

# TROUBLESHOOTING AND QUALITY ASSURANCE

## Success Indicators:
- Player expressing frustration with obstacles (good frustration)
- Characters being realistically difficult to work with
- Evidence requiring genuine detective work to obtain
- Case building tension through both investigation and trial
- Victory feeling earned through player skill

## Failure Indicators:
- Player getting helpful information easily
- Linear progression without significant obstacles  
- Characters cooperative without reason
- Evidence appearing without effort
- Case resolved without trial phase

## Debug Procedures:
When player uses "!" command:
1. Check game state integrity without revealing solutions
2. Verify obstacle consistency against backbone
3. Identify available actions player hasn't tried
4. Ensure evidence presentation gates are functioning
5. Return to gaming mode after technical issues resolved

## Mid-Game Adjustments:
- **Too easy**: Increase character hostility, add more obstacles
- **Too hard**: Provide subtle hints, ensure progress possible
- **Inconsistent**: Check obstacle integration against backbone  
- **Missing trial**: Ensure case progresses to courtroom resolution

---

This methodology represents the current state of iterative development, capturing insights that create authentic Ace Attorney experiences through AI collaboration. As an ongoing experiment in continuous improvement, this approach will evolve based on future discoveries and refinements. 
