from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from fractal import Fractal
from fractal.contrib.fastapi.routers import Routes
from fractal.contrib.fastapi.routers.domain.models import AdapterInfo, Info
from fractal.contrib.fastapi.routers.tokens import get_payload, get_payload_roles
from fractal.contrib.tokens.fractal import DummyTokenServiceFractal
from fractal.contrib.tokens.models import TokenPayload, TokenPayloadRoles
from fractal.core.models import Model
from fractal.core.services import Service
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


class DefaultRestRouterService(Service, ABC):
    domain_entity_class: Type[Model]
    entities_route: str
    entity_route: str
    entity_contract: Type[BaseModel]
    create_entity_contract: Type[BaseModel]

    @abstractmethod
    def add_entity(
        self,
        contract: BaseModel,
        **kwargs,
    ):
        raise NotImplementedError

    @abstractmethod
    def find_entities(
        self,
        q: str = "",
        **kwargs,
    ):
        raise NotImplementedError

    @abstractmethod
    def get_entity(
        self,
        entity_id: UUID,
        **kwargs,
    ):
        raise NotImplementedError

    @abstractmethod
    def update_entity(
        self,
        entity_id: UUID,
        contract: BaseModel,
        **kwargs,
    ):
        raise NotImplementedError

    @abstractmethod
    def delete_entity(
        self,
        entity_id: UUID,
        **kwargs,
    ) -> Dict:
        raise NotImplementedError


class Contract(BaseModel, ABC):
    @abstractmethod
    def to_entity(self, **kwargs):
        raise NotImplementedError


class BasicRestRouterService(DefaultRestRouterService):
    def add_entity(
        self,
        contract: Contract,
        **kwargs,
    ):
        try:
            UUID(contract.id)
        except (ValueError, TypeError):
            contract.id = None
        _entity = contract.to_entity(
            user_id=kwargs.get("sub"), account_id=kwargs.get("account")
        )
        return self.ingress_service.add(_entity, str(kwargs.get("sub")))

    def find_entities(
        self,
        q: str = "",
        **kwargs,
    ):
        return self.ingress_service.find(str(kwargs.get("account")), q)

    def get_entity(
        self,
        entity_id: UUID,
        **kwargs,
    ):
        return self.ingress_service.get(str(entity_id), str(kwargs.get("account")))

    def update_entity(
        self,
        entity_id: UUID,
        contract: Contract,
        **kwargs,
    ):
        if _entity := self.get_entity(entity_id, **kwargs):
            _entity = _entity.update(contract.dict())
        else:
            _entity = contract.to_entity(
                id=entity_id,
                user_id=kwargs.get("sub"),
                account_id=kwargs.get("account"),
            )
        return self.ingress_service.update(
            str(entity_id), _entity, str(kwargs.get("sub"))
        )

    def delete_entity(
        self,
        entity_id: UUID,
        **kwargs,
    ) -> Dict:
        self.ingress_service.delete(
            str(entity_id), str(kwargs.get("sub")), str(kwargs.get("account"))
        )
        return {}


def inject_default_rest_routes(
    fractal: Fractal,
    *,
    router_service_class: Type[DefaultRestRouterService],
    roles: Dict[str, List[str]] = None,
):
    if roles is None:
        roles = {}

    router = APIRouter()

    @router.post(
        router_service_class().entities_route,
        response_model=router_service_class().domain_entity_class,
        status_code=status.HTTP_201_CREATED,
        name=f"Add {router_service_class().domain_entity_class.__name__}",
    )
    def add_entity(
        entity: router_service_class().create_entity_contract,
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(fractal, roles=roles.get("add", ["user"]))
        ),
    ):
        return router_service_class().add_entity(
            contract=entity,
            **payload.dict(),
        )

    @router.get(
        router_service_class().entities_route,
        response_model=List[router_service_class().domain_entity_class],
        status_code=status.HTTP_200_OK,
        name=f"Find {router_service_class().domain_entity_class.__name__} entities",
    )
    def find_entities(
        q: Optional[str] = "",
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(fractal, roles=roles.get("get", ["user"]))
        ),
    ):
        return router_service_class().find_entities(
            q=q,
            **payload.dict(),
        )

    @router.get(
        router_service_class().entity_route,
        response_model=router_service_class().domain_entity_class,
        status_code=status.HTTP_200_OK,
        name=f"Get {router_service_class().domain_entity_class.__name__} entity",
    )
    def get_entity(
        entity_id: UUID,
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(fractal, roles=roles.get("get", ["user"]))
        ),
    ):
        return router_service_class().get_entity(
            entity_id=entity_id,
            **payload.dict(),
        )

    @router.put(
        router_service_class().entity_route,
        response_model=router_service_class().domain_entity_class,
        status_code=status.HTTP_200_OK,
        name=f"Update {router_service_class().domain_entity_class.__name__}",
    )
    def update_entity(
        entity_id: UUID,
        entity: router_service_class().entity_contract,
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(fractal, roles=roles.get("update", ["user"]))
        ),
    ):
        return router_service_class().update_entity(
            entity_id=entity_id,
            contract=entity,
            **payload.dict(),
        )

    @router.delete(
        router_service_class().entity_route,
        response_model=Dict,
        status_code=status.HTTP_200_OK,
        name=f"Delete {router_service_class().domain_entity_class.__name__}",
    )
    def delete_entity(
        entity_id: UUID,
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(fractal, roles=roles.get("delete", ["user"]))
        ),
    ) -> Dict:
        return router_service_class().delete_entity(
            entity_id=entity_id,
            **payload.dict(),
        )

    return router
