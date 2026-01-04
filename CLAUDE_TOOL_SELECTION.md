# How Claude API Decides Which Tools to Call 🔧

## Overview

Claude doesn't use explicit "if-then" rules. Instead, it uses **intelligent pattern matching** based on:
1. **System Prompt** - High-level instructions
2. **Tool Descriptions** - What each tool does
3. **Tool Schemas** - Parameters and requirements
4. **Conversation Context** - Previous messages
5. **User Query Analysis** - Understanding the request

---

## 📋 The Decision Process

```
┌─────────────────────────────────────────────────────────┐
│              CLAUDE'S TOOL SELECTION PROCESS           │
└─────────────────────────────────────────────────────────┘

1. RECEIVE USER QUERY
   │
   ├─► Analyze user intent
   │   - What is the user asking?
   │   - What information do they need?
   │   - What actions are required?
   │
   ▼
2. REVIEW AVAILABLE TOOLS
   │
   ├─► Read tool descriptions (19 tools available)
   │   - get_bible_verse: "查詢指定的聖經經文..."
   │   - search_bible: "搜尋聖經經文..."
   │   - get_word_analysis: "取得原文字彙分析..."
   │   - etc.
   │
   ├─► Match query intent to tool capabilities
   │   - "John 3:16" → get_bible_verse
   │   - "verses about love" → search_bible
   │   - "Greek word for love" → get_word_analysis
   │
   ▼
3. CHECK TOOL SCHEMAS
   │
   ├─► Verify required parameters
   │   - get_bible_verse requires: book, chapter, verse
   │   - Can extract from user query?
   │
   ├─► Check optional parameters
   │   - version: default "unv" for Chinese users
   │   - include_strong: needed for word analysis?
   │
   ▼
4. APPLY SYSTEM PROMPT GUIDELINES
   │
   ├─► "Use appropriate tools to fetch accurate information"
   │
   ├─► "For Chinese users, default to 和合本 (unv)"
   │
   ├─► "For original language questions, use word analysis"
   │
   ▼
5. DECIDE: CALL TOOL OR RESPOND DIRECTLY
   │
   ├─► If tool needed → Call tool(s)
   │
   └─► If no tool needed → Generate direct response
```

---

## 🎯 Key Factors in Tool Selection

### 1. System Prompt (Primary Guidance)

**Location:** `src/chatbot.py` lines 28-44

```python
self.system_prompt = """You are a helpful Bible study assistant. 
You have access to the FHL (Faith, Hope, Love 信望愛站) Bible API through MCP tools.

Available capabilities:
- Look up Bible verses in multiple translations (和合本, KJV, etc.)
- Search for verses by keyword
- Get word analysis (Greek/Hebrew)
- Look up Strong's dictionary entries
- Access commentaries
- Get topical studies

When users ask about Bible verses or topics:
1. Use the appropriate tools to fetch accurate information
2. Provide the verse text along with context when helpful
3. For Chinese users, default to 和合本 (unv) unless they specify otherwise
4. For original language questions, use word analysis and Strong's tools

Be respectful, accurate, and helpful in discussing Scripture."""
```

**What it does:**
- ✅ Defines Claude's role (Bible study assistant)
- ✅ Lists available capabilities (high-level overview)
- ✅ Provides decision guidelines (when to use which tools)
- ✅ Sets defaults (unv for Chinese users)
- ✅ Establishes tone (respectful, accurate)

**Impact on tool selection:**
- Guides Claude to **always use tools** for Bible queries (not guess)
- Suggests **which tool category** to use based on query type
- Sets **default parameters** (version="unv" for Chinese)

---

### 2. Tool Descriptions (What Each Tool Does)

**Location:** `FHL-MCP-Server/src/fhl_bible_mcp/server.py` (Tool definitions)

