from app.services.parser import parse_dispute

def test_parse_dispute():
    text = "TXN-123 проблема с такси"
    result = parse_dispute(text)
    assert result["order_id"] == "TXN-123"