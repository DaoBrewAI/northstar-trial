"""calc-ops 验收测试：节点 subtract。

只通过 `from calc import subtract` 这个对外接口验证，不依赖实现细节。
被测接口在每个测试函数内部导入：接口不存在时失败的是这条测试，不是收集阶段。
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSubtractOperator:
    """验收 1：subtract 的结果（值和类型）与 `-` 运算符一致。"""

    def test_int_operands_return_int(self):
        from calc import subtract

        result = subtract(5, 3)
        assert result == 2
        assert type(result) is int

    def test_negative_result(self):
        from calc import subtract

        assert subtract(3, 5) == -2

    def test_float_operands_return_float(self):
        from calc import subtract

        result = subtract(5.5, 0.5)
        assert result == 5.0
        assert type(result) is float

    def test_float_error_matches_operator_exactly(self):
        from calc import subtract

        # 不做四舍五入：必须和运算符的浮点结果逐位一致
        assert subtract(0.3, 0.1) == 0.3 - 0.1
        assert subtract(0.3, 0.1) == 0.19999999999999998

    def test_zero_and_identity(self):
        from calc import subtract

        assert subtract(0, 0) == 0
        assert subtract(7, 0) == 7
        assert subtract(7, 7) == 0

    def test_mixed_int_float_returns_float(self):
        from calc import subtract

        result = subtract(5, 2.0)
        assert result == 3.0
        assert type(result) is float

    def test_str_minus_int_raises_type_error(self):
        from calc import subtract

        with pytest.raises(TypeError):
            subtract("a", 1)

    def test_none_operand_raises_type_error(self):
        from calc import subtract

        with pytest.raises(TypeError):
            subtract(None, 1)

    def test_is_module_level_function_of_calc(self):
        import calc

        assert callable(getattr(calc, "subtract", None))

    def test_add_unchanged(self):
        from calc import add

        assert add(1, 2) == 3
        assert type(add(1, 2)) is int


class TestSubtractSuite:
    """验收 2：tests/test_calc.py 里有 test_subtract，`-k subtract` 至少选中并通过 1 个。"""

    def _run_pytest(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_test_calc_defines_test_subtract(self):
        proc = self._run_pytest("--collect-only", "-q", "tests/test_calc.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        pattern = re.compile(r"test_calc\.py::(?:.*::)?test_subtract(?:\[.*\])?$")
        collected = [line for line in proc.stdout.splitlines() if pattern.search(line.strip())]
        assert collected, (
            "tests/test_calc.py 里没有名为 test_subtract 的测试。collect-only 输出：\n"
            + proc.stdout
        )

    def test_k_subtract_selects_and_passes_at_least_one(self):
        proc = self._run_pytest("-q", "tests/test_calc.py", "-k", "subtract")
        output = proc.stdout + proc.stderr
        assert proc.returncode == 0, output
        match = re.search(r"(\d+) passed", output)
        assert match is not None, output
        assert int(match.group(1)) >= 1, output
        assert not re.search(r"\d+ failed", output), output
        assert not re.search(r"\d+ error", output), output
