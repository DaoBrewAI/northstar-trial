import pytest

from calc import add, subtract


def test_add():
    assert add(1, 2) == 3


def test_subtract():
    assert subtract(5, 3) == 2
    assert type(subtract(5, 3)) is int
    assert subtract(3, 5) == -2
    assert subtract(5.5, 0.5) == 5.0
    assert type(subtract(5.5, 0.5)) is float
    assert subtract(0.3, 0.1) == 0.3 - 0.1
    with pytest.raises(TypeError):
        subtract("a", 1)
