def test_is_healthy(inmemory_repository):
    assert inmemory_repository.is_healthy()


def test_add(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    assert len(inmemory_repository.entities) == 1
    assert list(inmemory_repository.entities.values())[0] == an_object


def test_update(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    assert list(inmemory_repository.entities.values())[0].name != "update"

    an_object.name = "update"
    inmemory_repository.update(an_object)

    assert len(inmemory_repository.entities) == 1
    assert list(inmemory_repository.entities.values())[0].name == "update"


def test_update_upsert(inmemory_repository, an_object):
    inmemory_repository.update(an_object, upsert=True)

    assert len(inmemory_repository.entities) == 1
    assert list(inmemory_repository.entities.values())[0] == an_object


def test_update_upsert_ignore(inmemory_repository, an_object):
    inmemory_repository.update(an_object)

    assert len(inmemory_repository.entities) == 0


def test_remove_one(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    from fractal_specifications.generic.operators import EqualsSpecification

    inmemory_repository.remove_one(EqualsSpecification("id", an_object.id))

    assert len(inmemory_repository.entities) == 0


def test_find_one(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    from fractal_specifications.generic.operators import EqualsSpecification

    assert (
        inmemory_repository.find_one(EqualsSpecification("id", an_object.id))
        == an_object
    )


def test_find(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    assert len(list(inmemory_repository.find())) == 1


def test_find_with_specification(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    from fractal_specifications.generic.operators import EqualsSpecification

    assert (
        len(list(inmemory_repository.find(EqualsSpecification("id", an_object.id))))
        == 1
    )


def test_find_with_specification_empty(inmemory_repository, an_object):
    inmemory_repository.add(an_object)

    from fractal_specifications.generic.operators import EqualsSpecification

    assert len(list(inmemory_repository.find(EqualsSpecification("id", 2)))) == 0
