# Conversation Logging Guide 📝

## Overview

The Bible Chatbot now automatically saves all conversations, tool calls, and responses for future analysis. Logs are saved in the `logs/` directory.

## Features

✅ **Automatic Logging** - All conversations are saved automatically  
✅ **Multiple Formats** - JSON (structured) and/or Text (human-readable)  
✅ **Complete Data** - User messages, responses, tool calls, timing, errors  
✅ **Session Tracking** - Each session gets a unique timestamped file  
✅ **Easy Analysis** - JSON format perfect for data analysis  

---

## Log Files Location

All logs are saved in the `logs/` directory:

```
logs/
├── conversation_20250115_143022.json  # JSON format (structured)
└── conversation_20250115_143022.txt  # Text format (readable)
```

**File naming:** `conversation_YYYYMMDD_HHMMSS.{format}`

---

## What Gets Logged

### 1. User Messages
- Every user input/question

### 2. Assistant Responses
- Complete Claude responses
- Final text output

### 3. Tool Calls
- Tool name
- Input parameters
- Tool ID

### 4. Tool Results
- Success/failure status
- Execution time
- Result length
- Error messages (if any)

### 5. Timing Information
- Tools loading time
- API call times
- Tool execution times
- Total response time

### 6. Errors
- Any exceptions or errors
- Error messages

### 7. Session Summary
- Total messages
- Total session time
- Start/end timestamps

---

## Log Formats

### JSON Format (Structured)

**File:** `conversation_YYYYMMDD_HHMMSS.json`

**Structure:**
```json
[
  {
    "timestamp": "2025-01-15T14:30:22.123456",
    "user_message": "What does John 3:16 say?",
    "assistant_response": "約翰福音 3:16 說：神愛世人...",
    "tool_calls": [
      {
        "name": "get_bible_verse",
        "input": {
          "book": "John",
          "chapter": 3,
          "verse": "16",
          "version": "unv"
        },
        "id": "toolu_xxx"
      }
    ],
    "tool_results": [
      {
        "tool_name": "get_bible_verse",
        "tool_use_id": "toolu_xxx",
        "time": 1.52,
        "is_error": false,
        "result_length": 245
      }
    ],
    "timing": {
      "tools_loading": 0.01,
      "initial_api_call": 2.15,
      "tool_execution": 1.52,
      "total": 3.68
    },
    "error": null
  }
]
```

**Use Cases:**
- Data analysis (Python, pandas, etc.)
- Performance analysis
- Tool usage statistics
- Error tracking
- Automated reporting

### Text Format (Human-Readable)

**File:** `conversation_YYYYMMDD_HHMMSS.txt`

**Example:**
```
Bible Chatbot Conversation Log
Session ID: 20250115_143022
Started: 2025-01-15 14:30:22
================================================================================

[2025-01-15T14:30:22.123456]
User: What does John 3:16 say?

Tool Calls (1):
  - get_bible_verse: {'book': 'John', 'chapter': 3, 'verse': '16', 'version': 'unv'}

Tool Results:
  ✅ get_bible_verse (1.52s)

Timing:
  tools_loading: 0.01s
  initial_api_call: 2.15s
  tool_execution: 1.52s
  total: 3.68s

Assistant: 約翰福音 3:16 說：神愛世人，甚至將他的獨生子賜給他們，叫一切信他的，不至滅亡，反得永生。
--------------------------------------------------------------------------------
```

**Use Cases:**
- Quick review
- Sharing with others
- Debugging
- Manual analysis

---

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Enable/disable logging (default: true)
ENABLE_LOGGING=true

# Log format: "json", "text", or "both" (default: "both")
LOG_FORMAT=both
```

### Programmatic Configuration

```python
from bible_chatbot import BibleChatbot

# Enable logging with both formats (default)
chatbot = BibleChatbot(server_path, enable_logging=True, log_format="both")

# Only JSON format
chatbot = BibleChatbot(server_path, enable_logging=True, log_format="json")

# Only text format
chatbot = BibleChatbot(server_path, enable_logging=True, log_format="text")

# Disable logging
chatbot = BibleChatbot(server_path, enable_logging=False)
```

---

## Analysis Examples

### 1. Analyze Tool Usage (Python)

```python
import json
from pathlib import Path

