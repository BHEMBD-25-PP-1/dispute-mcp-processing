import json
import sys

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


mcp = FastMCP("afisha-mock")

MOCK_TICKETS = {
    "AFISHA-8891": {
        "order_id": "AFISHA-8891",
        "event": "Stand-up Hall, 12 мая",
        "ticket_status": "not_activated",
        "payment_status": "success",
        "refund_allowed": True,
    },
    "TXN-77210": {
        "order_id": "AFISHA-8891",
        "event": "Stand-up Hall, 12 мая",
        "ticket_status": "not_activated",
        "payment_status": "success",
        "refund_allowed": True,
    },
}


@mcp.tool()
async def get_ticket_details(order_id: str) -> str:
    """Получить детали билета по ID заказа или транзакции (эмуляция Афиши)."""
    ticket = MOCK_TICKETS.get(order_id)
    if not ticket:
        return json.dumps({"error": f"Заказ {order_id} не найден"}, ensure_ascii=False)
    return json.dumps(ticket, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--transport=sse":
        mcp.run(transport="sse")
    else:
        mcp.run()
