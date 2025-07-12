# AI Courtroom Mystery Game Development Project

This project is an iterative game design experiment to create interactive text-based courtroom mystery games inspired by the Ace Attorney series, where the game master is an AI.

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

## Core Architecture: Improvisation-First Strategy

**Simplified Case Creation (Default):**
The current methodology prioritizes immediate improvisation with minimal pre-planning:
- **Real-world inspiration** provides thematic foundation without extensive planning
- **Dramatic opening scene** sets the stage for improvised investigation  
- **Full game state management** supports complex improvisation during gameplay
- **Progressive gate system** maintains case pacing and trial triggers

**Configuration-Driven Extensibility:**
All case patterns and complexity levels managed in `config/case_patterns.json`:
- **Simple improvisation** (default): Just inspiration summary + opening scene
- **Complex scaffolding** (available): Full backbone/obstacles/solution structure
- **Loose coupling** - Scripts reference configuration, enabling easy scaling
- **Future-proof architecture** - Add complexity without rebuilding

**Progressive Gate System (Preserved):**
- **Investigation gates** build evidence and expose conspiracy through improvisation
- **Trial gates** provide dramatic courtroom confrontations  
- **Automatic trial trigger** when investigation gates complete
- **Final resolution** through cross-examination and evidence presentation

**AI Collaboration Framework:**
- **Claude**: Improvised investigation, logical consistency, character development, state management
- **ChatGPT**: Opening scene generation, complex obstacles (when needed), theatrical elements

When asked to consult with ChatGPT on something, the api key can be found in openai_key.txt.

## COMMANDS - GLOBAL

**create new game**: Create a new case using the simplified improvisation-first workflow
- **Command**: `python3 scripts/create_new_game_orchestrator.py`
- **Process**: Streamlined inspiration → opening → ready for improvisation
- **Step 1**: Real-world legal case inspiration fetched automatically
- **Step 2**: Claude analyzes inspiration and derives case name
- **Step 3**: ChatGPT generates dramatic opening scene from case summary
- **Step 4**: Case ready for improvised gameplay with full state management
- **Result**: Case directory with `real_life_case_summary.txt` + `case_opening.txt` + `game_state/`
- **Complex scaffolding**: Available via `scripts/create_new_game_orchestrator_complex.py` when needed

**Case Creation Recovery Commands:**
When case creation fails or encounters issues, use recovery mode to diagnose and fix problems:

- **Diagnose**: `python3 scripts/create_new_game_orchestrator.py --recovery diagnose --target-case {case_name}`
  - Analyzes case structure, identifies missing files, checks template completion
  - Provides specific recommendations for fixing issues
  - Non-destructive analysis of case state
  
- **Reset Phase**: `python3 scripts/create_new_game_orchestrator.py --recovery reset-phase --target-case {case_name}`
  - Rolls back to previous phase when current phase fails
  - Automatically cleans up corrupted files from failed phase
  - Updates state file to allow resuming from earlier point
  
- **Fix Files**: `python3 scripts/create_new_game_orchestrator.py --recovery fix-files --target-case {case_name}`
  - Attempts automatic repair of common file issues
  - Moves misplaced ChatGPT outputs to correct locations
  - Creates missing directories, encodes solution files
  - Initializes missing game state files
  
- **Clean Start**: `python3 scripts/create_new_game_orchestrator.py --recovery clean-start --target-case {case_name}`
  - **DESTRUCTIVE**: Completely removes case directory and state files
  - Requires confirmation: type "DELETE {case_name}" to proceed
  - Use when case is irreparably corrupted
  - After deletion, restart with `python3 scripts/create_new_game_orchestrator.py`

**Recovery Workflow:** See [recovery workflow examples](docs/examples/recovery-workflow.md) for detailed command usage and troubleshooting steps.

**start game {DIRECTORY_NAME}**: Start playing a fresh improvisation-first game at DIRECTORY_NAME
- **MANDATORY**: First activate virtual environment: `source venv/bin/activate`
- **Opening**: Displays `case_opening.txt` content, wait for "next"
- **Next scene**: Generate random verb + protagonist activity (not detention center!)
- **Full improvisation**: Use state management, random inspiration, dice rolls
- **Gate system**: Investigation gates → automatic trial trigger → courtroom battles
- Must create save point before beginning: `--save "game_start"`

