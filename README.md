# Gimme

**Zero-dependency MCP input collector for AI-Human communication.**

---

> **🤖 Using with Hermes Agent on a headless VPS?**
> 
> **STOP** — Don't set up Gimme as an MCP server. It will hang.
> 
> Read [`HERMES_INTEGRATION.md`](HERMES_INTEGRATION.md) for the correct approach: extend Hermes's native `clarify` tool with `fields[]` support.

---

## Quick Start

```bash
git clone https://github.com/jarodow/Gimme.git
cd Gimme
python mcp_server.py
```

GUI window opens. On headless servers (no `$DISPLAY`), CLI mode starts automatically.

### Force CLI Mode

```bash
python mcp_server.py --cli
# or
USE_CLI=1 python mcp_server.py
```

## When to Use Gimme

| Your Agent | Use Gimme? | How |
|------------|------------|-----|
| **Desktop GUI agent** (Zed, Cline, etc.) | ✅ Yes | MCP server with GUI forms |
| **Headless VPS agent** (SSH terminal) | ⚠️ Direct import only | `from mcp_server import cli_input` |
| **Headless VPS agent** (MCP mode) | ❌ No | MCP stdio conflicts with interactive TUI |
| **Custom CLI tool** | ✅ Yes | Direct import or subprocess |

### Why MCP Mode Doesn't Work on Headless VPS

When Hermes (or any agent) runs on a headless VPS and you SSH in:

1. **MCP stdio occupies stdin/stdout** — The protocol pipe is used for JSON-RPC framing, not connected to your terminal
2. **CLI prompts go to stderr** — But reads from `sys.stdin` which is the MCP pipe, not your SSH session
3. **Result**: Tool hangs waiting for input that never arrives

**Solution**: Agent frameworks should extend their own TUI with native form rendering (see: Hermes `clarify` tool with `fields[]`).

## One-Liner MCP Setup

### Zed (Desktop)
```json
"gimme": {"command": "python3", "args": ["/path/to/Gimme/mcp_server.py"]}
```

### Cline / Roo Code (Desktop)
```bash
Command: python3
Args: /path/to/Gimme/mcp_server.py
```

### Manual (Any MCP Host)
```json
{
  "mcpServers": {
    "gimme": {
      "command": "python3",
      "args": ["/path/to/Gimme/mcp_server.py"]
    }
  }
}
```

⚠️ **Common pitfall**: `args` must be a list `["arg1", "arg2"]`, not a string `"arg1 arg2"`.

## Direct Python Import (Headless VPS / TUI Fallback)

For agents that need to render forms in their own terminal session:

```python
from mcp_server import cli_input

schema = {
    "title": "Workout Log",
    "fields": [
        {"name": "exercise", "type": "select", "label": "Exercise",
         "options": ["Leg Press", "Calf Extension", "Chest Press"]},
        {"name": "sets", "type": "number", "label": "Sets", "default": 3},
        {"name": "reps", "type": "number", "label": "Reps", "default": 10},
        {"name": "weight", "type": "number", "label": "Weight (lbs)"}
    ]
}

result = cli_input(schema)
# {'exercise': 'Leg Press', 'sets': 3, 'reps': 10, 'weight': 225}
```

See `examples/hermes_callback.py` for full callback integration pattern.

## Field Types

All 14 field types work in both GUI and CLI modes:

| Type | Description | Example Use |
|------|-------------|-------------|
| `text`, `email`, `number` | Single-line input | Name, email, quantity |
| `password` | Hidden text | API keys, credentials |
| `textarea` | Multi-line | Feedback, descriptions |
| `select` | Dropdown (single choice) | Language, theme |
| `multiselect` | Checkboxes (multiple) | Features to enable |
| `checkbox` | Yes/no toggle | Enable notifications |
| `slider` | Range slider (0-100) | Confidence threshold |
| `rating` | 1-5 or 1-10 scale | Priority score |
| `tags` | Comma/newline separated | Tech stack, keywords |
| `file` | File picker | Select config file |
| `datetime` | Date + time picker | Schedule task |
| `range` | Time range (start-end) | Active hours |

