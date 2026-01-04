# Bible Chatbot - Code Structure Flowchart 📊

## Overview

This document explains the complete code structure and data flow of the Bible Chatbot system, which integrates Claude API with the FHL Bible MCP Server. **Updated with latest features: logging, history pruning, and performance optimizations.**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         BIBLE CHATBOT SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
        ┌───────────▼──────────┐        ┌──────────▼──────────┐
        │  Bible Chatbot App   │        │  FHL-MCP-Server     │
        │  (bible-chatbot/)    │        │  (FHL-MCP-Server/)   │
        └───────────┬──────────┘        └──────────┬──────────┘
                    │                               │
        ┌───────────┴──────────┐        ┌──────────┴──────────┐
        │                      │        │                      │
┌───────▼──────┐    ┌─────────▼──────┐ │  ┌─────────────────▼──────────┐
│  chatbot.py  │    │  mcp_client.py  │◄─┼──│  MCP Server (stdio)       │
│              │    │                │    │  │  - Tools (19 tools)        │
│  - BibleChatbot│    │  - FHLBibleClient│    │  - Resources (7 types)    │
│  - ConversationLogger│  - connect()   │    │  - Prompts (4 templates)   │
│  - main()     │    └────────────────┘    │  └─────────────────┬──────────┘
└───────┬──────┘                            │                    │
        │                                   │  ┌─────────────────▼──────────┐
        │                                   │  │  FHL API Client             │
        │                                   │  │  (fhl_bible_mcp/api/)       │
        │                                   └──┼── HTTP Requests             │
        │                                      └─────────────────┬──────────┘
        │                                                         │
        │                                      ┌──────────▼──────────┐
        │                                      │   FHL Bible API     │
        │                                      │  (bible.fhl.net)    │
        │                                      └─────────────────────┘
        │
        └──────────────────────────────────────┐
                                                 │
                                    ┌────────────▼────────────┐
                                    │  Conversation Logger    │
                                    │  - JSON logs            │
                                    │  - Text logs            │
                                    │  - Session tracking     │
                                    └─────────────────────────┘
```

---

## 📁 Project Structure

```
bible-chatbot/
├── src/
│   ├── __init__.py          # Package exports
│   ├── chatbot.py           # Main chatbot class (BibleChatbot + ConversationLogger)
│   └── mcp_client.py        # MCP client wrapper (FHLBibleClient)
│
├── logs/                    # Conversation logs (auto-generated)
│   ├── conversation_YYYYMMDD_HHMMSS.json  # JSON format
│   └── conversation_YYYYMMDD_HHMMSS.txt    # Text format
│
├── FHL-MCP-Server/          # External MCP Server
│   ├── src/
│   │   └── fhl_bible_mcp/
│   │       ├── server.py           # MCP Server main
│   │       ├── api/                # FHL API client
│   │       ├── tools/              # 19 tool functions
│   │       │   ├── verse.py
│   │       │   ├── search.py
│   │       │   ├── strongs.py
│   │       │   ├── commentary.py
│   │       │   ├── info.py
│   │       │   └── audio.py
│   │       ├── resources/          # Resource handlers
│   │       └── prompts/           # Prompt templates
│   └── pyproject.toml
│
├── pyproject.toml           # Chatbot package config
├── .env                     # API keys and config
│   ├── ANTHROPIC_API_KEY
│   ├── ENABLE_LOGGING
│   └── LOG_FORMAT
└── README.md
```

---

## 🔄 Execution Flow

### 1. Application Startup Flow (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    START: python src/chatbot.py                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  main() function│
                    │  (chatbot.py)   │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 1. Load environment (.env)   │
              │    - ANTHROPIC_API_KEY       │
              │    - ENABLE_LOGGING          │
              │    - LOG_FORMAT              │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 2. Create BibleChatbot       │
              │    - Initialize Anthropic    │
              │    - Create FHLBibleClient   │
              │    - Initialize Logger       │
              │    - Set max_history (10)    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 3. Connect to MCP Server     │
              │    async with client.connect()│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 4. Start interactive loop    │
              │    - Read user input          │
              │    - Process with chatbot     │
              │    - Log conversation         │
              │    - Display response         │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 5. On exit: Log summary      │
              │    - Total messages           │
              │    - Total time                │
              │    - Save session summary     │
              └──────────────────────────────┘
```

