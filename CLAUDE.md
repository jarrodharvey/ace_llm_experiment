# AI Courtroom Mystery Game Development Project

This project creates interactive text-based courtroom mystery games inspired by the Ace Attorney series, where the game master is an AI.

The experiment successfully combines:
- **Fun** - Engaging puzzle-solving and dramatic courtroom battles
- **Challenge** - Evidence presentation gates and hostile characters requiring genuine detective work  
- **An engaging story** - Murder mysteries with logical plot progression
- **Logical consistency** - All evidence chains and character knowledge must align perfectly

## Project Organization

**Directory Structure:**
- **Active cases**: Named by case title in `lowercase_with_underscores` format
- **Archive**: All previous experimental cases stored in `previous_cases/` directory
- **Lessons learned**: See [`docs/reference/lessons-learned-archive.md`](docs/reference/lessons-learned-archive.md)

## Core Architecture: Improvisation-First Strategy

**Simplified Case Creation:**
The methodology prioritizes immediate improvisation with minimal pre-planning:
- **Real-world inspiration** provides thematic foundation without extensive planning
- **Dramatic opening scene** sets the stage for improvised investigation  
- **Full game state management** supports complex improvisation during gameplay
- **Progressive gate system** maintains case pacing and trial triggers

**AI Collaboration Framework:**
- **Claude**: Improvised investigation, logical consistency, character development, state management
- **ChatGPT**: Opening scene generation, theatrical elements

When asked to consult with ChatGPT on something, the api key can be found in openai_key.txt.

## EVERGREEN EXPERIMENT RULE

**CRITICAL AI DIRECTIVE:** This project is an evergreen experiment focused on continuous improvement without legacy burden.

**NEVER IMPLEMENT BACKWARD COMPATIBILITY:**
- **No legacy case support** - Old cases that break with new features should be archived
- **No migration scripts** - System updates apply to new cases only
- **No backward compatibility layers** - Clean, modern implementation always takes precedence
- **No legacy code paths** - Remove outdated functionality completely when updating

**RATIONALE:**
- **Prevents codebase bloat** - Maintains clean, focused implementation
- **Accelerates development** - No need to consider legacy constraints
- **Improves AI logic** - No complex compatibility decision trees
- **Encourages innovation** - Freedom to implement better solutions without compromise

**WHEN SYSTEM CHANGES BREAK EXISTING CASES:**
1. **Archive broken cases** to `previous_cases/` directory
2. **Update documentation** to reflect new methodology
3. **Create fresh test cases** using new system
4. **Focus on forward progress** - no time spent on legacy support

**ENFORCEMENT:** Any AI suggestion of backward compatibility should be immediately rejected in favor of clean, modern implementation.

## COMMANDS - GLOBAL

**create new game**: Create a new case using the improvisation-first workflow
- **Command**: `python3 scripts/create_new_game_orchestrator.py`
- **Process**: Streamlined inspiration → opening → ready for improvisation
- **Step 1**: Real-world legal case inspiration fetched automatically
- **Step 2**: Claude analyzes inspiration and derives case name
- **Step 3**: ChatGPT generates dramatic opening scene from case summary
- **Step 4**: Case ready for improvised gameplay with full state management
- **Result**: Case directory with `real_life_case_summary.txt` + `case_opening.txt` + `game_state/`

**CRITICAL ERROR HANDLING REQUIREMENT:**
When case creation errors occur, you MUST identify and fix the root cause rather than pursuing manual workarounds:
- **Step 1**: Analyze the specific error message and trace to its source code location
- **Step 2**: Fix the underlying issue in the appropriate script or configuration
- **Step 3**: Test the fix to ensure it resolves the problem completely
- **Step 4**: Update documentation or tests if the fix reveals a systemic issue
- **NEVER**: Skip error analysis in favor of manual case creation or workarounds
- **NEVER**: Ignore broken scripts and proceed with partial implementations

**start game {DIRECTORY_NAME}**: Start playing a fresh improvisation-first game at DIRECTORY_NAME
- **MANDATORY VALIDATION FIRST**: Run comprehensive pre-game validation with root cause analysis
- **Validation Command**: `python3 scripts/start_game_validator.py {DIRECTORY_NAME}`
- **ZERO TOLERANCE RULE**: If validation fails, you MUST investigate and fix root causes before proceeding
- **NO WORKAROUNDS**: Never attempt manual fixes, partial starts, or validation bypasses
- **Opening Display Logic**: 
  - Read and display the contents of `{DIRECTORY_NAME}/case_opening.txt`
  - End with "Type 'next' to continue"
  - Wait for user to type "next" before proceeding
  - After "next", use `python3 scripts/game_state_manager.py {DIRECTORY_NAME} --resume` to begin gameplay
