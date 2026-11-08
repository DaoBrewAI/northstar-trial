"""calc-ops 验收测试：节点 divide。

只通过 `from calc import divide` 这个对外接口验证，不依赖实现细节。
被测接口在每个测试函数内部导入：接口不存在时失败的是这条测试，不是收集阶段。
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDivideOperator:
    """验收 1：divide 是真除法，结果（值和类型）与 `/` 运算符一致；除零抛 ZeroDivisionError。"""

    def test_true_division_not_floor(self):
        from calc import divide

        assert divide(7, 2) == 3.5

    def test_exact_int_division_returns_float(self):
        from calc import divide

        result = divide(6, 3)
        assert result == 2.0
        assert type(result) is float

    def test_negative_dividend(self):
        from calc import divide

        assert divide(-7, 2) == -3.5
        assert divide(7, -2) == -3.5

    def test_repeating_fraction_matches_operator_exactly(self):
        from calc import divide

        assert divide(1, 3) == 1 / 3
        assert divide(2, 3) == 2 / 3

    def test_zero_dividend(self):
        from calc import divide

        result = divide(0, 5)
        assert result == 0.0
        assert type(result) is float

    def test_float_operands(self):
        from calc import divide

        assert divide(1.5, 0.5) == 3.0
        assert divide(1.0, 4) == 0.25

    def test_int_by_zero_raises_zero_division_error(self):
        from calc import divide

        with pytest.raises(ZeroDivisionError):
            divide(1, 0)

    def test_float_by_zero_raises_zero_division_error(self):
        from calc import divide

        # 不返回 inf/nan，必须抛异常
        with pytest.raises(ZeroDivisionError):
            divide(1.0, 0.0)

    def test_zero_by_zero_raises_zero_division_error(self):
        from calc import divide

        with pytest.raises(ZeroDivisionError):
            divide(0, 0)

    def test_str_dividend_raises_type_error(self):
        from calc import divide

        with pytest.raises(TypeError):
            divide("a", 1)

    def test_none_operand_raises_type_error(self):
        from calc import divide

        with pytest.raises(TypeError):
            divide(None, 1)

    def test_is_module_level_function_of_calc(self):
        import calc

        assert callable(getattr(calc, "divide", None))

    def test_add_subtract_multiply_unchanged(self):
        from calc import add, multiply, subtract

        assert add(1, 2) == 3
        assert subtract(5, 3) == 2
        assert multiply(4, 3) == 12
        assert type(multiply(4, 3)) is int


class TestDivideSuite:
    """验收 2：tests/test_calc.py 里有 test_divide（覆盖除零），`-k divide` 至少选中并通过 1 个。"""

    def _run_pytest(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_test_calc_defines_test_divide(self):
        proc = self._run_pytest("--collect-only", "-q", "tests/test_calc.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        pattern = re.compile(r"test_calc\.py::(?:.*::)?test_divide(?:\[.*\])?$")
        collected = [line for line in proc.stdout.splitlines() if pattern.search(line.strip())]
        assert collected, (
            "tests/test_calc.py 里没有名为 test_divide 的测试。collect-only 输出：\n"
            + proc.stdout
        )

    def test_test_calc_covers_zero_division(self):
        # 验收标准要求 test_divide 覆盖“除数为 0 抛 ZeroDivisionError”。
        # 只看测试源码是否提到 ZeroDivisionError，不依赖它怎么写断言。
        source = (REPO_ROOT / "tests" / "test_calc.py").read_text(encoding="utf-8")
        assert "ZeroDivisionError" in source, "tests/test_calc.py 没有覆盖除零抛 ZeroDivisionError"

    def test_k_divide_selects_and_passes_at_least_one(self):
        proc = self._run_pytest("-q", "tests/test_calc.py", "-k", "divide")
        output = proc.stdout + proc.stderr
        assert proc.returncode == 0, output
        match = re.search(r"(\d+) passed", output)
        assert match is not None, output
        assert int(match.group(1)) >= 1, output
        assert not re.search(r"\d+ failed", output), output
        assert not re.search(r"\d+ error", output), output
