"""trial-p1-1 验收测试：calc.power(a, b) 必须和 a ** b 完全一致。

只通过 `from calc import power` 这个对外接口测；被测接口在每个测试函数里面导入，
接口还不存在时失败在测试上而不是收集阶段。
"""
import ast
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TEST_CALC = REPO_ROOT / "tests" / "test_calc.py"


# ---------------------------------------------------------------------------
# power-impl：值和类型都和 ** 一致
# ---------------------------------------------------------------------------


def _same(result, expected):
    """值相等且类型相同。"""
    return result == expected and type(result) is type(expected)


def test_power_signature_two_positional_args():
    from calc import power

    assert callable(power)
    assert _same(power(2, 3), 8)
    # 恰好两个位置参数：少一个、多一个都和设计不符
    with pytest.raises(TypeError):
        power(2)
    with pytest.raises(TypeError):
        power(2, 3, 5)


def test_power_int_exponent():
    from calc import power

    r = power(2, 3)
    assert r == 8
    assert type(r) is int

    r = power(0, 0)
    assert r == 1
    assert type(r) is int

    r = power(-2, 3)
    assert r == -8
    assert type(r) is int

    r = power(5, 1)
    assert r == 5
    assert type(r) is int

    r = power(7, 0)
    assert r == 1
    assert type(r) is int


def test_power_negative_exponent():
    from calc import power

    r = power(2, -1)
    assert r == 0.5
    assert type(r) is float

    r = power(-2, -2)
    assert r == 0.25
    assert type(r) is float

    r = power(2.5, -2)
    assert r == 2.5 ** -2
    assert type(r) is float

    r = power(1, -5)
    assert r == 1.0
    assert type(r) is float  # int 的负指数得 float，不能保留 int


def test_power_float():
    from calc import power

    r = power(2.0, 3)
    assert r == 8.0
    assert type(r) is float

    r = power(4, 0.5)
    assert r == 2.0
    assert type(r) is float

    r = power(2.5, 2)
    assert r == 6.25
    assert type(r) is float

    r = power(2, 0.5)
    assert r == 2 ** 0.5
    assert type(r) is float

    r = power(1.5, 0)
    assert r == 1.0
    assert type(r) is float


GRID = [-3, -1, 0, 1, 2, 5, -2.5, 0.5, 3.0]
GRID_CASES = [
    (a, b)
    for a in GRID
    for b in GRID
    if not (a == 0 and b < 0)  # 0 或 0.0 的负次方会抛错，单独测
]


@pytest.mark.parametrize("a,b", GRID_CASES, ids=[f"{a}**{b}" for a, b in GRID_CASES])
def test_power_matches_operator_grid(a, b):
    from calc import power

    expected = a ** b
    result = power(a, b)
    assert result == expected
    assert type(result) is type(expected)


def test_power_bool_and_complex_inputs():
    from calc import power

    assert _same(power(True, 2), True ** 2)
    assert _same(power(2, True), 2 ** True)
    assert _same(power(False, 0), False ** 0)
    assert _same(power(2j, 2), (2j) ** 2)
    assert _same(power(2, 1j), 2 ** 1j)


def test_power_complex_result():
    from calc import power

    expected = (-8) ** (1 / 3)
    result = power(-8, 1 / 3)
    assert type(expected) is complex  # 前提：Python 自己就返回 complex
    assert result == expected
    assert type(result) is complex

    expected = (-3) ** 0.5
    result = power(-3, 0.5)
    assert result == expected
    assert type(result) is complex


def test_power_errors_match_operator():
    from calc import power

    with pytest.raises(ZeroDivisionError):
        power(0, -1)
    with pytest.raises(ZeroDivisionError):
        power(0.0, -1)
    with pytest.raises(ZeroDivisionError):
        power(0, -0.5)
    with pytest.raises(OverflowError):
        power(10.0, 400)
    with pytest.raises(TypeError):
        power("a", 2)
    with pytest.raises(TypeError):
        power(2, "a")
    with pytest.raises(TypeError):
        power(None, 2)


def test_add_unchanged():
    from calc import add

    assert add(1, 2) == 3
    assert type(add(1, 2)) is int


# ---------------------------------------------------------------------------
# power-test：tests/test_calc.py 里有 test_power，而且它真的在测东西
# ---------------------------------------------------------------------------


def _top_level_function_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _run_pytest(args, extra_env=None):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return proc.returncode, proc.stdout + proc.stderr


def test_test_calc_defines_test_power_and_keeps_test_add():
    names = _top_level_function_names(TEST_CALC)
    assert "test_power" in names, "tests/test_calc.py 里没有顶层函数 test_power"
    assert "test_add" in names, "tests/test_calc.py 里的 test_add 被删了"


def test_test_power_passes_against_real_power():
    code, out = _run_pytest(["tests/test_calc.py::test_power"])
    assert code == 0, out
    assert re.search(r"\b\d+ passed\b", out), out
    assert "failed" not in out, out


def test_test_add_still_passes():
    code, out = _run_pytest(["tests/test_calc.py::test_add"])
    assert code == 0, out
    assert re.search(r"\b1 passed\b", out), out


# 几个“坏掉的 power”。test_power 必须能抓住每一个，否则它没覆盖验收要求的断言：
#   always_float        -> power(2, 3) 返回 8.0，类型不是 int
#   negate_negative_exp -> power(2, -1) 返回 -0.5，值不对
#   round_float_base    -> 浮点底数时取整，值和类型都偏离 a ** b
#   swallow_zero_div    -> power(0, -1) 返回 None 而不是抛 ZeroDivisionError
MUTANT_PLUGIN = '''
import os


def _always_float(a, b):
    return float(a ** b)


def _negate_negative_exp(a, b):
    r = a ** b
    return -r if b < 0 else r


def _round_float_base(a, b):
    r = a ** b
    return round(r) if isinstance(a, float) else r


def _swallow_zero_div(a, b):
    try:
        return a ** b
    except ZeroDivisionError:
        return None


MUTANTS = {
    "always_float": _always_float,
    "negate_negative_exp": _negate_negative_exp,
    "round_float_base": _round_float_base,
    "swallow_zero_div": _swallow_zero_div,
}


def pytest_runtest_setup(item):
    mutant = MUTANTS[os.environ["POWER_MUTANT"]]
    import calc
    calc.power = mutant
    mod = getattr(item, "module", None)
    if mod is not None and hasattr(mod, "power"):
        mod.power = mutant
'''


@pytest.mark.parametrize(
    "mutant",
    ["always_float", "negate_negative_exp", "round_float_base", "swallow_zero_div"],
)
def test_test_power_catches_broken_power(tmp_path, mutant):
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    (plugin_dir / "power_mutant_plugin.py").write_text(MUTANT_PLUGIN, encoding="utf-8")

    pythonpath = str(plugin_dir)
    if os.environ.get("PYTHONPATH"):
        pythonpath += os.pathsep + os.environ["PYTHONPATH"]

    code, out = _run_pytest(
        ["-p", "power_mutant_plugin", "tests/test_calc.py::test_power"],
        extra_env={"PYTHONPATH": pythonpath, "POWER_MUTANT": mutant},
    )
    assert code == 1, f"mutant {mutant}: 期望 test_power 失败（退出码 1），实际 {code}\n{out}"
    assert re.search(r"\b\d+ failed\b", out), f"mutant {mutant}: 输出里没有 'N failed'\n{out}"
