from dataclasses import make_dataclass

from fractal.core.specifications.account_id_specification import AccountIdSpecification


def test_account_id_specification():
    spec = AccountIdSpecification("abc")
    DC = make_dataclass("DC", [("account_id", int)])
    assert spec.is_satisfied_by(DC(**dict(account_id="abc")))
