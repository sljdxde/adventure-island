# v0.9 数据 Schema 冻结（双端对齐唯一依据）

> 本文件是 Swift 端、HTML 端、数据生成器三方对齐的唯一依据。字段名/类型/枚举值以本文件为准。
> 任何内容/数值只允许在 `ios/tools/gen_content.py` 中修改并重新生成 JSON；禁止双端各写一份。
> 新题型必须 Swift（`LevelView.swift` 题型总线）与 HTML（`index.html` renderStep）两端都实现。

## 0. 文件所有权（防止并行冲突，严格遵守）

| 子代理 | 可改文件 | 禁止触碰 |
|---|---|---|
| 数据 D | `ios/tools/gen_content.py`、`ios/tools/validate.py`、`ios/tools/gen_preview_data.py`（仅加 KEYMAP）、生成的 `Resources/*.json` | 任何 `.swift`、`index.html` |
| Swift S | `ios/AdventureIsland/*.swift`（含新建）、`ios/AdventureIsland/Resources`（只读，不改） | gen_content.py、index.html |
| HTML H | `ios/preview/index.html`（含 EMOJI 行加键、保留 `/* DATA-BEGIN/END */` 标记完整） | gen_content.py、任何 .swift、Resources JSON |
| 资产 A | `design/tools/gen-assets.mjs`、`design/assets/**`、同步 xcassets（用 sync_assets.py）、`Common.swift` 的 IconEmoji | gen_content.py、题型逻辑、index.html |

新图标 emoji 兜底：A 负责 `Common.swift` IconEmoji；H 负责 `index.html` EMOJI（各自加键，emoji 可自定，不必逐字相同）。

注意：数据 D 生成 JSON 后**不要**跑 `gen_preview_data.py`（它会改 index.html，与 H 冲突）。数据注入由集成阶段统一跑。

## 1. 目标关卡数（regular 关 + 自动 review/boss）

regular 关沿用现有结构：**cn 用 board 棋盘关；math/pinyin/english/astro/geo 用 linear 线性关**（与现状一致，不把 math 改成棋盘）。
每个关卡学科在 regular 之后由 `add_review_levels`（2 个 review，board 关）+ `add_boss_level`（1 个 boss）自动追加。

| 学科 | regular 关数 | JSON 总关数（含 2 review + 1 boss） |
|---|---|---|
| cn | 30 | 33 |
| math | 34 | 37 |
| pinyin | 16 | 19 |
| english | 24 | 27 |
| astro | 16 | 19 |
| geo（新） | 12 | 15 |

- cn：30 个识字关（`cn-0`..`cn-29`），每关含 teach + 若干问题 + 1 个 write 关，board 棋盘。删除现有 `cn-14`「第15关复习挑战」（其内容被新关吸收，净增 15 关）。
- math：在现有 15 关基础上按决策 9 新增 19 关（34 总），线性。
- pinyin：现有 12 + 新增 4（四声/复韵母/前鼻/拼读大挑战）= 16。
- english：现有 12 + 新增 12 主题词场 = 24。
- astro：现有 10 + 新增 6 = 16。
- geo：中国章 6 + 世界章 6 = 12。

## 2. 通用交互行为（所有新题型必须满足）

- 答对：播放庆祝（confetti + 音效 + praise 文案），自动推进（linear 进下一步 / board 回棋盘 / 最后一步进结算）。
- 答错：轻提示（抖动/弹回 + 鼓励文案），**不扣分、不惩罚、可立即重答**（防挫败铁律）。
- 静音可完整玩：所有信息有视觉等价，不依赖声音。
- 判题逻辑在 step 数据字段中给出明确答案，渲染器只做比较。

## 3. 新题型字段定义（7 个新 kind）

### 3.1 write（写字引擎）

- 田字格坐标统一 `viewBox="0 0 100 100"`，田字格：外框 8..92、十字中线 50。
- 每笔一条 SVG path（`d`）与起点（`start`）。

