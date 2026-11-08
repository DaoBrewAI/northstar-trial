from calc import add


def test_add():
    assert add(1, 2) == 3


def test_subtract():
    from calc import subtract
    assert subtract(3, 1) == 2
