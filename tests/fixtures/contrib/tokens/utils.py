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
def token(token_roles_service_fractal, user, account):
    return token_roles_service_fractal.context.token_service.generate(
        {
            "sub": user.id,
            "account": account.id,
        }
    )


@pytest.fixture
def admin_role_token(token_roles_service_fractal, user, account):
    return token_roles_service_fractal.context.token_service.generate(
        {
            "sub": user.id,
            "account": account.id,
            "roles": ["admin"],
        }
    )


@pytest.fixture
def token_service_application_context(
    fake_application_context_class,
    dummy_json_token_service_class,
    dummy_roles_service_class,
):
    application_context = fake_application_context_class()
    application_context.token_service = application_context.install_service(
        dummy_json_token_service_class, name="token_service"
    )()
    application_context.roles_service = application_context.install_service(
        dummy_roles_service_class, name="roles_service"
    )()
    return application_context
