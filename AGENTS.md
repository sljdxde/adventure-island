# AGENTS.md — 探险岛 / adventure-island 仓库工作规则

本文件约束在本仓库内工作的 AI Agent 与人类开发者。
面向用户的产出口径见 `ios/README.md`，内容唯一源与工具链见 `ios/docs/工作进展与待办-*.md`。

---

## 1. 分工边界：**HTML 优先，Swift 不新做**

**规则：只做 HTML 侧（`ios/preview/index.html` 及其渲染/数据链路）；Swift 原生端不做新功能。**

- ✅ 要做：`ios/preview/index.html` 的渲染、交互、样式、审计工具（`ios/tools/*.py` 里服务 HTML 的部分）、内容生成器产出（`gen_content.py` 的数据产物对两端可见，但**新增渲染只落在 HTML**）
- ❌ 不做：`ios/AdventureIsland/**` 新增视图/交互/动画；不为追平 HTML 而去改 Swift
- ⚠️ 例外（仅这两类，不要扩大）：
  1. **编译/测试破坏性修复**——若数据 schema 变更让 Swift 侧无法解码或 xcodebuild 直接编译失败，允许做最小改动使其恢复编译与测试通过；改完在本文件外的记录文档里点名说明
  2. **工具脚本**——`ios/tools/` 下的 Python 脚本照常维护

**已按本规则暂缓的历史项**（不要再接单去做 Swift 版）：
- `AstroAnimView.swift` 的天文 13 种动画之外，v0.11/v0.12 新增的 15 种学科动画
  （pydraw/tone/merge、walk/rainbow/countpop/fall/heartbeat/train、river/wall/mountain/panda/drift/windmill）
  仅在 HTML 端实现，Swift 端这些关保持静态大字卡。
- 历史交接文档里的「Swift 端补 15 种学科动画渲染」「放开 LetterStepView 的 isAstro 门槛」
  已作废，不要因为文档未删就当待办。

## 2. 内容唯一源与改动顺序

关卡/收集册数据的唯一源是 `ios/tools/gen_content.py`，**不要手改 JSON**。任何内容改动按此顺序复跑：

```bash
python3 ios/tools/gen_content.py      # 重新生成 Resources/*.json
python3 ios/tools/gen_preview_data.py # 把数据注入 preview/index.html 的 DATA 段
python3 ios/tools/validate.py         # 结构闸门：应 147 通过 / 0 失败
python3 ios/tools/audit_preview.py    # 语义闸门：图文一致/声母一致/题面去重（应 0 FAIL）
```

- `gen_preview_data.py` 只替换 `/* === DATA-BEGIN === */ ~ /* === DATA-END === */` 之间的段落；
  `CHINA_MAP` / `WORLD_MAP`（地图轮廓）住在独立的 MAPS 段，不会被覆盖——同样也不要把地图轮廓写进 DATA 段。
- 两个闸门（validate / audit）必须同时为绿才算完成；只跑一个不算。

## 3. 收尾口径

- 内容或 `ios/preview/index.html` 有变动 → 重打离线包（zip 命令见交接文档第五节），并核对与仓库逐字节一致。
- 改完更新 `ios/docs/工作进展与待办-*.md`，把「已完成」与「仍待办」写清，**不要留下虚假的已完成声明**。
