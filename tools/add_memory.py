from collections.abc import Generator
from typing import Any
import json
from mem0 import MemoryClient
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Mem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Initialize client with API key from credentials
        client = MemoryClient(api_key=self.runtime.credentials["mem0_api_key"])
        
        # Format messages
        messages = [
            {"role": "user", "content": tool_parameters["user"]},
            {"role": "assistant", "content": tool_parameters["assistant"]}
        ]
        
        # Add to memory
        result = client.add(messages, user_id=tool_parameters["user_id"])
        
        # Return JSON format
        yield self.create_json_message({
            "status": "success",
            "messages": messages,
            "memory_ids": [r["id"] for r in result if r.get("event") == "ADD"]
        })
        
        # Return text format
        text_response = "Memory added successfully\n\n"
        text_response += "Added messages:\n"
        for msg in messages:
            text_response += f"- {msg['role']}: {msg['content']}\n"
        if result:
            text_response += f"\nMemory IDs: {', '.join(r['id'] for r in result if r.get('event') == 'ADD')}"
        
        yield self.create_text_message(text_response)
