# 题型朗读清单：30 种 step kind 各念什么

对应票：`.scratch/v0.13-narration/issues/02-kind-narration-inventory.md`
口径来源：`.scratch/v0.13-narration/map.md` 的 Notes（已锁定，不再重议）
本次只读 `ios/preview/index.html` 与 `ios/AdventureIsland/Resources/*.json`，未改任何文件。

## 基线数字（用来判断覆盖面）

| 指标 | 数值 |
|---|---|
| `renderStep(sub, st)` 的 case | 30 个 + 1 个兜底（第 1936 行） |
| 数据里实际出现的 kind | **29 种**（`cmp` 在六科数据里 0 步，只有渲染器） |
| 关卡 / 步骤总数 | 600 关 / 2102 步 |
| 迷你棋盘关（`lv.board`） | **120 关**（识字村 100 + 其余五科各 4） |
| Boss 关（`lv.boss`） | 6 关（每科 1） |
| `options[]` 总数 / 有 `text` / 纯图标 | 4035 / 3320 / 715（另有 `compare` 的 21 条用 `label`，不在 `options` 里） |

715 个纯图标选项的分科数（与票 07 的「识字村 442、环球号 97、英语 71、天文 42、思维 35、拼音 28」完全一致，可作为该票的数字佐证）：
`listen` 442（识字村 436 + 天文 6）、`quiz` 195（环球 91 / 英语 60 / 拼音 28 / 思维 12 / 天文 4）、`tapall` 45、`pattern` 33。

## 1. 总表

「题面」= 渲染器里那条 `.q-pill` 的文字来源；「选项」= 孩子手指要点的那一组东西。
行号是函数定义行（`index.html`）。

