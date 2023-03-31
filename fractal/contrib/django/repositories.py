from dataclasses import asdict
from typing import Dict, Generator, Optional, Type

from django.db.models import ForeignKey, Model, Q
from fractal_specifications.contrib.django.specifications import (
    DjangoOrmSpecificationBuilder,
)
from fractal_specifications.generic.specification import Specification

from fractal.core.repositories import Entity, Repository


class DjangoModelRepositoryMixin(Repository[Entity]):
    def __init__(self, django_model: Type[Model], domain_model: Entity):
        self.django_model = django_model
        self.domain_model = domain_model

    def add(self, entity: Entity) -> Entity:
        direct_data, related_data = self.__get_direct_related_data(entity)
        obj = self.django_model.objects.create(**direct_data)
        entity.id = obj.id
        return entity

    def update(self, entity: Entity, upsert=False) -> Entity:
        if entities := self.django_model.objects.filter(pk=entity.id):
            direct_data, related_data = self.__get_direct_related_data(entity)
            entities.update(**direct_data)
            return self.django_model.objects.get(pk=entity.id)
        elif upsert:
            return self.add(entity)

    def __get_direct_related_data(self, entity: Entity):
        direct_data = {}
        related_data = {}

        def field_name(field):
            if type(field) is ForeignKey:
                return field.name + "_id"
            return field.name

        direct_fields = [field_name(f) for f in self.django_model._meta.fields]
        for k, v in asdict(entity).items():
            if type(v) == list:
                related_data[k] = v
            else:
                if k in direct_fields:
                    direct_data[k] = v
        return direct_data, related_data

    def __get_obj(self, specification: Specification):
        _filter = DjangoOrmSpecificationBuilder.build(specification)
        if type(_filter) is list:
            obj = self.django_model.objects.get(*_filter)
        elif type(_filter) is dict:
            obj = self.django_model.objects.get(**_filter)
        elif type(_filter) is Q:
            obj = self.django_model.objects.get(_filter)
        else:
            raise self.django_model.DoesNotExist
        return obj

    def remove_one(self, specification: Specification):
        self.__get_obj(specification).delete()

    def find_one(self, specification: Specification) -> Optional[Entity]:
        return self._obj_to_domain(self.__get_obj(specification).__dict__)

    def find(
        self,
        specification: Specification = None,
        *,
        offset: int = 0,
        limit: int = 0,
        order_by: str = "",
    ) -> Generator[Entity, None, None]:
        if _filter := DjangoOrmSpecificationBuilder.build(specification):
            queryset = self.django_model.objects.filter(_filter)
        else:
            queryset = self.django_model.objects.all()

        order_by = order_by or self.order_by
        if order_by:
            queryset = queryset.order_by(order_by)

        if limit:
            queryset.offset(offset).limit(limit)

        for obj in queryset:
            yield self._obj_to_domain(obj.__dict__)

    def is_healthy(self) -> bool:
        return True

    def _obj_to_domain(self, obj: Dict) -> Entity:
        return self.domain_model.clean(**obj)
