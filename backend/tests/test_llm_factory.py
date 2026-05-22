from types import SimpleNamespace

import pytest

from app.llm import factory


def test_get_llm_client_rejects_unknown_provider(monkeypatch):
    monkeypatch.setattr(factory, "gigachat_settings", SimpleNamespace(LLM_PROVIDER="none"))

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        factory.get_llm_client()
