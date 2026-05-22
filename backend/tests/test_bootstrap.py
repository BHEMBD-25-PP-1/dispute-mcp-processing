from types import SimpleNamespace

import pytest

from app.services import bootstrap


class _Result:
    def __init__(self, user):
        self.user = user

    def scalar_one_or_none(self):
        return self.user


class _FakeSession:
    def __init__(self, user=None):
        self.user = user
        self.added = []
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def execute(self, statement):
        return _Result(self.user)

    def add(self, user):
        self.added.append(user)

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_seed_operator_user_skips_when_seed_credentials_are_missing(monkeypatch):
    monkeypatch.setattr(bootstrap.settings, "seed_operator_username", None)
    monkeypatch.setattr(bootstrap.settings, "seed_operator_password", None)
    monkeypatch.setattr(
        bootstrap,
        "AsyncSessionLocal",
        lambda: (_ for _ in ()).throw(AssertionError("session should not be opened")),
    )

    await bootstrap.seed_operator_user()


@pytest.mark.asyncio
async def test_seed_operator_user_creates_new_operator(monkeypatch):
    session = _FakeSession()
    monkeypatch.setattr(bootstrap.settings, "seed_operator_username", "operator")
    monkeypatch.setattr(bootstrap.settings, "seed_operator_password", "secret")
    monkeypatch.setattr(bootstrap, "hash_password", lambda password: f"hashed:{password}")
    monkeypatch.setattr(bootstrap, "AsyncSessionLocal", lambda: session)

    await bootstrap.seed_operator_user()

    assert session.committed is True
    assert session.added[0].username == "operator"
    assert session.added[0].password_hash == "hashed:secret"
    assert session.added[0].role == "OPERATOR"


@pytest.mark.asyncio
async def test_seed_operator_user_updates_existing_operator(monkeypatch):
    user = SimpleNamespace(username="operator", password_hash="old", role="ADMIN")
    session = _FakeSession(user=user)
    monkeypatch.setattr(bootstrap.settings, "seed_operator_username", "operator")
    monkeypatch.setattr(bootstrap.settings, "seed_operator_password", "secret")
    monkeypatch.setattr(bootstrap, "hash_password", lambda password: f"hashed:{password}")
    monkeypatch.setattr(bootstrap, "AsyncSessionLocal", lambda: session)

    await bootstrap.seed_operator_user()

    assert session.committed is True
    assert user.password_hash == "hashed:secret"
    assert user.role == "OPERATOR"
    assert session.added == []