**Example Tool Definition:**
```python
Tool(
    name="get_bible_verse",
    description="查詢指定的聖經經文。支援單節、多節、節範圍查詢。",
    inputSchema={
        "type": "object",
        "properties": {
            "book": {
                "type": "string",
                "description": "經卷名稱（中文或英文縮寫，如：約、John、創世記、Genesis）"
            },
            "chapter": {"type": "integer", "description": "章數"},
            "verse": {
                "type": "string",
                "description": "節數（支援格式：'1', '1-5', '1,3,5', '1-2,5,8-10'）"
            },
            "version": {
                "type": "string",
                "description": "聖經版本代碼（預設：unv）"
            },
            # ... more parameters
        },
        "required": ["book", "chapter", "verse"]
    }
)
```

**What Claude sees:**
- **Tool name**: `get_bible_verse`
- **Description**: "查詢指定的聖經經文。支援單節、多節、節範圍查詢。"
- **Parameters**: What each parameter does and what's required

**How Claude uses it:**
1. Reads description to understand tool purpose
2. Matches user query to tool description
3. Checks if it can extract required parameters from query
4. Decides if this tool is appropriate

**Example matching:**
```
User: "What does John 3:16 say?"
  │
  ├─► Claude reads: "get_bible_verse - 查詢指定的聖經經文"
  │
  ├─► Matches: User wants a specific verse (John 3:16)
  │
  ├─► Checks parameters:
  │   - book: "John" ✅ (can extract)
  │   - chapter: 3 ✅ (can extract)
  │   - verse: 16 ✅ (can extract)
  │   - version: "unv" ✅ (default from system prompt)
  │
  └─► Decision: CALL get_bible_verse
```

---

### 3. Tool Input Schemas (Parameter Requirements)

**What Claude analyzes:**

**Required Parameters:**
- Must be extractable from user query or have defaults
- If missing → Claude won't call the tool (or will ask user)

**Optional Parameters:**
- Claude decides based on context
- Example: `include_strong=True` if user asks about original languages

**Parameter Descriptions:**
- Help Claude understand what each parameter means
- Guide parameter extraction from natural language

**Example:**
```python
"verse": {
    "type": "string",
    "description": "節數（支援格式：'1', '1-5', '1,3,5', '1-2,5,8-10'）"
}
```

Claude learns:
- Verse can be single: "16"
- Verse can be range: "16-18"
- Verse can be multiple: "16,18,20"
- Verse can be complex: "16-18,20,22-24"

---

### 4. Conversation Context

**How Claude uses conversation history:**

```python
messages=self.conversation_history  # Sent to Claude API
```

**Context helps Claude:**
1. **Remember previous tool calls**
   - If user asked about John 3:16, then asks "What about verse 17?"
   - Claude knows "verse 17" refers to John 3:17

2. **Understand follow-up questions**
   - User: "Get John 3:16"
   - User: "Now get it in KJV"
   - Claude knows to use same book/chapter/verse, different version

3. **Maintain conversation flow**
   - Previous context informs tool selection
   - Avoids redundant tool calls

**Example:**
```
User: "What does John 3:16 say?"
Claude: [Calls get_bible_verse(book="John", chapter=3, verse=16, version="unv")]
        "約翰福音 3:16 說：神愛世人..."

User: "What's the Greek word for 'love' in that verse?"
Claude: [Remembers context: John 3:16]
        [Calls get_word_analysis(book="John", chapter=3, verse=16, word="愛")]
        "在約翰福音 3:16 中，'愛' 的希臘文是..."
```

---

### 5. User Query Analysis

**Claude analyzes the user's natural language:**

**Pattern Matching Examples:**

| User Query | Claude's Analysis | Tool Selected |
|------------|-------------------|---------------|
| "John 3:16" | Specific verse reference | `get_bible_verse` |
| "verses about love" | Keyword search | `search_bible` |
| "Greek word for love" | Original language analysis | `get_word_analysis` |
| "commentary on John 3:16" | Commentary needed | `get_commentary` |
| "Strong's number for agape" | Strong's dictionary | `lookup_strongs` |
| "audio of Psalm 23" | Audio content | `get_audio_bible` |
| "list Bible versions" | Information query | `list_bible_versions` |

