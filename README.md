# Gimme

**Zero-dependency MCP GUI for AI-Human communication.**

## Quick Start

```bash
python mcp_server.py
```

Window opens. AI agent controls what appears.

## Field Types

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
     "default_multi": ["auto-save"]}
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

## MCP Host Config

```json
{
  "mcpServers": {
    "gimme": {
      "command": "python",
      "args": ["/path/to/gimme/mcp_server.py"]
    }
  }
}
```

## What This Solves

| AI Needs | Before (CLI) | After (Gimme) |
|----------|--------------|---------------|
| Yes/No decision | Type "yes" | Checkbox |
| Pick from options | Type option name | Dropdown |
| Multiple selections | Comma list | Checkboxes |
| Confidence level | Type "70%" | Slider |
| File path | Type full path | Browse button |
| Schedule | Parse date format | Date/time pickers |
| Priority | Type 1-5 | Rating buttons |
| Tech stack | Parse commas | Tags input |

## Files

```
gimme/
├── mcp_server.py    (~200 lines)
├── README.md
├── LICENSE
└── .gitignore
```

**Zero dependencies** - tkinter is Python stdlib.

## License

MIT
