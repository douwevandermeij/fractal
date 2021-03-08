from dataclasses import asdict
from typing import Dict, Generator, Optional, Type

from django.db.models import Model, Q

from fractal.contrib.django.specifications import DjangoOrmSpecificationBuilder
from fractal.core.repositories import Entity, Repository
from fractal.core.specifications.generic.specification import Specification


class DjangoModelRepositoryMixin(Repository[Entity]):
    def __init__(self, django_model: Type[Model], domain_model: Entity):
        self.django_model = django_model
        self.domain_model = domain_model

    def add(self, entity: Entity) -> Entity:
        self.django_model.objects.create(**asdict(entity))
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if entities := self.django_model.objects.filter(pk=entity.id):
            entities.update(**asdict(entity))
            return self.django_model.objects.get(pk=entity.id)
        elif upsert:
            return self.add(entity)

    def __get_obj(self, specification: Specification):
        filter = DjangoOrmSpecificationBuilder.build(specification)
        if type(filter) is list:
            obj = self.django_model.objects.get(*filter)
        elif type(filter) is dict:
            obj = self.django_model.objects.get(**filter)
        elif type(filter) is Q:
            obj = self.django_model.objects.get(filter)
        else:
            raise self.django_model.DoesNotExist
        return obj

    def remove_one(self, specification: Specification):
        self.__get_obj(specification).delete()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        return self._obj_to_domain(self.__get_obj(specification).__dict__)

    def find(
        self, specification: Specification = None
    ) -> Generator[Entity, None, None]:
        filter = DjangoOrmSpecificationBuilder.build(specification)
        if type(filter) is list:
            queryset = self.django_model.objects.filter(*filter)
        elif type(filter) is dict:
            queryset = self.django_model.objects.filter(**filter)
        elif type(filter) is Q:
            queryset = self.django_model.objects.filter(filter)
        else:
            queryset = self.django_model.objects.all()

        for obj in queryset:
            yield self._obj_to_domain(obj.__dict__)

    def is_healthy(self) -> bool:
        return True

    def _obj_to_domain(self, obj: Dict) -> Entity:
        return self.domain_model.clean(**obj)