- **Game Flow**: Validation → opening text → user types "next" → state manager takes over
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
- `--inspire-random` - Get pure random word inspiration
- `--inspire-contextual` - Get pure random word with context details
- `--must-inspire {context}` - FORCING FUNCTION for off-script responses (uses pure random)
- `--inspiration-history` - Show all inspiration usage history
- `--roll [modifier] [description]` - Roll a d20 with optional modifier and description
- `--action-check {action} [difficulty] [evidence_count] [character_trust] [additional_modifier]` - Make action check with contextual modifiers
- `--dice-history` - Show recent dice roll history
- `--client-name` - Show client name for dialogue substitution

**Character Name Generation (Anti-Repetition):**
- `--generate-name [role]` - Generate unique character name with optional role hint (e.g., "judge", "prosecutor")
- `--generate-names {count}` - Generate multiple unique character names at once
- `--name-suggestions "{description}"` - Get multiple name options based on character description
- `--generate-age [role]` - Generate appropriate age for character with optional role-based constraints
- `--generate-occupation {age} {role}` - Generate occupation for specific age and role combination
- **Uniqueness Guarantee**: Names automatically avoid duplicates from entire project history
- **Age Generation**: Role-appropriate ages (judges: 40-70, students: 18-30, security: 21-55, etc.)
- **Occupation Mapping**: Role hints map to appropriate occupations (detective→detective, student→student)
- **Faker Integration**: Fallback to Faker's job generator for creative occupations when no role mapping exists
- **Supported Roles**: Judge, prosecutor, witness, detective, police, lawyer, doctor, security guard, student, etc.
- **Usage**: Use for all new character creation to prevent repetitive names across cases

**Red Herring Classification System (Anti-Pattern Prevention):**
- `--generate-name-classified [role]` - Generate complete character (name, age, occupation) with automatic killer/red herring classification
- `--classify-character "{character_name}" {case_length} [role_hint]` - Manually classify character with optional role weighting
- `--check-character-role "{character_name}"` - Check existing character classification (GM reference only)
- `--list-classifications` - List all killer/red herring classifications for case (GM reference only)
- `--classification-stats` - Show classification statistics and expected probabilities
- `--show-spoilers` - **TESTING ONLY**: Reveal actual classifications (never use during gameplay)
- **Case-Length Scaling**: Base killer probability decreases with case length (1-day: 50%, 2-day: 33%, 3-day: 25%)
- **Role-Based Weighting**: Role types affect killer probability for narrative realism:
  - **High Authority (0.3x)**: detective, judge, police, client, prosecutor, doctor - Rare but shocking twists
  - **Normal Authority (1.0x)**: witness, lawyer, court staff, journalist - Standard probability  
  - **High Suspicion (1.8x)**: security guard, business rival, ex-partner, family member, debtor - Likely suspects
- **Combined Probabilities**: Final probability = Base probability × Role weight (capped at 95%)
- **Examples**: 
  - 1-day detective: 50% × 0.3 = 15% killer chance (Christie-style rare twist)
  - 3-day security guard: 25% × 1.8 = 45% killer chance (obvious suspect)
  - 2-day witness: 33% × 1.0 = 33% killer chance (normal)
- **Deterministic RNG**: Same character name + role always gets same classification (based on name + role hash)
- **Base64 Storage**: Classifications stored in encrypted format to prevent player spoilers
- **Spoiler Protection**: Commands hide classifications during gameplay unless `--show-spoilers` is used
- **Purpose**: Prevents predictable patterns while creating appropriate narrative tension and surprise
- **Usage**: Always provide role hints when generating characters to ensure proper weighting
- **CRITICAL**: Never use `--show-spoilers` during actual gameplay - only for testing and debugging

**Family Relationship Management:**
- `--create-family {size} [--family-surname {surname}]` - Create entire family with shared surname
- `--add-family-member "{existing_name}:{relationship}"` - Add family member to existing character
- `--surname-suggestions {existing_names...}` - Get surname suggestions avoiding conflicts
- **Supported Relationships**: spouse, sibling, parent, child, father, mother, son, daughter, brother, sister
- **Automatic Surname Sharing**: Family members automatically share surnames
- **Family Tracking**: System tracks which surnames belong to which families
- **Usage Examples**:
  - `--create-family 3` → Creates parents + child with shared surname
  - `--add-family-member "John Smith:brother"` → Creates "FirstName Smith" as John's brother
  - `--surname-suggestions "John Doe" "Jane Smith"` → Suggests surnames not conflicting with Doe/Smith

