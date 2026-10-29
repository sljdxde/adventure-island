# iPadOS 16+ Safari 的 speechSynthesis 能自动播到哪一步

对应票：`.scratch/v0.13-narration/issues/01-ipad-tts-behavior.md`
口径来源：`.scratch/v0.13-narration/map.md` 的 Notes（不重议）
本次只读 WebKit 源码 / WebKit Bugzilla / Apple 文档 / MDN，未改仓库代码、未跑构建。

**一句话结论：能出声，但必须有一次「说话动作落在用户手势的同步栈里」来解禁；解禁一次对整个
document 永久有效。真正会咬人的是第二件事——`cancel()` 之后立刻 `speak()` 在 WebKit 里是
长期未修的坑（2018 开票、2026-03 才在 main 修掉），而现有的 `speak()` 恰好就是这个写法。**

证据强度约定：**[主源]** = WebKit 源码 / WebKit Bugzilla / Apple 官方文档；**[推断]** = 由主源
机制推出但无直接陈述；**需要真机验证** = 没有任何来源能坐实，只能 iPad 上试。

---

## 1. 免手势自动朗读能不能出声（**阻塞项**）

### 结论

- 能，条件是：**某一次 `speak()` 必须发生在用户手势事件派发的同一个同步调用栈里**。
- 一次解禁，整个 document 后续所有 `speak()` 都不再需要手势。
- 手势本身（哪怕是「点关卡进关」那次点击）**不够**；只有在手势栈里调用过 `speak()` 才算数。
  点击后 `setTimeout(…, 400)` 里的 `speak()` **不在**手势栈里，会被静默丢弃。

### 依据

iOS 家族默认要求用户手势才能开始语音。设置项默认值就在 WebKit 的偏好表里，
`RequiresUserGestureForAudioPlayback` 在 `PLATFORM(IOS_FAMILY)` 下默认 **true**：

```yaml
RequiresUserGestureForAudioPlayback:
  type: bool
  defaultValue:
    "PLATFORM(IOS_FAMILY)": true
    default: false
```

