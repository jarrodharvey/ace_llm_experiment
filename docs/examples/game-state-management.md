# Game State Management Examples

## Starting a Gaming Session

```bash
# Get current context for resuming
python3 scripts/game_state_manager.py the_courtroom_conspiracy --resume

# Check current status and available actions
python3 scripts/game_state_manager.py the_courtroom_conspiracy --status
python3 scripts/game_state_manager.py the_courtroom_conspiracy --actions
```

## During Investigation

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

## Trial Preparation

```bash
# Check if trial is ready
python3 scripts/game_state_manager.py the_courtroom_conspiracy --validate

# Create save point before trial
python3 scripts/game_state_manager.py the_courtroom_conspiracy --save "before_trial"

# Start trial when ready
python3 scripts/game_state_manager.py the_courtroom_conspiracy --start-trial
```

## Save Management

```bash
# List all saves
python3 scripts/game_state_manager.py the_courtroom_conspiracy --list-saves

# Restore from save
python3 scripts/game_state_manager.py the_courtroom_conspiracy --restore "before_trial"

# Clean up old saves
python3 scripts/game_state_manager.py the_courtroom_conspiracy --cleanup 5
```

*Last updated: 2025-07-10*