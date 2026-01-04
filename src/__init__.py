"""
Bible Chatbot - A conversational Bible study assistant.
"""

# Support both package import and direct execution
try:
    from .chatbot import BibleChatbot
    from .mcp_client import FHLBibleClient
except ImportError:
    from chatbot import BibleChatbot
    from mcp_client import FHLBibleClient

__all__ = ["BibleChatbot", "FHLBibleClient"]

