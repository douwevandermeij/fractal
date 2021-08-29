import pytest


@pytest.fixture
def mongo_specification_builder():
    from fractal.contrib.mongo.specifications import MongoSpecificationBuilder

    return MongoSpecificationBuilder