## Example Schemas

### Multi-Select (Features)
```json
{
  "title": "Enable Features",
  "fields": [
    {"name": "features", "type": "multiselect", "label": "Which to enable?",
     "options": ["auto-save", "linting", "formatting", "tests"],
     "default": ["auto-save"]}
  ]
}
```

### Slider (Confidence)
```json
{
  "title": "AI Confidence",
  "fields": [
    {"name": "threshold", "type": "slider", "label": "Minimum confidence %",
     "min": 0, "max": 100, "default": 70}
  ]
}
```

### Tags (Copy/Paste Friendly)
```json
{
  "title": "Tech Stack",
  "fields": [
    {"name": "stack", "type": "tags", "label": "Your technologies",
     "default": ["Python", "Docker", "PostgreSQL"]}
  ]
}
```

### File Picker
```json
{
  "title": "Project Location",
  "fields": [
    {"name": "project_dir", "type": "file", "label": "Project folder",
     "directory": true, "default": "C:/Projects"}
  ]
}
```

### Rating (Priority)
```json
{
  "title": "Task Priority",
  "fields": [
    {"name": "priority", "type": "rating", "label": "How important?",
     "max": 5, "default": 3}
  ]
}
```

## CLI Example Session

```
=== Profile Setup ===

Name *: [John Doe]: Alice Smith
Language *: 1:Python | 2:JavaScript | 3:Rust [Python]: 1
Enable notifications? [y/N]: y
Tech stack (comma/newline separated) [Python, Docker]: Python, PostgreSQL, Docker
Confidence threshold (0-100) [70]: 85
```

## Testing

### Quick Test with Bare JSON
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python mcp_server.py --cli
```

### Test Tool Call
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"vibe_ui","arguments":{"schema":{"title":"Test","fields":[{"name":"q","type":"text"}]}}}}' | python mcp_server.py --cli
```

## What This Solves

| AI Needs | Before (CLI) | After (Gimme) |
|----------|--------------|---------------|
| Yes/No decision | Type "yes" | Checkbox / `[y/N]` |
| Pick from options | Type option name | Dropdown / `1-3` list |
| Multiple selections | Comma list | Checkboxes / comma-sep |
| Confidence level | Type "70%" | Slider / `(0-100)` |
| File path | Type full path | Browse / path prompt |
| Schedule | Parse date format | Date picker / `YYYY-MM-DD` |
| Priority | Type 1-5 | Rating / `(1-5)` |
| Tech stack | Parse commas | Tags / comma-newline |

## Files

```
gimme/
├── mcp_server.py              (~250 lines)
├── README.md                  (this file)
├── HERMES_INTEGRATION.md      (Hermes-specific guide - READ THIS)
├── LICENSE
├── .gitignore
└── examples/
    └── hermes_callback.py     (Callback integration example)
```

**Zero dependencies** - tkinter is Python stdlib (only imported in GUI mode).

## How It Works

1. **Auto-detect**: Checks `--cli` flag, `USE_CLI` env var, or `$DISPLAY` presence
2. **MCP protocol**: JSON-RPC 2.0 over stdio with Content-Length framing
3. **Fallback**: Also accepts bare JSON for testing (hermes mcp test compatibility)
4. **Clean streams**: CLI prompts go to stderr, JSON-RPC stays on stdout

## For Agent Framework Developers

If you're building an agent that runs on headless servers (SSH, VPS, etc.):

1. **Don't use Gimme as MCP** — The stdio protocol conflicts with interactive terminal input
2. **Do extend your TUI** — Add native form rendering to your existing clarify/input tool
3. **Optional: Use cli_input()** — Import directly for the input logic, render in your own TUI

See `examples/hermes_callback.py` for the callback pattern.

## License

MIT