```json
{
  "id": "cn-0-wr",
  "kind": "write",
  "char": "一",
  "pinyin": "yī",
  "strokes": [
    {"d": "M22 50 L78 50", "start": {"x": 22, "y": 50}}
  ],
  "question": "写一写：看一笔、描一笔，写「一」",
  "praise": "写得真好，汉字卡到手！"
}
```

渲染器行为：
1. 进入当前笔：演示动画（HTML 用 stroke-dasharray/dashoffset 逐笔生长；Swift 用 Shape trim 或重复描），可重播。
2. 手指沿该笔轨迹描写：采样 path，手指位置与轨迹距离超过容差（约 12 单位）→ 该笔轻推重来（无负面文案）。
3. 写对该笔 → 逐笔点亮（变色/发光）。
4. 全部笔画写完 → 整字完成：**subject=="cn" 时调用 `store.learnHanzi(char)`（写完才入册）**；subject=="pinyin" 描红字母不入汉字册。
5. 自动推进。

数据 D 注意：
- 30 个汉字每关都要给完整 strokes（标准笔顺）。pinyin 拼读关的字母描红（b/a/m/o）复用 write，char 字段放字母。
- 移除 `LevelView.onAppear` 里 cn 基于 teach 的 `learnHanzi`（改由 write 完成时调用），保证「写完才入册」。
- 示例笔画（100 坐标）：
  - 二：`M28 38 L72 38`、`M22 62 L78 62`
  - 三：`M30 32 L70 32`、`M26 50 L74 50`、`M22 68 L78 68`
  - 十：`M24 50 L76 50`、`M50 24 L50 76`
  - 人：`M50 26 Q40 52 30 74`、`M50 40 Q60 58 72 74`
  - 大：`M26 40 L74 40`、`M50 24 Q44 50 34 76`、`M50 46 Q60 62 72 76`
  - 小：竖钩 `M50 26 L50 66 Q48 72 42 70`、左点 `M40 44 Q32 52 30 60`、右点 `M60 44 Q68 52 70 60`
  - 上：`M50 22 L50 38`、`M34 38 L66 38`、`M24 62 L76 62`
  - 下：`M26 40 L74 40`、`M50 26 L50 72`、`M62 48 Q70 52 72 60`
  - 其余字（星/手/14 旧字）按标准笔顺补齐，每笔都要有 d 与 start。

### 3.2 muldiv（乘除）

```json
{
  "id": "math-mul-1",
  "kind": "muldiv",
  "op": "×",
  "mode": "groups",
  "groups": 3,
  "per": 2,
  "icon": "train",
  "unit": "辆",
  "options": [5, 6, 8],
  "answer": 1,
  "question": "3 组小车，每组 2 辆，一共几辆？",
  "hint": "几个几：3 个 2，连加 2+2+2",
  "praise": "乘法小能手：3×2=6！"
}
```

字段规则：
- 乘法 `op:"×"`，`mode:"groups"`：必有 `groups`、`per`，答案 = groups×per。
- 除法平均分 `op:"÷"`，`mode:"average"`：必有 `total`、`groups`，答案 = total/groups（每人几个）。
- 除法包含除 `op:"÷"`，`mode:"contain"`：必有 `total`、`per`，答案 = total/per（能分几组）。
- 除法全部整除。`options` 为 3 个数字，`answer` 为正确项下标。

渲染器可视化：
- 乘法：groups 行/组，每组 per 个 icon。
- 平均分：groups 个盘子，把 total 个 icon 平均分到各盘。
- 包含除：每盘 per 个，共 total/per 盘。

### 3.3 cards（扑克算术）

```json
{
  "id": "math-cards-1",
  "kind": "cards",
  "mode": "make10",
  "target": 10,
  "pick": 2,
  "cards": [3, 7, 2, 8, 5, 1],
  "question": "凑十大战：点 2 张牌，恰好凑成 10",
  "praise": "凑十成功！"
}
```

