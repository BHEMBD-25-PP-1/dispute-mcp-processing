import sys
import json

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    class FastMCP:
        def __init__(self, name: str):
            self.name = name

        def tool(self):
            def decorator(func):
                return func

            return decorator

        def run(self, transport: str | None = None):
            raise RuntimeError("Install the mcp package to run the mock MCP server")

mcp = FastMCP("taxi-mock")

MOCK_RIDES = {
    "TXN-98765": {
        "order_id": "TXN-98765",
        "status": "completed",
        "route": "ул. Тверская, 10 → ул. Ленина, 5",
        "datetime": "2025-12-01T15:30:00",
        "amount": 1250.00,
        "currency": "RUB",
        "payment_status": "success",
        "driver": "Иван Петров",
        "car": "Kia Rio X123XX177",
    },
    "TXN-12345": {
        "order_id": "TXN-12345",
        "status": "cancelled",
        "route": "—",
        "datetime": "2025-12-02T09:15:00",
        "amount": 0.0,
        "currency": "RUB",
        "payment_status": "refunded",
        "driver": "—",
        "car": "—",
    },
}

@mcp.tool()
async def get_ride_details(order_id: str) -> str:
    """Получить детали поездки по ID заказа (эмуляция Такси)"""
    ride = MOCK_RIDES.get(order_id)
    if not ride:
        return json.dumps({"error": f"Заказ {order_id} не найден"}, ensure_ascii=False)
    return json.dumps(ride, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--transport=sse":
        import uvicorn
        mcp.run(transport="sse")
    else:
        mcp.run()