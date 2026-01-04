# Bible Chatbot 📖

A conversational Bible study assistant powered by Claude API and the FHL (信望愛站) MCP Server. Features automatic conversation logging, parallel tool execution, and rate limit protection.

## ✨ Features

- 🔍 **Look up Bible verses** in multiple translations (和合本, KJV, etc.)
- 📚 **Search verses** by keyword
- 🔤 **Greek/Hebrew word analysis** with Strong's dictionary
- 📖 **Access commentaries** and topical studies
- 💬 **Natural conversation interface** with Claude
- ⚡ **Parallel tool execution** for faster responses (2-5x speedup)
- 📝 **Automatic conversation logging** (JSON & text formats)
- 🛡️ **Rate limit protection** with automatic history pruning
- ⏱️ **Performance tracking** for all operations

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Installation

1. **Clone this repository:**
```bash
git clone https://github.com/Peter-Tan/FHLbible-chatbot.git
cd bible-chatbot
```

2. **Clone the FHL MCP Server:**
```bash
git clone https://github.com/ytssamuel/FHL-MCP-Server.git FHL-MCP-Server
```

3. **Setup the FHL server:**
```bash
cd FHL-MCP-Server
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
cd ..
```

4. **Setup this project:**
```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

5. **Configure environment:**
```bash
cp env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

6. **Run the chatbot:**
```bash
cd src
python chatbot.py
```

## 📖 Usage Examples

```
You: What does John 3:16 say?

You: 請查詢約翰福音 3:16 的和合本經文

You: What's the Greek word for "love" in 1 Corinthians 13?

You: Search for verses about faith

You: Compare John 3:16 in KJV and 和合本
```

## 🏗️ Project Structure

```
bible-chatbot/
├── src/
│   ├── __init__.py          # Package exports
│   ├── chatbot.py           # Main chatbot (BibleChatbot + ConversationLogger)
│   └── mcp_client.py        # MCP client wrapper (FHLBibleClient)
├── logs/                    # Conversation logs (auto-generated)
│   ├── conversation_*.json  # JSON format
│   └── conversation_*.txt   # Text format
├── FHL-MCP-Server/          # FHL MCP Server (submodule or cloned)
├── pyproject.toml           # Package configuration
├── .env                     # Your API keys (not committed)
├── env.example              # Environment template
└── README.md
```

## 🎯 Key Features

### 1. Parallel Tool Execution
Tools execute simultaneously for 2-5x faster responses when multiple tools are needed.

### 2. Automatic Logging
All conversations are automatically saved to `logs/` directory in both JSON and text formats for analysis.

### 3. Rate Limit Protection
Automatic history pruning prevents exceeding Claude API rate limits (30,000 tokens/minute).

### 4. Performance Tracking
Detailed timing information for all operations (API calls, tool execution, etc.).

## 📊 Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────▶│   BibleChatbot  │────▶│   Claude API    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 │ MCP Protocol (stdio)
                                 ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  FHLBibleClient │────▶│ FHL-MCP-Server  │
                        └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │   FHL API       │
                                                │  (bible.fhl.net)│
                                                └─────────────────┘
```

## 📝 Configuration

### Environment Variables

Create a `.env` file (see `env.example`):

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional
ENABLE_LOGGING=true          # Enable conversation logging (default: true)
LOG_FORMAT=both              # "json", "text", or "both" (default: "both")
```

### Programmatic Configuration

```python
from bible_chatbot import BibleChatbot

chatbot = BibleChatbot(
    server_path="./FHL-MCP-Server",
    max_history=10,          # Keep last 10 messages (prevents rate limits)
    enable_logging=True,     # Enable logging
    log_format="both"        # Save both JSON and text
)
```

## 📚 Documentation

- **[CODE_STRUCTURE.md](CODE_STRUCTURE.md)** - Complete code structure and flowcharts
- **[CLAUDE_TOOL_SELECTION.md](CLAUDE_TOOL_SELECTION.md)** - How Claude selects tools
- **[PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md)** - Performance optimizations
- **[RATE_LIMIT_ANALYSIS.md](RATE_LIMIT_ANALYSIS.md)** - Rate limit prevention
- **[LOGGING_GUIDE.md](LOGGING_GUIDE.md)** - Conversation logging guide

## 🔧 Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests (if available)
pytest
```

### Code Structure

The chatbot uses a layered architecture:
1. **Presentation Layer**: `chatbot.py` - User interaction & logging
2. **Integration Layer**: `mcp_client.py` - MCP protocol wrapper
3. **Service Layer**: `FHL-MCP-Server` - Tool execution
4. **Data Layer**: `FHL API` - Bible data source

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FHL 信望愛站](https://www.fhl.net/) for the Bible API
- [Anthropic](https://www.anthropic.com/) for Claude API
- [MCP](https://modelcontextprotocol.io/) for the Model Context Protocol specification
- [FHL-MCP-Server](https://github.com/ytssamuel/FHL-MCP-Server) by ytssamuel

## ⚠️ Important Notes

- **API Keys**: Never commit your `.env` file. It's already in `.gitignore`.
- **Rate Limits**: The chatbot automatically prunes conversation history to prevent rate limit errors.
- **Logs**: Conversation logs are saved locally in `logs/` directory. Review privacy considerations.

## 🐛 Troubleshooting

### Rate Limit Errors
- The chatbot automatically prunes history, but if you still hit limits, reduce `max_history` parameter.

### MCP Server Connection Issues
- Ensure FHL-MCP-Server is properly installed: `cd FHL-MCP-Server && uv pip install -e .`
- Check that the venv exists: `ls FHL-MCP-Server/.venv`

### Logging Not Working
- Check `ENABLE_LOGGING=true` in `.env`
- Verify write permissions for `logs/` directory

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for Bible study and research
