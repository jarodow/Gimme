# Hermes Agent Integration Guide

## ⚠️ STOP: Read This Before Setting Up Gimme

**If you are running Hermes Agent on a headless VPS and accessing it via SSH:**

### ❌ DO NOT set up Gimme as an MCP server

```bash
# DON'T DO THIS - it will hang indefinitely
hermes mcp add gimme --command python3 --args "mcp_server.py --cli"
```

**Why it fails:**
- MCP uses stdin/stdout for JSON-RPC protocol
- CLI mode needs stdin/stdout for your terminal input
- These conflict → tool calls hang forever waiting for input

### ✅ DO THIS: Extend Hermes's Native TUI

Hermes already has a `clarify` tool that renders in your terminal. Extend it with `fields[]` support.

---

## The Right Architecture for Hermes

```
┌─────────────────────────────────────────────────────────┐
│  Your SSH Terminal Session                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Hermes Agent TUI                               │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │  clarify(fields=[...])                   │   │   │
│  │  │  → Renders form directly in TUI          │   │   │
│  │  │  → Reads from your terminal              │   │   │
│  │  │  → Returns result to agent               │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Key insight**: The form rendering must live **inside** Hermes's TUI layer, not in an external MCP process.

---

## Implementation: Extend `clarify` Tool

### Step 1: Add `fields[]` Parameter

**File**: `tools/clarify_tool.py`

```python
def clarify(question: str, choices: list[str] | None = None, fields: list[dict] | None = None):
    """
    Present input to the user and return their response.
    
    Args:
        question: The question text to display.
        choices: Up to 4 predefined options (mutually exclusive with fields).
        fields: Up to 8 field definitions for a multi-field form.
    """
    if fields:
        return _render_form(question, fields)
    elif choices:
        return _render_choices(question, choices)
    else:
        return _render_text_input(question)
```

### Step 2: Add Form Rendering

**File**: `cli.py` (or wherever Hermes renders TUI)

```python
def _render_form(title: str, fields: list[dict]) -> dict:
    """Render multi-field form in terminal TUI."""
    import sys
    from mcp_server import cli_input  # Optional: reuse input logic
    
    # Option A: Use cli_input() for input collection
    schema = {"title": title, "fields": fields}
    return cli_input(schema)
    
    # Option B: Render natively in Hermes TUI (recommended)
    # Use your existing TUI library (rich, textual, prompt_toolkit, etc.)
```

### Step 3: Fix Arrow Key Bindings

**Important**: Forms are vertical lists. Arrow keys should match this:

| Key | Action |
|-----|--------|
| ↑/↓ | Navigate between fields |
| ←/→ | Cycle select options / adjust numeric values |
| Tab/Enter | Advance to next field (submit on last) |
| Esc | Cancel form |

**Bug found in Hermes**: Left/right navigated fields, up/down cycled values (inverted). Swap these.

---

## Field Schema Reference

Each field in `fields[]`:

```python
{
    "name": "exercise",           # Key in returned dict
    "label": "Exercise",          # Display label
    "type": "select",             # text, number, select, multiselect, range
    "options": ["A", "B", "C"],   # Required for select/multiselect
    "default": "A",               # Pre-filled value
    "min": 1,                     # For number/range
    "max": 10,                    # For number/range
    "required": True              # Whether field is required
}
```

---

## Example: Agent Calls clarify with fields

```python
# Agent code
result = await agent.tools.clarify(
    question="Log your workout set",
    fields=[
        {"name": "exercise", "type": "select", "label": "Exercise",
         "options": ["Leg Press", "Calf Extension", "Chest Press"],
         "default": "Leg Press"},
        {"name": "sets", "type": "number", "label": "Sets", "default": 3},
        {"name": "reps", "type": "number", "label": "Reps", "default": 10},
        {"name": "weight", "type": "number", "label": "Weight (lbs)", "default": 225}
    ]
)

# Returns: {'exercise': 'Leg Press', 'sets': 3, 'reps': 10, 'weight': 225}
```

---

## What About Gimme's `cli_input()`?

You **can** import it directly for the input logic:

```python
from mcp_server import cli_input

def clarify_callback(question, choices=None, fields=None):
    if fields:
        return cli_input({"title": question, "fields": fields})
    # ... handle choices/text
```

**But**: This still has limitations:
- Reads from `sys.stdin` (may conflict if Hermes also uses stdin)
- Writes to `sys.stderr` (will work, but not integrated with Hermes TUI styling)
- No access to Hermes session state, user preferences, etc.

**Better**: Render forms natively in Hermes's TUI framework.

---

## Testing Your Implementation

### Test 1: Simple Choice (Existing Behavior)
```python
result = await agent.tools.clarify(
    question="Choose environment",
    choices=["staging", "production"]
)
# Should render: 1: staging, 2: production
```

### Test 2: Multi-Field Form (New Behavior)
```python
result = await agent.tools.clarify(
    question="Deploy config",
    fields=[
        {"name": "env", "type": "select", "label": "Environment",
         "options": ["staging", "production"]},
        {"name": "replicas", "type": "number", "label": "Replicas", "default": 3}
    ]
)
# Should render interactive form with both fields
```

### Test 3: Degradation (Backward Compatibility)
If a callback only accepts `(question, choices)` without `fields`:
- Form should degrade to sequential single-field prompts
- Each field becomes one clarify call
- No breaking changes to existing integrations

---

## Summary Checklist

- [ ] **Don't** set up Gimme as MCP server (will hang on headless VPS)
- [ ] **Do** extend `clarify` tool with `fields[]` parameter
- [ ] **Do** render forms in Hermes's native TUI
- [ ] **Do** fix arrow key bindings (↑/↓ = navigate, ←/→ = cycle values)
- [ ] **Do** support degradation for old callbacks (sequential prompts)
- [ ] **Optional**: Import `cli_input()` for input logic (but native TUI is better)

---

## Questions?

See `examples/hermes_callback.py` in the Gimme repo for a callback pattern example.

For the full field type list and schema, see Gimme's README.md.
