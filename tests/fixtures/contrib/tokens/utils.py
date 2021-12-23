import uuid
from dataclasses import dataclass

import pytest


@pytest.fixture
def account():
    @dataclass
    class Account:
        id: str

    return Account(str(uuid.uuid4()))


@pytest.fixture
def user(account):
    @dataclass
    class User:
        id: str
        account_id: str

    return User(str(uuid.uuid4()), account.id)


@pytest.fixture
def token(token_service_fractal, user, account):
    return token_service_fractal.context.token_service.generate(
        {
            "sub": user.id,
            "account": account.id,
        }
    )
