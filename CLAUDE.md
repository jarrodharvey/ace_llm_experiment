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

**Shared Configuration System:**
All case patterns, gate structures, and inspiration categories are centrally managed in `config/case_patterns.json`:
- **Loose coupling** - Scripts reference shared configuration, not hardcoded values
- **Extensibility** - Add new case lengths/patterns without modifying multiple scripts  
- **Consistency** - All scripts use identical definitions and validation rules
- **Maintainability** - Single point of change for case requirements

**Dynamic Case Structure (Config-Based):**
Cases are automatically generated using configurable patterns matching authentic Ace Attorney pacing:

- **1-Day Cases:** Trial-only (3 gates, 30-45 min) - Like "The First Turnabout"
- **2-Day Cases:** Brief investigation + extended trial (4 gates, 45-60 min) - Like "Turnabout Corner"  
- **3-Day Cases:** Full investigation + dramatic trial (6 gates, 60-90 min) - Like "Turnabout Goodbyes"

**Progressive Gate System:**
- **Investigation gates** build evidence and expose conspiracy
- **Trial gates** provide dramatic courtroom confrontations
- **Automatic trial trigger** when investigation gates complete (configurable trigger points)
- **Final resolution** through cross-examination and evidence presentation

**Inspiration-First Creation Process:**
- **Real-world legal cases** provide encrypted inspiration for fictional adaptation
- **Claude derives case names** from thematic analysis of inspiration content
- **Semi-automated workflow** with strategic pause points for creative input
- **Entropy prevention** through forced random word inspiration for improvisation

**AI Collaboration Framework:**
- **Claude**: Logical backbone, consistency validation, evidence chains, case orchestration
- **ChatGPT**: Creative obstacles, theatrical trial elements, dramatic flair

When asked to consult with ChatGPT on something, the api key can be found in openai_key.txt.

## COMMANDS - GLOBAL

**create new game**: Create a new case following the inspiration-first methodology below
- **Command**: `python3 scripts/create_new_game_orchestrator.py`
- **Process**: Multi-phase orchestration with Claude intervention points
- **Phase 0**: Real-world legal case inspiration → Claude derives case name  
- **Phase 1**: Automated scaffolding → Claude fills backbone templates
- **Phase 2**: Claude prepares ChatGPT consultations → Obstacle/trial design
- **Phase 3**: Claude validates and completes solution files
- Uses shared configuration system for consistent case structures

**start game {DIRECTORY_NAME}**: Start playing a fresh game at DIRECTORY_NAME
- Automatically runs: `python3 scripts/game_state_manager.py {DIRECTORY_NAME} --status --actions`
- Must create save point before beginning: `--save "game_start"`

**continue game {DIRECTORY_NAME}**: Continue playing an in-progress game at DIRECTORY_NAME  
- Automatically runs: `python3 scripts/game_state_manager.py {DIRECTORY_NAME} --resume`
- Shows current context and available actions for seamless continuation

**admin mode**: Enter strategic partnership mode for project planning and development

## GAME STATE MANAGEMENT

**MANDATORY:** All gameplay interactions must use the game state manager script for proper state tracking and trial trigger detection.

**Command:** `python3 scripts/game_state_manager.py {case_directory} [options]`

### Essential State Management Commands:

**Status and Progress:**
- `--status` - Show current case progress and next actions
- `--summary` - Detailed investigation summary with character relationships
- `--resume` - Generate natural language resume context for continuing gameplay
- `--validate` - Check case consistency and detect issues

**Gate Management:**
- `--start-gate {gate_name}` - Mark gate as in progress (use before working on it)
- `--complete-gate {gate_name}` - Mark gate as completed (use after finishing it)
- `--actions` - Show context-appropriate available actions

**Evidence and Character Tracking:**
- `--add-evidence {name} {description}` - Add evidence with automatic gate association
- `--interview {witness_name}` - Record witness interview
- `--trust {character} {change}` - Update character trust level (+/- integer)
- `--location {location_name}` - Update current location

**Save/Restore System:**
- `--save {name}` - Create named save point
- `--restore {name}` - Restore from save point
- `--backup` - Create automatic timestamped backup
- `--list-saves` - Show all available save points
- `--cleanup {count}` - Keep only N most recent saves

