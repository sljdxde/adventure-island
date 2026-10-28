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
python3 ios/tools/check_registry.py   # 注册表闸门：题型/动画/图标清单与渲染器是否对得上（<1 秒）
python3 ios/tools/validate.py         # 结构闸门：应 148 通过 / 1 已知警告 / 0 失败
python3 ios/tools/audit_preview.py    # 语义闸门：图文一致/声母一致/题面去重（应 0 项不一致）
```

- `gen_preview_data.py` 只替换 `/* === DATA-BEGIN === */` 到 `/* === DATA-END === */` 之间的段落；
  `CHINA_MAP` / `WORLD_MAP`（地图轮廓）住在独立的 MAPS 段，不会被覆盖——同样也不要把地图轮廓写进 DATA 段。
- **三个闸门必须同时为绿**：check_registry（清单一致）/ validate（结构）/ audit（语义）。
  改了渲染或动画再加 `preview_sweep.py`（六科全量约 20 分钟，`--steps=2` 快查）。
- `validate.py` 的 1 条警告是 `PinyinSpeech.swift` 圆括号启发式（字符串里的半角括号），属基线，不是新增问题。

## 3. 收尾口径

- 内容或 `ios/preview/index.html` 有变动 → 重打离线包（**包名带版本号**，脚本会先删同名旧包并自检）：

  ```bash
  python3 ios/tools/pack_release.py 1.0.2     # 产物：探险岛-HTML离线包-v1.0.2.zip
  ```

  - 包名与解压目录都带版本号：iPad「文件」解压出来的文件夹就是 `探险岛-HTML离线包-v1.0.2/`，
    多版本可共存、好区分。**包内不要再套一层版本目录**，否则会「v1.0.2 里面还有 v1.0.2」。
  - zip 内结构固定为扁平的 `design/` + `ios/preview/index.html`（两者同级；
    `index.html` 里是 `../../design/...` 的相对引用，层级不能乱；清单以脚本为准，**不要自行增删裁剪**——2026-10-28 曾因裁剪清单出过错包）。
  - 脚本会自检 zip 内 `index.html` 与本地 md5 一致、design 文件数一致；任一项不过退出码 1。
  - 旧命名的 `探险岛-HTML离线包.zip` 已被版本化命名取代，发现它还在就删掉，别让两个包混用。

- 改完更新 `ios/docs/工作进展与待办-*.md`，把「已完成」与「仍待办」写清，**不要留下虚假的已完成声明**。

## 4. UI 表达纪律

- **Avoid unnecessary secondary labels and descriptions. Let the layout do the explaining.**
  （避免多余的二级标签和文字说明，让布局本身完成解释——能用位置/分组/视觉层级表达的，就不要再加一行小字标注；每个界面元素的存在都要有信息职责，装饰性重复文案一律删。）

---
