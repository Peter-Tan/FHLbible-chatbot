# Rate Limit Analysis: Why 30,000 Tokens/Minute is Exceeded

## 🔴 The Problem

**Error:** `429 - Rate limit exceeded: 30,000 input tokens per minute`

## 📊 Token Usage Breakdown

### What Gets Sent with EVERY API Call:

```
┌─────────────────────────────────────────────────────────┐
│              TOKEN USAGE PER API CALL                   │
└─────────────────────────────────────────────────────────┘

1. System Prompt
   ├─ Size: ~150 tokens
   └─ Sent: Every call (lines 69, 137)

2. Tool Definitions (19 tools)
   ├─ Size: ~5,000-8,000 tokens (estimated)
   ├─ Includes: name, description, inputSchema for each tool
   └─ Sent: Every call (lines 70, 138) ⚠️ MAJOR CONTRIBUTOR

3. Conversation History
   ├─ Size: GROWS with each message
   ├─ Includes:
   │   - All user messages
   │   - All assistant responses (with tool calls)
   │   - All tool results (can be LARGE)
   └─ Sent: Every call (lines 71, 139) ⚠️ GROWS UNBOUNDED

4. Current User Message
   ├─ Size: ~10-100 tokens (usually small)
   └─ Sent: Every call
```

### Example Token Calculation:

**First Message:**
```
System prompt:        150 tokens
19 tool definitions:  6,000 tokens
User message:          20 tokens
─────────────────────────────────
Total:                ~6,170 tokens ✅ OK
```

**After 5 Messages with Tool Calls:**
```
System prompt:        150 tokens
19 tool definitions:  6,000 tokens
Conversation history: 15,000 tokens (growing!)
User message:          20 tokens
─────────────────────────────────
Total:               ~21,170 tokens ✅ Still OK
```

**After 10 Messages with Large Tool Results:**
```
System prompt:        150 tokens
19 tool definitions:  6,000 tokens
Conversation history: 35,000 tokens ⚠️ TOO LARGE!
User message:          20 tokens
─────────────────────────────────
Total:               ~41,170 tokens ❌ EXCEEDS LIMIT!
```

**Multiple API Calls Per Request:**
- Initial call: ~21,170 tokens
- Tool use iteration 1: ~25,000 tokens (with tool results)
- Tool use iteration 2: ~28,000 tokens (more results)
- **Total in 1 minute: >30,000 tokens** ❌

---

## 🎯 Root Causes

### 1. **Unbounded Conversation History** ⚠️ PRIMARY ISSUE

**Problem:**
```python
# Lines 53-56, 87-90, 127-130, 151-154
self.conversation_history.append(...)  # Never pruned!
```

**Impact:**
- History grows with every message
- Tool results can be large (full verse text, commentary)
- Each API call sends ENTIRE history
- After 5-10 messages, history can be 20,000+ tokens

**Example:**
```python
# Message 1: User asks for John 3:16
conversation_history = [
    {"role": "user", "content": "What does John 3:16 say?"},
    {"role": "assistant", "content": [tool_use]},
    {"role": "user", "content": [tool_result: "約翰福音 3:16\n神愛世人，甚至將他的獨生子賜給他們，叫一切信他的，不至滅亡，反得永生。"]},
    {"role": "assistant", "content": "約翰福音 3:16 說..."}
]
# ~500 tokens

# Message 5: History includes all previous messages + tool results
# ~5,000 tokens

# Message 10: History is huge
# ~20,000+ tokens
```

### 2. **Large Tool Definitions** ⚠️ SECONDARY ISSUE

**Problem:**
- 19 tools with detailed schemas sent with EVERY call
- Each tool has: name, description, inputSchema
- Some tool descriptions are very detailed (e.g., articles tool)

**Impact:**
- ~6,000 tokens per API call
- Sent even when tools aren't used
- Cannot be avoided (Claude needs tools to decide)

**Example Tool Size:**
```python
Tool(
    name="get_bible_verse",
    description="查詢指定的聖經經文。支援單節、多節、節範圍查詢。",  # ~20 tokens
    inputSchema={
        "type": "object",
        "properties": {
            "book": {"type": "string", "description": "..."},  # ~15 tokens
            "chapter": {"type": "integer", "description": "..."},  # ~10 tokens
            # ... more properties
        }
    }  # ~200 tokens per tool
)
# Total per tool: ~250 tokens
# 19 tools × 250 = ~4,750 tokens
```

### 3. **Large Tool Results** ⚠️ CONTRIBUTING FACTOR

**Problem:**
- Tool results can be very large
- Full verse text: ~100-500 tokens
- Commentary: ~500-2000 tokens
- Search results: ~1000-5000 tokens

**Impact:**
- Tool results added to conversation history
- History grows quickly with large results
- Sent with every subsequent API call

**Example:**
```python
# Tool result for get_bible_verse
result = """約翰福音 3:16
神愛世人，甚至將他的獨生子賜給他們，叫一切信他的，不至滅亡，反得永生。

約翰福音 3:17
因為神差他的兒子降世，不是要定世人的罪，乃是要叫世人因他得救。"""
# ~150 tokens

# Tool result for get_commentary
result = """[長篇註釋內容，可能數千字]"""
# ~2000+ tokens
```

