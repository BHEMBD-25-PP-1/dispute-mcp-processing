from app.services.dispute_parser import _normalize_service, parse_dispute

def test_parse_dispute():
    text = "transaction_id=TXN-123, order_id=TAXI-240518 проблема с такси"
    result = parse_dispute(text)
    assert result["order_id"] == "TAXI-240518"
    assert result["transaction_id"] == "TXN-123"
    assert result["service_hint"] is None


def test_parse_dispute_recognizes_service_hints_and_user_ids():
    taxi = parse_dispute("клиент №USER-7, заказ №TAXI-240518, сервис: такси")
    afisha = parse_dispute("user_id=USER-8 order_id=AFISHA-8891 service=afisha")

    assert taxi["user_id"] == "USER-7"
    assert taxi["service_hint"] == "taxi"
    assert afisha["service_hint"] == "afisha"
    assert _normalize_service("unknown") is None
