from collections.abc import Generator
from typing import Any
import json
from mem0 import MemoryClient
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RetrieveMem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Initialize client with API key from credentials
        client = MemoryClient(api_key=self.runtime.credentials["mem0_api_key"])
        
        # Search memory
        results = client.search(
            query=tool_parameters["query"],
            user_id=tool_parameters["user_id"]
        )
        
        # Return JSON format
        yield self.create_json_message({
            "query": tool_parameters["query"],
            "results": [{
                "id": r["id"],
                "memory": r["memory"],
                "score": r["score"],
                "categories": r.get("categories", []),
                "created_at": r["created_at"]
            } for r in results]
        })
        
        # Return text format
        text_response = f"Query: {tool_parameters['query']}\n\nResults:\n"
        if results:
            for idx, r in enumerate(results, 1):
                text_response += f"\n{idx}. Memory: {r['memory']}"
                text_response += f"\n   Score: {r['score']:.2f}"
                text_response += f"\n   Categories: {', '.join(r.get('categories', []))}"
        else:
            text_response += "\nNo results found."
            
        yield self.create_text_message(text_response)