- `mode:"make10"`：pick=2，所选两牌之和==target。
- `mode:"target"`：pick=3，`target` 12/15，三张牌经加减（可加可减）凑出 target。
- 渲染器画扑克牌（圆角牌面 + 数字 + 花色 ♠♥♦♣，程序化绘制，复用 memory 扑克风）；点选高亮，达到 pick 张判题；错误则取消选择、不扣分。
- 数据保证：至少存在一组合法解。

### 3.4 sudoku（数独）

```json
{
  "id": "math-sudoku-1",
  "kind": "sudoku",
  "size": 4,
  "symbols": ["duck", "apple", "star", "moon"],
  "givens": [
    {"r": 0, "c": 0, "v": 0},
    {"r": 0, "c": 2, "v": 2},
    {"r": 1, "c": 1, "v": 3},
    {"r": 3, "c": 3, "v": 1}
  ],
  "solution": [[0,1,2,3],[2,3,1,0],[1,0,3,2],[3,2,0,1]],
  "question": "图案数独：每行、每列、每个 2×2 宫图标不重复",
  "praise": "数独侦探，推理成功！"
}
```

- 4×4 盘，`symbols` 4 个图标；`givens` 给定格（v 为 symbols 下标），数量 4-8；`solution` 为完整解（行列宫不重复、唯一解）。
- 渲染器：givens 固定显示；点空格弹 4 选盘，填入；与行/列/宫冲突则图标弹回（不扣分）；填满且==solution 即完成。
- 数据 D 用内置求解器保证唯一解（写在 gen_content.py 或校验中）。

### 3.5 clock（钟表）

```json
{
  "id": "math-clock-1",
  "kind": "clock",
  "mode": "read",
  "hour": 3,
  "minute": 0,
  "options": ["3:00", "4:00", "2:00"],
  "answer": 0,
  "question": "看钟面：现在是几点？",
  "praise": "认时小达人！"
}
```

- `mode:"read"`：钟面 SVG（1-12 数字 + 时针短、分针长），按 hour/minute 摆针，3 个文字选项。
- `mode:"set"`：给定目标 hour/minute（minute 仅 0 或 30），玩家拨针（拖拽时针/分针，按角度量化；拖拽不稳时提供点按数字设时针、整点/半点切换），确认后判定。
- 整点/半点：hour 1-12，minute∈{0,30}。

### 3.6 money（人民币）

金额单位统一为「角」整数（避免小数）：1角=1，5角=5，1元=10，5元=50，10元=100。

```json
{
  "id": "math-money-1",
  "kind": "money",
  "price": 60,
  "denominations": [
    {"value": 1, "label": "1角", "icon": "m-jiao1"},
    {"value": 5, "label": "5角", "icon": "m-jiao5"},
    {"value": 10, "label": "1元", "icon": "m-yuan1"},
    {"value": 50, "label": "5元", "icon": "m-yuan5"},
    {"value": 100, "label": "10元", "icon": "m-yuan10"}
  ],
  "question": "买东西：点钱币，恰好付清 6 元",
  "praise": "付钱小能手，正好付清！"
}
```

- 渲染器：显示标价（角→元角换算显示）；点币加入付款（同币可多点），实时合计；可点已选币移除；「确认」时合计==price 即成功，多付提示不判错。
- 练习币视觉用人民币红/绿配色，**与金币明显区分**。
- 数据保证：存在恰好付清的组合。

### 3.7 mappuzzle（地理拼图）

坐标 `viewBox="0 0 100 60"`。每个 region 用绝对坐标 polygon（即拼对时所在位置），渲染器据此算目标质心。