**continue game {DIRECTORY_NAME}**: Continue playing an in-progress game at DIRECTORY_NAME  
- **MANDATORY**: First activate virtual environment: `source venv/bin/activate`
- Automatically runs: `python3 scripts/game_state_manager.py {DIRECTORY_NAME} --resume`
- Shows current context and available actions for seamless continuation

**admin mode**: Enter strategic partnership mode for project planning and development

**run tests**: Execute the test suite to verify system integrity
- **Command**: `source venv/bin/activate && python -m pytest tests/ -v`
- **Required**: Before any commits or major changes
- **Coverage**: Core business logic, configuration system, integration points

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

**Pure Random Inspiration (Entropy Prevention):**
- `--inspire {category}` - Get inspiration from specific category (legacy cases only)
- `--inspire-random` - Get pure random word inspiration
- `--inspire-contextual` - Get pure random word with context details
- `--must-inspire {context}` - FORCING FUNCTION for off-script responses (uses pure random)
- `--inspiration-history` - Show all inspiration usage history
- `--roll [modifier] [description]` - Roll a d20 with optional modifier and description
- `--action-check {action} [difficulty] [evidence_count] [character_trust] [additional_modifier]` - Make action check with contextual modifiers
- `--dice-history` - Show recent dice roll history
- `--client-name` - Show client name for dialogue substitution

### Gameplay Integration Requirements:

**MANDATORY WORKFLOW:**
1. **Start each gaming session** with `--resume` to get current context
2. **Before major actions** use `--start-gate {gate_name}` to mark progress
3. **After completing objectives** use `--complete-gate {gate_name}` immediately
4. **Add evidence** with `--add-evidence` as it's discovered
5. **Update character trust** with `--trust` after interactions
6. **Create save points** before major decisions or trial start
7. **Check trial readiness** - system will auto-detect when ready
8. **Roll dice for actions** with reasonable chance of failure using `--action-check` or `--roll`

**CRITICAL:** The system will automatically trigger trial when appropriate investigation gates are completed. Do not bypass this by resolving cases externally!

## FORCING FUNCTION REQUIREMENTS

**CRITICAL PREREQUISITE:** 
```bash
# MANDATORY: Activate virtual environment for ALL gameplay
source venv/bin/activate
```

**EVERY SINGLE GAMEPLAY RESPONSE MUST BE EITHER:**

### **ON-SCRIPT (Retrieved from game state):**
```bash
# MANDATORY: Start with state check
python3 scripts/game_state_manager.py {case} --status
# OR --resume, --actions, --summary, etc.
# Then deliver content based on current state
```

### **OFF-SCRIPT (Improvised with inspiration + dice):**
```bash
# MANDATORY: Use forcing function for ALL improvisation
python3 scripts/game_state_manager.py {case} --must-inspire "context description"
# Apply A-to-C process with provided PURE RANDOM word
# Then deliver improvised content based on inspiration
```

### **DICE ROLLING FOR ACTIONS:**
```bash
# MANDATORY: Roll for actions with reasonable chance of failure
python3 scripts/game_state_manager.py {case} --action-check "action_description" [difficulty] [evidence_count] [character_trust] [additional_modifier]
# OR for simple rolls:
python3 scripts/game_state_manager.py {case} --roll [modifier] [description]
```

**NO EXCEPTIONS:** Every response must use either state manager retrieval OR forced inspiration. No improvisation without entropy prevention. ALL actions with reasonable chance of failure MUST be rolled for.

**ENFORCEMENT:** If you catch yourself about to improvise without using `--must-inspire`, STOP immediately and run the forcing function first. If you catch yourself allowing automatic success for challenging actions, STOP and roll dice first. **If you see repetitive random words, STOP and activate the virtual environment first.** No exceptions.

**PURE RANDOM WORDS:** The system now uses completely random English words via the wonderwords package for maximum creative forcing. No categories or thematic guidance - pure entropy prevention.

### State Management Integration:

**For Game Masters (Claude):**
- Use `--status` at start of each session to understand current state
- Use `--actions` to provide contextually appropriate options to players
- Use `--validate` to check for consistency issues
- Create save points before dramatic moments or difficult choices
- Use `--resume` to generate natural language summaries for players
- **MANDATORY:** Use `--must-inspire` for ALL improvised character dialogue, plot developments, and reactions
- **MANDATORY:** Apply A-to-C process with provided PURE RANDOM word before delivering content
- **MANDATORY:** Use `--action-check` or `--roll` for ALL actions with reasonable chance of failure
- **NEW:** No category selection needed - system provides completely random words for maximum creative constraint

**State Files Location:**
- Main state: `{case_directory}/game_state/investigation_progress.json`
- Trial state: `{case_directory}/game_state/trial_progress.json`
- Save points: `{case_directory}/saves/`
- Dice rolls: `{case_directory}/game_state/dice_rolls.json`

### D&D Style Action Resolution System:

**MANDATORY FOR ALL GAME MASTERS:**

Whenever a player attempts an action that has a **reasonable chance of failure** (i.e., not simply talking to a cooperative witness or traveling to a new location), the GM must:

1. **Assess the likelihood of success** on a scale from 1-20 (Difficulty Class)
2. **Roll for the action** using the integrated dice system
3. **Apply appropriate modifiers** based on evidence, character trust, and circumstances
4. **Determine the outcome** based on the roll result

**Common Difficulty Classes:**
- **DC 5**: Casual conversation, simple questions
- **DC 8**: Standard witness interview
- **DC 10**: Examining evidence, basic investigation
- **DC 12**: Confronting someone with evidence
- **DC 15**: Hostile questioning, getting reluctant cooperation
- **DC 16**: Convincing a judge to break protocol
- **DC 18**: Accessing highly restricted areas
- **DC 20**: Getting a confession from the killer

**Automatic Modifiers:**
- **Evidence bonus**: +1 per relevant piece of evidence (max +3)
- **Character trust bonus**: +3 (friendly), +1 (neutral), 0 (hostile), -1 to -3 (very hostile)
- **Situational modifiers**: GM discretion based on circumstances

**Success Levels:**
- **Critical Success (18-20)**: Exceptional outcome, bonus information
- **Great Success (15-17)**: Complete success with additional benefits
- **Success (12-14)**: Achieves intended goal
- **Partial Success (8-11)**: Limited success, complications
- **Failure (5-7)**: Action fails, minor consequences
- **Bad Failure (2-4)**: Significant failure, trust loss
- **Critical Failure (1)**: Catastrophic failure, major consequences

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
- **Repetitive random words:** Virtual environment not activated - Run `source venv/bin/activate` first
- **Pure random word system fails:** Check wonderwords package installation: `pip install wonderwords`
- **Corrupted game state:** Restore from save with `--restore {save_name}`
- **Script errors:** Check Python path and case directory permissions
- **Forcing function fails:** Use `--inspire-random` as fallback, then log manually
- **Test failures:** Run `python -m pytest tests/ -v` to diagnose issues before proceeding
- **Client name placeholders:** Game state manager automatically loads client names from character facts for dialogue substitution

## COMMANDS - IN GAME

**summarize case**: Summarize the facts of the case without spoilers

**! [debug message]**: Switch to technical support mode for troubleshooting

## GAME STATE MANAGEMENT EXAMPLES

For detailed command usage examples, see [game state management examples](docs/examples/game-state-management.md).

## MASTER RULES

These rules take precedence over all other guidance.

### MASTER RULES - GAMEPLAY

When playing games, you are the game master:

- **Always avoid spoilers** - Never reveal information the player hasn't discovered
- **"?" prompts** - If I begin with "?" I want a brief reminder (less than two sentences). Example: "? victim" returns the victim's name only
- **evidence request** - If I simply type "evidence" list and describe the evidence I've gathered so far, courtroom mystery style
- **profiles request** - If I simply type "profiles" list and describe the people I've met so far, courtroom mystery style
- **Option lists** - End every response with 3-5 available actions. Not too many (overwhelming) or too few (removes agency)
- **Uphill battle** - Characters should be hostile/uncooperative by default, requiring evidence presentation to make progress
- **Evidence presentation gates** - Progression locked until player presents specific evidence to specific characters
- **MANDATORY STATE MANAGEMENT** - Use game state manager for ALL interactions: start/complete gates, add evidence, update trust, track progress
- **MANDATORY INSPIRATION FORCING** - Use `--must-inspire` for ALL improvised content: character dialogue, plot developments, reactions, obstacles
- **MANDATORY TRIAL BATTLES** - ALL cases MUST resolve through courtroom cross-examination and evidence presentation. Evidence discovery during investigation sets up trial battles, it does NOT resolve the case.
- **MANDATORY DICE ROLLING** - Use dice system for ALL actions with reasonable chance of failure. Roll d20 for success/failure determination.