**Claude's reasoning process:**

1. **Extract intent:**
   - "What does X say?" → Need verse text
   - "What is the Greek word?" → Need word analysis
   - "Search for verses about Y" → Need search

2. **Extract parameters:**
   - "John 3:16" → book="John", chapter=3, verse=16
   - "verses about love" → keyword="love"
   - "in KJV" → version="kjv"

3. **Match to tool:**
   - Intent + Parameters → Select appropriate tool

---

## 🔄 Complete Example Flow

### Example 1: Simple Verse Query

**User:** "What does John 3:16 say?"

**Claude's Process:**

```
1. READ SYSTEM PROMPT
   └─► "Use appropriate tools to fetch accurate information"
   └─► "For Chinese users, default to 和合本 (unv)"

2. ANALYZE USER QUERY
   └─► Intent: Get specific verse text
   └─► Parameters: book="John", chapter=3, verse=16

3. REVIEW TOOLS
   └─► get_bible_verse: "查詢指定的聖經經文"
   └─► ✅ Matches intent perfectly

4. CHECK SCHEMA
   └─► Required: book ✅, chapter ✅, verse ✅
   └─► Optional: version → use "unv" (default)

5. DECISION
   └─► CALL: get_bible_verse(book="John", chapter=3, verse=16, version="unv")
```

**Result:**
```json
{
  "type": "tool_use",
  "name": "get_bible_verse",
  "input": {
    "book": "John",
    "chapter": 3,
    "verse": "16",
    "version": "unv"
  }
}
```

---

### Example 2: Complex Query with Multiple Tools

**User:** "Compare John 3:16 in KJV and 和合本, and get the Greek word for 'love'"

**Claude's Process:**

```
1. ANALYZE QUERY
   └─► Multiple intents:
       - Get verse in KJV
       - Get verse in 和合本 (unv)
       - Get Greek word analysis

2. MATCH TO TOOLS
   └─► get_bible_verse (for KJV)
   └─► get_bible_verse (for unv)
   └─► get_word_analysis (for Greek)

3. EXTRACT PARAMETERS
   └─► Common: book="John", chapter=3, verse=16
   └─► Different: version="kjv" vs version="unv"
   └─► Word analysis: word="love"

4. DECISION
   └─► CALL 3 tools in parallel:
       - get_bible_verse(book="John", chapter=3, verse=16, version="kjv")
       - get_bible_verse(book="John", chapter=3, verse=16, version="unv")
       - get_word_analysis(book="John", chapter=3, verse=16, word="love")
```

**Result:**
```json
[
  {
    "type": "tool_use",
    "name": "get_bible_verse",
    "input": {"book": "John", "chapter": 3, "verse": "16", "version": "kjv"}
  },
  {
    "type": "tool_use",
    "name": "get_bible_verse",
    "input": {"book": "John", "chapter": 3, "verse": "16", "version": "unv"}
  },
  {
    "type": "tool_use",
    "name": "get_word_analysis",
    "input": {"book": "John", "chapter": 3, "verse": 16, "word": "love"}
  }
]
```

---

## 🎓 How to Improve Tool Selection

### 1. Enhance System Prompt

**Current:**
```python
"When users ask about Bible verses or topics:
1. Use the appropriate tools to fetch accurate information
2. Provide the verse text along with context when helpful
3. For Chinese users, default to 和合本 (unv) unless they specify otherwise
4. For original language questions, use word analysis and Strong's tools"
```

**Could be enhanced with:**
- More specific tool selection guidelines
- Examples of when to use each tool category
- Handling of ambiguous queries
- Error recovery strategies

### 2. Improve Tool Descriptions

**Good description:**
```python
description="查詢指定的聖經經文。支援單節、多節、節範圍查詢。"
```