| kind | 渲染函数（行号） | 题面文字来源 | 选项来源 | 选项有文字？ | 现有 🔊？ | 建议念法 |
|---|---|---|---|---|---|---|
| teach | `teachHTML` 2711 | **无 `question` 字段**，题面是 JS 写死的 `看一看：{char} 是怎么变来的？` | 无选项；`char` / `pinyin` / `words[].text`（197/197 带 `say`） | 无选项，词卡全有文字 | **有**（2723 `speak(pinyin。char)`；词卡点击可读） | 念「日，rì。日出，生日，日子。」（map.md Notes 第 6 条）；题面那句是硬编码模板，可念可不念 |
| letter | `letterHTML` 3302 | `st.question`（374/374 都有） | 无选项；大卡 `st.display` + `examples[].text`/`say`（779 条，672 带 `say`）+ `fact`/`stats` | 无选项，例词全有文字 | **有**（3332 `speak(display)`；例词点击读 `say ‖ text`） | 念题面 + `display` + 最多 2 个例词（`say ‖ text`）。**不念** `fact` / `stats`（书面语，与 Notes 第 6 条同口径） |
| listen | `listenHTML` 3341 | `st.question`（题面）+ `st.prompt ‖ st.speakText`（大卡内容；113 个用 `promptIcon` 换成了图标） | `st.options`（1137 项，695 有 `text`，**442 纯图标**） | 部分（61%） | **有**（3361「想听点这里」念 `speakText`） | 念题面 + 念 `speakText`；选项有文字念文字，纯图标按 Notes 第 3 条念「第 N 张」 |
| quiz | `quizHTML` 3381 | `st.question`（893/893） | `st.options`（2679 项，2484 有 `text`，**195 纯图标**） | 大部分（93%） | 无 | 念题面 + 逐个选项：有文字念文字，纯图标念「第 N 张」 |
| count | `countHTML` 3420 | `st.question`（32/32） | `st.countOptions` = **裸数字数组**（32/32）；有 `countRange` 时运行时随机重算 | 数字本身 | 无 | 念题面 + 数字选项（「2，3，4」）。题面已含「数数看」，不再加话 |
| compare | `compareHTML` 3471 | `st.question`（7/7） | `st.compareOptions[].label`（21/21，**字段名是 `label` 不是 `text`**） | 有 | 无 | 念题面 + 三个 label（苹果多 / 香蕉多 / 一样多） |
| cmp | `cmpHTML` 3502 | `st.question` | `st.rows[].name` + `.label`/`.value` | 有 | 无 | 念题面 + 逐行「名字：数值」。**数据里 0 步**，实现时可先留空分支 |
| blend | `blendHTML` 3544 | `st.question`（36/36） | `st.parts`（拼块）+ `st.options[].text`（108/108） | 有 | 无 | 念题面 + 选项文字（ba / bo / bu）。注意拼音科走 `pyConvert`，音节会被念成同音字（见 §3） |
| arith | `arithHTML` 3578 | `st.question`（25/25） | `st.arithOptions` = **裸数字**（25/25） | 数字 | 无 | 念题面 + 数字选项 |
| pattern | `patternHTML` 3638 | `st.question`（11/11；仅 2/11 在文字里复述了序列） | `st.options` = **33 项全纯图标**；`st.seq` 39 项全是图标 id | **无** | 无 | 念题面 + 三个「第 N 张」。序列本身念不出（见 §2） |
| split | `splitHTML` 3670 | `st.question`（3/3） | `st.arithOptions` 裸数字 | 数字 | 无 | 念题面 + 数字选项 |
| order | `orderHTML` 3713 | `st.question`（4/4） | `st.nums` 裸数字（4/4；`items[].name` 分支数据里 0 步） | 数字 | 无 | 念题面 + 数字；若将来走 `items` 分支念 `name` |
| neighbor | `neighborHTML` 3753 | `st.question`（4/4） | `st.arithOptions` 裸数字 | 数字 | 无 | 念题面 + 数字选项 |
| memory | `memoryHTML` 3786 | `st.question`（28/28） | `st.cards` 168 张，牌背朝上；84 有 `text`、84 只有 `icon` | 一半 | 无 | 只念题面（不念牌面，翻牌前念等于泄题也是杂音） |
| dice | `diceHTML` 3840 | `st.question`（2/2） | `st.countOptions` 裸数字，**掷完才由 3866 动态插入** | 数字 | 无 | 念题面 + 「点一下骰子」；掷出落定后再念三个数字 |
| write | `writeHTML` 3903 | `st.question`（98/98） | 无选项；`char` + `pinyin` + `strokes` | 无选项 | **有**（3922 `speak(char)`） | 念题面 + 「日，rì」+ 一句「先看一遍，再用手指描红色的那一笔」（对齐 3916 的提示文案） |
| muldiv | `muldivHTML` 3981 | `st.question`（20/20） | `st.options` 裸数字（20/20） | 数字 | 无 | 念题面 + 数字选项 |
| cards | `cardsHTML` 4020 | `st.question`（4/4） | `st.cards` 裸数字（4/4），点满 `pick` 张 | 数字（牌面） | 无 | 念题面 + 牌面数字；不念 `target`（题面已有） |
| sudoku | `sudokuHTML` 4069 | `st.question`（2/2，规则句可念） | `st.symbols` = 4 个**图标 id**；调色板由 `sudCellTap` 动态生成 | **无** | 无 | 念题面 + 「点一个空格，再选一个图案」；四个符号念不出（见 §2） |
| clock | `clockHTML` 4130 | `st.question`（6/6） | `read`：`st.options` 是**字符串数组**（"3:00"，5/6）；`set`：无选项，目标是 `clockLabel(hour,minute)` | read 有 / set 无 | 无 | read 念题面 + 选项（把 "3:00" 念成「3 点」）；set 念「拨到 9 点半，然后点拨好啦」 |
| money | `moneyHTML` 4178 | `st.question`（3/3） | `st.denominations[].label`（15/15）+ 标价 `priceText`（渲染器 4182 自己算） | 有 | 无 | 念题面 + 标价 + 面额（1 角、5 角、1 元…） |
| mappuzzle | `mappuzzleHTML` 4259 | `st.question`（7/7） | 渲染器读 **`st.pieces`（数据里根本没有）**；数据只有 `st.regions[].label`（44/44） | 数据有文字、渲染器没读 | 无 | 先对齐字段（§2）；对齐后念题面 + 6 个区域名 |
| match | `matchHTML` 1969 | `st.question`（13/13） | `st.pairs[].left` / `.right` 的 `text`（39/39 两端都有） | 有 | 无 | 念题面 + 「左边：日、月、山。右边：太阳、月亮、大山。」 |
| shadow | `shadowHTML` 2014 | `st.question`（7/7） | `st.options[].text`（21/21）+ 剪影图标 `st.shadow` | 有 | 无 | 念题面 + 三个选项文字。**不念** `st.shadow` 的图标名（念了等于给答案） |
| tapall | `tapallHTML` 2049 | `st.question`（10/10，且题面已说明要挑什么） | `st.options` 57 项，仅 12 有 `text`，45 纯图标 | 大部分无 | 无 | 念题面 + 有文字念文字、纯图标念「第 N 张」。题面信息量够，序号只是定位 |
| sequence | `sequenceHTML` 2079 | `st.question`（8/8，题面已写出序列「3→2→1」） | `st.seq` 25 项全是字符串（一/二/三），直接渲染成按钮 | 有 | 无 | 只念题面（题面已含序列），不念 `seq` 以免重复 |
| balance | `balanceHTML` 2109 | `st.question`（13/13） | **没有 options 字段**；左右标签是 `left`/`right` 的 `text`（26/26 有）；两个按钮文案写死在 2127-2128 | 有（左右标签） | 无 | 念题面 + 「左边：大象。右边：小鸟。」+ 两个按钮「左边更重 / 右边更重」 |
| sort | `sortHTML` 2148 | `st.question`（8/8） | `st.bins[].label`（16/16）+ `st.items[].text`（47/47） | 有 | 无 | 念题面 + 两个筐名 + 待分类卡片文字 |
| lineup | `lineupHTML` 2193 | `st.question`（4/4） | `st.lineup[].text`（14/14） | 有 | 无 | 念题面 + 卡片文字；不念「谁第几个」（顺序就是答案） |
| spotlight | `spotlightHTML` 2230 | `st.question`（5/5，且 5/5 题面已写出目标是什么） | **没有 options 字段**；`targetIcon` + `decoys`（图标 id 数组） | **无** | 无 | 只念题面（目标物已经在题面文字里）；干扰项全是图标，念不了也不该念 |
| （兜底） | `renderStep` 1936 | 无数据 | — | — | — | 正常数据走不到；念「这一题还没做好」即可，不必专门做 |

