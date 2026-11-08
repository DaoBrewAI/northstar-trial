import pytest

from calc import add, divide, multiply, subtract


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


def test_multiply():
    assert multiply(4, 3) == 12
    assert type(multiply(4, 3)) is int
    assert multiply(-2, 3) == -6
    assert multiply(2, 3.0) == 6.0
    assert type(multiply(2, 3.0)) is float
    assert multiply(0.1, 3) == 0.1 * 3
    assert multiply("ab", 3) == "ab" * 3
    with pytest.raises(TypeError):
        multiply("a", "b")


def test_divide():
    assert divide(7, 2) == 3.5
    assert divide(6, 3) == 2.0
    assert type(divide(6, 3)) is float
    assert divide(-7, 2) == -3.5
    assert divide(1, 3) == 1 / 3
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
    with pytest.raises(ZeroDivisionError):
        divide(1.0, 0.0)
    with pytest.raises(ZeroDivisionError):
        divide(0, 0)
    with pytest.raises(TypeError):
        divide("a", 1)
