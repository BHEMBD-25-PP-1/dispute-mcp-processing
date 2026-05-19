from app.mcp.base import BaseMCPClient


MOCK_SERVICE_DATA = {
    "taxi": {
        "TAXI-240518": {
            "route": "Аэропорт Внуково -> Тверская, 9",
            "ride_status": "not_completed",
            "payment_status": "captured",
            "refund_allowed": True,
        },
        "TXN-98765": {
            "route": "Аэропорт Внуково -> Тверская, 9",
            "ride_status": "not_completed",
            "payment_status": "captured",
            "refund_allowed": True,
        },
    },
    "afisha": {
        "AFISHA-8891": {
            "event": "Stand-up Hall, 12 мая",
            "ticket_status": "not_activated",
            "refund_allowed": True,
        },
        "TXN-77210": {
            "event": "Stand-up Hall, 12 мая",
            "ticket_status": "not_activated",
            "refund_allowed": True,
        },
    },
}


class MCPClient(BaseMCPClient):

    def call(self, service: str, payload: dict):
        if service not in MOCK_SERVICE_DATA:
            return {
                "service": service or "unknown",
                "status": "skipped",
                "data": None,
                "message": "Сервис не определен, MCP-запрос не выполнялся",
            }

        service_data = MOCK_SERVICE_DATA[service]
        lookup_ids = [payload.get("order_id"), payload.get("transaction_id")]
        record = next((service_data[item] for item in lookup_ids if item in service_data), None)
        if not record:
            return {
                "service": service,
                "status": "not_found",
                "data": None,
                "message": "Данные по идентификаторам не найдены",
            }

        return {
            "service": service,
            "status": "found",
            "data": record,
            "message": "Данные найдены",
        }