# Case Creation Recovery Workflow Examples

## Recovery Commands Reference

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

## Example Recovery Workflow

```bash
# Case creation fails during Phase 3
python3 scripts/create_new_game_orchestrator.py --recovery diagnose --target-case my_failed_case

# If files are misplaced, try automatic fixes
python3 scripts/create_new_game_orchestrator.py --recovery fix-files --target-case my_failed_case

# If phase is corrupted, reset to previous phase
python3 scripts/create_new_game_orchestrator.py --recovery reset-phase --target-case my_failed_case

# Resume from the reset phase
python3 scripts/create_new_game_orchestrator.py --resume case_creation_state_*.json --phase phase_2
```

*Last updated: 2025-07-10*