### 4. **Multiple API Calls Per Request** ⚠️ AMPLIFIER

**Problem:**
- Each tool use iteration makes a new API call
- Each call sends: system + tools + full history
- If Claude needs 2-3 iterations, that's 2-3x the tokens

**Example:**
```
Request 1:
- Initial call: 21,000 tokens
- Tool iteration 1: 25,000 tokens (with results)
- Tool iteration 2: 28,000 tokens (more results)
─────────────────────────────────────────────
Total: 74,000 tokens in ~30 seconds ❌
```

---

## 💡 Solutions

### Solution 1: Prune Conversation History ✅ RECOMMENDED

**Implementation:**
```python
def prune_history(self, keep_last: int = 10):
    """Keep only the last N messages to reduce token usage."""
    if len(self.conversation_history) > keep_last:
        # Keep system context + last N messages
        self.conversation_history = self.conversation_history[-keep_last:]
```

**Impact:**
- Limits history to ~5,000-10,000 tokens
- Prevents unbounded growth
- Trade-off: Loses some context (but usually OK)

### Solution 2: Summarize Tool Results ✅ RECOMMENDED

**Implementation:**
```python
def summarize_tool_result(self, result: str, max_length: int = 500) -> str:
    """Truncate or summarize large tool results."""
    if len(result) > max_length:
        return result[:max_length] + "... [truncated]"
    return result
```

**Impact:**
- Reduces large tool results from 2000+ to ~500 tokens
- Keeps essential information
- Trade-off: May lose some detail

### Solution 3: Add Token Counting & Rate Limit Handling

**Implementation:**
```python
import tiktoken  # For token counting

def count_tokens(self, text: str) -> int:
    """Estimate token count."""
    encoding = tiktoken.encoding_for_model("claude-sonnet-4")
    return len(encoding.encode(text))

def check_rate_limit(self):
    """Check if we're approaching rate limit."""
    # Track tokens used in last minute
    # If > 25,000, wait or prune history
```

### Solution 4: Only Send Recent Context

**Implementation:**
```python
def get_recent_messages(self, max_tokens: int = 20000) -> list:
    """Get recent messages that fit within token limit."""
    messages = []
    token_count = 0
    
    # Add messages from end (most recent) until limit
    for msg in reversed(self.conversation_history):
        msg_tokens = self.count_tokens(str(msg))
        if token_count + msg_tokens > max_tokens:
            break
        messages.insert(0, msg)
        token_count += msg_tokens
    
    return messages
```

### Solution 5: Use Streaming (Future)

**Implementation:**
- Use Claude's streaming API
- Process responses incrementally
- May help with rate limits (check API docs)

---

## 🛠️ Quick Fix Implementation

### Immediate Fix: Add History Pruning

```python
class BibleChatbot:
    def __init__(self, server_path: str | Path, max_history: int = 10):
        # ... existing code ...
        self.max_history = max_history  # Limit conversation history
    
    def _prune_history(self):
        """Prune conversation history if it gets too long."""
        if len(self.conversation_history) > self.max_history:
            # Keep last N messages
            self.conversation_history = self.conversation_history[-self.max_history:]
            print(f"  📝 Pruned history to last {self.max_history} messages")
    
    async def chat(self, user_message: str) -> str:
        # ... existing code ...
        
        # After adding to history, prune if needed
        self._prune_history()
        
        # ... rest of method ...
```

### Add Token Estimation (Optional)

```python
def estimate_tokens(self, messages: list, tools: list) -> int:
    """Rough estimate of token count."""
    # System prompt: ~150
    # Tools: ~6,000 (19 tools)
    # Messages: ~50 tokens per message (rough estimate)
    # User message: ~20 tokens
    
    tool_tokens = 6000
    message_tokens = len(messages) * 50
    system_tokens = 150
    
    return tool_tokens + message_tokens + system_tokens
```

---

## 📈 Expected Improvements

### Before Fix:
- Message 1: ~6,000 tokens ✅
- Message 5: ~21,000 tokens ✅
- Message 10: ~41,000 tokens ❌ (exceeds limit)

### After Fix (with history pruning):
- Message 1: ~6,000 tokens ✅
- Message 5: ~11,000 tokens ✅ (pruned to last 10)
- Message 10: ~11,000 tokens ✅ (pruned to last 10)

**Improvement:** ~70% reduction in token usage for long conversations

---

## 🎯 Recommended Action Plan

1. **Immediate:** Add history pruning (Solution 1)
2. **Short-term:** Add token counting and warnings
3. **Medium-term:** Summarize large tool results
4. **Long-term:** Implement smart context management

---

## 📝 Summary

**Why rate limit is hit:**
1. ✅ **Unbounded conversation history** (PRIMARY)
2. ✅ **Large tool definitions** (6,000 tokens per call)
3. ✅ **Large tool results** (added to history)
4. ✅ **Multiple API calls** (amplifies the problem)

**Quick fix:**
- Prune conversation history to last 10 messages
- This alone should solve 80% of rate limit issues

**Long-term solution:**
- Smart context management
- Token counting and rate limit handling
- Summarize large results

