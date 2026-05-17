from app.mcp.base import BaseMCPClient

class MCPClient(BaseMCPClient):

    def call(self, service: str, payload: dict):

        # MOCK implementation
        return {
            "service": service,
            "data": {
                "status": "mock",
                "order_id": payload.get("order_id"),
                "details": f"Mock response from {service} MCP"
            }
        }