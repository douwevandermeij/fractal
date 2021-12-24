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
def token(dummy_token_service_fractal, user, account):
    return dummy_token_service_fractal.context.token_service.generate(
        {
            "sub": user.id,
            "account": account.id,
        }
    )


@pytest.fixture
def admin_role_token(dummy_token_service_fractal, user, account):
    return dummy_token_service_fractal.context.token_service.generate(
        {
            "sub": user.id,
            "account": account.id,
            "roles": ["admin"],
        }
    )


@pytest.fixture
def token_service_application_context(fake_application_context_class, dummy_json_token_service_class):
    application_context = fake_application_context_class()
    application_context.install_service(dummy_json_token_service_class, name="token_service")
    return application_context
