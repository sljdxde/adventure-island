# HTML 模拟器先行，Swift 原生端暂缓

2026-09-30 起的迭代方式：新功能与修复**只实现并验收在 HTML 浏览器模拟器**（`ios/preview/index.html`，由内容生成器注入数据），Swift 原生端**暂时冻结、不再追平**。这是产品负责人在孩子试玩后明确的要求（"swift 不用管，这个暂时不实现"）。

理由：孩子的实际使用载体就是模拟器导出的 HTML 离线包，Swift 端追平是双倍工作量且当前无人使用；先把玩法在模拟器上打磨到位，Swift 端留待后续一次性重建。

## Consequences

- 期间所有工单、规格的实施口径默认「仅模拟器端」；涉及 Swift 的验收项一律挂起而非完成。
- `ios/AdventureIsland/` 下的 Swift 代码（含 BoardView/BossView/CeremonyView 等 v0.8 实现）会逐渐落后于模拟器行为，追平前不要把它当作现状的参照。
- 解除冻结时，应以 `docs/specs/` 最新规格 + 模拟器实际行为为准重新对齐，而不是基于旧 Swift 代码增量修改。
