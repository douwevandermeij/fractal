import pytest


def test_is_healthy(sqlalchemy_test_repository):
    assert sqlalchemy_test_repository.is_healthy()


def test_add(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")
    res = sqlalchemy_test_repository.add(obj)

    assert res == obj

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.name == "test"


def test_find_no_spec(sqlalchemy_test_repository, sqlalchemy_test_model):
    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = list(sqlalchemy_test_repository.find())

    assert len(res) == 2
    assert res == [obj1, obj2]


def test_find_with_spec(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = list(sqlalchemy_test_repository.find(EqualsSpecification("id", "test1")))

    assert len(res) == 1
    assert res[0] == obj1


def test_find_with_spec_no_result(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = list(sqlalchemy_test_repository.find(EqualsSpecification("id", "no_result")))

    assert len(res) == 0


def test_find_with_spec_multiple_results(
    sqlalchemy_test_repository, sqlalchemy_test_model
):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = list(sqlalchemy_test_repository.find(EqualsSpecification("name", "test")))

    assert len(res) == 2
    assert res == [obj1, obj2]


def test_find_with_and_spec(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    from fractal.core.specifications.generic.collections import AndSpecification

    res = list(
        sqlalchemy_test_repository.find(
            AndSpecification(
                [
                    EqualsSpecification("name", "test"),
                    EqualsSpecification("description", "test"),
                ]
            )
        )
    )

    assert len(res) == 2
    assert res == [obj1, obj2]


def test_find_with_or_spec(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.collections import OrSpecification
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = list(
        sqlalchemy_test_repository.find(
            OrSpecification(
                [EqualsSpecification("id", "test1"), EqualsSpecification("id", "test2")]
            )
        )
    )

    assert len(res) == 2
    assert res == [obj1, obj2]


def test_update(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")
    sqlalchemy_test_repository.add(obj)

    obj.name = "update"
    res = sqlalchemy_test_repository.update(obj)

    assert res == obj
    assert res.name == "update"

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.name == "update"


def test_update_add_item(
    sqlalchemy_test_repository, sqlalchemy_test_model, sqlalchemy_test_sub_model
):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")
    sqlalchemy_test_repository.add(obj)

    sub_obj = sqlalchemy_test_sub_model("item", item_id=obj.id)
    obj.items = [sub_obj]
    res = sqlalchemy_test_repository.update(obj)

    assert res == obj
    assert res.items == [sub_obj]

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.items == [sub_obj]


def test_update_delete_item(
    sqlalchemy_test_repository, sqlalchemy_test_model, sqlalchemy_test_sub_model
):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")
    sqlalchemy_test_repository.add(obj)
    sub_obj = sqlalchemy_test_sub_model("item", item_id=obj.id)
    obj.items = [sub_obj]
    sqlalchemy_test_repository.update(obj)

    obj.items = []
    res = sqlalchemy_test_repository.update(obj)

    assert res == obj
    assert res.items == []

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.items == []


def test_update_item(
    sqlalchemy_test_repository, sqlalchemy_test_model, sqlalchemy_test_sub_model
):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")
    sqlalchemy_test_repository.add(obj)
    sub_obj = sqlalchemy_test_sub_model("item", item_id=obj.id)
    obj.items = [sub_obj]
    sqlalchemy_test_repository.update(obj)

    obj.items[0].name = "update"
    sqlalchemy_test_repository.update(obj)

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.items[0].name == "update"


# TODO fix test for py39
# def test_update_item_error(
#     sqlalchemy_test_repository_error, sqlalchemy_test_model, sqlalchemy_test_sub_model
# ):
#     from fractal.contrib.sqlalchemy.repositories import UnknownListItemTypeException
#
#     obj = sqlalchemy_test_model("test")
#     sqlalchemy_test_repository_error.add(obj)
#     sub_obj = sqlalchemy_test_sub_model("item", item_id=obj.id)
#     obj.items = [sub_obj]
#
#     with pytest.raises(UnknownListItemTypeException):
#         sqlalchemy_test_repository_error.update(obj)


def test_update_upsert(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")

    res = sqlalchemy_test_repository.update(obj, upsert=True)

    assert res == obj

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res == obj
    assert res.name == "test"


def test_update_upsert_error(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj = sqlalchemy_test_model("test")

    res = sqlalchemy_test_repository.update(obj, upsert=False)

    assert res is None

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test"))

    assert res is None


def test_remove_one(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    sqlalchemy_test_repository.remove_one(EqualsSpecification("id", "test1"))

    res = list(sqlalchemy_test_repository.find())

    assert len(res) == 1
    assert res == [obj2]


def test_find_one(sqlalchemy_test_repository, sqlalchemy_test_model):
    from fractal.core.specifications.generic.operators import EqualsSpecification

    obj1 = sqlalchemy_test_model("test1")
    obj2 = sqlalchemy_test_model("test2")
    sqlalchemy_test_repository.add(obj1)
    sqlalchemy_test_repository.add(obj2)

    res = sqlalchemy_test_repository.find_one(EqualsSpecification("id", "test2"))

    assert res == obj2