- [UnifiedWebPreferences.yaml#L5193-L5200](https://github.com/WebKit/WebKit/blob/main/Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml#L5193-L5200)
- 该值经 `Document::requiresUserGestureForAudioPlayback()` 读出来（导航策略优先，否则用全局设置）：
  [Document.cpp#L7980-L7990](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/Document.cpp#L7980-L7990)

`SpeechSynthesis` 在创建时据此挂上限制位，`speak()` 里检查并**只认手势栈**：

```cpp
// 构造：iOS 家族，若文档要求手势才允许音频，就挂上 RequireUserGestureForSpeechStart
#if PLATFORM(IOS_FAMILY)
    if (document->requiresUserGestureForAudioPlayback())
        m_restrictions = BehaviorRestrictionFlags::RequireUserGestureForSpeechStart;
#endif

void SpeechSynthesis::speak(SpeechSynthesisUtterance& utterance)
{
#if PLATFORM(IOS_FAMILY)
    if (UserGestureIndicator::processingUserGesture())
        removeBehaviorRestriction(BehaviorRestrictionFlags::RequireUserGestureForSpeechStart);
    else if (userGestureRequiredForSpeechStart())
        return;          // ← 直接返回：不排队、不报错、不派发任何事件
#endif
    ...
}
```

- [SpeechSynthesis.cpp#L64-L72](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L64-L72)
- [SpeechSynthesis.cpp#L162-L175](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L162-L175)（`845b737422` 是 2026-10-12 的 main 快照）
- 这条限制的来历与「iOS 一直要求手势」确认于此：<https://bugs.webkit.org/show_bug.cgi?id=223473>（2021-03，RESOLVED FIXED，落地 commit [ce54d0c](https://github.com/WebKit/WebKit/commit/ce54d0c2624cacc60e871550ecc3c5856ba1625c)）

### 三个容易踩空的细节

1. **`processingUserGesture()` 只认同步栈。** 手势 token 默认不往微任务之后传播
   （`ShouldPropagateToMicroTask::No`），`setTimeout` / `requestAnimationFrame` / `await`
   之后都不算。见 [UserGestureIndicator.h](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/UserGestureIndicator.h)
   （同文件里 `maximumIntervalForUserGestureForwarding = 1_s` 只用于「转发」场景，不改变这一点）。
2. **静默失败，没有任何信号。** `speak()` 在限制未解除时直接 `return`：没有 `onerror`，
   `speechSynthesis.speaking` 仍是 `false`，控制台也没东西。所以「没声音」时从 JS 侧看不出原因。
3. **解禁是按 document 记的。** `window.speechSynthesis` 是每个 window 一个、懒创建并缓存的实例，
   限制位只会被移除、不会再加回来（[LocalDOMWindowSpeechSynthesis.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/Modules/speech/LocalDOMWindowSpeechSynthesis.cpp)）。
   本仓库是单 document 的 SPA，所以**一次解禁管整局**；但主屏 Web App 冷启动、Safari 刷新
   都是新 document，得重新解禁。

### 和现有代码的关系

`index.html` 里现在所有 `speak()` 调用都挂在 `onclick` 上（词卡、🔊、「想听点这里」、写字的读一读……），
所以 v0.12 一直是「能用」的——不是因为免手势，而是**每次都在手势里**。
`speak()` 本体见 [index.html#L1427-L1446](ios/preview/index.html#L1427-L1446)。

新增的「每题渲染后 0.4 秒自动念」正好落进坑里：渲染发生在点击后的同步栈，0.4 秒后已经不在了。
如果不管，现象会是「第一题永远没声音，孩子点过一次 🔊 之后突然开始有声音」。

### 怎么解（三选一，推荐第 1 个）

1. **把第一次朗读放进手势里，别用 0.4 秒延时。** 进关/进学的点击处理里 render 之后同步
   `speak(第一条)`（map.md 决策 4 的 0.4 秒只用于后续题目；第一条在点击瞬间念反而更自然）。
2. 进关点击处理里同步跑一次「暖机」：`const u=new SpeechSynthesisUtterance(' '); u.volume=0; speechSynthesis.speak(u);`
   —— 只做一次，之后的延时朗读全部放行。空串/空格音轨的行为属于 **需要真机验证** 项（历史上曾有
   「零长度 utterance 毒化后续语音」的 bug，[bug 129403](https://bugs.webkit.org/show_bug.cgi?id=129403) 已于 2014 修掉，但没在 iPadOS 16+ 上验证过）。
3. 什么都不做，靠「点 🔊 再念一遍」当第一次解禁 —— 能自愈（按钮在手势里），但第一题一定是哑的，不推荐。

> Safari 的「设置 → Safari → 网站设置 → 自动播放」可以让用户放宽这条策略（映射到同一个偏好），
> 但**不能依赖**：主屏 Web App + `file://` 文档大概率不在「网站设置」列表里，实际就是默认值（要求手势）。
> 这一点属于 **[推断] + 需要真机验证**。

---

## 2. 静音开关 / 系统音量 / 锁屏 / 后台（补充项）

### 机制

WebKit 的语音走 UI 进程的 `AVSpeechSynthesizer`（[WebSpeechSynthesisClient.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebKit/WebProcess/WebCoreSupport/WebSpeechSynthesisClient.cpp)），
而 `AVSpeechSynthesizer` **默认使用 App 当前的 audio session 类别**
（`usesApplicationAudioSession` 默认为真：[Apple 文档](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession)）。

WebKit 为语音合成这条路**没有设置** audio session 类别（[PlatformSpeechSynthesizerCocoa.mm](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/platform/cocoa/PlatformSpeechSynthesizerCocoa.mm)
与 [WebSpeechSynthesisClient.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebKit/WebProcess/WebCoreSupport/WebSpeechSynthesisClient.cpp) 里都没有 `AVAudioSession` 调用；
类别只在播放 HTML 媒体时由 `AudioSessionIOS` 改成 `AVAudioSessionCategoryPlayback`）。

而 iOS 的默认类别 `soloAmbient` 的官方定义就是：**「Your audio is silenced by screen locking and by the Silent switch」**
——[Apple 文档：soloAmbient](https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/soloambient)。

### 由此得出的行为表

| 情形 | 对**正在播**的语音 | 对**已排队未播**的语音 | 证据 |
|---|---|---|---|
| 侧边静音开关打开 | 大概率整段听不见 | 照样「播」，只是听不见 | [推断]（soloAmbient 定义 + WebKit 不设类别）；**需要真机验证** |
| 系统媒体音量调到 0 | 听不见 | 同上 | [推断]；音量不可读，无法检测 |
| 锁屏 | 网页 App 被挂起 → 停 | 队列被清空 | WebKit 17+ 源码有 `suspend()`/`stop()`；iPadOS 16 无对应源码保证，**需要真机验证** |
| 切到别的 App（后台） | 同上：停 | 清空 | 同上 |
| 中途播过 `<audio>`/`<video>` | 可能反而「解锁」成 playback 类别，静音开关不再影响 | — | [推断]，**需要真机验证** |

关键源码：`suspend()` 与 `stop()` 都调用 `stopPlatformSpeech()`，清空队列并让平台取消，
而且**不派发任何事件**（[SpeechSynthesis.cpp#L370-L395](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L370-L395)）。
这套 `ActiveDOMObject` 挂起逻辑是 2023-08 才加进来的（[bug 260207](https://bugs.webkit.org/show_bug.cgi?id=260207)、
[commit 527353138b](https://github.com/WebKit/WebKit/commit/527353138b) 进一步修 stop 的同步派发崩溃），
**所以 iPadOS 16 上「切后台会不会继续念」不能按现源码推断 → 需要真机验证。**

### 对 v1 的要求

- 不要做任何「能听见吗」的自动判断（没有任何 Web API 能查静音开关/音量）。
- **回到前台必须重念当前题**：`visibilitychange` → `hidden` 时记下「当前该念什么」，`visible` 时重念。
- 静音开关这件事只能在家长说明里写一句「听不到声音时先看侧边开关」，代码兜不住。
- 打断是否可靠（`cancel()` 在 iOS 上能不能立刻停住声音）——`cancel()` 的语义在 MDN 有明确写法
  （[MDN cancel()](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/cancel)），
  但「点选项后 100ms 内真的安静了」这点**需要真机验证**。

---

## 3. zh-CN 音色与中英混排（补充项）

### 3.1 音色

- **网页只能看到内置（compact）音色。** WebKit 为了反指纹，只把 `AVSpeechSynthesisVoiceQualityDefault`
  的音色暴露给 `getVoices()`：[bug 203689](https://bugs.webkit.org/show_bug.cgi?id=203689)（2019，已修）。
- **下载的「增强/优质」音色在网页里拿不到**：`getVoices()` 不列它们，最新一条反馈仍 open
  （[bug 290497](https://bugs.webkit.org/show_bug.cgi?id=290497)，2025-03，NEW）。
  → 所以「先让家长下载增强音色再朗读」这条路**在 Web 侧根本不通**，不要写进使用说明。
- 语音按 `lang` 匹配；匹配不到时**不报错**，`avVoice` 为 `nil`，交回系统默认音色
  （[PlatformSpeechSynthesizerCocoa.mm#L147-L187](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/platform/cocoa/PlatformSpeechSynthesizerCocoa.mm#L147-L187)）——
  表现是「用错语言的嗓子念中文」，不是无声。
- `zh-CN`（普通话-中国大陆）是 Apple 语音合成支持的语言（Apple 功能可用性页面列出
  *Mandarin Chinese (China mainland)*，[HT206175](https://support.apple.com/en-us/HT206175) 现重定向到功能可用性页）。
  **但「每台 iPad 上一定已装 zh-CN 紧凑音色」没有主源能坐实 → 需要真机验证**（进关时打一条
  `getVoices().map(v=>v.lang)` 到控制台看一眼即可）。
- 别把「音色列表里有某条」当硬前提：iOS 16.0.2 出过 `getVoices()` 丢掉 ja-JP 音色的回归
  （[bug 250665](https://bugs.webkit.org/show_bug.cgi?id=250665)，2023 开票，至今未定位）。
  另有 `voiceschanged` 只在 2023-08 才在 Cocoa 端补齐实现（[bug 260228](https://bugs.webkit.org/show_bug.cgi?id=260228)），
  所以**不要等 `voiceschanged` 再开始念**。

### 3.2 一次 `speak()` 多条 utterance（中英混排）

- 排队顺序**有保证**：Web Speech 层是 FIFO 队列（[WebKit 源码 `m_utteranceQueue`](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L162-L175)、
  [MDN speak()](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/speak)），
  平台层 `AVSpeechSynthesizer` 也文档化地「按收到顺序排队播」
  （[Apple：AVSpeechSynthesizer](https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer)）。
- **不会互相打断**：只有 `cancel()` 能截断正在播的那条。
- 每条按自己的 `lang` 选音色，所以「中文段 zh-CN + 英文段 en-US」的写法是成立的。
- 代价：**每换一条 utterance 都有一次合成切换的空隙**（听感上像句间多停了半拍）。把一句话拆成
  很多碎片会明显变慢、变断续；现有 `speakSeg()` 按连续拉丁字母切段（[index.html#L1427-L1437](ios/preview/index.html#L1427-L1437)），
  对「一个英文单词夹在中文里」这种频率是可接受的，别进一步按词或按字拆。

---

## 4. `cancel()` 的可靠性（**阻塞项**）

### 结论

`cancel()` 本身在 SPA 里能把队列清干净；**「`cancel()` 之后立刻 `speak()`」是 WebKit 长期未修的坑**，
而现有 `speak()` 恰好就是这个组合。v1 的自动朗读 + 切题 + 答错提示会高频踩到它。

### 证据（两个都还活着 / 刚修）

1. **`cancel()` 后紧跟的 `speak()` 会被吞掉** —— [bug 191745](https://bugs.webkit.org/show_bug.cgi?id=191745)。
   最小复现（2018-11 报在 Safari 12）：

   ```js
   synth.speak(u1);  synth.cancel();
   synth.speak(u2);  synth.speak(u3);
   // 实际：只念 u3；期望：u2 然后 u3
   ```

   2018 年开票，直到 **2026-03 才在 WebKit main 修掉**
   （[commit 3dc3ba3a4d](https://github.com/WebKit/WebKit/commit/3dc3ba3a4d52cd8f24e6c7d491b90b2830f5bcd8)，
   提交说明原话：*"Because cancel() callbacks happen asynchronously on the platform synthesizer,
   they can clear out the wrong utterance."*）。
   → **iPadOS 16/17/18 都在未修区间内**；更晚的系统要看是否已带上这个修复（**需要真机验证**）。

2. **`cancel()` 后立刻排的 utterance 收不到事件** —— [bug 238189](https://bugs.webkit.org/show_bug.cgi?id=238189)（2022-03，**仍 NEW**）。
   报告者在 macOS 15.3 与 **iOS 15.4** 都复现：打断后新句子**有声音**，但
   `onstart` / `onend` / `onboundary` 一个都不触发。
   → 也就是说同一段代码在不同版本上，表现可能是「完全没声」或「有声但没事件」。
   **哪一种，需要真机验证**；但两种情况都要求我们不许依赖事件。

3. 历史同类 bug（说明这块一直不稳）：`cancel()` 不触发 `onend`（iOS 13.4.1 回归，
   [bug 211776](https://bugs.webkit.org/show_bug.cgi?id=211776)，2020 修）；`clear()` 顺带吃掉后面的
   `speak()`（同上 191745）。

### 对 v1 的要求

- **不要在「正在播」的同一 tick 里 `cancel()` + `speak()`。** 至少隔一个宏任务 + 一点余量
  （建议 60-100ms，具体值 **需要真机验证**，可试 0/50/100/150 四档）。
- 更稳的做法是**让打断与朗读天然错开**（和 map.md 决策 4 正好兼容）：
  - 孩子点选项 → 只 `cancel()`，并把「朗读代际」+1，**当场不念任何东西**；
  - 答错提示本来就该晚半拍，放在 `setTimeout(…, 300+)` 里再念，天然过了危险窗口。
- **不要用 `onend` 串接下一条**（238189：cancel 之后 `onend` 不触发，链会断死，后面全哑）。
  要串接就用「整体取出、一次排完」的写法，或者用计时器兜底。
- 加一个看门狗兜底：`speak()` 之后约 800ms 如果 `speechSynthesis.speaking === false && pending === false`，
  就把「🔊 再念一遍」高亮/浮出来，让孩子自己点（点击是手势，顺带还能补一次解禁）。

---

## 5. 主屏 Web App 与 Safari 标签页的差别（补充项）

- **引擎层面没有差别**：主屏 Web App 跑的还是同一份 WebKit，第 1 节那条手势检查里
  也没有任何 standalone 分支；WebKit Bugzilla 里也没有搜到「主屏模式语音不响」这类专门条目
  （搜过 `summary=standalone`、`summary="home screen" speech`）。两者跑的是同一套系统 WebKit →
  speechSynthesis 的机制一致，这部分是**[主源]**；「实际听感也一致」仍是 **[推断]**。
- 真正不同的是**生命周期和可配置性**：
  - 主屏模式是 App 式实体，有自己的 App 切换器条目，切后台/锁屏就是挂起
    （[WebKit 博客：Web Push for Web Apps on iOS and iPadOS](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)）；
  - 没有地址栏 → 家长基本改不了「网站设置 → 自动播放」，第 1 节的手势限制实际上总是生效
    （**[推断]**：主屏 App 不是 Safari 里的一个站点，`file://` 也不在「网站设置」列表里）；
  - 独立进程/独立存储，冷启动会重新加载 document → 解禁状态每次冷启动都要重来。
- 本仓库用的是 `<meta name="apple-mobile-web-app-capable" content="yes">`（[index.html#L6](ios/preview/index.html#L6)）
  + 从「文件」App 用 Safari 打开的 `file://` 文档，属于 iOS 16.4 manifest 之前的老路径。
  「老路径与新 manifest 路径在语音策略上完全一致」这一点官方没有明文 → **需要真机验证**（在两种入口各跑一次第 1 节的验收）。

---

## 需要真机验证的清单（没有来源能坐实，只能 iPad 上试）

1. 自动朗读第一题是否真的哑掉（第 1 节的核心风险）。
2. 点一次 🔊 之后，后续**自动**朗读是否都恢复（验证「一次解禁管整局」）。
3. 侧边静音开关打开时，语音是否真的听不见；先播一段 `<audio>` 后是否变得听得见。
4. 锁屏 / 切后台 / 回前台：声音是否停、回来后 `speechSynthesis` 是否卡在 `paused:true`。
5. `cancel()` 后立刻 `speak()` 的实际表现（无声 / 有声无事件），以及 60-100ms 延时是否足够消除。
6. 点选项打断后，声音多久真正停下来。
7. `getVoices()` 里的 `zh-CN` 音色名与数量；中英混排两条 utterance 之间的实际停顿。
8. 主屏入口 vs Safari 标签页入口，上述结论是否一致。

---

## v1 该怎么写（含必须加的兜底）

```js
/* ---- 1. 手势解禁 + 朗读，共用一条路径 ---- */
let speechUnlocked = false;
let sayGen = 0;                      // 朗读代际：切题/打断时 +1，旧的回调自动作废

function unlockSpeech(){             // 只允许在 onclick/touchend 的同步栈里调用
  if (speechUnlocked) return;
  try {
    const u = new SpeechSynthesisUtterance(' ');   // 空格，volume 0，听不见
    u.volume = 0;
    speechSynthesis.speak(u);
    speechUnlocked = true;
  } catch (e) {}
}

/* ---- 2. 说一句话（可多段不同 lang） ---- */
function sayNow(parts){              // parts: [{text, lang}]，按顺序一次排完
  for (const p of parts) {
    const u = new SpeechSynthesisUtterance(p.text);
    u.lang = p.lang || 'zh-CN';
    u.rate = 0.8; u.pitch = 1.15;    // 与 v0.12 一致
    speechSynthesis.speak(u);
  }
}

function say(parts){
  const my = ++sayGen;
  try {
    speechSynthesis.cancel();        // 先停旧的
    setTimeout(() => {               // 隔一个宏任务，躲开「cancel 后立刻 speak」的坑
      if (my !== sayGen) return;
      sayNow(parts);
      setTimeout(() => {             // 看门狗：没念出来就把「再念一遍」亮出来
        if (my !== sayGen) return;
        if (!speechSynthesis.speaking && !speechSynthesis.pending) showReplayHint();
      }, 800);
    }, 80);
  } catch (e) {}
}

/* ---- 3. 打断：只停不念 ---- */
function hush(){ sayGen++; try { speechSynthesis.cancel(); } catch (e) {} }
```

要点逐条：

1. **进关/进学的点击处理里同步 `unlockSpeech()`**（或干脆直接把第一条朗读同步念掉，省掉暖机）。
   这是整个功能能不能出声的开关，必须先写、先验。
2. `speak()` 走「先 `cancel()`，隔 80ms 再排」。**任何打断 + 立刻重念的组合都必须这样写**，
   包括答错提示、再念一遍、切题。80ms 是待验证的初值。
3. **不要用 `onend` 串接下一条**，不要依赖 `onstart`/`onerror` 做状态机。
   （238189：cancel 之后这些事件整组不触发。）
4. **不要读 `speechSynthesis.speaking` 来决定「要不要念」**——挂起/取消后它可能停在旧值。
   用我们自己的 `sayGen` 代际号。
5. **不要做音色选择 UI，不要引导下载增强音色。** 只设 `u.lang`；`u.voice` 留空。
6. **中英混排按「整段中文 + 整段英文」拆 2 段**，不要按词拆；拼音仍走 `pyConvert` 转同音字。
7. `visibilitychange`：`hidden` 记住「当前该念什么」，`visible` 时重新 `say()` 当前题
   （锁屏/切后台必然把语音掐掉）。
8. 保留「🔊 再念一遍」：它既是产品需求，也是**手势解禁的自愈入口**——第一次自动朗读万一哑了，
   孩子点一下 🔊 之后整局都恢复正常。
9. 家长说明（`探险岛-iPad使用说明.txt`）加一句：**听不到朗读先看 iPad 侧边静音开关**；
   不要写「可下载增强音色改善音质」——网页拿不到增强音色。
10. 验收顺序：先在 iPad 上只做第 1 节的解禁实验（进关能不能直接出声）→ 再做第 4 节的
    「打断后立刻念」实验 → 两关都通了再铺全六科。

---

## 来源

主源（WebKit 源码 / Bugzilla / Apple / MDN）：

- WebKit 源码 `SpeechSynthesis.cpp`（手势限制 + 队列 + 挂起）：
  [L64-L72](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L64-L72)、
  [L162-L175](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L162-L175)、
  [L370-L395](https://github.com/WebKit/WebKit/blob/845b737422/Source/WebCore/Modules/speech/SpeechSynthesis.cpp#L370-L395)
- WebKit 偏好默认值 `RequiresUserGestureForAudioPlayback`（iOS 家族 true）：
  [UnifiedWebPreferences.yaml](https://github.com/WebKit/WebKit/blob/main/Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml#L5193-L5200)
- `Document::requiresUserGestureForAudioPlayback()`：
  [Document.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/Document.cpp#L7980-L7990)
- 手势栈判定 / token 传播：[UserGestureIndicator.h](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/dom/UserGestureIndicator.h)
- 语音合成走 UI 进程：[WebSpeechSynthesisClient.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebKit/WebProcess/WebCoreSupport/WebSpeechSynthesisClient.cpp)
- 音色按 `lang` 匹配、匹配不到给 nil：
  [PlatformSpeechSynthesizerCocoa.mm](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/platform/cocoa/PlatformSpeechSynthesizerCocoa.mm#L147-L187)
- Bugzilla 223473（iOS 一直要求手势，2021 改成跟随 autoplay 策略）：<https://bugs.webkit.org/show_bug.cgi?id=223473>
- Bugzilla 191745（cancel 后紧跟的 speak 被吞，2018 开票 / 2026-03 修复）：<https://bugs.webkit.org/show_bug.cgi?id=191745>，
  修复 commit：[3dc3ba3a4d](https://github.com/WebKit/WebKit/commit/3dc3ba3a4d52cd8f24e6c7d491b90b2830f5bcd8)
- Bugzilla 238189（cancel 后立刻排的 utterance 收不到事件，仍 NEW）：<https://bugs.webkit.org/show_bug.cgi?id=238189>
- Bugzilla 211776（iOS 13.4.1 cancel 不触发 onend）：<https://bugs.webkit.org/show_bug.cgi?id=211776>
- Bugzilla 203689（网页只暴露内置音色，反指纹）：<https://bugs.webkit.org/show_bug.cgi?id=203689>
- Bugzilla 242588（曾经只能用「朗读内容」里选中的那条音色）：<https://bugs.webkit.org/show_bug.cgi?id=242588>
- Bugzilla 290497（下载的音色不出现在 getVoices()，仍 open）：<https://bugs.webkit.org/show_bug.cgi?id=290497>
- Bugzilla 250665（iOS 16.0.2 起 getVoices() 漏掉 ja-JP）：<https://bugs.webkit.org/show_bug.cgi?id=250665>
- Bugzilla 260207 / 260228（SpeechSynthesis 改为 ActiveDOMObject；Cocoa 补 voiceschanged）：
  <https://bugs.webkit.org/show_bug.cgi?id=260207>、<https://bugs.webkit.org/show_bug.cgi?id=260228>
- commit 527353138b（`stop()`/`suspend()` 清队列且不派发事件，2026-08）：<https://github.com/WebKit/WebKit/commit/527353138b>
- Apple：`soloAmbient` 类别（静音开关与锁屏会静音）：<https://developer.apple.com/documentation/avfaudio/avaudiosession/category-swift.struct/soloambient>
- Apple：`AVSpeechSynthesizer`（平台侧 FIFO 队列）：<https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer>
- Apple：`usesApplicationAudioSession`（默认用 App 的 audio session）：<https://developer.apple.com/documentation/avfaudio/avspeechsynthesizer/usesapplicationaudiosession>
- Apple：`AVSpeechSynthesisVoice`（语言/音质可选，语言列表指向功能可用性页）：<https://developer.apple.com/documentation/avfaudio/avspeechsynthesisvoice>、<https://support.apple.com/en-us/HT206175>
- MDN：`speak()` 排队语义 / `cancel()` 清空队列：<https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/speak>、<https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/cancel>
- WebKit 博客：主屏 Web App 是 App 式实体（独立 App 切换器条目等）：<https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/>
