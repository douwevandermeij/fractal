import pytest


@pytest.fixture
def django_specification_builder():
    from fractal.contrib.django.specifications import DjangoOrmSpecificationBuilder

    return DjangoOrmSpecificationBuilder