### 2. MCP Client Connection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│         FHLBibleClient.connect() - Context Manager              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │ 1. Get Server Parameters     │
              │    - Find venv python        │
              │    - Build StdioServerParams  │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 2. Create stdio_client       │
              │    - Spawn subprocess        │
              │    - Connect via stdin/stdout│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 3. Initialize ClientSession   │
              │    - Handshake with server    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 4. List Available Tools       │
              │    - Call session.list_tools()│
              │    - Cache tool definitions   │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 5. Yield client (ready)       │
              │    - Tools available         │
              │    - Ready for tool calls    │
              └──────────────────────────────┘
```

### 3. Chat Message Processing Flow (Updated with Logging & Pruning)

```
┌─────────────────────────────────────────────────────────────────┐
│              User Input: "What does John 3:16 say?"           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │ BibleChatbot.chat()          │
              │ 1. Add user message to       │
              │    conversation_history       │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 2. Prune History (NEW)       │
              │    _prune_history()          │
              │    - Keep last 10 messages   │
              │    - Prevent rate limits     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 3. Get tools from MCP client │
              │    get_tools_for_claude()     │
              │    Returns: 19 tool schemas   │
              │    ⏱️  Log: tools_loading time│
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 4. Call Claude API           │
              │    messages.create()         │
              │    - model: claude-sonnet-4  │
              │    - system: system_prompt   │
              │    - tools: 19 tool schemas  │
              │    - messages: history        │
              │    ⏱️  Log: initial_api_call time│
              └──────────────┬───────────────┘
                             │
                             ▼
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────▼──────┐   ┌────────▼────────┐
            │ stop_reason  │   │ stop_reason   │
            │ == "end_turn"│   │ == "tool_use"  │
            └───────┬──────┘   └────────┬───────┘
                    │                  │
                    │                  ▼
                    │      ┌───────────────────────┐
                    │      │ Extract tool calls    │
                    │      │ from response.content │
                    │      │ 📋 Log: tool_calls    │
                    │      └───────────┬───────────┘
                    │                  │
                    │                  ▼
                    │      ┌───────────────────────┐
                    │      │ Execute tools in      │
                    │      │ PARALLEL (NEW)         │
                    │      │ asyncio.gather()       │
                    │      │ ⏱️  Log: tool times    │
                    │      └───────────┬───────────┘
                    │                  │
                    │                  ▼
                    │      ┌───────────────────────┐
                    │      │ Add tool results to    │
                    │      │ conversation_history   │
                    │      └───────────┬───────────┘
                    │                  │
                    │                  ▼
                    │      ┌───────────────────────┐
                    │      │ Call Claude again      │
                    │      │ (with tool results)    │
                    │      │ ⏱️  Log: api_call time │
                    │      └───────────┬───────────┘
                    │                  │
                    └──────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 5. Extract final text        │
              │    from response.content     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 6. Log Conversation (NEW)    │
              │    logger.log_message()      │
              │    - User message             │
              │    - Assistant response       │
              │    - Tool calls & results     │
              │    - Timing data              │
              │    - Save to JSON & Text      │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ 7. Add to history & return    │
              │    Display to user            │
              └──────────────────────────────┘
```

### 4. Tool Call Execution Flow (Updated - Parallel Execution)

```
┌─────────────────────────────────────────────────────────────────┐
│  Claude decides to call: get_bible_verse("John", 3, 16, "unv") │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │ Extract Multiple Tool Calls   │
              │ (if Claude requests multiple) │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Execute in PARALLEL (NEW)    │
              │ asyncio.gather([             │
              │   execute_tool(tool1),       │
              │   execute_tool(tool2),       │
              │   execute_tool(tool3)        │
              │ ])                           │
              │                              │
              │ OLD: Sequential (slow)      │
              │ Tool1 → Tool2 → Tool3       │
              │                              │
              │ NEW: Parallel (fast)         │
              │ Tool1 ┐                     │
              │ Tool2 ├─ All at once         │
              │ Tool3 ┘                     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ For each tool:              │
              │ 1. Log tool call            │
              │ 2. Call MCP client           │
              │ 3. Measure execution time    │
              │ 4. Log result                │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ FHLBibleClient.call_tool()   │
              │ - name: "get_bible_verse"    │
              │ - arguments: {...}           │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ session.call_tool()          │
              │ (MCP Protocol)               │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ MCP Server receives request  │
              │ (FHL-MCP-Server)             │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Route to tool handler        │
              │ get_bible_verse()            │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Call FHL API Client          │
              │ endpoints.get_verse()        │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ HTTP Request to FHL API      │
              │ GET bible.fhl.net/api/...    │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ FHL API Response             │
              │ JSON: {verse_text, ...}      │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Format as TextContent        │
              │ Return via MCP Protocol      │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ Return to chatbot            │
              │ Result string                │
              │ ⏱️  Log: execution time      │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │ All tools complete            │
              │ (parallel execution)         │
              │ ⏱️  Total time: max(times)    │
              └──────────────────────────────┘
