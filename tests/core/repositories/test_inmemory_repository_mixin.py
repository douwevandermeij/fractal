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


def test_find(inmemory_repository, an_object, another_object, yet_another_object):
    inmemory_repository.add(an_object)
    inmemory_repository.add(another_object)
    inmemory_repository.add(yet_another_object)

    assert len(list(inmemory_repository.find())) == 3


def test_find_order_by(
    inmemory_repository, an_object, another_object, yet_another_object
):
    inmemory_repository.add(an_object)
    inmemory_repository.add(another_object)
    inmemory_repository.add(yet_another_object)

    assert [i.name for i in inmemory_repository.find(order_by="name")] == [
        another_object.name,
        an_object.name,
        yet_another_object.name,
    ]
    assert [i.name for i in inmemory_repository.find(order_by="-name")] == [
        yet_another_object.name,
        an_object.name,
        another_object.name,
    ]


def test_find_offset_limit(
    inmemory_repository, an_object, another_object, yet_another_object
):
    inmemory_repository.add(an_object)
    inmemory_repository.add(another_object)
    inmemory_repository.add(yet_another_object)

    assert [i.name for i in inmemory_repository.find(limit=1)] == [an_object.name]
    assert [i.name for i in inmemory_repository.find(order_by="-name", limit=1)] == [
        yet_another_object.name
    ]
    assert [i.name for i in inmemory_repository.find(offset=2, limit=1)] == [
        yet_another_object.name
    ]
    assert [
        i.name for i in inmemory_repository.find(offset=2, order_by="-name", limit=1)
    ] == [another_object.name]


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