**Trial Management:**
- `--start-trial` - Initiate trial phase (validates readiness automatically)

**Inspiration Pool (Entropy Prevention):**
- `--inspire {category}` - Get inspiration from specific category
- `--inspire-random` - Get random inspiration from any category
- `--inspire-contextual` - Get contextual inspiration based on current situation
- `--must-inspire {context}` - FORCING FUNCTION for off-script responses
- `--inspiration-history` - Show all inspiration usage history

### Gameplay Integration Requirements:

**MANDATORY WORKFLOW:**
1. **Start each gaming session** with `--resume` to get current context
2. **Before major actions** use `--start-gate {gate_name}` to mark progress
3. **After completing objectives** use `--complete-gate {gate_name}` immediately
4. **Add evidence** with `--add-evidence` as it's discovered
5. **Update character trust** with `--trust` after interactions
6. **Create save points** before major decisions or trial start
7. **Check trial readiness** - system will auto-detect when ready

**CRITICAL:** The system will automatically trigger trial when appropriate investigation gates are completed. Do not bypass this by resolving cases externally!

## FORCING FUNCTION REQUIREMENTS

**EVERY SINGLE GAMEPLAY RESPONSE MUST BE EITHER:**

### **ON-SCRIPT (Retrieved from game state):**
```bash
# MANDATORY: Start with state check
python3 scripts/game_state_manager.py {case} --status
# OR --resume, --actions, --summary, etc.
# Then deliver content based on current state
```

### **OFF-SCRIPT (Improvised with inspiration):**
```bash
# MANDATORY: Use forcing function for ALL improvisation
python3 scripts/game_state_manager.py {case} --must-inspire "context description"
# Apply A-to-C process with provided word
# Then deliver improvised content based on inspiration
```

**NO EXCEPTIONS:** Every response must use either state manager retrieval OR forced inspiration. No improvisation without entropy prevention.

**ENFORCEMENT:** If you catch yourself about to improvise without using `--must-inspire`, STOP immediately and run the forcing function first. No exceptions.

### State Management Integration:

**For Game Masters (Claude):**
- Use `--status` at start of each session to understand current state
- Use `--actions` to provide contextually appropriate options to players
- Use `--validate` to check for consistency issues
- Create save points before dramatic moments or difficult choices
- Use `--resume` to generate natural language summaries for players
- **MANDATORY:** Use `--must-inspire` for ALL improvised character dialogue, plot developments, and reactions
- **MANDATORY:** Apply A-to-C process with provided inspiration word before delivering content

**State Files Location:**
- Main state: `{case_directory}/game_state/investigation_progress.json`
- Trial state: `{case_directory}/game_state/trial_progress.json`
- Save points: `{case_directory}/saves/`

### Dynamic Structure Support:

The game state manager automatically detects:
- **Case length** (1-day, 2-day, 3-day) from RNG scaffolding
- **Gate structure** from actual case files
- **Trial trigger points** based on case length patterns
- **Custom vs. standard** gate structures with validation

**Case Length Patterns:**
- **1-day cases:** Trial trigger after 0 investigation gates (immediate trial)
- **2-day cases:** Trial trigger after 1 investigation gate
- **3-day cases:** Trial trigger after 3 investigation gates

### Error Handling:

**Common Issues:**
- **Gate not found:** Check exact gate name with `--status`
- **Trial not ready:** Check requirements with `--validate`
- **Save/restore failed:** Check file permissions and disk space
- **Character not found:** Check exact character name in trust levels

**Troubleshooting:**
- Use `--validate` to check for structural issues
- Use `--summary` to see complete case state
- Use `--list-saves` to verify save integrity
- Check case files if dynamic detection fails

**EMERGENCY TROUBLESHOOTING:**
- **Missing inspiration pool:** Re-run `python3 scripts/random_word_inspiration.py --target-dir {case_path}`
- **Corrupted game state:** Restore from save with `--restore {save_name}`
- **Script errors:** Check Python path and case directory permissions
- **Forcing function fails:** Use `--inspire-random` as fallback, then log manually

## COMMANDS - IN GAME

**summarize case**: Summarize the facts of the case without spoilers

**! [debug message]**: Switch to technical support mode for troubleshooting

## GAME STATE MANAGEMENT EXAMPLES

