import pytest


@pytest.fixture
def firestore_specification_builder():
    from fractal.contrib.gcp.firestore.specifications import (
        FirestoreSpecificationBuilder,
    )

    return FirestoreSpecificationBuilder
