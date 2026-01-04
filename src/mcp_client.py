"""
MCP Client for FHL Bible Server
Connects to the FHL-MCP-Server and exposes its tools for use with LLMs.
"""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class FHLBibleClient:
    """Client for interacting with FHL Bible MCP Server."""
    
    def __init__(self, server_path: str | Path):
        """
        Initialize the FHL Bible client.
        
        Args:
            server_path: Path to the FHL-MCP-Server directory
        """
        self.server_path = Path(server_path)
        self.session: ClientSession | None = None
        self._tools: list[dict] = []
    
    def _get_server_params(self) -> StdioServerParameters:
        """Get the server parameters for stdio connection."""
        # Use the venv python in the server directory
        venv_python = self.server_path / ".venv" / "bin" / "python"
        if not venv_python.exists():
            # Try Windows path
            venv_python = self.server_path / ".venv" / "Scripts" / "python.exe"
        
        if not venv_python.exists():
            raise FileNotFoundError(
                f"Python not found in FHL-MCP-Server venv. "
                f"Please run: cd {self.server_path} && uv venv && uv pip install -e ."
            )
        
        return StdioServerParameters(
            command=str(venv_python),
            args=["-m", "fhl_bible_mcp"],
            env={"PYTHONPATH": str(self.server_path / "src")}
        )
    
    @asynccontextmanager
    async def connect(self):
        """Context manager for connecting to the FHL MCP server."""
        server_params = self._get_server_params()
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                
                # Cache available tools
                tools_response = await session.list_tools()
                self._tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in tools_response.tools
                ]
                
                yield self
                
                self.session = None
    
    @property
    def tools(self) -> list[dict]:
        """Get available tools in Anthropic tool format."""
        return self._tools
    
    def get_tools_for_claude(self) -> list[dict]:
        """Format tools for Claude API."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"]
            }
            for tool in self._tools
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> str:
        """
        Call a tool on the FHL server.
        
        Args:
            name: Tool name (e.g., "get_bible_verse")
            arguments: Tool arguments
            
        Returns:
            Tool result as string
        """
        if not self.session:
            raise RuntimeError("Not connected. Use 'async with client.connect():'")
        
        result = await self.session.call_tool(name, arguments)
        
        # Extract text content from result
        if result.content:
            texts = [c.text for c in result.content if hasattr(c, 'text')]
            return "\n".join(texts)
        return ""
    
    async def list_resources(self) -> list[dict]:
        """List available resources from the server."""
        if not self.session:
            raise RuntimeError("Not connected")
        
        response = await self.session.list_resources()
        return [
            {"uri": r.uri, "name": r.name, "description": r.description}
            for r in response.resources
        ]
    
    async def read_resource(self, uri: str) -> str:
        """Read a resource by URI."""
        if not self.session:
            raise RuntimeError("Not connected")
        
        response = await self.session.read_resource(uri)
        if response.contents:
            texts = [c.text for c in response.contents if hasattr(c, 'text')]
            return "\n".join(texts)
        return ""


# Quick test
async def main():
    """Test the FHL Bible client."""
    # Adjust path to your FHL-MCP-Server location
    server_path = Path(__file__).parent.parent / "FHL-MCP-Server"
    
    client = FHLBibleClient(server_path)
    
    async with client.connect():
        print("✅ Connected to FHL Bible MCP Server")
        print(f"\n📚 Available tools ({len(client.tools)}):")
        for tool in client.tools[:5]:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        
        # Test a simple verse lookup
        print("\n🔍 Testing verse lookup (John 3:16)...")
        result = await client.call_tool("get_bible_verse", {
            "book": "John",
            "chapter": 3,
            "verse": 16,
            "version": "unv"  # 和合本
        })
        print(f"Result:\n{result}")


if __name__ == "__main__":
    asyncio.run(main())
