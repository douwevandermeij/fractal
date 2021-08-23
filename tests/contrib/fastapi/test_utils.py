import pytest

data = [
    (pytest.lazy_fixture("a_base_model_object"), {"id": "1", "name": "default_name"}),
    ({1, 2, 3}, [1, 2, 3]),
]


@pytest.mark.parametrize("obj, expected", data)
def test_base_model_enhanced_encoder(obj, expected):
    from fractal.contrib.fastapi.utils.json_encoder import BaseModelEnhancedEncoder

    assert BaseModelEnhancedEncoder().default(obj) == expected
