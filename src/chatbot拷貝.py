"""
Bible Chatbot - Integrates FHL MCP Server with Claude API
"""

import asyncio
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

# Support both direct execution and package import
try:
    from .mcp_client import FHLBibleClient
except ImportError:
    from mcp_client import FHLBibleClient

load_dotenv()


class BibleChatbot:
    """A chatbot that uses Claude + FHL Bible MCP tools."""
    
    def __init__(self, server_path: str | Path):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.mcp_client = FHLBibleClient(server_path)
        self.conversation_history: list[dict] = []
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
            async def execute_tool(tool_call):
                """Execute a single tool call with timing"""
                tool_name = tool_call.name
                call_start = time.time()
                print(f"  🔧 Calling tool: {tool_name}")
                try:
                    result = await self.mcp_client.call_tool(
                        tool_name,
                        tool_call.input
                    )
                    call_time = time.time() - call_start
                    print(f"  ✅ {tool_name} completed in {call_time:.2f}s")
                    return {
                        "type": "tool_result",
                        "tool_use_id": tool_call.id,
                        "content": result
                    }
                except Exception as e:
                    call_time = time.time() - call_start
                    print(f"  ❌ {tool_name} failed in {call_time:.2f}s: {str(e)}")
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
        
        return final_text
        
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
        
        return final_text
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []


async def main():
    """Run an interactive chat session."""
    server_path = Path(__file__).parent.parent / "FHL-MCP-Server"
    
    print("🔌 Connecting to FHL Bible MCP Server...")
    chatbot = BibleChatbot(server_path)
    
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
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