```

---

## 🧩 Component Details

### 1. BibleChatbot Class (Updated)

**Location:** `src/chatbot.py`

**Responsibilities:**
- Manages conversation with Claude API
- Handles tool use loop
- Maintains conversation history
- **Prunes history to prevent rate limits** (NEW)
- **Logs all conversations** (NEW)
- Formats responses

**Key Methods:**
```python
__init__(server_path, max_history=10, enable_logging=True, log_format="both")
chat(user_message)         # Process user message (async)
_prune_history()           # Prune history to last N messages (NEW)
clear_history()            # Reset conversation
```

**New Features:**
- **History Pruning**: Automatically keeps only last 10 messages to prevent rate limits
- **Logging**: Automatic conversation logging to JSON and/or text files
- **Performance Tracking**: Logs timing for all operations
- **Parallel Tool Execution**: Executes multiple tools simultaneously

**Data Flow:**
```
User Input → chat() → Prune History → Claude API → Parallel Tool Calls → MCP Server → Results → Claude → Response → Log → User
```

### 2. ConversationLogger Class (NEW)

**Location:** `src/chatbot.py`

**Responsibilities:**
- Saves all conversations to files
- Supports JSON and text formats
- Tracks session metadata
- Records tool calls and results
- Logs timing information

**Key Methods:**
```python
__init__(log_dir="logs", format="json")  # Initialize logger
log_message(user_message, assistant_response, tool_calls, tool_results, timing, error)
log_summary(total_messages, total_time)   # Session summary
```

**Log File Structure:**
- **JSON Format**: `conversation_YYYYMMDD_HHMMSS.json` - Structured data for analysis
- **Text Format**: `conversation_YYYYMMDD_HHMMSS.txt` - Human-readable logs

**Logged Data:**
- Timestamp
- User messages
- Assistant responses
- Tool calls (name, input parameters)
- Tool results (success/failure, execution time)
- Timing metrics (all operations)
- Errors (if any)

### 3. FHLBibleClient Class

**Location:** `src/mcp_client.py`

**Responsibilities:**
- Manages MCP protocol connection
- Wraps MCP client session
- Formats tools for Claude
- Executes tool calls

**Key Methods:**
```python
__init__(server_path)           # Initialize with server path
connect()                        # Context manager for connection
get_tools_for_claude()          # Format tools for Claude API
call_tool(name, arguments)      # Execute tool call (async)
```

**Connection Lifecycle:**
```
connect() → Initialize → List Tools → Cache → Ready → (use) → Disconnect
```

### 4. FHL-MCP-Server

**Location:** `FHL-MCP-Server/src/fhl_bible_mcp/`

**Components:**

#### a) Server (`server.py`)
- Main MCP server instance
- Registers 19 tools
- Handles MCP protocol
- Routes tool calls

#### b) Tools (19 total)
- **Verse Tools** (3): `get_bible_verse`, `get_bible_chapter`, `query_verse_citation`
- **Search Tools** (2): `search_bible`, `search_bible_advanced`
- **Strong's Tools** (3): `get_word_analysis`, `lookup_strongs`, `search_strongs_occurrences`
- **Commentary Tools** (4): `get_commentary`, `list_commentaries`, `search_commentary`, `get_topic_study`
- **Info Tools** (4): `list_bible_versions`, `get_book_list`, `get_book_info`, `search_available_versions`
- **Audio Tools** (3): `get_audio_bible`, `list_audio_versions`, `get_audio_chapter_with_text`

#### c) API Client (`api/endpoints.py`)
- HTTP client for FHL Bible API
- Handles authentication
- Formats requests/responses

#### d) Resources (`resources/`)
- URI-based resource access
- 7 resource types (bible://, strongs://, etc.)

#### e) Prompts (`prompts/`)
- 4 study templates
- Structured Bible study workflows

---

## 🔌 Communication Protocols

### 1. MCP Protocol (stdio)

```
Chatbot                    MCP Server
   │                           │
   │─── Initialize ───────────>│
   │<── Capabilities ──────────│
   │                           │
   │─── List Tools ───────────>│
   │<── Tool List ─────────────│
   │                           │
   │─── Call Tool ────────────>│
   │     (name, args)          │
   │                           │─── HTTP ───> FHL API
   │                           │<── Response ────│
   │<── Tool Result ───────────│
   │     (text content)        │