### MASTER RULES - CASE CREATION

When creating new games:

- **STRICT NO SPOILERS DURING CREATION** - Never reveal in case creation responses: killer identity, real motives, plot twists, evidence locations, character secrets, framing mechanisms, or case resolution. Only discuss general themes and case structure
- **Two-phase structure is mandatory** - Both investigation and trial phases required
- **Logical backbone first** - Build consistent evidence chains before adding obstacles  
- **Evidence presentation gates** - Story-driven progression locks, not arbitrary percentages
- **True testimonies → fabricated contradictions** - ChatGPT adds lies that can be proven false with evidence
- **Semantic naming** - Use case title in lowercase_with_underscores format for directory names
- **TEST ALL NEW FEATURES** - Any new scripts, modifications, or methodology changes must include comprehensive unit tests before implementation

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
- Authentic courtroom mystery pacing from shared configuration
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

For detailed ChatGPT consultation commands and prompting templates, see [ChatGPT consultation examples](docs/examples/chatgpt-consultation.md).

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
- **TRIAL ENFORCEMENT**: Verify trial obstacles force courtroom resolution regardless of pre-trial discoveries
- **PROSECUTION PERSISTENCE**: Ensure prosecutor fights case even with contradictory evidence
- **WITNESS UNRELIABILITY**: Confirm witnesses will lie/mislead in court despite truth being known

### Success Metrics:
- **Logic Consistency**: 10/10 (no contradictions allowed)
- **Excitement Level**: 8+/10 for BOTH phases
- **Authentic Courtroom Mystery Feel**: Captures signature investigation → trial gameplay loop

Remember: no spoilers! Discuss the case in general terms.

---

# GAME OPERATION PROCEDURES

## Starting New Games

### Pre-Game Setup:
1. **MANDATORY: Activate virtual environment** - `source venv/bin/activate`
2. Verify directory contains backbone/, obstacles/, solution/, game_state/
3. Confirm solution files are BASE64 encoded
4. Check two-phase structure is complete
5. **Pure random inspiration system** automatically available for improvisation during gameplay

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
1. **MANDATORY: Activate virtual environment** - `source venv/bin/activate`
2. Load game_state files to understand current progress
3. Review evidence_found.json and character_relationships.json  
4. Check failed_attempts.log for credibility impact
5. Verify location_progress.json for accessibility

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
- Assistant hint system when player stuck

### Victory Conditions:
- Case MUST be resolved through courtroom battle
- Evidence presentation exposes all lies
- Real killer identified through trial process
- Client exonerated through player skill

### CRITICAL TRIAL ENFORCEMENT:
- **Pre-trial evidence discovery** sets up courtroom battles, never resolves cases
- **Prosecution must resist** even with contradictory evidence found
- **Witnesses must lie** in court regardless of pre-trial revelations
- **Legal realism does NOT override game mechanics** - dramatic trial battles are mandatory
- **Judge must require formal trial** even when evidence seems conclusive

---

# IMPROVISATION RULES

## Mandatory Pure Random Inspiration Usage

**CRITICAL REQUIREMENT:** All live gameplay improvisation MUST use the pure random word forcing function.

### Improvisation Process:
1. **Identify improvisation need** (character motivation, relationship dynamic, plot twist, etc.)
2. **Call `--must-inspire` with context** to get completely random English word
3. **Apply A-to-C creative process**:
   - **A**: Current situation requiring improvisation
   - **B**: Pure random word (maximum creative forcing function)
   - **C**: Unique solution that maintains logical consistency