### 取值陷阱（实现时最容易踩的四处）

1. **字段名不统一**：文字在多数 kind 叫 `text`，`compare` 叫 `label`，`cmp` 叫 `name`/`label`，`letter` 的例词还有 `say` 覆盖 `text`。按 `o.text` 一把抓会漏掉 `compare` 全部 21 条。
2. **选项不是对象**：`countOptions` / `arithOptions` / `nums` / `muldiv.options` / `cards.cards` 都是**裸数字**，`o.text` 会取到 `undefined`。
3. **选项是字符串**：`clock.options`（"3:00"）、`sequence.seq`（"一"）、`blend.parts`、`pattern.seq`（图标 id）都是字符串，不是对象。
4. **没有选项数组的 kind**：`teach` / `letter` / `write`（无选项）、`balance`（左右二选一，文案写死）、`spotlight`（目标 + 干扰项）、`cards`（牌面）、`money`（面额表）、`mappuzzle`（拼块）。这些必须按 kind 单独拼装。

## 2. 必须新增字段才能念的 kind

判据：题面或题面所指的「题目本体」在数据里**没有任何文字**，只靠现有字段念不出来。

| kind | 缺什么 | 具体表现 | 建议 |
|---|---|---|---|
| **sudoku** | `symbols` 只有图标 id（`duck/apple/star/moon`），调色板无文字 | 念不出「四个符号是什么」，也念不出「这格该放哪个」 | 二选一：给 `symbols` 配中文名（如 `symbolNames:["鸭子","苹果","星星","月亮"]`），或题面里直接写死「用鸭子、苹果、星星、月亮填空」 |
| **pattern** | `seq` 全是图标 id，`options` 33/33 无文字 | 只有 2/11 的题面在文字里复述了序列，其余 9/11 念完题面孩子仍不知道前面排了什么 | 给 `seq` 元素补 `say`（「星星、月亮、星星」），或统一改题面模板把它写进文字 |
| **spotlight** | `targetIcon` + `decoys` 都是图标 id | 目前靠题面文字兜住了（5/5 题面都写了目标），但一旦题面改成泛问就彻底念不出 | 补一个 `targetSay`，题面通用时用它 |
| mappuzzle（半属此类） | 数据有 `regions[].label`，渲染器读的是 `pieces` | 不是缺字段，是**字段名不一致**：`mappuzzleHTML` 的 `st.pieces` 恒为 `undefined`，现在一张拼块都不渲染 | 先统一字段（改渲染器读 `regions[].label` 或让生成器同时产 `pieces`），再谈念法 |
| teach（可选） | 无 `question` 字段 | 题面靠 JS 硬编码模板，改文案要改代码 | 可接受现状（模板简单），不必为此改 schema |

