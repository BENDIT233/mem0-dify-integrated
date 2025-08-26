from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Mem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get credentials
        api_key = self.runtime.credentials.get("mem0_api_key", "").strip()
        base_url = self.runtime.credentials.get("mem0_base_url", "").strip()
        
        # Use default base URL if not provided
        if not base_url:
            base_url = "https://api.mem0.ai"
        
        # Construct full API URL
        api_url = f"{base_url}/v1/memories/"
        
        # Format messages
        messages = [
            {"role": "user", "content": tool_parameters["user"]},
            {"role": "assistant", "content": tool_parameters["assistant"]}
        ]
        
        # Prepare payload
        payload = {
            "messages": messages,
            "user_id": tool_parameters["user_id"]
        }
        
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Token {api_key}"
        
        # Make direct HTTP request to mem0 API
        try:
            response = httpx.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Return JSON format
            yield self.create_json_message({
                "status": "success",
                "messages": messages,
                "memory_ids": [r["id"] for r in result if isinstance(r, dict) and r.get("event") == "ADD"]
            })
            
            # Return text format
            text_response = "Memory added successfully\n\n"
            text_response += "Added messages:\n"
            for msg in messages:
                text_response += f"- {msg['role']}: {msg['content']}\n"
            
            memory_ids = [r["id"] for r in result if isinstance(r, dict) and r.get("event") == "ADD"]
            if memory_ids:
                text_response += f"\nMemory IDs: {', '.join(memory_ids)}"
            
            yield self.create_text_message(text_response)
            
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_message = f"Error: {error_data['detail']}"
            except:
                pass
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to add memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to add memory: {error_message}")
