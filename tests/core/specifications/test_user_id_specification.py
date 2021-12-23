from dataclasses import make_dataclass

from fractal.core.specifications.user_id_specification import UserIdSpecification


def test_user_id_specification():
    spec = UserIdSpecification("abc")
    DC = make_dataclass("DC", [("user_id", int)])
    assert spec.is_satisfied_by(DC(**dict(user_id="abc")))