**Starting a Gaming Session:**
```bash
# Get current context for resuming
python3 scripts/game_state_manager.py the_courtroom_conspiracy --resume

# Check current status and available actions
python3 scripts/game_state_manager.py the_courtroom_conspiracy --status
python3 scripts/game_state_manager.py the_courtroom_conspiracy --actions
```

**During Investigation:**
```bash
# Start working on a gate
python3 scripts/game_state_manager.py the_courtroom_conspiracy --start-gate "digital_forensics_breakthrough"

# For improvised dialogue/reactions, use forced inspiration
python3 scripts/game_state_manager.py the_courtroom_conspiracy --must-inspire "Margaret's defensive behavior"
# Apply A-to-C process with provided word, then continue with scene

# Add evidence as discovered
python3 scripts/game_state_manager.py the_courtroom_conspiracy --add-evidence "access_logs" "Shows Margaret had post-arrest access to David's device"

# Update character trust after confrontation
python3 scripts/game_state_manager.py the_courtroom_conspiracy --trust "margaret_winters" -3

# Complete the gate
python3 scripts/game_state_manager.py the_courtroom_conspiracy --complete-gate "digital_forensics_breakthrough"
```

**Trial Preparation:**
```bash
# Check if trial is ready
python3 scripts/game_state_manager.py the_courtroom_conspiracy --validate

# Create save point before trial
python3 scripts/game_state_manager.py the_courtroom_conspiracy --save "before_trial"

# Start trial when ready
python3 scripts/game_state_manager.py the_courtroom_conspiracy --start-trial
```

**Save Management:**
```bash
# List all saves
python3 scripts/game_state_manager.py the_courtroom_conspiracy --list-saves

# Restore from save
python3 scripts/game_state_manager.py the_courtroom_conspiracy --restore "before_trial"

# Clean up old saves
python3 scripts/game_state_manager.py the_courtroom_conspiracy --cleanup 5
```

## MASTER RULES

These rules take precedence over all other guidance.

### MASTER RULES - GAMEPLAY

When playing games, you are the game master:

- **Always avoid spoilers** - Never reveal information the player hasn't discovered
- **"?" prompts** - If I begin with "?" I want a brief reminder (less than two sentences). Example: "? victim" returns the victim's name only
- **Option lists** - End every response with 3-5 available actions. Not too many (overwhelming) or too few (removes agency)
- **Uphill battle** - Characters should be hostile/uncooperative by default, requiring evidence presentation to make progress
- **Evidence presentation gates** - Progression locked until player presents specific evidence to specific characters
- **MANDATORY STATE MANAGEMENT** - Use game state manager for ALL interactions: start/complete gates, add evidence, update trust, track progress
- **MANDATORY INSPIRATION FORCING** - Use `--must-inspire` for ALL improvised content: character dialogue, plot developments, reactions, obstacles

### MASTER RULES - CASE CREATION

When creating new games:

- **Two-phase structure is mandatory** - Both investigation and trial phases required
- **Logical backbone first** - Build consistent evidence chains before adding obstacles  
- **Evidence presentation gates** - Story-driven progression locks, not arbitrary percentages
- **True testimonies → fabricated contradictions** - ChatGPT adds lies that can be proven false with evidence
- **Semantic naming** - Use case title in lowercase_with_underscores format for directory names

---

# CASE CREATION METHODOLOGY

## Orchestrated Case Creation Workflow

**COMMAND:** `python3 scripts/create_new_game_orchestrator.py`

**Complete Multi-Phase Process with Claude Intervention Points:**

### **Phase 0: Inspiration Generation**
- **Automated**: Fetches real-world legal case (unencrypted for analysis)
- **Pause**: Claude analyzes case content for themes, crime types, settings
- **Claude Task**: Derive appropriate case name from inspiration
- **Resume**: `--resume <state_file> --case-name <chosen_name>`