**Interactive Trial System (Cross-Examination):**
- `--start-cross-examination "{witness_name}"` - Begin cross-examination of specified witness
- `--press {statement_id}` - Press witness for more details on statement (A, B, C, etc.) - **INFORMATION ONLY**
- `--present {statement_id} "{evidence_name}"` - Present evidence against specific statement - **CASE PROGRESS**
- `--hint [statement_id]` - Get context-aware hint (general or for specific statement)
- `--check-victory` - Check cross-examination victory status and progress
- `--end-cross-examination` - End current cross-examination session
- `--show-statements` - Display current witness statements and available commands
- **Authentic Ace Attorney Experience**: OBJECTION! moments, evidence-based puzzle solving, penalty system
- **Press vs. Present Distinction**: Press actions provide clarifying information only; evidence presentation creates dramatic OBJECTION moments and advances the case
- **Clean UI**: During cross-examination, Available Actions menu is suppressed for cleaner interface; statements and command reminders shown instead
- **OBJECTION Moments**: Evidence presentation triggers authentic courtroom drama with forced inspiration for unique responses
- **Victory Conditions**: Must expose critical lies through correct evidence presentation, not pressing
- **Penalty System**: Wrong evidence presentations accumulate penalties, leading to game over if excessive

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

### **CONTEXT RESTORATION (After context window break):**
```bash
# MANDATORY: Restore complete narrative context first
python3 scripts/game_state_manager.py {case} --list-narrative-saves
python3 scripts/game_state_manager.py {case} --restore-narrative {latest_save.json}
# Then continue with normal ON-SCRIPT or OFF-SCRIPT responses
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

**CONTEXT WINDOW PROTOCOL:** When continuing a case after context window break, ALWAYS restore narrative context first using `--restore-narrative`. Never guess or assume case details.

**ENFORCEMENT:** If you catch yourself about to improvise without using `--must-inspire`, STOP immediately and run the forcing function first. If you catch yourself allowing automatic success for challenging actions, STOP and roll dice first. **If you see repetitive random words, STOP and activate the virtual environment first.** If continuing a case without context restoration, STOP and restore narrative context first. No exceptions.

**PURE RANDOM WORDS:** The system uses completely random English words via the wonderwords package for maximum creative forcing. No categories or thematic guidance - pure entropy prevention.

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

**State Files Location:**
- Main state: `{case_directory}/game_state/investigation_progress.json`
- Trial state: `{case_directory}/game_state/trial_progress.json`
- Save points: `{case_directory}/saves/`
- Dice rolls: `{case_directory}/game_state/dice_rolls.json`
- **Enhanced narrative saves**: `{case_directory}/narrative_saves/`

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

### Enhanced Narrative Save System (Context Window Solution):

**PROBLEM SOLVED:** Context window breaks cause narrative drift - cases shift from assault to murder, victims change identity, evidence significance is lost.

**PERMANENT SOLUTION:** Comprehensive narrative saves at every stage gate completion automatically preserve complete case context.

**Automatic Narrative Preservation:**
- **Complete case facts**: Charges, victim status, defendant details, incident summary
- **Evidence significance**: Not just "what" but "why it matters" and trial implications
- **Character dynamics**: Relationships, secrets, credibility issues, player interactions
- **Plot threads**: Unresolved mysteries, dramatic stakes, emotional investment
- **Legal strategy**: Approach, key arguments, expected objections, evidence presentation plan

**Seamless Context Restoration:**
```bash
# List available narrative saves for case
python3 scripts/game_state_manager.py {case} --list-narrative-saves

# Restore complete narrative context from any save
python3 scripts/game_state_manager.py {case} --restore-narrative {filename.json}

