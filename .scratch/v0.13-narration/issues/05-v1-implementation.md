Type: task
Status: resolved
Blocked by: 01, 02, 03, 04, 09

# v1 实现：进入关卡就自动念

## Question

只改 `ios/preview/index.html`（渲染层），数据一个字节不改。做完要满足：

1. 抽一个 `narrateStep(sub, st)` 生成朗读稿（按 02 的题型清单与 03 的样张口径）
2. 三条入口都要触发自动念：普通关 `renderLevel()`、迷你棋盘题（`L.bd.mode==="question"` 的 `boverlay`）、
   Boss 战（`bossHTML` 里内嵌的题）。**同一道题只念一次**（重渲染别重复念）
3. 每题渲染后 0.4 秒开念；孩子点选项立刻 `speechSynthesis.cancel()`
4. 答错念一句短提示（用 `hint`），答对不念
5. 每题常驻「🔊 再念一遍」按钮（位置不能压住选项、不挡小人）
6. 「学一学」卡：字 + 拼音 + 例词（`words[].say` / `examples[].say`）
7. 家长中心朗读开关（按 04 的结论），状态要能持久化（现有 `save()` 那套）
8. 兜底：`speechSynthesis` 不可用、被静音、报错，一律静默降级，不崩、不卡关

验收：

- 六科各进 3 关，逐题听一遍（含一关棋盘关、一个 Boss 关）
- 三门闸门全绿：`check_registry.py` / `validate.py` / `audit_preview.py`
- `preview_sweep.py --steps=2` 快查不新增失败

## 实现约束（来自票 02，别重踩）

- 挂点选 `renderLevel` 收尾的 `afterStepRender()`（约 1899）一处，能同时覆盖普通关、棋盘 `boverlay`、boss 内嵌题。
- `currentStepObj()`（约 3891）对 boss 关取错步——boss 只推进 `L.boss.qi`，从不动 `L.step`，得自己按 `b.qi` 取。
- `?AISolve=1` 时（`S.autoSolve`，约 4225）**必须跳过朗读**，否则 `preview_sweep` 会对着 2102 步开念。
- 0.4 秒那次 `setTimeout` 必须登记进 `S.timeouts`，否则 `timersClear()` 清不掉，会跨关抢声。
- 「点了就停」在 `#stage` 捕获阶段挂一次 `pointerdown` → `speechSynthesis.cancel()`，不要去改 30 个 pick 函数。
- 选项字段形态不统一（裸数字、字符串、`label`、根本没有 options），朗读文本提取要按 kind 分支，不能一把梭。
- 「再念一遍」按钮放在 `.lv-body` 之外，别压住选项。

参考：`speak(t, sub)` 与 `speakSeg` 在 `index.html` 约 1427-1446 行；题型总表见 `.scratch/v0.13-narration/research/02-kind-narration-inventory.md`。

## 实现约束（来自票 01，别重踩）

- **解禁必须在点击的同步栈里**：iPad WebKit 只在用户手势同步栈内允许 `speak()`，`setTimeout` 里的调用会被静默丢弃。
  所以进关/进学科那一下点击的 handler 里要同步 `speak()` 第一句（暖机或直接念第一题），此后整个 document 永久解禁，
  各题才能走 0.4 秒延时。冷启动/刷新要重新解禁——顺手让「🔊 再念一遍」也能自愈。
- **禁止同 tick `cancel(); speak();`**（WebKit bug 191745，现有 `speak()` 正是这个写法）：打断或重念要错开 60-100ms；
  **禁止用 `onend` 串接下一条**（bug 238189 下 onend 不触发，会永久卡死）；给「再念一遍」加看门狗：
  800ms 内没进入 speaking 状态就把它亮出来，让孩子能自己点。
- 不指望增强音色：网页只能拿到内置 compact 音色，别在界面或文档里引导用户「下载更好的语音」。
- 静音开关会静音且 JS 无法检测：没有声音时不要弹错误，按 04 的结论静默处理。

## 已拆解（2026-10-19）

本票不单独执行，实际工作拆成七个垂直切片：票 10（最小闭环）、11（选项）、12（学一学卡）、
13（其余题型）、14（再念一遍）、15（家长中心）、16（棋盘与 Boss）。
上面的验收项已下放到各切片，票 06（iPad 实测）改为挡在这七张之后。

## Answer

已拆解并全部落地（票 10-16）。本票作为汇总票关闭：验收项已下放到各切片并逐条验过，
票 06（iPad 实听调语速）与票 07（是否补 say 数据）仍是人要做的事。
