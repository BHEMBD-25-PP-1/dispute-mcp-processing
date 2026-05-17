from app.services.nlu import build_prompt

def test_build_prompt_contains_text():

    text = "TXN-123 проблема такси"

    prompt = build_prompt(text)

    assert "TXN-123" in prompt
    assert "проблема такси" in prompt