```json
{
  "id": "geo-world-puzzle",
  "kind": "mappuzzle",
  "map": "world",
  "regions": [
    {"id": "northamerica", "label": "北美洲", "color": "#F4A259", "points": [[10,14],[30,12],[34,30],[24,40],[12,34]]},
    {"id": "southamerica", "label": "南美洲", "color": "#E07A5F", "points": [[24,42],[34,40],[34,56],[26,58],[22,48]]},
    {"id": "europe", "label": "欧洲", "color": "#9B8CE8", "points": [[44,16],[54,14],[56,26],[46,28]]},
    {"id": "africa", "label": "非洲", "color": "#F2C14E", "points": [[46,28],[58,28],[60,50],[50,56],[44,44]]},
    {"id": "asia", "label": "亚洲", "color": "#8AB8E8", "points": [[56,12],[84,14],[86,38],[66,40],[56,28]]},
    {"id": "oceania", "label": "大洋洲", "color": "#7FC6A4", "points": [[76,46],[90,44],[92,54],[80,56]]},
    {"id": "antarctica", "label": "南极洲", "color": "#B8D4E8", "points": [[30,56],[70,56],[72,60],[30,60]]}
  ],
  "question": "拼一拼：把大洲块拖回世界地图轮廓",
  "praise": "七大洲拼好啦，地球在你手里！"
}
```

- 渲染器：地图区显示各 region 的虚线轮廓（ghost，在绝对位置）；未拼的块放底部托盘（同 polygon 平移）；拖块跟随手指，松手时若该块质心接近其目标质心（容差约 8 单位）→ 吸附归位并锁定；全部归位即完成，**调用 `learnGeo(id)` 把该 puzzle 涉及的地区加入 learnedGeo**。
- 中国 puzzle：把雄鸡切成约 6 个几何块（不对应省份），同 schema。
- 数据保证：块 id 唯一、块数与轮廓区域数一致。

## 4. 地理新学科（geo）接入清单

- Swift：
  - `Theme.swift`：AppTheme 加 `case geo`，并给 sky/panelStroke/titleStroke 配色（地球蓝绿，如 sky `#6FD0A8→#A8E5C8` 或独立大地色系）；`SubjectConfig.map` 加 `"geo": SubjectConfig(file:"geo_levels", title:"环球号", guide:"panda", theme:.geo)`。
  - `MapView.swift`：zones 加 geo 水管（用现有 pipe 颜色，如 pipe-green 已用，可用新色或复用；label 环球号，subject geo），pipesRow 布局能容纳 7 根（缩小间距/换行，保证不溢出）。
  - 路由：`Route` 已有 `.level(subject:index:)`，geo 复用，无需新 case。
- HTML：
  - `SUBJECTS` 加 `geo:{title:"环球号",pipe:...,guide:"panda",theme:"theme-geo",meta:"中国 · 世界"}`；加对应 CSS theme；ZONES 加 geo。
- 数据：
  - `gen_content.py` 生成 `geo_levels.json`（结构与其他 SubjectFile 同：subject/title/guide/levels），跑 add_review_levels/add_boss_level。
  - `gen_preview_data.py` KEYMAP 加 `"geo_levels":"geo"`。
  - `ProgressSnapshot` 加 `learnedGeo:[String]`（decodeIfPresent 默认空，旧快照兼容）；Store 加 `learnGeo`。HTML state S 加 `learnedGeo:[]`。
- 每关结构：学一学（letter/teach 地标风物卡）+ 1-3 题（quiz/listen/memory/pattern/mappuzzle）。地标风物优先，不背 34 省。

## 5. 收集册与徽章（工单 13）

- 分组 7→8，顺序：`["science","sticker","hanzi","pinyin","english","astro","geo","badge"]`（geo 插在 badge 前）。
- 各组扩容：
  - hanzi：14→30（与字表一致，写完才亮）。
  - pinyin：补四声符号（ā á ǎ à）、复韵母 ai ei ui、前鼻韵母 an en in 等卡。
  - english：12→约 60（与主题词表一致）。
  - astro：10→16（与天文关一致）。
  - science：**保持现状**（工单 12 不做，不扩实验）。
  - geo：新建，每关 1-2 张地标/风物卡（约 15-20 张）。
