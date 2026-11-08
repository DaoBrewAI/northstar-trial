"""trial-p1-2 验收测试：calc.floor_divide(a, b) 必须和 a // b 完全一致，
calc.modulo(a, b) 必须和 a % b 完全一致（值和类型、异常都一致）。

只通过 `from calc import floor_divide` / `from calc import modulo` 这个对外接口测；
被测接口在每个测试函数里面导入，接口还不存在时失败在测试上而不是收集阶段。
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


def _same(result, expected):
    """值相等且类型相同。"""
    return result == expected and type(result) is type(expected)


# ---------------------------------------------------------------------------
# fdiv-mod-impl：签名
# ---------------------------------------------------------------------------


def test_floor_divide_signature_two_positional_args():
    from calc import floor_divide

    assert callable(floor_divide)
    assert _same(floor_divide(7, 2), 3)
    # 恰好两个位置参数：少一个、多一个都和设计不符
    with pytest.raises(TypeError):
        floor_divide(7)
    with pytest.raises(TypeError):
        floor_divide(7, 2, 1)


def test_modulo_signature_two_positional_args():
    from calc import modulo

    assert callable(modulo)
    assert _same(modulo(7, 2), 1)
    with pytest.raises(TypeError):
        modulo(7)
    with pytest.raises(TypeError):
        modulo(7, 2, 1)


# ---------------------------------------------------------------------------
# fdiv-mod-impl：整数（验收 1）
# ---------------------------------------------------------------------------


def test_floor_divide_int():
    from calc import floor_divide

    r = floor_divide(7, 2)
    assert r == 3
    assert type(r) is int

    r = floor_divide(-7, 2)
    assert r == -4  # 向负无穷取整，int(a / b) 会给 -3
    assert type(r) is int

    r = floor_divide(7, -2)
    assert r == -4
    assert type(r) is int

    r = floor_divide(-7, -2)
    assert r == 3
    assert type(r) is int


def test_modulo_int():
    from calc import modulo

    r = modulo(7, 2)
    assert r == 1
    assert type(r) is int

    r = modulo(-7, 2)
    assert r == 1  # 符号跟除数走，math.fmod 会给 -1.0
    assert type(r) is int

    r = modulo(7, -2)
    assert r == -1
    assert type(r) is int

    r = modulo(-7, -2)
    assert r == -1
    assert type(r) is int


# ---------------------------------------------------------------------------
# fdiv-mod-impl：浮点（验收 2）
# ---------------------------------------------------------------------------


def test_floor_divide_float():
    from calc import floor_divide

    r = floor_divide(7.5, 2)
    assert r == 3.0
    assert type(r) is float

    r = floor_divide(-7.5, 2)
    assert r == -4.0
    assert type(r) is float

    r = floor_divide(7, 2.0)
    assert r == 3.0
    assert type(r) is float  # 一边是 float 就得 float，不能转回 int


def test_modulo_float():
    from calc import modulo

    r = modulo(7.5, 2)
    assert r == 1.5
    assert type(r) is float

    r = modulo(-7.5, 2)
    assert r == 0.5
    assert type(r) is float

    r = modulo(7.5, -2)
    assert r == -0.5
    assert type(r) is float


# ---------------------------------------------------------------------------
# fdiv-mod-impl：和运算符逐点对比（验收 3）
# ---------------------------------------------------------------------------

GRID_A = [-7, -1, 0, 1, 7, -7.5, 0.5, 7.5]
GRID_B = [-2, -1, 1, 2, 3, -2.5, 0.5, 2.0]
GRID_CASES = [(a, b) for a in GRID_A for b in GRID_B]
GRID_IDS = [f"{a},{b}" for a, b in GRID_CASES]


@pytest.mark.parametrize("a,b", GRID_CASES, ids=GRID_IDS)
def test_floor_divide_matches_operator_grid(a, b):
    from calc import floor_divide

    expected = a // b
    result = floor_divide(a, b)
    assert result == expected
    assert type(result) is type(expected)


@pytest.mark.parametrize("a,b", GRID_CASES, ids=GRID_IDS)
def test_modulo_matches_operator_grid(a, b):
    from calc import modulo

    expected = a % b
    result = modulo(a, b)
    assert result == expected
    assert type(result) is type(expected)


# ---------------------------------------------------------------------------
# fdiv-mod-impl：除数为 0（验收 4）
# ---------------------------------------------------------------------------


def test_floor_divide_zero_divisor():
    from calc import floor_divide

    with pytest.raises(ZeroDivisionError):
        floor_divide(7, 0)
    with pytest.raises(ZeroDivisionError):
        floor_divide(7.0, 0)
    with pytest.raises(ZeroDivisionError):
        floor_divide(7, 0.0)
    with pytest.raises(ZeroDivisionError):
        floor_divide(0, 0)
    with pytest.raises(ZeroDivisionError):
        floor_divide(-7.5, 0.0)


def test_modulo_zero_divisor():
    from calc import modulo

    with pytest.raises(ZeroDivisionError):
        modulo(7, 0)
    with pytest.raises(ZeroDivisionError):
        modulo(7.0, 0)
    with pytest.raises(ZeroDivisionError):
        modulo(7, 0.0)
    with pytest.raises(ZeroDivisionError):
        modulo(0, 0)
    with pytest.raises(ZeroDivisionError):
        modulo(-7.5, 0.0)


# ---------------------------------------------------------------------------
# fdiv-mod-impl：其他错误和非数值输入也跟运算符走（验收 5）
# ---------------------------------------------------------------------------


def test_floor_divide_other_errors_match_operator():
    from calc import floor_divide

    with pytest.raises(TypeError):
        floor_divide(2j, 1)
    with pytest.raises(TypeError):
        floor_divide(None, 2)
    with pytest.raises(TypeError):
        floor_divide(2, None)
    with pytest.raises(TypeError):
        floor_divide("a", 2)
    with pytest.raises(TypeError):
        floor_divide(2, "a")
    # bool 是 int 的子类，和 // 一样得 int
    assert _same(floor_divide(True, 2), True // 2)
    assert _same(floor_divide(7, True), 7 // True)


def test_modulo_other_errors_match_operator():
    from calc import modulo

    with pytest.raises(TypeError):
        modulo(2j, 1)
    with pytest.raises(TypeError):
        modulo(None, 2)
    with pytest.raises(TypeError):
        modulo(2, None)
    with pytest.raises(TypeError):
        modulo(2, "a")
    # 不做参数类型检查：字符串走 % 的格式化行为（设计决定 4）
    assert _same(modulo("a%s", 2), "a2")
    assert _same(modulo(True, 2), True % 2)
    assert _same(modulo(7, True), 7 % True)


# ---------------------------------------------------------------------------
# fdiv-mod-impl：已有函数不变（验收 6）
# ---------------------------------------------------------------------------


def test_add_and_power_unchanged():
    from calc import add, power

    assert _same(add(1, 2), 3)
    assert _same(power(2, 3), 8)
    assert _same(power(2, -1), 0.5)
    with pytest.raises(ZeroDivisionError):
        power(0, -1)


# ---------------------------------------------------------------------------
# fdiv-mod-test：tests/test_calc.py 里有 test_floor_divide / test_modulo，而且它们真的在测东西
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


def test_test_calc_defines_new_tests_and_keeps_old():
    names = _top_level_function_names(TEST_CALC)
    assert "test_floor_divide" in names, "tests/test_calc.py 里没有顶层函数 test_floor_divide"
    assert "test_modulo" in names, "tests/test_calc.py 里没有顶层函数 test_modulo"
    assert "test_add" in names, "tests/test_calc.py 里的 test_add 被删了"
    assert "test_power" in names, "tests/test_calc.py 里的 test_power 被删了"


def test_test_floor_divide_passes_against_real_floor_divide():
    code, out = _run_pytest(["tests/test_calc.py::test_floor_divide"])
    assert code == 0, out
    assert re.search(r"\b1 passed\b", out), out
    assert "failed" not in out, out


def test_test_modulo_passes_against_real_modulo():
    code, out = _run_pytest(["tests/test_calc.py::test_modulo"])
    assert code == 0, out
    assert re.search(r"\b1 passed\b", out), out
    assert "failed" not in out, out


def test_test_add_and_test_power_still_pass():
    code, out = _run_pytest(["tests/test_calc.py::test_add", "tests/test_calc.py::test_power"])
    assert code == 0, out
    assert re.search(r"\b2 passed\b", out), out


# 几个“坏掉的实现”。test_floor_divide / test_modulo 必须能抓住每一个，
# 否则它没覆盖验收要求的断言：
#   floor_divide:
#     trunc_toward_zero -> int(a / b)，floor_divide(-7, 2) 给 -3；浮点时类型也变 int
#     always_float      -> floor_divide(7, 2) 给 3.0，类型不是 int
#     swallow_zero_div  -> floor_divide(7, 0) 返回 None 而不是抛 ZeroDivisionError
#   modulo:
#     fmod              -> math.fmod(a, b)，modulo(-7, 2) 给 -1.0，符号和类型都不对
#     always_float      -> modulo(7, 2) 给 1.0，类型不是 int
#     swallow_zero_div  -> modulo(7, 0) 返回 None 而不是抛 ZeroDivisionError
MUTANT_PLUGIN = '''
import math
import os


def _fd_trunc_toward_zero(a, b):
    return int(a / b)


def _fd_always_float(a, b):
    return float(a // b)


def _fd_swallow_zero_div(a, b):
    try:
        return a // b
    except ZeroDivisionError:
        return None


def _mod_fmod(a, b):
    return math.fmod(a, b)


def _mod_always_float(a, b):
    return float(a % b)


def _mod_swallow_zero_div(a, b):
    try:
        return a % b
    except ZeroDivisionError:
        return None


MUTANTS = {
    "floor_divide": {
        "trunc_toward_zero": _fd_trunc_toward_zero,
        "always_float": _fd_always_float,
        "swallow_zero_div": _fd_swallow_zero_div,
    },
    "modulo": {
        "fmod": _mod_fmod,
        "always_float": _mod_always_float,
        "swallow_zero_div": _mod_swallow_zero_div,
    },
}


def pytest_runtest_setup(item):
    target = os.environ["CALC_MUTANT_TARGET"]
    mutant = MUTANTS[target][os.environ["CALC_MUTANT_NAME"]]
    import calc
    setattr(calc, target, mutant)
    mod = getattr(item, "module", None)
    if mod is not None and hasattr(mod, target):
        setattr(mod, target, mutant)
'''


def _run_with_mutant(tmp_path, target, mutant):
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    (plugin_dir / "calc_mutant_plugin.py").write_text(MUTANT_PLUGIN, encoding="utf-8")

    pythonpath = str(plugin_dir)
    if os.environ.get("PYTHONPATH"):
        pythonpath += os.pathsep + os.environ["PYTHONPATH"]

    test_id = f"tests/test_calc.py::test_{target}"
    code, out = _run_pytest(
        ["-p", "calc_mutant_plugin", test_id],
        extra_env={
            "PYTHONPATH": pythonpath,
            "CALC_MUTANT_TARGET": target,
            "CALC_MUTANT_NAME": mutant,
        },
    )
    assert code == 1, f"{target} mutant {mutant}: 期望 test_{target} 失败（退出码 1），实际 {code}\n{out}"
    assert re.search(r"\b\d+ failed\b", out), f"{target} mutant {mutant}: 输出里没有 'N failed'\n{out}"


@pytest.mark.parametrize("mutant", ["trunc_toward_zero", "always_float", "swallow_zero_div"])
def test_test_floor_divide_catches_broken_floor_divide(tmp_path, mutant):
    _run_with_mutant(tmp_path, "floor_divide", mutant)


@pytest.mark.parametrize("mutant", ["fmod", "always_float", "swallow_zero_div"])
def test_test_modulo_catches_broken_modulo(tmp_path, mutant):
    _run_with_mutant(tmp_path, "modulo", mutant)
