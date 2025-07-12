# Start Game Failure Troubleshooting Guide

## Root Cause Analysis Framework

When game startup fails, follow this systematic approach to identify and fix root causes rather than applying superficial workarounds.

## Common Failure Patterns and Solutions

### 1. Virtual Environment Issues

**Error Pattern:**
```
Virtual environment not activated - run 'source venv/bin/activate' first
```

**Root Cause Analysis:**
- Python interpreter not running in isolated environment
- System-wide packages may conflict with project requirements
- wonderwords package not available in current environment

**Solution:**
```bash
# Always activate virtual environment first
source venv/bin/activate

# Verify activation worked
python3 -c "import sys; print(sys.prefix)"
# Should show path containing 'venv'

# Re-run validation
python3 scripts/start_game_validator.py {case_name}
```

**Prevention:**
- Always run activation command before ANY game operations
- Add alias to shell configuration: `alias activate='source venv/bin/activate'`
- Never skip this step "just for quick tests"

### 2. Missing Case Structure

**Error Pattern:**
```
Missing required files for simple improvisation case: ['real_life_case_summary.txt']
Case directory does not exist: {case_path}
```

**Root Cause Analysis:**
- Case creation process was incomplete or failed
- Files were manually moved or deleted
- Case creation script had errors that weren't addressed

**Solution:**
```bash
# For simple cases: Use case creation orchestrator
python3 scripts/create_new_game_orchestrator.py

# For complex cases: Use complex orchestrator
python3 scripts/create_new_game_orchestrator_complex.py

# If case exists but files missing: Use recovery mode
python3 scripts/create_new_game_orchestrator.py --recovery diagnose --target-case {case_name}
```

**Prevention:**
- Always complete case creation process fully
- Don't manually modify case structure
- Use recovery tools for case repairs

### 3. JSON Syntax Errors

**Error Pattern:**
```
Invalid JSON in case_structure.json: Expecting ',' delimiter: line 5 column 12
Cannot read character_facts.json: [Errno 2] No such file or directory
```

**Root Cause Analysis:**
- Manual editing introduced syntax errors
- File encoding issues
- Incomplete file creation process

**Solution:**
```bash
# Validate JSON syntax
python3 -c "import json; json.load(open('case_name/backbone/case_structure.json'))"

# If syntax error, fix manually or regenerate
# For regeneration:
python3 scripts/create_new_game_orchestrator.py --recovery fix-files --target-case {case_name}
```

**Prevention:**
- Use proper JSON editors with syntax highlighting
- Don't manually edit JSON unless necessary
- Use case creation tools instead of manual file creation

### 4. GameStateManager Initialization Failures

**Error Pattern:**
```
GameStateManager initialization failed: 'CaseConfigManager' object has no attribute 'get_gates_for_case_length'
Gate structure mismatch. Expected: [...], Got: [...]
```

**Root Cause Analysis:**
- Code changes broke GameStateManager compatibility
- Configuration file corruption
- Case structure inconsistent with expectations

**Solution:**
```bash
# Test GameStateManager directly
python3 scripts/game_state_manager.py {case_name} --validate

# If configuration issues:
python3 -c "from case_config import get_config_manager; print(get_config_manager().config)"

# If code compatibility issues: Check recent changes
git log --oneline -10

# Run test suite to identify broken components
source venv/bin/activate
python -m pytest tests/test_game_state_manager.py -v
```

**Prevention:**
- Run test suite before committing changes
- Follow methodology alignment rules
- Use configuration-driven patterns

### 5. File Permission Issues

**Error Pattern:**
```
PermissionError: [Errno 13] Permission denied: 'case_name/game_state'
Cannot create game_state directory: Permission denied
```

**Root Cause Analysis:**
- Insufficient filesystem permissions
- Files owned by different user
- Directory structure locked by system

**Solution:**
```bash
# Check permissions
ls -la {case_name}/

# Fix permissions if needed
chmod -R 755 {case_name}/
chown -R $USER:$USER {case_name}/

# Create missing directories
mkdir -p {case_name}/game_state
```

**Prevention:**
- Ensure proper permissions on project directory
- Don't run commands with sudo unless necessary
- Use consistent user for all project operations

### 6. Package Dependencies Missing

**Error Pattern:**
```
ModuleNotFoundError: No module named 'wonderwords'
ImportError: cannot import name 'GameStateManager'
```

**Root Cause Analysis:**
- Required packages not installed in virtual environment
- Python path issues
- Virtual environment corrupted

