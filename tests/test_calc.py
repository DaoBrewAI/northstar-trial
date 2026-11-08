import pytest

from calc import add, floor_divide, modulo, power


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


def test_floor_divide():
    r = floor_divide(7, 2)
    assert r == 3
    assert type(r) is int

    r = floor_divide(-7, 2)
    assert r == -4
    assert type(r) is int

    r = floor_divide(7, -2)
    assert r == -4
    assert type(r) is int

    r = floor_divide(7.5, 2)
    assert r == 7.5 // 2
    assert type(r) is type(7.5 // 2)

    r = floor_divide(-7.5, 2)
    assert r == -7.5 // 2
    assert type(r) is type(-7.5 // 2)

    with pytest.raises(ZeroDivisionError):
        floor_divide(7, 0)
    with pytest.raises(ZeroDivisionError):
        floor_divide(7.5, 0.0)


def test_modulo():
    r = modulo(7, 2)
    assert r == 1
    assert type(r) is int

    r = modulo(-7, 2)
    assert r == 1
    assert type(r) is int

    r = modulo(7, -2)
    assert r == -1
    assert type(r) is int

    r = modulo(7.5, 2)
    assert r == 7.5 % 2
    assert type(r) is type(7.5 % 2)

    r = modulo(-7.5, 2)
    assert r == -7.5 % 2
    assert type(r) is type(-7.5 % 2)

    with pytest.raises(ZeroDivisionError):
        modulo(7, 0)
    with pytest.raises(ZeroDivisionError):
        modulo(7.5, 0.0)
