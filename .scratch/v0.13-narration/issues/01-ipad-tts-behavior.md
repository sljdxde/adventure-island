Type: research
Status: resolved
Blocked by: —

# iPad Safari 的 speechSynthesis 能自动播到哪一步

## Question

运行环境不是普通网页：padOS 16+ 的 Safari，`ios/preview/index.html` 从「文件」App 打开后
「添加到主屏幕」当独立 Web App 全屏跑（见仓库根的 `探险岛-iPad使用说明.txt`）。

要查清的事实（决定自动朗读怎么写，不决定念什么）：

1. 免用户手势的自动朗读在这套环境下能不能出声？进关本身是一次点击，这次点击够不够解禁语音？
2. 侧边静音开关、系统音量、锁屏、切后台，对已排队与正在播的语音分别什么影响？
3. `zh-CN` 音色在 iPadOS 上是否一定存在（是否需要用户先下载「增强音质」）？中英混排逐句
   `speak()` 的排队顺序与打断行为如何？
4. SPA 里切题时 `speechSynthesis.cancel()` 是否可靠？iOS 上「cancel 后立刻 speak 新句」有没有已知静音 bug、要不要加延时？
5. 主屏 Web App 模式与 Safari 标签页模式在这几点上有差异吗？

产出：结论 + 来源链接 + 一段「v1 该怎么写」的明确建议（含必须加的兜底）。
优先级：第 1、4 条是阻塞项，其余是补充。

## Answer

产出：[01-ipad-tts-behavior.md](../research/01-ipad-tts-behavior.md)（含 8 条「需要真机验证」清单）。

### 阻塞项

1. **免手势朗读在这台设备上不成立**：WebKit 默认 `RequiresUserGestureForAudioPlayback=true`，`speak()`
   只在「当前正处于用户手势的同步栈」里才解除限制，否则直接 return——不排队、不报错、无事件。
   → 进关那次点击本身不够；**0.4 秒的定时器永远解禁不了**，第一题会永远没声音。
   解禁后整个 document 永久有效（SPA 一次管整局，冷启动/刷新要重来）。
2. **`cancel()` 后紧跟 `speak()` 会被吞**（WebKit bug 191745，2018 开票 2026-03 才修；bug 238189 仍 NEW）。
   现有 `speak()`（`index.html` L1427-1446）正是 `cancel(); speak();` 同 tick 写法，切题/答错/再念都会高频踩。
   → 禁止同 tick cancel+speak；**禁止用 `onend` 串接下一条**；打断或重念要错开 60-100ms。

### 补充项

- 静音开关大概率静音朗读（WebKit 不给语音设 audio session 类别 → 跟随 soloAmbient），**且 JS 无法检测**。
- 锁屏/切后台会掐掉语音（17+ 的 suspend 清队列）。
- 网页只能拿到内置 compact 音色，下载的增强音色拿不到（bug 203689 / 290497）——别指望靠用户下载改善音质。
- 多段不同 `lang` 的 utterance 按 FIFO 播、互不打断，但每条之间有合成切换空隙，别按词拆句。
- 主屏 Web App 与标签页在语音机制上无差异。

### 对地图的连带修改

- 地图 Notes 口径 4 已加票 01 修正（进关同步解禁）。
- 票 04 加一项「静音开关静音且不可检测，家长中心要不要写一句提示」。
- 票 05 加实现约束（暖机、禁同 tick cancel、看门狗、禁 onend 串接）。
- 票 06 的实测清单直接用研究文件里的 8 条。