# Get context summary for specific save
python3 scripts/game_state_manager.py {case} --narrative-summary {filename.json}
```

**GUARANTEED CONTINUITY:** No more "who died?" confusion. Cases maintain perfect narrative coherence across any context window break.

**Implementation Details:**
- **Automatic creation**: Enhanced saves trigger on every gate completion
- **Comprehensive context**: Captures narrative essence beyond game mechanics
- **Natural language summaries**: Generated for immediate context restoration
- **Zero data loss**: All critical details preserved for seamless gameplay continuation

### Dynamic Structure Support:

The game state manager automatically detects:
- **Case length** (1-day, 2-day, 3-day) from case structure
- **Gate structure** from actual case files
- **Trial trigger points** based on case length patterns

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

## MASTER RULES

These rules take precedence over all other guidance.

### MASTER RULES - GAMEPLAY

When playing games, you are the game master:

- **Always avoid spoilers** - Never reveal information the player hasn't discovered
- **"?" prompts** - If I begin with "?" I want a brief reminder (less than two sentences). Example: "? victim" returns the victim's name only
- **evidence request** - If I simply type "evidence" list and describe the evidence I've gathered so far, courtroom mystery style
- **profiles request** - If I simply type "profiles" list and describe the people I've met so far, courtroom mystery style
- **save game request** - If I simply type "save game" create a manual save point using game state manager: `--save "manual_save_[timestamp]"` allowing me to close/reopen context window
- **Option lists** - End every response with 3-5 available actions. Not too many (overwhelming) or too few (removes agency)
- **Cross-examination UI** - During cross-examination, suppress "Available Actions" menu. Instead show witness statements A-E and command reminders: `press [A-E]` | `present [A-E] "[evidence_name]"` | `check-victory` | `end-cross-examination`
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
- **Evidence presentation gates** - Story-driven progression locks, not arbitrary percentages
- **Semantic naming** - Use case title in lowercase_with_underscores format for directory names
- **TEST ALL NEW FEATURES** - Any new scripts, modifications, or methodology changes must include comprehensive unit tests before implementation

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

# TESTING AND QUALITY ASSURANCE

## Unit Test Requirements

**MANDATORY:** All new features and system modifications must include corresponding unit tests.

### Test Coverage Standards:
- **Core Business Logic:** 100% test coverage required for game state management, evidence handling, character trust, gate transitions
- **Integration Points:** Script interactions and data persistence must have integration tests
- **Error Handling:** All error conditions and edge cases must be tested

### Running Tests:

**Before Committing Changes:**
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Test Suite Must Pass:** No commits allowed with failing tests

### Failure Response Protocol:

**When Tests Fail:**
1. **Do not proceed** with implementation until tests pass
2. **Identify root cause** of test failure
3. **Fix code or update tests** as appropriate
4. **Verify fix** with multiple test runs
5. **Add additional tests** if gap in coverage discovered

---

## START GAME RULES (PERMANENT)

**MANDATORY:** All game startup attempts MUST follow these permanent rules to ensure system integrity and prevent gameplay failures.

### **Rule 1: Comprehensive Pre-Game Validation (REQUIRED)**

**Before ANY game startup:**
```bash
# MANDATORY: Use validation-only command
source venv/bin/activate
python3 scripts/start_game_validator.py {case_name}
```

**After validation passes:**
- Claude displays case opening text from `case_opening.txt`
- Claude waits for user to type "next"
- Claude then uses game state manager to begin gameplay

**ZERO TOLERANCE POLICY:**
- **If validation fails**: STOP immediately and fix root causes
- **No manual workarounds**: Never bypass validation or attempt partial fixes
- **No assumptions**: Never assume "it will work anyway"
- **Root cause analysis**: Investigate WHY each error occurred and fix the underlying issue

### **Rule 2: Virtual Environment Enforcement**

**CRITICAL REQUIREMENT:**
- Virtual environment MUST be activated before ANY game operations
- Command: `source venv/bin/activate`
- Validation will BLOCK game start if environment not active
- **NO EXCEPTIONS**: Even for "quick tests" or "just checking"

### **Rule 3: System Integrity Validation**

**Comprehensive checks include:**
- **Case Structure**: File/directory requirements for case type
- **File Integrity**: JSON syntax, content validation, encoding
- **Game State Manager**: Initialization and validation capabilities
- **Dependencies**: Required packages and environment setup

### **Rule 4: Error Response Protocol**

**When validation fails:**
1. **READ the error messages completely** - don't guess or assume
2. **Identify root cause** - trace error to its source component
3. **Fix the underlying issue** - not just the symptom
4. **Re-run validation** - confirm fix resolves the problem
5. **Document pattern** - if systemic, update prevention measures

**PROHIBITED responses:**
- Manual file creation to "work around" missing structure
- Partial game starts with "we'll fix it later"
- Ignoring warnings or treating them as unimportant
- Bypassing validation "just this once"

### **Rule 5: Quality Gate Enforcement**

**Game startup is BLOCKED until:**
- ✅ All validation phases pass
- ✅ Virtual environment confirmed active
- ✅ Case structure validated for type
- ✅ GameStateManager initializes successfully

**NO EXCEPTIONS** - even for:
- "Simple test runs"
- "I know it will work"
- "Just want to check quickly"
- "It worked before"

### **Rule 6: Continuous Monitoring**

**During gameplay:**
- Monitor for any system errors or inconsistencies
- If issues emerge, STOP and run diagnostics
- Apply same root cause analysis principles
- Never continue with compromised system state

### **Validation Tools Available:**

**Primary (Validation Only):**
- `python3 scripts/start_game_validator.py {case_name}` - Comprehensive validation

**Diagnostic:**
- `python3 scripts/game_state_manager.py {case_name} --validate` - State validation
- `python3 scripts/game_state_manager.py {case_name} --resume` - Begin gameplay after validation

### **Enforcement Priority:**

These rules take **ABSOLUTE PRECEDENCE** over:
- Convenience or speed
- "It probably works" assumptions  
- Desire to start quickly
- Previous successful runs

**Remember:** Prevention of issues is always better than debugging gameplay failures mid-session.

---

This methodology represents the current state of iterative development, capturing insights that create authentic courtroom mystery experiences through AI collaboration. The improvisation-first approach ensures each case feels unique while maintaining proper pacing inspired by the Ace Attorney series.