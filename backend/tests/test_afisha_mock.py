import asyncio
import json

from mcp_servers.afisha_mock import get_ticket_details


def test_get_ticket_details_existing():
    result_json = asyncio.run(get_ticket_details("AFISHA-8891"))
    result = json.loads(result_json)

    assert result["order_id"] == "AFISHA-8891"
    assert result["ticket_status"] == "not_activated"
    assert result["refund_allowed"] is True


def test_get_ticket_details_missing():
    result_json = asyncio.run(get_ticket_details("UNKNOWN"))
    result = json.loads(result_json)

    assert "error" in result
    assert "не найден" in result["error"]
