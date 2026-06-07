# Gimme

**Zero-dependency MCP input collector for AI-Human communication.**

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

## One-Liner MCP Setup

### Zed
```bash
# Add to Zed settings.json under "mcpServers":
"gimme": {"command": "python3", "args": ["/path/to/Gimme/mcp_server.py", "--cli"]}
```

### Cline / Roo Code
```bash
# In MCP settings UI, add server:
Command: python3
Args: /path/to/Gimme/mcp_server.py --cli
```

### Hermes MCP
```bash
hermes mcp add gimme --command python3 --args "/path/to/Gimme/mcp_server.py --cli"
```

### Manual (Any Host)
```json
{
  "mcpServers": {
    "gimme": {
      "command": "python3",
      "args": ["/path/to/Gimme/mcp_server.py", "--cli"]
    }
  }
}
```

⚠️ **Common pitfall**: `args` must be a list `["arg1", "arg2"]`, not a string `"arg1 arg2"`.

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
User can paste from Excel (newlines) or type comma-separated.

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

### Date/Time Scheduling
```json
{
  "title": "Schedule Task",
  "fields": [
    {"name": "run_at", "type": "datetime", "label": "When to run?",
     "default": "2025-01-15 09:00"}
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

Same schema works in both modes automatically.

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
├── mcp_server.py    (~250 lines)
├── README.md
├── LICENSE
└── .gitignore
```

**Zero dependencies** - tkinter is Python stdlib (only imported in GUI mode).

## How It Works

1. **Auto-detect**: Checks `--cli` flag, `USE_CLI` env var, or `$DISPLAY` presence
2. **MCP protocol**: JSON-RPC 2.0 over stdio with Content-Length framing
3. **Fallback**: Also accepts bare JSON for testing (hermes mcp test compatibility)
4. **Clean streams**: CLI prompts go to stderr, JSON-RPC stays on stdout

## License

MIT