```

### 2. Claude API Protocol

```
Chatbot                    Claude API
   │                           │
   │─── POST /v1/messages ────>│
   │     {                     │
   │       model,              │
   │       system,             │
   │       tools,              │
   │       messages            │
   │     }                     │
   │                           │
   │<── Response ──────────────│
   │     {                     │
   │       content: [          │
   │         {type: "tool_use",│
   │          name, input}     │
   │       ],                  │
   │       stop_reason         │
   │     }                     │
   │                           │
   │─── POST /v1/messages ────>│
   │     (with tool results)   │
   │<── Final Response ────────│
```

---

## 📊 Data Structures

### Conversation History Format

```python
conversation_history: list[dict] = [
    {
        "role": "user",
        "content": "What does John 3:16 say?"
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_xxx",
                "name": "get_bible_verse",
                "input": {"book": "John", "chapter": 3, "verse": 16, "version": "unv"}
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "toolu_xxx",
                "content": "約翰福音 3:16\n神愛世人，甚至將他的獨生子賜給他們..."
            }
        ]
    },
    {
        "role": "assistant",
        "content": "約翰福音 3:16 說：神愛世人，甚至將他的獨生子賜給他們..."
    }
]
```

**Note:** History is automatically pruned to last 10 messages to prevent rate limits.

### Log Entry Format (NEW)

```python
log_entry = {
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
            "is_error": False,
            "result_length": 245
        }
    ],
    "timing": {
        "tools_loading": 0.01,
        "initial_api_call": 2.15,
        "tool_execution": 1.52,
        "total": 3.68
    },
    "error": None
}
```

### Tool Schema Format

```python
tool = {
    "name": "get_bible_verse",
    "description": "Get a Bible verse by book, chapter, and verse",
    "input_schema": {
        "type": "object",
        "properties": {
            "book": {"type": "string"},
            "chapter": {"type": "integer"},
            "verse": {"type": "integer"},
            "version": {"type": "string"}
        },
        "required": ["book", "chapter", "verse", "version"]
    }
}
```

---

## 🔄 Complete Request-Response Cycle (Updated)

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE CYCLE EXAMPLE                        │
└─────────────────────────────────────────────────────────────────┘

1. USER INPUT
   "What does John 3:16 say?"

2. CHATBOT PROCESSING
   ├─ Add to conversation_history
   ├─ Prune history (keep last 10) ← NEW
   ├─ Get tools from MCP client (19 tools)
   └─ Call Claude API

3. CLAUDE DECISION
   ├─ Analyzes: "User wants Bible verse"
   ├─ Selects tool: get_bible_verse
   └─ Returns: tool_use request

4. TOOL EXECUTION (PARALLEL) ← UPDATED
   ├─ Extract tool calls
   ├─ Execute in parallel using asyncio.gather() ← NEW
   ├─ For each tool:
   │   ├─ Log tool call
   │   ├─ mcp_client.call_tool()
   │   ├─ MCP Protocol → FHL-MCP-Server
   │   ├─ HTTP GET → FHL API
   │   ├─ Return result
   │   └─ Log execution time
   └─ All tools complete (parallel, faster!)

5. CLAUDE FINAL RESPONSE
   ├─ Receives tool results
   ├─ Generates natural language response
   └─ Returns: "約翰福音 3:16 說：神愛世人..."

6. LOGGING ← NEW
   ├─ Save to JSON: conversation_YYYYMMDD_HHMMSS.json
   ├─ Save to Text: conversation_YYYYMMDD_HHMMSS.txt
   └─ Include: message, response, tools, timing, errors

7. USER SEES
   "約翰福音 3:16 說：神愛世人，甚至將他的獨生子賜給他們..."
```

---

## 🎯 Key Design Patterns

### 1. **Context Manager Pattern**
- `FHLBibleClient.connect()` uses `@asynccontextmanager`
- Ensures proper connection lifecycle
- Automatic cleanup on exit

### 2. **Tool Use Loop Pattern**
- Claude can make multiple tool calls
- Loop continues until `stop_reason != "tool_use"`
- Each iteration adds results to history

