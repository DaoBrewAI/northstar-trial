"""calc-ops 验收测试：节点 multiply。

只通过 `from calc import multiply` 这个对外接口验证，不依赖实现细节。
被测接口在每个测试函数内部导入：接口不存在时失败的是这条测试，不是收集阶段。
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestMultiplyOperator:
    """验收 1：multiply 的结果（值和类型）与 `*` 运算符一致。"""

    def test_int_operands_return_int(self):
        from calc import multiply

        result = multiply(4, 3)
        assert result == 12
        assert type(result) is int

    def test_negative_operand(self):
        from calc import multiply

        assert multiply(-2, 3) == -6
        assert multiply(-2, -3) == 6

    def test_mixed_int_float_returns_float(self):
        from calc import multiply

        result = multiply(2, 3.0)
        assert result == 6.0
        assert type(result) is float

    def test_float_error_matches_operator_exactly(self):
        from calc import multiply

        # 不做四舍五入：必须和运算符的浮点结果逐位一致
        assert multiply(0.1, 3) == 0.1 * 3
        assert multiply(0.1, 3) == 0.30000000000000004

    def test_zero_and_identity(self):
        from calc import multiply

        assert multiply(0, 5) == 0
        assert multiply(5, 0) == 0
        assert multiply(1, 5) == 5

    def test_str_repeat_like_operator(self):
        from calc import multiply

        # 设计里的示例写的是 "abab"，但 Python 的 "ab" * 3 是 "ababab"。
        # 设计的决定 1 / N1 要求“结果和 Python 运算符完全一致”，以运算符为准。
        assert multiply("ab", 3) == "ab" * 3
        assert multiply("ab", 3) == "ababab"
        assert multiply(3, "ab") == "ababab"
        assert multiply("ab", 2) == "abab"

    def test_list_repeat_like_operator(self):
        from calc import multiply

        assert multiply([1], 2) == [1, 1]

    def test_str_times_str_raises_type_error(self):
        from calc import multiply

        with pytest.raises(TypeError):
            multiply("a", "b")

    def test_none_operand_raises_type_error(self):
        from calc import multiply

        with pytest.raises(TypeError):
            multiply(None, 2)

    def test_is_module_level_function_of_calc(self):
        import calc

        assert callable(getattr(calc, "multiply", None))

    def test_add_and_subtract_unchanged(self):
        from calc import add, subtract

        assert add(1, 2) == 3
        assert subtract(5, 3) == 2
        assert type(subtract(5, 3)) is int


class TestMultiplySuite:
    """验收 2：tests/test_calc.py 里有 test_multiply，`-k multiply` 至少选中并通过 1 个。"""

    def _run_pytest(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )

    def test_test_calc_defines_test_multiply(self):
        proc = self._run_pytest("--collect-only", "-q", "tests/test_calc.py")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        pattern = re.compile(r"test_calc\.py::(?:.*::)?test_multiply(?:\[.*\])?$")
        collected = [line for line in proc.stdout.splitlines() if pattern.search(line.strip())]
        assert collected, (
            "tests/test_calc.py 里没有名为 test_multiply 的测试。collect-only 输出：\n"
            + proc.stdout
        )

    def test_k_multiply_selects_and_passes_at_least_one(self):
        proc = self._run_pytest("-q", "tests/test_calc.py", "-k", "multiply")
        output = proc.stdout + proc.stderr
        assert proc.returncode == 0, output
        match = re.search(r"(\d+) passed", output)
        assert match is not None, output
        assert int(match.group(1)) >= 1, output
        assert not re.search(r"\d+ failed", output), output
        assert not re.search(r"\d+ error", output), output
