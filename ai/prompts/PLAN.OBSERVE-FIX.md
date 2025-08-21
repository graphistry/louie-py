# Plan Type: Observe-Fix Loop

A variant of standard PLAN.md for when you must execute to verify correctness.

## WHEN TO USE

User says: "doesn't work", "wrong output", "missing", "broken", "fix until working"

## THE LOOP (UNROLLED)

Each iteration creates these explicit plan steps:

```
Iteration N:
1. EXECUTE_ALL - Run entire suite
2. CREATE_MATRIX - Empty tracking matrix
3. FILL_MATRIX - Record each actual output
4. DIAGNOSE_FAILURES - Identify all ❌ root causes
5. APPLY_FIX - Fix one issue
6. EXECUTE_ALL_AGAIN - Full re-run
7. CREATE_NEW_MATRIX - Fresh empty matrix
8. FILL_NEW_MATRIX - Record all outputs again
9. CHECK_REGRESSIONS - Compare to previous matrix
10. If not all ✅, go to Iteration N+1
```

## EXPLICIT MATRIX STEPS

### Step 2: CREATE_MATRIX (empty)
```
Component | Expected | Actual | Status |
----------|----------|--------|--------|
Cell A    | "avg: 30"|        |        |
Cell B    | "sum: 90"|        |        |
Cell C    | "4 rows" |        |        |
```

### Step 3: FILL_MATRIX (execute and fill)
```
Component | Expected | Actual  | Status |
----------|----------|---------|--------|
Cell A    | "avg: 30"| "sum: 90"| ❌     |
Cell B    | "sum: 90"| "sum: 90"| ✅     |
Cell C    | "4 rows" | [empty]  | ❌     |
```

### Step 7-8: NEW MATRIX (after fix)
Start fresh, don't copy:
```
Component | Expected | Actual  | Status |
----------|----------|---------|--------|
Cell A    | "avg: 30"|         |        | ← Empty first
Cell B    | "sum: 90"|         |        | ← Then execute
Cell C    | "4 rows" |         |        | ← Then fill
```

## PLAN EXAMPLE

```yaml
Task: Fix notebook outputs

Iteration_1:
  - EXECUTE_ALL: Run notebook
  - CREATE_MATRIX: Build empty 5-cell matrix
  - FILL_MATRIX: Record outputs for cells A,B,C,D,E
  - DIAGNOSE_FAILURES: Found keyword order bug
  - APPLY_FIX: Reorder if-elif conditions
  - EXECUTE_ALL_AGAIN: Run notebook
  - CREATE_NEW_MATRIX: Fresh empty 5-cell matrix
  - FILL_NEW_MATRIX: Record new outputs
  - CHECK_REGRESSIONS: B broke! (was ✅, now ❌)
  
Iteration_2:
  - DIAGNOSE_FAILURES: B needs different keyword
  - APPLY_FIX: Add specific check for B
  - EXECUTE_ALL_AGAIN: Run notebook
  - CREATE_NEW_MATRIX: Fresh empty 5-cell matrix
  - FILL_NEW_MATRIX: Record new outputs
  - CHECK_REGRESSIONS: All ✅!
  - COMPLETE: All working simultaneously
```

## WHY EXPLICIT STEPS?

- Forces fresh observation (no copy-paste errors)
- Makes regressions visible in plan
- Creates audit trail of what was checked
- Prevents "assumed still working" mistakes

## CRITICAL: VALIDATE ALL

⚠️ **Fixing one thing can break another**

```
Example regression:
- Fix A: Change keyword priority 
- Breaks B: Different keyword now matches first
- Must verify A AND B still work
```

**ALWAYS:**
- Run ALL tests/cells after EACH fix
- Check previous ✅ items stayed ✅
- Don't just test the thing you fixed

## ANTI-PATTERN

❌ Wrong:
```
Fix Cell A → ✅
Fix Cell B → ✅
Commit "all fixed"
(Never checked if A still works after fixing B)
```

✅ Right:
```
Fix Cell A → A✅ B❌ C❌
Fix Cell B → A✅ B✅ C❌  (verify A still works!)
Fix Cell C → A❌ B✅ C✅  (regression! A broke)
Fix A again → A✅ B✅ C✅  (all work together)
```

## COMPLETION

ONLY when latest matrix shows ALL ✅ with no regressions.