另有 **715 个纯图标选项**（listen 442 / quiz 195 / tapall 45 / pattern 33）按 map.md Notes 第 9 条**v1 不补 `say`**，已在票 07 单独立项，此处不重复计入。

## 3. 念法有歧义、需要人拍板的 kind

没有「念题面 + 念选项」这种自然故事的题型。每行给一个建议默认值，人点头就能直接实现。

| kind | 卡在哪 | 建议默认 |
|---|---|---|
| sudoku | 数独没有「选项」，只有 16 格 + 4 个图标；念格位会变成 16 句 | 念题面规则 + 「点一个空格，再选一个图案放进去」，**不念符号名、不念格位** |
| mappuzzle | 拼块是地理轮廓，只有一个区域名；且当前字段不一致 | 念题面 + 六个区域名（「东北、西部、中部、东部、南方、海岛」），不念「第几块」 |
| write | 描红是看和画，不是听；笔顺念出来孩子跟不上手 | 念题面 + 「日，rì」+ 「先看一遍，再用手指描红色的那一笔」，**不念第几笔** |
| shadow | 剪影本身就是谜面，选项有文字 | 念题面 + 三个选项文字；**绝不念** `st.shadow` 的图标名 |
| spotlight | 干扰项全是图标，目标在题面里 | 只念题面，不念「第 N 个」——星空格子没有稳定序号，孩子对不上 |
| lineup | 卡片有文字，但「按什么顺序」只在题面 | 念题面 + 卡片文字（乱序念），**不念正确顺序** |
| sort | 两筐 + 六张卡，全念会很长 | 念题面 + 两个筐名 + 卡片文字；整句偏长时**拆两次念**（先念筐，停顿后再念卡片），语速本身留给票 06 |
| sequence | 题面已经把「3→2→1」写出来了 | 只念题面，**不念 `seq`**（重复且啰嗦） |
| memory | 牌背朝上，念牌面等于泄题 | 只念题面 + 「点两张翻一翻」 |
| tapall | 6 个格子、45 个没有文字 | 念题面（题面已说明挑什么）+ 有文字念文字，其余只念「第 N 张」 |
| count / dice | 「数一数」的题目本体就是画面里的鸭子/红点 | 念题面 + 数字选项；dice 额外加一句「点一下骰子」（选项是掷完才出现的） |
| clock | 选项是 "3:00" 这种字符串，直接念会变成「三冒号零零」 | 转写成「3 点」「7 点半」再念；set 模式念「拨到 9 点半」 |
| cards | 牌面数字念出来等于给了算式素材，但牌本来就摊在桌上 | 念题面 + 牌面数字（「3、7、2、8、5、1」），不念 `target` |
| blend | 拼音科 `speak()` 会走 `pyConvert`，`ba` 被念成同音字「八」 | 这是有意的路由（否则 TTS 念成英文字母名），建议保留；音节与声调的准确性要留到 iPad 实测（票 06）再定 |
| teach | 题面是硬编码模板，且「学一学」按 Notes 第 6 条念字+拼音+例词 | 念「字，拼音。例词1，例词2，例词3。」；硬编码题面那句可以不念，避免两句开场 |
| letter | `fact` / `stats` 是书面语，`display` 与例词才是内容 | 念题面 + `display` + 最多 2 个例词；**跳过** `fact` / `stats`（与 Notes 第 6 条「不念卡片上那句书面语」同口径） |

## 4. 实现入口

### 4.1 唯一漏斗：`renderStep(sub, st)`（1901）

30 个 kind 全部在这里分派，而且三条渲染路径最后都落到它：

