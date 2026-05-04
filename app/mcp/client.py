class MCPClient:
    def call(self, service: str, payload: dict):

        # MOCK вместо реального MCP сервиса
        return {
            "service": service,
            "data": {
                "status": "mock",
                "order_id": payload.get("order_id"),
                "raw_payload": payload
            }
        }