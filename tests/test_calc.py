import pytest

from calc import add, power


def test_add():
    assert add(1, 2) == 3


def test_power():
    r = power(2, 3)
    assert r == 8
    assert type(r) is int

    r = power(2, -1)
    assert r == 0.5
    assert type(r) is float

    r = power(2.5, 2)
    assert r == 2.5 ** 2
    assert type(r) is type(2.5 ** 2)

    with pytest.raises(ZeroDivisionError):
        power(0, -1)