- 新徽章（加入 badge 组，沿用现有徽章默认常显模式）：
  - `bg-writer` 小小书法家（写完 10 字）
  - `bg-mul` 乘法小达人
  - `bg-sudoku` 数独侦探
  - `bg-geo` 环球旅行家（geo 通关）
  - `bg-words50` 单词大富豪（约 50 词）
  - 徽章图标新增（见资产清单）。
- Swift CollectionView 与 HTML renderCollection 加 geo 组的标题/进度/解锁规则（geo 用 learnedGeo 判断）。

## 6. DEBUG 作弊参数（对齐现有 -AIStep/-AIFlip）

- Swift（仅 DEBUG）：
  - 现有 `-AIStep N`：linear 推进 N 步。
  - 新交互题（write/sudoku/clock-set/money/mappuzzle/cards）：在 DEBUG 下提供自动完成——可在视图内加一个 DEBUG 小按钮（如「自动完成」，仅 #if DEBUG 显示），或扩展 `-AIStep` 使其对交互题直接置为完成态。
- HTML：
  - 支持 URL query（如 `?AISolve=1`）设全局 `S.autoSolve=true`；交互题在 onAppear 时若 autoSolve 则自动填对/自动完成。
  - 现有机制若有 URL 解析则复用，没有则加一个最小解析。

## 7. 资产清单（新增图标，全部原创同风格，走 gen-assets.mjs）

- 天文：8 大行星（mercury/venus/earth/mars/jupiter/saturn/uranus/neptune，可复用 earth）、月相（newmoon/waxing/fullmoon 等约 4-5）、银河 milkyway、宇航服 astronaut、空间站 station、黑洞 blackhole、恒星（可复用 sun）。
- 数学：人民币 5 个（m-jiao1/m-jiao5/m-yuan1/m-yuan5/m-yuan10）、几何图形（triangle/pentagon 等，square/circle 可复用）、扑克牌（可程序化，无需图标）。
- 地理：中国/世界地图简化底图（china-map/world-map，可选）、长城 greatwall、天安门 tiananmen、珠峰 everest、长江黄河 river、狮子 lion、大象 elephant、袋鼠 kangaroo、企鹅（可复用 penguin）、北极熊 polarbear、自由女神 libertystatue、风车 windmill、城堡（可复用 castle）。
- 英语主题词：约 30 个缺口（dog/cat/fish/bread/milk/... 各主题），优先复用现有图标。
- 徽章：writer/mul/sudoku/geo/words50 图标。
- 每个新图标：gen-assets.mjs 加 `S.xxx` → 跑 node 生成 → `python3 ios/tools/sync_assets.py` 同步 xcassets + 夹具 → `Common.swift` IconEmoji 加 emoji 兜底 → `index.html` EMOJI 加同一 emoji。

## 8. 流水线与验证（集成阶段统一执行）

1. `python3 ios/tools/gen_content.py` 生成全部 JSON（含 geo_levels）。
2. `python3 ios/tools/validate.py` 静态校验（更新 SUBJECTS 计数为 33/37/19/27/19/15、新题型规则、8 分组顺序）。
3. `cd ios && xcodegen generate`（注册新 .swift）→ `xcodebuild ... build` 通过。
4. `python3 ios/tools/gen_preview_data.py` 注入 index.html（在 H 完成后）。
5. 机器比对：提取 index.html `/* DATA-BEGIN */` 段 json.loads，与各 Resources JSON 完全一致。
6. 截图抽查：商店/衣橱、新题型、地理、天文，无布局溢出。
7. 更新「探险岛-HTML离线包.zip」（单文件 index.html，保持包内 /探险岛/ 结构与命名）。
