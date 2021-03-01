from dataclasses import asdict
from typing import Generator, Optional, Type

from django.db.models import Model, Q

from fractal.contrib.django.specifications import DjangoOrmSpecificationBuilder
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


class DjangoModelRepositoryMixin(Repository[Entity]):
    def __init__(self, model: Type[Model]):
        self.model = model

    def add(self, entity: Entity) -> Entity:
        self.model.objects.create(**asdict(entity))
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if self.model.objects.filter(id=entity.id) or upsert:
            return self.add(entity)

    def __get_obj(self, specification: Specification):
        filter = DjangoOrmSpecificationBuilder.build(specification)
        if type(filter) is list:
            obj = self.model.objects.get(*filter)
        elif type(filter) is dict:
            obj = self.model.objects.get(**filter)
        elif type(filter) is Q:
            obj = self.model.objects.get(filter)
        else:
            raise self.model.DoesNotExist
        return obj

    def remove_one(self, specification: Specification):
        self.__get_obj(specification).delete()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        return self._obj_to_domain(self.__get_obj(specification).delete().__dict__)

    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        filter = DjangoOrmSpecificationBuilder.build(specification)
        if type(filter) is list:
            queryset = self.model.objects.filter(*filter)
        elif type(filter) is dict:
            queryset = self.model.objects.filter(**filter)
        elif type(filter) is Q:
            queryset = self.model.objects.filter(filter)
        else:
            queryset = self.model.objects.all()

        for obj in queryset:
            yield self._obj_to_domain(obj.__dict__)

    def is_healthy(self) -> bool:
        return True

    @staticmethod
    def _obj_to_domain(obj) -> Entity:
        raise NotImplementedError
