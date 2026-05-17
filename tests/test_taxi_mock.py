import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import asyncio
import pytest
from mcp_servers.taxi_mock import get_ride_details


def test_get_ride_details_existing():
    """Проверяем успешное получение данных о поездке."""
    result_json = asyncio.run(get_ride_details("TXN-98765"))
    result = json.loads(result_json)
    assert result["order_id"] == "TXN-98765"
    assert result["status"] == "completed"
    assert result["amount"] == 1250.00


def test_get_ride_details_missing():
    """Проверяем ответ при отсутствии заказа."""
    result_json = asyncio.run(get_ride_details("UNKNOWN"))
    result = json.loads(result_json)
    assert "error" in result
    assert "не найден" in result["error"]