**Solution:**
```bash
# Check package installation
pip list | grep wonderwords

# Install missing packages
pip install wonderwords

# If systematic issues, reinstall requirements
pip install -r requirements.txt

# If virtual environment corrupted, recreate
deactivate
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Prevention:**
- Maintain requirements.txt file
- Document all dependencies
- Test with fresh virtual environment periodically

## Systematic Debugging Process

### Step 1: Collect Complete Error Information

```bash
# Run validation with full output
python3 scripts/start_game_validator.py {case_name} 2>&1 | tee debug.log

# Check system environment
python3 --version
which python3
echo $VIRTUAL_ENV
```

### Step 2: Identify Error Category

Classify the error into one of these categories:
- **Environment**: Virtual environment, packages, permissions
- **Structure**: Missing files, directories, case organization
- **Content**: File corruption, JSON syntax, encoding
- **Code**: GameStateManager, configuration, compatibility
- **System**: Permissions, paths, filesystem

### Step 3: Apply Root Cause Analysis

For each error:
1. **What** exactly failed? (Read error message completely)
2. **Why** did it fail? (Trace to underlying cause)
3. **When** did it start failing? (Recent changes, environmental factors)
4. **Where** is the issue located? (Specific component, file, system layer)

### Step 4: Implement Comprehensive Fix

- Fix the root cause, not just the symptom
- Test the fix thoroughly
- Verify no regression in other components
- Document the issue and solution

### Step 5: Prevent Recurrence

- Update validation rules if needed
- Add tests to catch similar issues
- Improve documentation or error messages
- Consider architectural improvements

## Recovery Strategies

### Automated Recovery

```bash
# Comprehensive case diagnosis
python3 scripts/create_new_game_orchestrator.py --recovery diagnose --target-case {case_name}

# Attempt automatic fixes
python3 scripts/create_new_game_orchestrator.py --recovery fix-files --target-case {case_name}

# Reset to previous working state if needed
python3 scripts/create_new_game_orchestrator.py --recovery reset-phase --target-case {case_name}
```

### Manual Recovery (Last Resort)

Only when automated recovery fails:

```bash
# Backup current state
cp -r {case_name} {case_name}_backup_$(date +%Y%m%d_%H%M%S)

# Identify minimal viable structure
python3 scripts/start_game_validator.py {case_name}

# Manually fix critical files
# (Use this sparingly and document changes)

# Re-run validation to confirm fix
python3 scripts/start_game_validator.py {case_name}
```

### Complete Reset (Nuclear Option)

When case is irreparably corrupted:

```bash
# DESTRUCTIVE: Remove completely corrupted case
python3 scripts/create_new_game_orchestrator.py --recovery clean-start --target-case {case_name}
# Requires confirmation: type "DELETE {case_name}"

# Start fresh case creation
python3 scripts/create_new_game_orchestrator.py
```

## Validation Framework Testing

### Test Validation Components

```bash
# Test virtual environment detection
python3 -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"

# Test configuration loading
python3 -c "from case_config import get_config_manager; print('Config loaded:', bool(get_config_manager().config))"

# Test GameStateManager with minimal case
python3 -c "from game_state_manager import GameStateManager; print('GSM works:', bool(GameStateManager('test_case')))"
```

### Create Test Cases

```bash
# Create known-good case for testing
python3 scripts/create_new_game_orchestrator.py
# Use for baseline validation testing

# Create intentionally broken case for testing error handling
# (Manually introduce errors to test recovery)
```

## Emergency Protocols

### When All Validation Fails

1. **Document the complete error state**
   ```bash
   python3 scripts/start_game_validator.py {case_name} > validation_failure_$(date +%Y%m%d_%H%M%S).log 2>&1
   ```

2. **Preserve evidence for analysis**
   ```bash
   tar -czf case_failure_$(date +%Y%m%d_%H%M%S).tar.gz {case_name}/
   ```

3. **Test with known-good case**
   ```bash
   python3 scripts/start_game_validator.py previous_cases/the_phantom_ledger
   ```

4. **If system-wide failure detected**
   ```bash
   # Run full test suite
   source venv/bin/activate
   python -m pytest tests/ -v
   
   # Check for recent changes
   git status
   git log --oneline -5
   ```

5. **Escalate to development analysis**
   - Gather all logs and error evidence
   - Document exact reproduction steps
   - Identify when the issue first appeared
   - Note any environmental changes

## Success Metrics

After applying fixes, verify:

- ✅ Validation passes completely
- ✅ GameStateManager initializes successfully  
- ✅ Case structure matches configuration expectations
- ✅ All required files present and valid
- ✅ Virtual environment active and packages available
- ✅ No warnings or error messages
- ✅ Game can start and reach opening scene

Remember: **Root cause fixes prevent future failures, workarounds just delay them.**