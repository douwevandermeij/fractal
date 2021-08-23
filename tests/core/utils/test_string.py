import pytest

strings = [
    ("", ""),
    ("A", "a"),
    ("AaAaAa", "aa_aa_aa"),
]


@pytest.mark.parametrize("camel, snake", strings + [("AAA", "aaa")])
def test_camel_to_snake(camel, snake):
    from fractal.core.utils.string import camel_to_snake

    assert camel_to_snake(camel) == snake


@pytest.mark.parametrize("camel, snake", strings + [("Aaa", "aaa")])
def test_snake_to_camel(camel, snake):
    from fractal.core.utils.string import snake_to_camel

    assert snake_to_camel(snake) == camel
