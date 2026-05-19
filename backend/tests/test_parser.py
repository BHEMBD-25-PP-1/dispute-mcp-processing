from app.services.dispute_parser import parse_dispute

def test_parse_dispute():
    text = "transaction_id=TXN-123, order_id=TAXI-240518 проблема с такси"
    result = parse_dispute(text)
    assert result["order_id"] == "TAXI-240518"
    assert result["transaction_id"] == "TXN-123"
    assert result["service_hint"] is None