| 路径 | 代码位置 | 说明 |
|---|---|---|
| 普通线性关 | 1848 `body=renderStep(sub, steps[L.step])` | 直接进 `.lv-body` |
| **迷你棋盘关的题目** | 1838 `body+='<div class="boverlay"><div class="sticker">…renderStep(sub,st)…'` | **120 关**走这条，题面渲染在一层 `boverlay` 遮罩里，底下还压着棋盘 |
| **Boss 关** | 2663 `<div class="bb-step">${renderStep(S.lv.subject,st)}</div>` | 6 关，题目**内嵌**在心条之间，不是遮罩 |
| 棋盘开场卡 | 1832 `body=renderStep(sub, steps[0])` | teach / letter 的 intro |

所以「在哪里挂自动朗读」的答案是：**不必进 30 个渲染器，挂在 `renderLevel` 收尾（1899 的 `afterStepRender()`）一处即可**。取 `st` 时可以直接复用 `currentStepObj()`（3891）——它已经处理了「棋盘 question 态」与「线性态」两种取法。但注意 `currentStepObj()` **对 Boss 关是错的**：它最后 `return lv.steps[L.step]`，而 Boss 关推进的是 `L.boss.qi`（`bossCorrect` 2683 只改 `b.qi`，从不改 `L.step`），所以 Boss 路径必须自己按 `steps[Math.min(b.qi, …)]` 取，和 `bossHTML`（2631）保持同一份。

### 4.2 四个必须处理的问题

1. **重复触发**：`renderLevel()` 会因为答对后 `queueNext→nextStep`、重玩、休息遮罩、棋盘蹦跳等多种原因被反复调用。必须按 `st.id` 去重（念过的 id 记一份），否则同一题会被念两三遍。
2. **计时器要管**：Notes 第 4 条要求「渲染后 0.4 秒开念」。这个 `setTimeout` 必须登记进 `S.timeouts`（`timersClear`（1464）会清），否则跨关残留——仓库里 v0.12.2 已经为同类问题改过 15 处 `setTimeout(nextStep)`（见 1465 的注释）。
3. **必须跳过自动答题**：`?AISolve=1` 时 `S.autoSolve` 为真（4225），回归脚本/`preview_sweep.py` 会一路自动答题。朗读钩子若不判断 `S.autoSolve`，跑闸门时会对 2102 步疯狂开念。**这是最容易漏的一条。**
4. **点了就停**：Notes 第 4 条「孩子一点选项立刻停」。选项的点击入口分散在 `pickOpt` / `pickListen` / `pickCount` / `pickCmp` / `pickArith` / `pickBlend` / `tapAllToggle` / `matchPick` / `sortPick` / `sudoku` 的 `sudCellTap`… 逐个改要动 30 处；建议在 `#stage` 上挂一个捕获阶段的 `pointerdown` 统一 `speechSynthesis.cancel()`。

### 4.3 复用现成的东西

- **发声**：`speak(t, sub)`（1441）已经是学科路由唯一入口——英语/天文走 `speakSeg(t,"en-US")` 中英分段，拼音走 `pyConvert` 转同音字。自动朗读务必显式传 `sub`：现有 4 个按钮里有 3 个漏传（2723 / 3332 / 3361），只有 `write`（3922）传了。漏传时会退回 `S.lv.subject`，进关场景勉强成立，但收拾整齐更稳。
- **「🔊 再念一遍」**：现有 4 个按钮（teach 2723、letter 3332、listen 3361、write 3922）念的都是**卡片内容**，不是题面，复用不了。30 个渲染器各加一个按钮太散——建议放在 `renderLevel` 里 `.lv-body` 之外（HUD 下方），一次覆盖三种路径。
- **家长开关**：`renderParent()`（4673）里已有 `seg(标签,[可选值],当前值,格式化,回调)` 的分段控件范式（4703-4705），朗读开关照抄一行即可，状态存 `S.settings` 并 `save()`。

### 4.4 一个必须先处理的数据坑

`mappuzzle` 的渲染器（4259）从头到尾读 `st.pieces`，而生成器 `ios/tools/gen_content.py` 的 `mappuzzle_step`（3058）只产出 `st.regions`——六科数据里 7 个 mappuzzle 步骤**没有一个是带 `pieces` 的**。也就是说这一题型当前渲染出来只有底图、没有可拖的拼块。朗读要做这一题，得先决定：改渲染器读 `regions[].label`，还是让生成器同时产 `pieces`。这属于数据/渲染的既有不一致，不在本票范围内，但会挡住「拼地图」的念法。
