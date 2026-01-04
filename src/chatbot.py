"""
Bible Chatbot - Integrates FHL MCP Server with Claude API
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Support both direct execution and package import
try:
    from .mcp_client import FHLBibleClient
except ImportError:
    from mcp_client import FHLBibleClient

load_dotenv()


class ConversationLogger:
    """Logger for saving chatbot conversations and analysis data."""
    
    def __init__(self, log_dir: str | Path = "logs", format: str = "json"):
        """
        Initialize the logger.
        
        Args:
            log_dir: Directory to save log files
            format: Log format - "json", "text", or "both"
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.format = format
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file_json = self.log_dir / f"conversation_{self.session_id}.json"
        self.log_file_text = self.log_dir / f"conversation_{self.session_id}.txt"
        self.conversations = []
        
        # Write header to text file
        if format in ["text", "both"]:
            with open(self.log_file_text, "w", encoding="utf-8") as f:
                f.write(f"Bible Chatbot Conversation Log\n")
                f.write(f"Session ID: {self.session_id}\n")
                f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
    
    def log_message(self, user_message: str, assistant_response: str, 
                   tool_calls: list = None, tool_results: list = None,
                   timing: dict = None, error: str = None):
        """Log a complete conversation turn."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "tool_calls": tool_calls or [],
            "tool_results": tool_results or [],
            "timing": timing or {},
            "error": error
        }
        
        self.conversations.append(entry)
        
        # Save to JSON
        if self.format in ["json", "both"]:
            with open(self.log_file_json, "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        
        # Save to text
        if self.format in ["text", "both"]:
            with open(self.log_file_text, "a", encoding="utf-8") as f:
                f.write(f"\n[{entry['timestamp']}]\n")
                f.write(f"User: {user_message}\n")
                
                if tool_calls:
                    f.write(f"\nTool Calls ({len(tool_calls)}):\n")
                    for tc in tool_calls:
                        f.write(f"  - {tc.get('name', 'unknown')}: {tc.get('input', {})}\n")
                
                if tool_results:
                    f.write(f"\nTool Results:\n")
                    for tr in tool_results:
                        name = tr.get('tool_name', 'unknown')
                        success = "✅" if not tr.get('is_error') else "❌"
                        time_taken = tr.get('time', 0)
                        f.write(f"  {success} {name} ({time_taken:.2f}s)\n")
                
                if timing:
                    f.write(f"\nTiming:\n")
                    for key, value in timing.items():
                        f.write(f"  {key}: {value:.2f}s\n")
                
                if error:
                    f.write(f"\n❌ Error: {error}\n")
                
                f.write(f"\nAssistant: {assistant_response}\n")
                f.write("-" * 80 + "\n")
    
    def log_summary(self, total_messages: int, total_time: float):
        """Log session summary."""
        summary = {
            "session_id": self.session_id,
            "total_messages": total_messages,
            "total_time": total_time,
            "end_time": datetime.now().isoformat()
        }
        
        if self.format in ["text", "both"]:
            with open(self.log_file_text, "a", encoding="utf-8") as f:
                f.write(f"\n\n{'=' * 80}\n")
                f.write(f"Session Summary\n")
                f.write(f"Total Messages: {total_messages}\n")
                f.write(f"Total Time: {total_time:.2f}s\n")
                f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        return summary


class BibleChatbot:
    """A chatbot that uses Claude + FHL Bible MCP tools."""
    
    def __init__(self, server_path: str | Path, max_history: int = 10, 
                 enable_logging: bool = True, log_dir: str | Path = "logs", 
                 log_format: str = "both"):
        """
        Initialize the chatbot.
        
        Args:
            server_path: Path to FHL-MCP-Server directory
            max_history: Maximum number of messages to keep in history (default: 10)
                        Set to 0 to keep all history (not recommended)
            enable_logging: Enable conversation logging (default: True)
            log_dir: Directory to save log files (default: "logs")
            log_format: Log format - "json", "text", or "both" (default: "both")
        """
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.mcp_client = FHLBibleClient(server_path)
        self.conversation_history: list[dict] = []
        self.max_history = max_history
        self.logger = ConversationLogger(log_dir, log_format) if enable_logging else None
        self.current_tool_calls = []
        self.current_tool_results = []
        self.current_timing = {}
        self.system_prompt = """You are a helpful Bible study assistant. You have access to the FHL (Faith, Hope, Love 信望愛站) Bible API through MCP tools.

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

    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return the assistant's response.
        Handles tool calls automatically.
        """
        start_time = time.time()
        
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prune history before API call to reduce token usage
        self._prune_history()
        
        # Get tools from MCP server
        tools_start = time.time()
        tools = self.mcp_client.get_tools_for_claude()
        tools_time = time.time() - tools_start
        print(f"⏱️  Tools loaded in {tools_time:.2f}s")
        
        # Initial API call
        api_start = time.time()
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=self.system_prompt,
            tools=tools,
            messages=self.conversation_history
        )
        api_time = time.time() - api_start
        print(f"⏱️  Initial Claude API call: {api_time:.2f}s")
        
        # Handle tool use loop
        iteration = 0
        while response.stop_reason == "tool_use":
            iteration += 1
            print(f"\n🔄 Tool use iteration #{iteration}")
            
            # Extract tool calls
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            print(f"  📋 {len(tool_calls)} tool(s) requested")
            
            # Add assistant's response (with tool calls) to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Execute tool calls in PARALLEL (this is the key optimization)
            tool_start = time.time()
            self.current_tool_calls = []
            self.current_tool_results = []
            
            async def execute_tool(tool_call):
                """Execute a single tool call with timing"""
                tool_name = tool_call.name
                call_start = time.time()
                print(f"  🔧 Calling tool: {tool_name}")
                
                # Log tool call
                tool_call_info = {
                    "name": tool_name,
                    "input": tool_call.input,
                    "id": tool_call.id
                }
                self.current_tool_calls.append(tool_call_info)
                
                try:
                    result = await self.mcp_client.call_tool(
                        tool_name,
                        tool_call.input
                    )
                    call_time = time.time() - call_start
                    print(f"  ✅ {tool_name} completed in {call_time:.2f}s")
                    
                    tool_result_info = {
                        "tool_name": tool_name,
                        "tool_use_id": tool_call.id,
                        "time": call_time,
                        "is_error": False,
                        "result_length": len(result) if result else 0
                    }
                    self.current_tool_results.append(tool_result_info)
                    
                    return {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result
                    }
                except Exception as e:
                    call_time = time.time() - call_start
                    print(f"  ❌ {tool_name} failed in {call_time:.2f}s: {str(e)}")
                    
                    tool_result_info = {
                        "tool_name": tool_name,
                        "tool_use_id": tool_call.id,
                        "time": call_time,
                        "is_error": True,
                        "error": str(e)
                    }
                    self.current_tool_results.append(tool_result_info)
                    
                    return {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": f"Error: {str(e)}",
                        "is_error": True
                    }
            
            # Execute all tools in parallel using asyncio.gather
            tool_results = await asyncio.gather(*[execute_tool(tc) for tc in tool_calls])
            tool_time = time.time() - tool_start
            print(f"  ⏱️  All tools completed in {tool_time:.2f}s (parallel execution)")
            
            # Add tool results to history
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue the conversation
            api_start = time.time()
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.system_prompt,
                tools=tools,
                messages=self.conversation_history
            )
            api_time = time.time() - api_start
            print(f"  ⏱️  Claude API call: {api_time:.2f}s")
        
        # Extract final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text
        
        # Add final response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_text
        })
        
        total_time = time.time() - start_time
        print(f"\n⏱️  Total response time: {total_time:.2f}s")
        
        # Update timing info
        self.current_timing.update({
            "tools_loading": tools_time,
            "initial_api_call": api_time,
            "tool_execution": tool_time if 'tool_time' in locals() else 0,
            "total": total_time
        })
        
        # Log the conversation
        if self.logger:
            self.logger.log_message(
                user_message=user_message,
                assistant_response=final_text,
                tool_calls=self.current_tool_calls,
                tool_results=self.current_tool_results,
                timing=self.current_timing
            )
            print(f"  💾 Logged to: {self.logger.log_file_text if self.logger.format in ['text', 'both'] else self.logger.log_file_json}")
        
        return final_text
    
    def _prune_history(self):
        """Prune conversation history if it exceeds max_history to prevent rate limits."""
        if self.max_history > 0 and len(self.conversation_history) > self.max_history:
            old_count = len(self.conversation_history)
            self.conversation_history = self.conversation_history[-self.max_history:]
            print(f"  📝 Pruned history: {old_count} → {len(self.conversation_history)} messages")
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


async def main():
    """Run an interactive chat session."""
    server_path = Path(__file__).parent.parent / "FHL-MCP-Server"
    
    # Check if logging should be enabled (default: True)
    enable_logging = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
    log_format = os.getenv("LOG_FORMAT", "both")  # "json", "text", or "both"
    
    print("🔌 Connecting to FHL Bible MCP Server...")
    chatbot = BibleChatbot(server_path, enable_logging=enable_logging, log_format=log_format)
    
    if enable_logging:
        print(f"💾 Logging enabled: {log_format} format")
        print(f"   Logs saved to: {chatbot.logger.log_dir}")
    
    message_count = 0
    session_start = time.time()
    
    async with chatbot.mcp_client.connect():
        print("✅ Connected! Type 'quit' to exit, 'clear' to reset conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break
            if user_input.lower() == "clear":
                chatbot.clear_history()
                print("🗑️ Conversation cleared.\n")
                continue
            
            print("\n🤔 Thinking...")
            try:
                response = await chatbot.chat(user_input)
                print(f"\nAssistant: {response}\n")
                message_count += 1
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                # Log error if logging is enabled
                if chatbot.logger:
                    chatbot.logger.log_message(
                        user_message=user_input,
                        assistant_response="",
                        error=str(e)
                    )
        
        # Log session summary
        if chatbot.logger:
            total_time = time.time() - session_start
            summary = chatbot.logger.log_summary(message_count, total_time)
            print(f"\n📊 Session Summary:")
            print(f"   Total Messages: {message_count}")
            print(f"   Total Time: {total_time:.2f}s")
            print(f"   Logs saved to: {chatbot.logger.log_dir}")


if __name__ == "__main__":
    asyncio.run(main())
