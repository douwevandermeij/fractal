import uuid
from typing import Callable, Dict, List, Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from fractal import Fractal
from fractal.contrib.fastapi.routers import Routes
from fractal.contrib.fastapi.routers.domain.models import AdapterInfo, Info
from fractal.contrib.fastapi.routers.tokens import get_payload, get_payload_roles
from fractal.contrib.tokens.fractal import DummyTokenServiceFractal
from fractal.contrib.tokens.models import TokenPayload, TokenPayloadRoles
from fractal.core.command_bus.commands import (
    AddEntityCommand,
    DeleteEntityCommand,
    UpdateEntityCommand,
)
from fractal.core.models import Model
from fractal.core.repositories.filter_repository_mixin import FilterRepositoryMixin
from fractal.core.specifications.account_id_specification import AccountIdSpecification
from fractal.core.specifications.id_specification import IdSpecification
from fractal.core.utils.application_context import ApplicationContext
from fractal.core.utils.settings import Settings


def inject_default_routes(
    context: ApplicationContext, settings: Optional[Settings] = None
):
    router = APIRouter()

    @router.get(Routes.ROOT)
    def read_root():
        return {
            "FastAPI": settings.APP_NAME
            if settings and hasattr(settings, "APP_NAME")
            else "Fractal Service",
        }

    @router.get(Routes.INFO, responses={200: {"model": Info}})
    def info(
        payload: TokenPayload = Depends(
            get_payload(DummyTokenServiceFractal(context, settings))
        ),
    ):
        adapters = list(context.adapters())
        data = [
            AdapterInfo(
                adapter=adapter.__class__.__name__,
                status=False,
            )
            for adapter in adapters
        ]
        for i in range(len(data)):
            try:
                data[i].status_ok = adapters[i].is_healthy()
            except Exception as e:
                context.logger.error(e)
                data[i].status_ok = False
        return data

    return router


def inject_default_rest_routes(
    fractal: Fractal,
    *,
    domain_entity_class: Type[Model],
    entities_route: str,
    entity_route: str,
    entity_repository_name: str,
    entity_contract: Type[BaseModel],
    search_fields: List[str] = None,
    search_pre_processor: Callable = lambda i: i.lower(),
    add_entity_command: Type[AddEntityCommand],
    update_entity_command: Type[UpdateEntityCommand],
    delete_entity_command: Type[DeleteEntityCommand],
    roles: Dict[str, List[str]] = None,
):
    if search_fields is None:
        search_fields = []
    if roles is None:
        roles = {}

    router = APIRouter()

    def entity_repository():
        return getattr(fractal.context, entity_repository_name)

    def to_entity(self, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        return super(create_entity_contract, self).to_entity(**kwargs)

    create_entity_contract = type(
        f"Create{entity_contract.__name__}",
        (entity_contract,),
        {
            "id": "string",
            "to_entity": to_entity,
        },
    )

    @router.post(
        entities_route,
        response_model=domain_entity_class,
        status_code=status.HTTP_201_CREATED,
    )
    def add_entity(
        entity: create_entity_contract,
        payload: TokenPayloadRoles = Depends(get_payload_roles(fractal, roles=roles.get("add", ["user"]))),
    ):
        try:
            uuid.UUID(entity.id)
        except ValueError:
            entity.id = None
        _entity = entity.to_entity(user_id=payload.sub, account_id=payload.account)
        fractal.context.command_bus.handle(
            add_entity_command(
                entity=_entity,
            ),
        )
        return _entity

    @router.get(
        entities_route,
        response_model=List[domain_entity_class],
        status_code=status.HTTP_200_OK,
    )
    def entities(
        q: Optional[str] = "", payload: TokenPayloadRoles = Depends(get_payload_roles(fractal, roles=roles.get("get", ["user"])))
    ):
        if issubclass(entity_repository().__class__, FilterRepositoryMixin):
            return list(
                entity_repository().find_filter(
                    q,
                    fields=search_fields,
                    specification=AccountIdSpecification(str(payload.account)),
                    pre_processor=search_pre_processor,
                )
            )
        else:
            return list(
                entity_repository().find(AccountIdSpecification(str(payload.account)))
            )

    @router.get(
        entity_route, response_model=domain_entity_class, status_code=status.HTTP_200_OK
    )
    def entity(entity_id: UUID, payload: TokenPayloadRoles = Depends(get_payload_roles(fractal, roles=roles.get("get", ["user"])))):
        return entity_repository().find_one(
            AccountIdSpecification(str(payload.account)).And(
                IdSpecification(str(entity_id))
            )
        )

    @router.put(
        entity_route, response_model=domain_entity_class, status_code=status.HTTP_200_OK
    )
    def update_entity(
        entity_id: UUID,
        entity: entity_contract,
        payload: TokenPayloadRoles = Depends(get_payload_roles(fractal, roles=roles.get("update", ["user"]))),
    ):
        _entity = entity.to_entity(id=entity_id, user_id=payload.sub, account_id=payload.account)
        fractal.context.command_bus.handle(
            update_entity_command(
                id=str(entity_id),
                entity=_entity,
            ),
        )
        return _entity

    @router.delete(entity_route, response_model=Dict, status_code=status.HTTP_200_OK)
    def delete_entity(
        entity_id: UUID, payload: TokenPayloadRoles = Depends(get_payload_roles(fractal, roles=roles.get("delete", ["user"])))
    ) -> Dict:
        fractal.context.command_bus.handle(
            delete_entity_command(
                specification=AccountIdSpecification(str(payload.account)).And(
                    IdSpecification(str(entity_id))
                ),
            ),
        )
        return {}

    return router