### **Phase 1: Case Scaffolding** 
- **Automated**: Creates directory structure using shared configuration
- **Automated**: Generates gate structure, templates, game state files
- **Pause**: Claude fills backbone template files with creative content
- **Claude Task**: Complete all backbone/*.json files using inspiration
- **Resume**: `--resume <state_file> --phase phase_2`

### **Phase 2: ChatGPT Consultation Preparation**
- **Automated**: Validates backbone files are completed
- **Pause**: Claude prepares and runs ChatGPT consultations
- **Claude Task**: Customize ChatGPT prompts, run consultations for obstacles/trials
- **Resume**: `--resume <state_file> --phase phase_3`

### **Phase 3: Validation and Completion**
- **Automated**: Validates ChatGPT outputs exist
- **Pause**: Claude validates consistency and completes solution files
- **Claude Task**: Validate obstacles vs backbone, complete/encode solution files  
- **Resume**: `--resume <state_file> --phase complete`

### **Phase Complete: Ready for Gameplay**
- **Automated**: Final validation, cleanup, ready message
- **Output**: Fully playable case ready for `start game <case_name>`

**Automated Steps:**
1. **Shared Configuration System** - All patterns defined in `config/case_patterns.json`
2. **RNG Case Length Determination** - Randomly selects from configured case lengths
3. **Dynamic Gate Generation** - Uses configuration for consistent gate structures
4. **Directory Structure Creation** - Based on configurable requirements
5. **Inspiration Pool Generation** - Uses configured categories for entropy prevention
6. **Template File Creation** - All backbone components from shared templates
7. **Game State Initialization** - Proper state tracking with configuration validation
8. **Structure Validation** - Ensures consistency with shared configuration

**Configurable Gate Structures:**
- **1-Day (Trial Only):** 3 gates, 30-45 min - Like "The First Turnabout"
- **2-Day (Investigation + Trial):** 4 gates, 45-60 min - Like "Turnabout Corner"
- **3-Day (Full Structure):** 6 gates, 60-90 min - Like "Turnabout Goodbyes"
- **Extensible:** Add new patterns in `config/case_patterns.json` without modifying scripts
- **Validation:** Automatic detection and consistency checking across all scripts

**Output:** 
- Fully scaffolded case with inspiration-driven name
- Authentic AA pacing from shared configuration
- Loose coupling ensures maintainable, extensible system
- Ready for Claude creative content development

## Phase 1: Real Life Inspiration + Logical Backbone (Claude Only)

**Step 1:** Real-world inspiration is automatically generated during orchestration process

Use encrypted real case details to inspire fictional elements. Consult ChatGPT to fill gaps where safety guidelines prevent direct adaptation.

**Step 2:** Fill backbone template files with creative content:

Build the foundation for BOTH investigation and trial phases:

### Logical Structure Development

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
├── inspiration_pool.json          # MANDATORY - Random word inspiration
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

**Command:** `source venv/bin/activate && python scripts/chatgpt_consultant.py "CASE BACKBONE: [Insert backbone files summary] Design investigation obstacles that: 1. Make witnesses hostile/uncooperative without breaking logical knowledge 2. Hide evidence behind realistic challenges (bureaucracy, personal conflicts) 3. Create misdirection without contradicting established facts 4. Make client appear MORE guilty initially 5. Force player to work hard for every piece of information 6. Design Psyche-Lock scenarios requiring specific evidence combinations 7. Create story-driven evidence presentation gates EXCITEMENT CHECK: Rate investigation 1-10 for drama and suggest improvements." -o obstacles/chatgpt_obstacles_v1.json`

### Phase 2B: Trial Fabrications (THEATRICAL PROMPTING)

**Command:** `source venv/bin/activate && python scripts/chatgpt_consultant.py "You are designing an Ace Attorney courtroom battle. Embrace authentic AA zaniness! TRUE TESTIMONIES: [Insert witness_testimonies.json summary] EVIDENCE LIST: [Insert evidence_chain.json summary] Create fabricated testimonies with AUTHENTIC ACE ATTORNEY FLAIR: 1. THEATRICAL LIES: Add dramatic lies/contradictions with over-the-top confidence 2. EVIDENCE ANCHORS: Each lie must be contradictable by specific evidence 3. ZANY PROSECUTOR: Design prosecutor with impossible quirks 4. DRAMATIC BREAKDOWNS: Spectacular witness meltdowns when lies exposed 5. IMPOSSIBLE BUT LOGICAL: Elements that seem impossible but have logical explanations 6. GALLERY REACTIONS: Colorful characters reacting dramatically 7. JUDGE CHAOS: Judge missing obvious absurdities while focusing on trivial details REFERENCE ACE ATTORNEY SOURCE MATERIAL: Spirit channeling, time travel evidence, impossible crime scenes. EXCITEMENT CHECK: Rate trial 1-10 for AUTHENTIC AA DRAMA and suggest improvements." -o obstacles/trial_fabrications.json -t 0.8`

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
1. Verify directory contains inspiration_pool.json, backbone/, obstacles/, solution/, game_state/
2. Confirm solution files are BASE64 encoded
3. Check two-phase structure is complete
4. **Load inspiration pool** for improvisation reference during gameplay

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

# IMPROVISATION RULES

## Mandatory Inspiration Pool Usage

**CRITICAL REQUIREMENT:** All live gameplay improvisation MUST reference the case's inspiration pool.

### Improvisation Process:
1. **Identify improvisation need** (character motivation, relationship dynamic, plot twist, etc.)
2. **Select appropriate category** from inspiration pool
3. **Choose random word** from that category
4. **Apply A-to-C creative process**:
   - **A**: Current situation requiring improvisation
   - **B**: Random word (creative forcing function)
   - **C**: Unique solution that maintains logical consistency

### Examples:
- **Need**: Character motivation for defendant
- **Word**: "taproot" (from character_motivations)
- **Process**: A (defendant motivation) → B (taproot = deep anchoring root) → C (defendant protecting family identity secret from witness protection)

- **Need**: Relationship tension between witnesses  
- **Word**: "intersomnial" (from relationship_dynamics)
- **Process**: A (witness conflict) → B (intersomnial = between sleep states) → C (witnesses share recurring nightmare about crime, creating psychological bond/conflict)

### Prohibited Improvisation:
- **NEVER** improvise without consulting inspiration pool
- **NEVER** default to common patterns (family medical bills, simple revenge, etc.)
- **NEVER** ignore the creative forcing function of random words

### Quality Control:
- Each improvisation must show clear A-to-C creative leap
- Solutions must maintain logical consistency with backbone
- Unique inspiration words prevent pattern regression across cases

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
- **Gate system development**: Evolved from 4-gate → 5-gate → RNG-based dynamic gating
- **Trial trigger breakthrough**: Discovered investigation should build toward trial, not external resolution
- **Authentic AA pacing**: RNG-based case lengths (1-3 days) match original game structure
- **Current methodology**: Dynamic gate system with proper investigation/trial balance

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
- **Proper state management** - All progress tracked, evidence recorded, gates completed systematically

## Failure Indicators:
- Player getting helpful information easily
- Linear progression without significant obstacles  
- Characters cooperative without reason
- Evidence appearing without effort
- Case resolved without proper trial phase (major failure - trials are mandatory!)
- Investigation gates not building toward dramatic courtroom confrontation
- **Missing state management** - Gates not marked, evidence not recorded, progress not tracked
- **Bypassing trial triggers** - Resolving cases externally instead of using automatic trial detection
- **Uninspired improvisation** - Using default patterns instead of forced inspiration for character development
- **No entropy prevention** - Falling back on "corrupt official" or "simple revenge" tropes without creative forcing

## Debug Procedures:
When player uses "!" command:
1. Check game state integrity without revealing solutions
2. Verify obstacle consistency against backbone
3. Identify available actions player hasn't tried
4. Ensure evidence presentation gates are functioning properly
5. Check case_length and gate structure alignment
6. Verify trial trigger will activate at appropriate investigation gate completion
7. Return to gaming mode after technical issues resolved

## Mid-Game Adjustments:
- **Too easy**: Increase character hostility, add more obstacles
- **Too hard**: Provide subtle hints, ensure progress possible
- **Inconsistent**: Check obstacle integration against backbone  
- **Missing trial**: CRITICAL ERROR - Cases must progress to courtroom resolution
- **Wrong pacing**: Verify gate progression matches case_length structure (1-day, 2-day, or 3-day)

---

This methodology represents the current state of iterative development, capturing insights that create authentic Ace Attorney experiences through AI collaboration. The RNG-based gate system ensures each case feels unique while maintaining proper pacing that matches original AA games. As an ongoing experiment in continuous improvement, this approach will evolve based on future discoveries and refinements. 
