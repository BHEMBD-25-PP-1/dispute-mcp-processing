import pytest

from app.api.schemas import UserRole
from app.services import users


@pytest.mark.asyncio
async def test_user_crud_helpers(db_session):
    created = await users.create_user(
        db_session,
        username="operator",
        password_hash="hash-1",
        role=UserRole.ADMIN,
    )

    by_username = await users.get_user_by_username(db_session, "operator")
    by_id = await users.get_user_by_id(db_session, created.id)
    all_users = await users.get_all_users(db_session)
    missing = await users.get_user_by_username(db_session, "missing")

    await users.update_password(db_session, created, "hash-2")

    assert by_username.id == created.id
    assert by_id.username == "operator"
    assert [user.username for user in all_users] == ["operator"]
    assert missing is None
    assert created.password_hash == "hash-2"
