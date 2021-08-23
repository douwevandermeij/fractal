from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

import pytest

data = [
    (datetime(year=2021, month=8, day=19), "2021-08-19T00:00:00"),
    (time(hour=12, minute=30, second=59), "12:30:59"),
    ({1, 2, 3}, [1, 2, 3]),
    (UUID("12345678123456781234567812345678"), "12345678-1234-5678-1234-567812345678"),
    (Decimal(1.95), "1.95"),
    (pytest.lazy_fixture("an_object"), {"id": "1", "name": "default_name"}),
]


@pytest.mark.parametrize("obj, expected", data)
def test_enhanced_encoder(obj, expected):
    from fractal.core.utils.json_encoder import EnhancedEncoder

    assert EnhancedEncoder().default(obj) == expected


def test_enhanced_encoder_error():
    from fractal.core.utils.json_encoder import EnhancedEncoder

    with pytest.raises(TypeError):
        EnhancedEncoder().default(iter([1]))
