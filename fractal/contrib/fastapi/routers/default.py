from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fractal_repositories.core.entity import Model
from fractal_specifications.generic.specification import Specification
from fractal_tokens.services.generic import TokenPayload
from pydantic import BaseModel

from fractal import Fractal
from fractal.contrib.fastapi.routers import Routes
from fractal.contrib.fastapi.routers.domain.models import AdapterInfo, Info
from fractal.contrib.fastapi.routers.tokens import (
    TokenPayloadRoles,
    get_payload,
    get_payload_roles,
)
from fractal.core.services import Service


def inject_default_routes(fractal: Fractal):
    router = APIRouter()

    @router.get(Routes.ROOT)
    def read_root():
        return {
            "FastAPI": fractal.settings.APP_NAME
            if fractal.settings and hasattr(fractal.settings, "APP_NAME")
            else "Fractal Service",
        }

    @router.get(Routes.INFO, responses={200: {"model": Info}})
    def info(
        payload: TokenPayload = Depends(get_payload(fractal)),
    ):
        adapters = list(fractal.context.adapters())
        data = [
            AdapterInfo(
                adapter=adapter.__class__.__name__,
                status_ok=False,
            )
            for adapter in adapters
        ]
        for i in range(len(data)):
            try:
                data[i].status_ok = adapters[i].is_healthy()
            except Exception as e:
                fractal.context.logger.error(e)
                data[i].status_ok = False
        return data

    return router


class DefaultRestRouterService(Service, ABC):
    domain_entity_class: Type[Model]
    entities_route: str
    entity_route: str
    entities_endpoint: str
    entity_endpoint: str
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
    def find_entities(
        self,
        *,
        specification: Specification = None,
        **kwargs,
    ):
        return self.ingress_service.find(
            account_id=str(kwargs.get("account")),
            specification=specification,
            **kwargs,
        )

    def get_entity(
        self,
        entity_id: UUID,
        *,
        specification: Specification = None,
        **kwargs,
    ):
        return self.ingress_service.get(
            entity_id=str(entity_id),
            account_id=str(kwargs.get("account")),
            specification=specification,
        )

    def add_entity(
        self,
        contract: Contract,
        *,
        specification: Specification = None,
        **kwargs,
    ):
        try:
            UUID(contract.id)
        except (ValueError, TypeError):
            contract.id = None
        _entity = contract.to_entity(
            user_id=kwargs.get("sub"), account_id=kwargs.get("account")
        )
        return self.ingress_service.add(
            entity=_entity,
            user_id=str(kwargs.get("sub")),
            specification=specification,
        )

    def update_entity(
        self,
        entity_id: UUID,
        contract: Contract,
        *,
        specification: Specification = None,
        **kwargs,
    ):
        if _entity := self.get_entity(entity_id, specification=specification, **kwargs):
            _entity = _entity.update(
                {k: v for k, v in contract.dict().items() if v is not None}
            )
        else:
            _entity = contract.to_entity(
                id=entity_id,
                user_id=kwargs.get("sub"),
                account_id=kwargs.get("account"),
            )
        return self.ingress_service.update(
            entity_id=str(entity_id),
            entity=_entity,
            user_id=str(kwargs.get("sub")),
            specification=specification,
        )

    def delete_entity(
        self,
        entity_id: UUID,
        *,
        specification: Specification = None,
        **kwargs,
    ) -> Dict:
        self.ingress_service.delete(
            entity_id=str(entity_id),
            user_id=str(kwargs.get("sub")),
            account_id=str(kwargs.get("account")),
            specification=specification,
        )
        return {}


def inject_default_rest_routes(
    fractal: Fractal,
    *,
    router_service_class: Type[DefaultRestRouterService],
):
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
            get_payload_roles(
                fractal,
                endpoint=router_service_class().entities_endpoint,
                method="post",
            )
        ),
    ):
        return router_service_class().add_entity(
            contract=entity,
            specification=payload.specification,
            **payload.asdict(),
        )

    @router.get(
        router_service_class().entities_route,
        response_model=List[router_service_class().domain_entity_class],
        status_code=status.HTTP_200_OK,
        name=f"Find {router_service_class().domain_entity_class.__name__} entities",
    )
    def find_entities(
        q: Optional[str] = "",
        offset: int = 0,
        limit: int = 0,
        sort: str = "",
        payload: TokenPayloadRoles = Depends(
            get_payload_roles(
                fractal,
                endpoint=router_service_class().entities_endpoint,
                method="get",
            )
        ),
    ):
        return router_service_class().find_entities(
            q=q,
            offset=offset,
            limit=limit,
            order_by=sort,
            specification=payload.specification,
            **payload.asdict(),
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
            get_payload_roles(
                fractal,
                endpoint=router_service_class().entity_endpoint,
                method="get",
            )
        ),
    ):
        return router_service_class().get_entity(
            entity_id=entity_id,
            specification=payload.specification,
            **payload.asdict(),
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
            get_payload_roles(
                fractal,
                endpoint=router_service_class().entity_endpoint,
                method="put",
            )
        ),
    ):
        return router_service_class().update_entity(
            entity_id=entity_id,
            contract=entity,
            specification=payload.specification,
            **payload.asdict(),
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
            get_payload_roles(
                fractal,
                endpoint=router_service_class().entity_endpoint,
                method="delete",
            )
        ),
    ) -> Dict:
        return router_service_class().delete_entity(
            entity_id=entity_id,
            specification=payload.specification,
            **payload.asdict(),
        )

    return router