# Load log file
with open("logs/conversation_20250115_143022.json") as f:
    logs = json.load(f)

# Count tool usage
tool_counts = {}
for entry in logs:
    for tool_call in entry.get("tool_calls", []):
        tool_name = tool_call["name"]
        tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

print("Tool Usage:")
for tool, count in sorted(tool_counts.items(), key=lambda x: -x[1]):
    print(f"  {tool}: {count}")
```

### 2. Calculate Average Response Time

```python
import json

with open("logs/conversation_20250115_143022.json") as f:
    logs = json.load(f)

total_time = sum(entry["timing"]["total"] for entry in logs)
avg_time = total_time / len(logs)

print(f"Average response time: {avg_time:.2f}s")
```

### 3. Find Errors

```python
import json

with open("logs/conversation_20250115_143022.json") as f:
    logs = json.load(f)

errors = [entry for entry in logs if entry.get("error")]
print(f"Found {len(errors)} errors:")
for entry in errors:
    print(f"  {entry['timestamp']}: {entry['error']}")
```

### 4. Export to CSV (Pandas)

```python
import json
import pandas as pd

with open("logs/conversation_20250115_143022.json") as f:
    logs = json.load(f)

# Create DataFrame
df = pd.DataFrame([
    {
        "timestamp": entry["timestamp"],
        "user_message": entry["user_message"],
        "response_length": len(entry["assistant_response"]),
        "tool_count": len(entry.get("tool_calls", [])),
        "total_time": entry["timing"]["total"],
        "has_error": entry.get("error") is not None
    }
    for entry in logs
])

# Save to CSV
df.to_csv("conversation_analysis.csv", index=False)
print(df.describe())
```

### 5. Analyze Tool Performance

```python
import json
from collections import defaultdict

with open("logs/conversation_20250115_143022.json") as f:
    logs = json.load(f)

tool_times = defaultdict(list)
tool_errors = defaultdict(int)

for entry in logs:
    for result in entry.get("tool_results", []):
        tool_name = result["tool_name"]
        tool_times[tool_name].append(result["time"])
        if result.get("is_error"):
            tool_errors[tool_name] += 1

print("Tool Performance:")
for tool, times in tool_times.items():
    avg_time = sum(times) / len(times)
    error_count = tool_errors.get(tool, 0)
    print(f"  {tool}:")
    print(f"    Average time: {avg_time:.2f}s")
    print(f"    Total calls: {len(times)}")
    print(f"    Errors: {error_count}")
```

---

## Log File Management

### View Recent Logs

```bash
# List all log files
ls -lt logs/

# View latest text log
tail -f logs/conversation_*.txt | head -100

# View latest JSON log
cat logs/conversation_*.json | jq '.[-1]'  # Last entry
```

### Clean Up Old Logs

```bash
# Delete logs older than 30 days
find logs/ -name "conversation_*.json" -mtime +30 -delete
find logs/ -name "conversation_*.txt" -mtime +30 -delete
```

### Archive Logs

```bash
# Archive logs by month
mkdir -p logs/archive
tar -czf logs/archive/2025-01.tar.gz logs/conversation_202501*.json logs/conversation_202501*.txt
```

---

## Best Practices

1. **Regular Cleanup** - Archive or delete old logs periodically
2. **Privacy** - Logs may contain sensitive information, handle accordingly
3. **Storage** - Logs can grow large, monitor disk space
4. **Analysis** - Use JSON format for programmatic analysis
5. **Review** - Use text format for quick human review

---

## Troubleshooting

### Logs Not Being Created

1. Check `ENABLE_LOGGING=true` in `.env`
2. Check write permissions for `logs/` directory
3. Check console output for error messages

### Logs Too Large

1. Reduce `max_history` parameter
2. Use only JSON format (smaller than text)
3. Implement log rotation

### Missing Data

1. Check if error occurred before logging
2. Verify log file format matches configuration
3. Check for file write errors

---

## Summary

✅ **Automatic logging** saves all conversations  
✅ **JSON format** for data analysis  
✅ **Text format** for human review  
✅ **Complete data** including timing and errors  
✅ **Easy configuration** via environment variables  

Logs are saved to `logs/` directory with timestamped filenames for easy organization and analysis.

