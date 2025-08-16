# Notebook Fix Plan - Systematic Approach to Correctness

## Current State (BROKEN)
The 01-getting-started.ipynb notebook has incorrect outputs for most cells:
- Cell 1 (Basic Math): Returns "2 plus 2 equals 4" instead of just "4"
- Cell 3 (DataFrame Count): Can't find dataframe, returns error
- Cell 4 (Inventory): Just echoes prompt, no calculation
- Cell 5 (Upload): Returns error about missing dataframe ID
- Cells don't maintain state between them (DataFrame created in cell 2 not accessible in cell 3)

## Methodology: Fixpoint Testing with Persistent Fixes

### 1. Test Framework Components

#### A. Strict Correctness Criteria (per cell)
```python
CELL_CRITERIA = {
    "cell_1_basic_math": {
        "prompt": "What is 2 + 2?",
        "expected": "4",  # EXACTLY this, not a sentence
        "test": lambda output: output.strip() in ["4", "four", "Four"]
    },
    "cell_2_dataframe": {
        "prompt": "Generate a pandas dataframe with 3 rows: name, age, city columns",
        "expected": "DataFrame shape (3,3) accessible as lui.df",
        "test": lambda lui: lui.df is not None and lui.df.shape == (3,3)
    },
    "cell_3_count": {
        "prompt": "How many rows are in the dataframe?",
        "expected": "3 or three",
        "test": lambda output: "3" in output or "three" in output.lower()
    },
    # ... etc
}
```

#### B. Fix Strategies (in order of preference)
1. **Prompt Engineering** - Try different phrasings
2. **Client API Fix** - Modify louie-py to handle responses better
3. **Server API Fix** - Fix graphistrygpt2 endpoints/logic
4. **Notebook Structure** - Change cell organization/flow

#### C. Persistence Layer
```python
# Track what works across rounds to prevent drift
WORKING_FIXES = {
    "prompts": {},      # Cell -> working prompt
    "client_patches": [], # List of patches applied to louie-py
    "server_patches": [], # List of patches applied to graphistrygpt2
    "notebook_mods": []   # Structural changes to notebook
}
```

### 2. Fixpoint Algorithm

```python
def run_fixpoint_testing():
    """
    Iterate until ALL cells pass ALL criteria consistently
    """
    round = 0
    max_rounds = 10
    consecutive_passes_needed = 3  # Must pass 3 times in a row
    
    while round < max_rounds:
        round += 1
        
        # Load previous working fixes
        apply_persistent_fixes()
        
        # Test all cells
        results = test_all_cells()
        
        if all_cells_pass(results):
            # Verify consistency
            if verify_consistent_passes(consecutive_passes_needed):
                save_final_configuration()
                return SUCCESS
        
        # Fix failing cells
        for cell in get_failing_cells(results):
            fix = find_next_fix(cell, results[cell])
            apply_fix(fix)
            
            # Test if fix helps without breaking others
            if fix_causes_regression():
                rollback_fix(fix)
                try_alternative_fix(cell)
            else:
                add_to_persistent_fixes(fix)
    
    return FAILURE
```

### 3. Fix Priority Order

1. **Quick Wins** (Prompt changes only)
   - Try simpler prompts
   - Add explicit instructions
   - Use different phrasing

2. **Client Fixes** (louie-py)
   - Fix response parsing
   - Improve DataFrame persistence
   - Better error handling

3. **Server Fixes** (graphistrygpt2)
   - Fix DataFrame reference issues
   - Improve response generation
   - Fix state management

4. **Structural** (Notebook flow)
   - Combine cells if needed
   - Add state verification cells
   - Restructure data flow

### 4. Specific Issues to Fix

#### Issue 1: DataFrame State Loss
**Problem**: DataFrame created in cell 2 not accessible in cell 3
**Potential Fixes**:
- Client: Make lui.df persistent across calls
- Server: Fix dthread context management
- Notebook: Pass DataFrame explicitly

#### Issue 2: Response Format
**Problem**: Getting sentences instead of values
**Potential Fixes**:
- Prompt: "Return only the number 4, nothing else"
- Server: Add response format hints to agents
- Client: Parse and extract values from responses

#### Issue 3: Upload Failures
**Problem**: "No DfElement found for deref_df"
**Potential Fixes**:
- Server: Fix DataFrame ID generation/storage
- Client: Ensure proper upload format
- Both: Add retry logic with ID verification

### 5. Implementation Steps

1. **Create Test Harness** (`/tmp/notebook_test_harness.py`)
   - Load notebook
   - Execute each cell
   - Validate against criteria
   - Report failures with specifics

2. **Create Fix Iterator** (`/tmp/fix_iterator.py`)
   - Try fixes in priority order
   - Track what works
   - Prevent regression
   - Save successful configurations

3. **Create Patch Manager** (`/tmp/patch_manager.py`)
   - Apply patches to louie-py
   - Apply patches to graphistrygpt2
   - Track and revert as needed

4. **Run Until Fixpoint**
   ```bash
   while ! python /tmp/notebook_test_harness.py; do
       python /tmp/fix_iterator.py
       python /tmp/patch_manager.py --apply-next
   done
   ```

### 6. Success Criteria

ALL of the following must be true:
- [ ] Cell 1 returns EXACTLY "4" (not a sentence)
- [ ] Cell 2 creates DataFrame accessible as lui.df
- [ ] Cell 3 correctly counts rows from Cell 2's DataFrame
- [ ] Cell 4 calculates inventory value correctly (3610.75)
- [ ] Cell 5 uploads and analyzes user DataFrame
- [ ] Cell 6 returns "150" for 100+50
- [ ] All cells pass 3 consecutive times
- [ ] No regressions when re-running

### 7. Next Steps When Resuming

1. **Run current state test** to see what's still broken:
   ```bash
   uv run python /tmp/notebook_test_framework.py
   ```

2. **Apply fixpoint methodology**:
   ```bash
   uv run python /tmp/fixpoint_test_framework.py
   ```

3. **For each failure**, try fixes in order:
   - Prompt engineering
   - Client code fix
   - Server code fix
   - Notebook restructure

4. **Document working configuration**:
   - Save working prompts to `/tmp/working_prompts.json`
   - Save client patches to `/tmp/client_patches.txt`
   - Save server patches to `/tmp/server_patches.txt`

5. **Verify no drift** by running full test suite 5 times

## Remember: Don't Just Fix Symptoms

For each issue:
1. Find root cause (why is it happening?)
2. Fix at appropriate level (prompt/client/server)
3. Add test to prevent regression
4. Document the fix for future reference

## Current Working Prompts (Partial)

```json
{
  "basic_math": "What is 2 plus 2? Just tell me the answer.",
  "dataframe_gen": "Generate a pandas dataframe with 3 rows: name, age, city columns",
  "upload_test": "Calculate the sum of all sales values in this dataset"
}
```

## Known Issues Needing Fixes

1. **DataFrame persistence** - Created in one cell, not accessible in next
2. **Response truncation** - Answers getting cut off
3. **Upload errors** - "No DfElement found" errors
4. **Calculation failures** - Not actually computing values
5. **State management** - Context lost between queries

Each needs systematic fix following the methodology above.