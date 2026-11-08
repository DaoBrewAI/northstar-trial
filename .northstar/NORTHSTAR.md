# NORTHSTAR — northstar-trial（orc 实跑用的玩具项目）

## 目标（what 和 why，不写 how）
- N1: calc 提供正确的四则运算，结果和 Python 运算符完全一致，方便验证 orc 的执行流程。
- N2: calc 的每个函数都有测试。

## 不可违反的约束
- N3: 只用 Python 标准库，不引入第三方依赖。

## 非目标（明确不做）
- X1: 不做命令行和界面。

## 完成的定义
- `python3 -m pytest -q` 全部通过。
