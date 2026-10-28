Type: task
Status: resolved
Blocked by: 10, 11
Parent: 05

# 16: 棋盘关与 Boss 关的朗读

**What to build:** 掷骰落到题目格弹出的题、Boss 战里内嵌的题，和普通关一样自动念、点即停、只念一次。

**Blocked by:** 10, 11

**Status:** ready-for-agent

- [ ] 棋盘关连走三格，每格的题都被念出来，且只念一次
- [ ] Boss 关连续答题每道都念，不会重念上一道
- [ ] 掉心、被击退等动画触发重绘时不会重新念
- [ ] 棋盘与战斗界面上的按钮、心条不被朗读层遮挡

## Answer

棋盘关与 Boss 关不是单独写的：`afterStepRender` 是三条路径的共同收口。
`voiceStep()` 修掉了 `currentStepObj()` 对 boss 关取错步的问题（boss 只推进 `L.boss.qi`），
`voiceKey()` 用 `b<qi>` / `q<pos>` / `s<step>` 区分位置，掉心重绘不会重念。
