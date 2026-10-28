Type: research
Status: resolved
Blocked by: —

# 30+ 种题型各自的朗读文本在哪

## Question

`index.html` 的 `renderStep(sub, st)` 分派到 30 多种题型渲染函数，数据在 `ios/AdventureIsland/Resources/*.json`
（唯一源是 `ios/tools/gen_content.py`）。自动朗读要给每一类题都找到「念什么」，得先有一张清单。

逐 kind 盘清楚：

- `renderStep` 里对应的渲染函数名、行号
- 题面字段是哪个（`question` / `prompt` / `display` / 自己的拼装逻辑）
- 选项数组叫什么（`options` / `countOptions` / `compareOptions` / 其它），选项里有没有文字（`text` / `say` / `label`）
- 现在界面上有没有 🔊 按钮（`speak(...)` 调用点）
- 按已锁定口径（见 `.scratch/v0.13-narration/map.md` 的 Notes）**建议每类题念什么**：
  念题面 + 哪些选项、还是只念序号、还是只念卡片文字

另外给两份清单：**必须新增字段才能念的 kind**（题面/选项都取不到文字），
**念法有歧义、需要人拍板的 kind**（例如数独、拼地图、写字、看影子这类没有「选项文字」概念的）。

产出：`.scratch/v0.13-narration/research/02-kind-narration-inventory.md`，一张表 + 两份清单。
只读仓库，不要改任何源码。

## Answer

产出：[02-kind-narration-inventory.md](../research/02-kind-narration-inventory.md)（31 行总表 + 两份清单 + 实现入口）。

要点：

- `renderStep` 有 30 个 case + 1 个兜底，**数据里只用到 29 种**（`cmp` 0 步）。600 关 / 2102 步，其中 120 关走棋盘、6 关 boss。
- 现有 🔊 只有 4 处（teach 2723 / letter 3332 / listen 3361 / write 3922），**念的都是卡片内容，不是题面**——不能复用，只能借 `speak()`。
- 数据形态不统一（实现会踩）：`compare` 的文字字段叫 `label`；`countOptions` / `arithOptions` / `nums` / `muldiv.options` / `cards.cards` 是裸数字；
  `clock.options`（「3:00」）、`sequence.seq`、`blend.parts` 是字符串；`balance` / `spotlight` / `cards` / `money` / `mappuzzle` 根本没有 options 数组。
- 必须新增字段才能念：`sudoku`（symbols 只有图标 id）、`pattern`（seq 全图标，题面也不复述序列）、`spotlight`（targetIcon 只有 id）。
- 纯图标选项 715 个（listen 442 / quiz 195 / tapall 45 / pattern 33），分科数与票 07 的数字逐项吻合。
- 16 条「念法有歧义」的题型已逐条给默认（见票 09）。

**顺带发现一个既有 bug（与朗读无关）**：`mappuzzle` 渲染器读 `st.pieces`，而 `gen_content.py` 的 `mappuzzle_step(3058)` 只产 `regions`
→ 现在 7 个拼地图步骤一张拼块都不渲染。已写进地图的 Out of scope，另开修复。

实现入口（写进票 05）：挂在 `renderLevel` 收尾的 `afterStepRender()` 一处即可覆盖普通/棋盘/boss 三条路径；
三个坑：`currentStepObj()`(3891) 对 boss 关取错步（boss 只改 `L.boss.qi`）、`?AISolve=1` 时 `S.autoSolve` 为真必须跳过朗读、
0.4s 计时器必须登记进 `S.timeouts`（`timersClear` 会清）。「点了就停」用 `#stage` 捕获阶段统一 `pointerdown` → `cancel()`，不改 30 个 pick 函数。