### 3. **Parallel Execution Pattern** (NEW)
- Multiple tools execute simultaneously using `asyncio.gather()`
- Significantly faster than sequential execution
- 2-5x speedup for multiple tool calls

### 4. **History Pruning Pattern** (NEW)
- Automatically limits conversation history
- Prevents rate limit errors
- Keeps only most recent messages

### 5. **Logging Pattern** (NEW)
- Automatic conversation logging
- Multiple formats (JSON, text)
- Complete data capture for analysis

### 6. **MCP Protocol Pattern**
- stdio-based communication
- Subprocess spawning
- JSON-RPC-like message format

### 7. **Dependency Injection**
- `BibleChatbot` receives `server_path`
- `FHLBibleClient` receives `server_path`
- Allows flexible configuration

---

## 🚀 Entry Points

### 1. Direct Execution
```bash
cd src
python chatbot.py
```
- Runs `main()` function
- Interactive chat loop
- Automatic logging enabled
- Direct import (no package structure needed)

### 2. Package Import
```python
from bible_chatbot import BibleChatbot, FHLBibleClient

chatbot = BibleChatbot(
    server_path="./FHL-MCP-Server",
    max_history=10,
    enable_logging=True,
    log_format="both"
)
```
- After `pip install -e .`
- Proper package structure
- Relative imports work

---

## 🔍 Error Handling

```
┌─────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING                            │
└─────────────────────────────────────────────────────────────────┘

1. Connection Errors
   ├─ Venv not found → FileNotFoundError
   ├─ Server startup fails → RuntimeError
   └─ MCP handshake fails → ConnectionError

2. Tool Call Errors
   ├─ Tool not found → RuntimeError
   ├─ Invalid arguments → ValidationError
   ├─ API failure → HTTPError
   └─ All caught → Error message in tool_result + logged

3. Claude API Errors
   ├─ API key invalid → AuthenticationError
   ├─ Rate limit → RateLimitError (prevented by history pruning)
   └─ Network error → ConnectionError

4. User Input Errors
   ├─ Empty input → Skip
   ├─ "quit" → Exit gracefully + log summary
   └─ "clear" → Reset history

5. Logging Errors
   ├─ File write fails → Silent failure (doesn't break chat)
   └─ Logged to console if critical
```

---

## ⚡ Performance Optimizations

### 1. Parallel Tool Execution (NEW)

**Before:**
```python
# Sequential execution
for tool_call in tool_calls:
    result = await call_tool(tool_call)  # Wait for each
# Time: Sum of all tool times
```

**After:**
```python
# Parallel execution
results = await asyncio.gather(*[execute_tool(tc) for tc in tool_calls])
# Time: Max of all tool times (2-5x faster!)
```

### 2. History Pruning (NEW)

**Before:**
- History grows unbounded
- After 10 messages: ~20,000+ tokens
- Rate limit exceeded

**After:**
- History pruned to last 10 messages
- After 10 messages: ~10,000 tokens
- Prevents rate limits

### 3. Timing & Logging (NEW)

- All operations timed
- Performance metrics logged
- Easy to identify bottlenecks

---

## 📝 Summary

The Bible Chatbot system follows a **layered architecture** with **new enhancements**:

1. **Presentation Layer**: `chatbot.py` - User interaction + Logging
2. **Integration Layer**: `mcp_client.py` - MCP protocol wrapper
3. **Service Layer**: `FHL-MCP-Server` - Tool execution
4. **Data Layer**: `FHL API` - Bible data source
5. **Logging Layer**: `ConversationLogger` - Conversation persistence (NEW)

**Key Flow:**
```
User → BibleChatbot → Prune History → Claude API → Parallel Tool Calls → MCP Client → MCP Server → FHL API → Results → Claude → Response → Log → User
```

**New Features:**
- ✅ **Parallel Tool Execution** - 2-5x faster for multiple tools
- ✅ **History Pruning** - Prevents rate limit errors
- ✅ **Automatic Logging** - Complete conversation tracking
- ✅ **Performance Metrics** - Timing for all operations
- ✅ **Error Tracking** - All errors logged

This architecture provides:
- ✅ Separation of concerns
- ✅ Modularity and testability
- ✅ Extensibility (easy to add tools)
- ✅ Protocol abstraction (MCP)
- ✅ Natural language interface (Claude)
- ✅ Performance optimization (parallel execution)
- ✅ Rate limit prevention (history pruning)
- ✅ Complete audit trail (logging)
