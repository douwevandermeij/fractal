from dataclasses import make_dataclass

from fractal.core.specifications.id_specification import IdSpecification


def test_id_specification():
    spec = IdSpecification(1)
    DC = make_dataclass("DC", [("id", int)])
    assert spec.is_satisfied_by(DC(**dict(id=1)))
