# NORTHSTAR — northstar-trial（信任层验收用的测试项目）

## 目标（what 和 why，不写 how）
- N1: 验证 northstar 信任层在真实的 Claude Code、Codex 和 GitHub CI 上都生效：agent 改不了受保护文件、签不了名，每次会话都能读到这份原文。

## 不可违反的约束
- N2: 这个仓库只放验收用的测试内容，不放任何产品代码或敏感信息。

## 非目标（明确不做）
- X1: 不在这里开发任何真实功能。

## 完成的定义
- 阶段 1 验收的每一项都有命令和输出作为证据，记录在 building-in-public PR #10 里。
