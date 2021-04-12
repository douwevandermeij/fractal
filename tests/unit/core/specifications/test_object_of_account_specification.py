from dataclasses import make_dataclass

from fractal.core.specifications.object_of_account_specification import (
    ObjectOfAccountSpecification,
)


def test_object_of_account_specification():
    spec = ObjectOfAccountSpecification("abc", "def")
    DC = make_dataclass("DC", [("id", str), ("account_id", str)])
    assert spec.is_satisfied_by(DC(**dict(id="abc", account_id="def")))
