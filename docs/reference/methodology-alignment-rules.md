# AI Rules for Methodology Alignment

## Critical Architecture Alignment Requirements

These rules ensure that any future changes to the case creation methodology maintain system-wide consistency and prevent regression.

## Rule 1: Dual Case Type Support (MANDATORY)

**Requirement:** All system components MUST support both case types:
- **Simple Improvisation Cases**: Real-world inspiration + opening scene + improvised gameplay
- **Complex Scaffolding Cases**: Full backbone/obstacles/solution structure

**Implementation Requirements:**

### Game State Manager
- MUST auto-detect case type from file structure
- MUST provide appropriate initialization for each type
- MUST validate according to case type requirements
- MUST handle missing files gracefully for simple cases

### Validation Systems
- MUST check file requirements appropriate to case type
- MUST validate gate structures using configuration-driven patterns
- MUST NOT assume presence of backbone/obstacles/solution directories for simple cases

### Configuration Management
- MUST drive case patterns from shared `config/case_patterns.json`
- MUST enable loose coupling between components
- MUST support extensibility without requiring core changes

## Rule 2: File Structure Detection Pattern

**Pattern Implementation:**
```python
def detect_case_type(self) -> str:
    # Check for complex case structure
    backbone_dir = self.case_path / "backbone"
    if backbone_dir.exists() and (backbone_dir / "case_structure.json").exists():
        return "complex"
    
    # Check for simple improvisation structure  
    real_life_file = self.case_path / "real_life_case_summary.txt"
    opening_file = self.case_path / "case_opening.txt"
    if real_life_file.exists() and opening_file.exists():
        return "simple_improvisation"
    
    # Fallback to complex for backward compatibility
    return "complex"
```

**Mandatory Usage:** ALL components that process case files MUST use this detection pattern.

## Rule 3: Configuration-Driven Gate Management

**Gate Structure Source:** All gate patterns MUST come from `config/case_patterns.json`

**Validation Logic:**
- Simple cases: Use `config_manager.get_gates_for_case_length(case_length)` 
- Complex cases: Use actual `investigation_gates` from state files
- Trial-only cases: Must handle empty investigation_gates correctly

**Error Prevention:** NEVER hardcode gate structures or file paths in business logic.

## Rule 4: Backward Compatibility Guarantee

**Legacy Case Support:** All previous cases in `previous_cases/` MUST continue working without modification.

**Testing Requirement:** Any changes MUST pass tests with both case types:
```bash
python3 scripts/game_state_manager.py the_midnight_masquerade --validate
python3 scripts/game_state_manager.py previous_cases/the_phantom_ledger --validate
```

**Regression Prevention:** If validation fails for existing cases, the change MUST be rejected.

## Rule 5: State File Adaptation

**Initialization Pattern:** 
- If required state files don't exist for simple cases, generate minimal valid state
- Use configuration patterns to determine appropriate structure
- Save generated state immediately for future consistency

**Method Signatures:** Maintain separate methods for initialization vs. persistence:
- `create_simple_improvisation_state()` - generates new state structure
- `save_current_state(state)` - persists provided state structure  
- `save_current_state_to_file()` - persists instance state

## Rule 6: Case Creation Script Alignment

**Default Behavior:** `create_new_game_orchestrator.py` MUST create simple improvisation cases by default.

**Complex Option:** `create_new_game_orchestrator_complex.py` MUST remain available for full scaffolding.

**Configuration Consistency:** Both scripts MUST reference the same `config/case_patterns.json` patterns.

## Rule 7: Testing and Quality Assurance

**Test Coverage Requirements:**
- Unit tests for both case type detection patterns
- Integration tests for state management with both types
- Validation tests for configuration consistency
- Regression tests for legacy case compatibility

**Test Execution:** Before any commits affecting case management:
```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Failure Response:** NO commits allowed with failing tests.

## Rule 8: Documentation Synchronization

**CLAUDE.md Updates:** Any methodology changes MUST be reflected in project instructions.

**Example Updates:** All examples and commands MUST work with current implementation.

**Configuration Documentation:** Changes to `config/case_patterns.json` MUST include usage examples.

## Enforcement Protocol

### When Making Changes:

1. **Identify Impact:** Does this change affect case creation, validation, or state management?
2. **Check Both Types:** Test with both simple and complex case structures
3. **Run Full Tests:** Execute complete test suite before proceeding
4. **Update Documentation:** Sync CLAUDE.md and examples with changes
5. **Validate Legacy:** Ensure previous cases continue working

### When Adding Features:

1. **Configuration First:** Add patterns to `config/case_patterns.json` if needed
2. **Detect Case Type:** Use file structure detection for behavior adaptation
3. **Test Both Paths:** Ensure feature works with simple and complex cases
4. **Write Tests:** Add comprehensive test coverage for new functionality
5. **Document Usage:** Update CLAUDE.md with new capabilities

### Emergency Fixes:

If system regression is detected:
1. **Immediate Rollback:** Revert changes causing regression
2. **Root Cause Analysis:** Identify what rules were violated
3. **Proper Fix:** Implement solution following all rules
4. **Enhanced Testing:** Add tests to prevent similar regressions

## Success Metrics

**System Health Indicators:**
- Both case types validate successfully: ✅
- Full test suite passes: ✅  
- Legacy cases remain functional: ✅
- New features work with both types: ✅
- Configuration drives behavior: ✅

**Failure Indicators:**
- Hardcoded file paths in business logic: ❌
- Case type assumptions without detection: ❌
- Validation failures for working cases: ❌
- Test regressions after changes: ❌
- Configuration bypassed for convenience: ❌

This rule set ensures that the system remains robust, extensible, and backward-compatible as the methodology continues to evolve through iterative experimentation.