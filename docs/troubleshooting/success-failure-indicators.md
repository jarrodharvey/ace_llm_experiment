# Success and Failure Indicators

## Success Indicators
- Player expressing frustration with obstacles (good frustration)
- Characters being realistically difficult to work with
- Evidence requiring genuine detective work to obtain
- Case building tension through both investigation and trial
- Victory feeling earned through player skill
- **Proper state management** - All progress tracked, evidence recorded, gates completed systematically

## Failure Indicators
- Player getting helpful information easily
- Linear progression without significant obstacles  
- Characters cooperative without reason
- Evidence appearing without effort
- **Case resolved without proper trial phase (CRITICAL FAILURE - trials are mandatory!)**
- Investigation gates not building toward dramatic courtroom confrontation
- **Missing state management** - Gates not marked, evidence not recorded, progress not tracked
- **Bypassing trial triggers** - Resolving cases externally instead of using automatic trial detection
- **Uninspired improvisation** - Using default patterns instead of forced inspiration for character development
- **No entropy prevention** - Falling back on "corrupt official" or "simple revenge" tropes without creative forcing
- **Legal realism overriding game mechanics** - Cases ending when evidence discovered instead of proceeding to trial
- **Prosecution surrendering** - Prosecutor giving up when contradictory evidence appears
- **Witnesses cooperating in court** - Witnesses telling truth in trial instead of lying for dramatic effect

## Debug Procedures
When player uses "!" command:
1. Check game state integrity without revealing solutions
2. Verify obstacle consistency against backbone
3. Identify available actions player hasn't tried
4. Ensure evidence presentation gates are functioning properly
5. Check case_length and gate structure alignment
6. Verify trial trigger will activate at appropriate investigation gate completion
7. Return to gaming mode after technical issues resolved

## Mid-Game Adjustments
- **Too easy**: Increase character hostility, add more obstacles
- **Too hard**: Provide subtle hints, ensure progress possible
- **Inconsistent**: Check obstacle integration against backbone  
- **Missing trial**: CRITICAL ERROR - Cases must progress to courtroom resolution
- **Wrong pacing**: Verify gate progression matches case_length structure (1-day, 2-day, or 3-day)
- **Case resolving early**: FORCE trial continuation with prosecution resistance and witness perjury
- **Realistic legal outcomes**: OVERRIDE with game mechanics - drama takes precedence over legal logic

*Last updated: 2025-07-10*