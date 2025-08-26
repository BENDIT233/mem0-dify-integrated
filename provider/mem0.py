from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.retrieve_memory import RetrieveMem0Tool


class Mem0Provider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证 base_url 格式（如果提供）
            base_url = credentials.get("mem0_base_url", "").strip()
            if base_url:
                # 确保 URL 格式正确
                if not base_url.startswith(("http://", "https://")):
                    raise ToolProviderCredentialValidationError(
                        "Base URL must start with http:// or https://"
                    )
                # 移除末尾的斜杠以保持一致性
                if base_url.endswith("/"):
                    credentials["mem0_base_url"] = base_url.rstrip("/")
            
            # 使用RetrieveMem0Tool来验证凭据
            tool = RetrieveMem0Tool.from_credentials(credentials)
            for _ in tool.invoke(
                tool_parameters={"query": "test", "user_id": "validation_test"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
