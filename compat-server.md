# Server-side Changes for Streaming Compat

Companion to louie-py `feat/streaming-compat-v2` branch.
Apply these to graphistrygpt PR #2628 (`feat/stream-run-tree-v2`).

## 1. Rename `payload` to `run_node` on `StreamingApiMessageRunUpdate`

**File:** `graphistrygpt/api/routes/runners.py`

```python
# Before
class StreamingApiMessageRunUpdate(BaseModel):
    type: Literal["StreamingApiMessageRunUpdate"] = "StreamingApiMessageRunUpdate"
    payload: RunNodeUpdate

# After
class StreamingApiMessageRunUpdate(BaseModel):
    type: Literal["StreamingApiMessageRunUpdate"] = "StreamingApiMessageRunUpdate"
    run_node: RunNodeUpdate
```

**Why:** Old louie-py clients check `if "payload" in data` and treat any payload as an element. Renaming to `run_node` makes old clients silently skip these messages.

## 2. Add `type` discriminator to all streaming message types

```python
class StreamingApiMessageStart(BaseModel):
    type: Literal["StreamingApiMessageStart"] = "StreamingApiMessageStart"
    dthread_id: Optional[DataThreadId] = None

class StreamingApiMessageOutputUpdate(BaseModel):
    type: Literal["StreamingApiMessageOutputUpdate"] = "StreamingApiMessageOutputUpdate"
    position: int
    payload: ElementUnion

class StreamingApiMessageTrace(BaseModel):
    type: Literal["StreamingApiMessageTrace"] = "StreamingApiMessageTrace"
    payload: Trace | ElementUnion

class StreamingApiMessageRunUpdate(BaseModel):
    type: Literal["StreamingApiMessageRunUpdate"] = "StreamingApiMessageRunUpdate"
    run_node: RunNodeUpdate

class StreamingApiMessageTerminal(BaseModel):
    type: Literal["StreamingApiMessageTerminal"] = "StreamingApiMessageTerminal"
    success: bool = True
    error: Optional[str] = None
```

**Why:** New louie-py clients route on `data.get("type")`. Adding `type` to all messages lets the client use type-discriminated handling instead of guessing from payload presence. This is backwards compatible -- old clients ignore unknown fields.

## Compatibility Matrix (after both changes)

| | Old server (no `type` field) | New server (`type` + `run_node`) |
|---|---|---|
| **Old louie-py** | works | works (ignores `run_node`, ignores `type`) |
| **New louie-py** | works (legacy `payload` fallback) | works (type-discriminated) |

## Test updates

In streaming tests, update any assertions that reference `msg.payload` on `StreamingApiMessageRunUpdate` to use `msg.run_node` instead:

```python
# Before
assert run_updates[0].payload.state == "Running"

# After
assert run_updates[0].run_node.state == "Running"
```
