# LouieAI Development Plan

## Fixed Issues

### Dataframe Fetching Issue (RESOLVED)

**Problem**: 
- `lui.df` was returning `None` even when dataframes were present
- Display showed "📊 DataFrame: None (shape: 100 x 14)"

**Root Causes Found**:
1. Server response format changed - elements have lowercase types (`'text'`, `'df'`) in addition to camelCase (`'TextElement'`, `'DfElement'`)
2. Text elements use `'value'` field instead of `'text'` field
3. DfElement uses `'id'` field instead of `'df_id'` or `'block_id'`
4. Arrow data was in file format, not stream format - needed to use `pa.ipc.open_file()` instead of `pa.ipc.open_stream()`

**Solution Applied**:
1. Updated all element type checks to handle both formats (e.g., `["TextElement", "text"]`)
2. Updated field extraction to check multiple field names (`'text'`, `'value'`, `'content'`)
3. Extended dataframe ID extraction to check `'id'` in addition to `'df_id'` and `'block_id'`
4. Fixed Arrow parsing to try file format first, then fall back to stream format

**Files Modified**:
- `src/louieai/_client.py` - Added support for lowercase element types and multiple field names
- `src/louieai/notebook/streaming.py` - Updated element formatting for both formats
- `src/louieai/notebook/cursor.py` - Updated text extraction to handle value field

## Test Credentials (for integration tests)

```python
# Test credentials for integration testing
# DO NOT COMMIT - Keep in .gitignore
g = graphistry.register(
    api=3,
    server='graphistry-dev.grph.xyz',
    personal_key_id='CU5V6VZJB7', 
    personal_key_secret='32RBP6PUCSUVAIYJ',
    org_name='databricks-pat-botsv3'
)

lui = louieai.louie(g, server_url='https://louie-dev.grph.xyz', share_mode='Private')
```

## Verification

The fix has been verified with:
1. Simple dataframe creation works: `lui.df` returns proper DataFrame
2. Databricks data fetching works: Returns actual data with correct shape
3. Text extraction works: `lui.text` returns proper content
4. Arrow format parsing works with both file and stream formats

## Next Steps

- [ ] Add unit tests for the new element type formats
- [ ] Add integration tests for Arrow dataframe fetching
- [ ] Consider adding format version detection for future compatibility