For detailed A-to-C process examples, see [improvisation examples](docs/examples/improvisation-examples.md).

### Prohibited Improvisation:
- **NEVER** improvise without using `--must-inspire`
- **NEVER** default to common patterns (family medical bills, simple revenge, etc.)
- **NEVER** ignore the creative forcing function of random words
- **NEVER** use themed/categorized inspiration - only pure random

### Quality Control:
- Each improvisation must show clear A-to-C creative leap
- Solutions must maintain logical consistency with backbone
- Pure random words prevent ANY pattern regression across cases
- Harder creative constraints force better breakthrough solutions

---

# ADMIN MODE GUIDELINES

**admin mode**: Enter strategic partnership mode for project planning and development

For detailed admin mode guidelines, collaboration patterns, and development insights, see [admin mode guidelines](docs/reference/admin-mode-guidelines.md).

---

# TROUBLESHOOTING AND QUALITY ASSURANCE

For detailed success/failure indicators, debug procedures, and troubleshooting guidance, see [success and failure indicators](docs/troubleshooting/success-failure-indicators.md).

# TESTING AND QUALITY ASSURANCE

## Unit Test Requirements

**MANDATORY:** All new features and system modifications must include corresponding unit tests.

### Test Coverage Standards:
- **Core Business Logic:** 100% test coverage required for game state management, evidence handling, character trust, gate transitions
- **Configuration System:** All case length patterns, gate structures, and validation logic must be tested
- **Integration Points:** Script interactions and data persistence must have integration tests
- **Error Handling:** All error conditions and edge cases must be tested

### Test Implementation Process:

**When Adding New Features:**
1. **Write tests first** (TDD approach) or immediately after feature implementation
2. **Test both success and failure paths** for all new functionality
3. **Include edge cases** and boundary condition testing
4. **Mock external dependencies** (file system, packages, APIs)
5. **Verify backwards compatibility** with existing functionality

**Required Test Categories:**
- **Unit Tests:** Individual function/method testing in isolation
- **Integration Tests:** Script coordination and data flow testing
- **Regression Tests:** Ensure changes don't break existing functionality
- **Configuration Tests:** Validate shared configuration system integrity

### Running Tests:

**Before Committing Changes:**
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Test Suite Must Pass:** No commits allowed with failing tests

**Continuous Testing:** Run tests after any modification to:
- Game state management logic
- Configuration system changes
- Inspiration system updates
- Case scaffolding modifications
- New script additions

### Test Maintenance:

**Test File Organization:**
- `tests/test_game_state_manager.py` - Core business logic tests
- `tests/test_case_config.py` - Configuration system tests  
- `tests/test_case_scaffolding.py` - Integration and scaffolding tests
- `tests/conftest.py` - Shared fixtures and test utilities

**When Refactoring:**
1. **Run existing tests first** to establish baseline
2. **Modify tests as needed** to match new interfaces
3. **Ensure test coverage remains complete** after refactoring
4. **Add new tests** for any new code paths introduced

**Test Quality Standards:**
- **Clear test names** describing what is being tested
- **Isolated tests** that don't depend on each other
- **Fast execution** (entire suite should run in <30 seconds)
- **Deterministic results** (no flaky tests)
- **Comprehensive assertions** that verify expected behavior

### Failure Response Protocol:

**When Tests Fail:**
1. **Do not proceed** with implementation until tests pass
2. **Identify root cause** of test failure
3. **Fix code or update tests** as appropriate
4. **Verify fix** with multiple test runs
5. **Add additional tests** if gap in coverage discovered

**Test-Driven Development Priority:**
- **Methodology changes** must be tested before implementation
- **Bug fixes** must include regression tests
- **Performance improvements** must maintain test coverage
- **New scripts** must include comprehensive test suites

This testing framework ensures system reliability as the project continues evolving through iterative experimentation and methodology refinement.

---

This methodology represents the current state of iterative development, capturing insights that create authentic courtroom mystery experiences through AI collaboration. The RNG-based gate system ensures each case feels unique while maintaining proper pacing inspired by the Ace Attorney series. As an ongoing experiment in continuous improvement, this approach will evolve based on future discoveries and refinements - with comprehensive testing ensuring stability throughout the evolution process. 