**Better description (more context):**
```python
description="""查詢指定的聖經經文。支援單節、多節、節範圍查詢。

使用時機：
- 用戶明確提到書卷、章節、節數時
- 例如："John 3:16", "約翰福音 3:16", "創世記 1:1-5"

不適用於：
- 關鍵字搜尋（使用 search_bible）
- 整章查詢（使用 get_bible_chapter）
"""
```

### 3. Add Examples to Tool Schemas

**Current schema:**
```python
"book": {
    "type": "string",
    "description": "經卷名稱（中文或英文縮寫，如：約、John、創世記、Genesis）"
}
```

**Enhanced with examples:**
```python
"book": {
    "type": "string",
    "description": "經卷名稱（中文或英文縮寫，如：約、John、創世記、Genesis）",
    "examples": ["John", "約", "約翰福音", "Genesis", "創世記"]
}
```

---

## 📊 Tool Selection Decision Tree

```
USER QUERY
    │
    ├─► Contains verse reference? (John 3:16, 約翰福音 3:16)
    │   └─► YES → get_bible_verse
    │
    ├─► Contains search keywords? (verses about love, 關於愛的經文)
    │   └─► YES → search_bible
    │
    ├─► Asks about original language? (Greek, Hebrew, 希臘文, 希伯來文)
    │   └─► YES → get_word_analysis or lookup_strongs
    │
    ├─► Asks for commentary? (註釋, commentary, 解經)
    │   └─► YES → get_commentary
    │
    ├─► Asks for topic study? (主題, topic, 查經)
    │   └─► YES → get_topic_study
    │
    ├─► Asks for audio? (有聲, audio, 朗讀)
    │   └─► YES → get_audio_bible
    │
    └─► Asks for information? (版本列表, 書卷列表)
        └─► YES → list_bible_versions or get_book_list
```

---

## 🔍 Debugging Tool Selection

### How to see what Claude is thinking:

**1. Check the tool use response:**
```python
if response.stop_reason == "tool_use":
    tool_calls = [block for block in response.content if block.type == "tool_use"]
    for tool_call in tool_calls:
        print(f"Tool: {tool_call.name}")
        print(f"Input: {tool_call.input}")
```

**2. Add logging:**
```python
print(f"📋 {len(tool_calls)} tool(s) requested")
for tc in tool_calls:
    print(f"  🔧 {tc.name}: {tc.input}")
```

**3. Check conversation history:**
```python
# See what Claude saw
print(json.dumps(self.conversation_history, indent=2, ensure_ascii=False))
```

---

## 📝 Summary

### How Claude Decides:

1. **System Prompt** → Provides high-level guidance
2. **Tool Descriptions** → Understands what each tool does
3. **Tool Schemas** → Knows required/optional parameters
4. **User Query** → Analyzes intent and extracts parameters
5. **Conversation Context** → Uses previous messages for context

### Key Points:

- ✅ Claude uses **intelligent pattern matching**, not hardcoded rules
- ✅ Tool descriptions are **critical** - they guide selection
- ✅ System prompt sets **defaults and guidelines**
- ✅ Claude can call **multiple tools in parallel**
- ✅ Conversation history provides **context** for follow-up questions

### To Improve Tool Selection:

1. **Enhance system prompt** with more specific guidelines
2. **Improve tool descriptions** with use cases and examples
3. **Add examples** to tool schemas
4. **Monitor tool selection** with logging
5. **Refine based on** actual usage patterns

---

## 🎯 Best Practices

### For Tool Descriptions:
- ✅ Be specific about what the tool does
- ✅ Mention when to use it
- ✅ Include examples if helpful
- ✅ Note any limitations

### For System Prompt:
- ✅ Set clear defaults
- ✅ Provide decision guidelines
- ✅ Give examples of tool usage
- ✅ Handle edge cases

### For Tool Schemas:
- ✅ Clear parameter descriptions
- ✅ Mark required vs optional
- ✅ Provide examples
- ✅ Document parameter formats

