# 调研：游戏 UI 美化相关 Skill 与 MCP

日期：2026-10-15。数据全部来自 GitHub API 一手实测（`gh api` / REST search & repos 端点，star 数与最近推送日期均为**当日实测值**，会随时间变化）。本文件只做调研记录，不改任何代码。

> **被评估对象**：本仓 HTML 端 UI——单文件 `ios/preview/index.html`（实测 4187 行），
> DOM + CSS 动画 + 内联 SVG/Emoji 图标，无游戏引擎，跑 iPad Safari。
> 美化目标：棋盘主页、星区选关、关卡内题型界面、学一学动画舞台的**视觉品质**
>（配色 / 图标 / 插画 / 布局 / 动效），不是做新游戏。
> 仓库约束（AGENTS.md）：只动 HTML 侧；AI Agent 用 SKILL.md 技能 + 可配 MCP server；
> 内容唯一源在 `ios/tools/gen_content.py`，双闸门 + sweep 必须保绿。

---

## 一、TL;DR 推荐榜

| 名次 | 项目 | 实测 star（2026-10-15） | 一句话理由 |
|---|---|---|---|
| 🥇 1 | **anthropics/skills**（重点用其中 frontend-design / webapp-testing / theme-factory 三个子 skill） | 181,187 | 官方 skill 库、SKILL.md 形式与本仓工作方式完全对齐；零 API key 零付费；frontend-design 管「怎么做不像模板的视觉决策」，webapp-testing 管「截图看效果」的视觉闭环，正好补上本仓只有静态 sweep、没有「眼睛」的缺口 |
| 🥈 2 | **microsoft/playwright-mcp** | 38,154 | 微软官方 Playwright MCP：让 Agent 打开 index.html 逐屏截图、读 console、点交互——「改 CSS → 截图对比 → 再改」的迭代闭环缺它不行；npx 一行接入，无 API key |
| 🥉 3 | **ConardLi/garden-skills**（取其 web-design-engineer 子 skill） | 12,902 | 中文、纯 HTML/CSS/JS 输出、理念「bar is stunning, not functional」，含 design critique 工作流；可先让它对探险岛四个界面出一轮评审 + 改造方案，再人工挑着落地 |

**不推荐追的反例**：CoplayDev/unity-mcp（14,955 star）与 Coding-Solo/godot-mcp（6,090 star）——都是游戏引擎编辑器的桥，本仓无引擎可挂，AGENTS.md 也明确不新增 Swift/引擎，装了没有操作对象。详见第四节。

---

## 二、候选对比表（star 数均为 2026-10-15 GitHub API 实测）

### A. Skill / 技能库类

| 项目 | star | 最近推送 | 能力一句话 | 适配度 | 接入成本 | 风险 |
|---|---|---|---|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 181,187 | 2026-10-09 | 官方 Agent Skills 库，含 frontend-design / canvas-design / theme-factory / web-artifacts-builder / webapp-testing / brand-guidelines 等 19 个 | **高** | 零 key 零付费；webapp-testing 需 `pip install playwright` | 极低（官方持续维护） |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 8,509 | 2026-08-17 | Google Stitch（AI UI 设计生成）配套 skills，按 Agent Skills 标准写 | 中 | 需另配 Stitch MCP server + Google 账号 | 中（绑定 Google 服务可用性） |
| [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 12,902 | 2026-10-11 | 中文技能合集：web-design-engineer / motion-showreel / gpt-image-2 / beautiful-article | **中高** | 零 key；拷单个 skill 目录即用 | 低-中（个人维护，活跃） |
| [xiaopu-ai/web-design](https://github.com/xiaopu-ai/web-design) | 787 | 2026-06-24 | 中文 web 视觉设计 SKILL：先出 DESIGN.md 规范、确认后再生码 | 中 | 零 key | 中（低频更新，2026-06 后未推） |
| [AThevon/genjutsu](https://github.com/AThevon/genjutsu) | 486 | 2026-10-05 | 动效 / 微交互向 creative-coding skills | 中 | 零 key | 中 |
| [yzfly/awesome-design-html](https://github.com/yzfly/awesome-design-html) | 161 | 2026-06-14 | 115 套品牌化 HTML 设计模板作 skill（93 web + 22 iOS） | 低-中 | 零 key | 中 |
| [Gamezxz/pixel-art-studio](https://github.com/Gamezxz/pixel-art-studio) | 83 | 2026-07-11 | Claude 直接用 Python/Pillow 逐像素作画、自渲染自批评的 skill | 低 | 零 key 零依赖 | 中 |
| [scenario-labs/skills](https://github.com/scenario-labs/skills) | 1,005 | 2026-10-14 | 游戏资产（贴图/精灵/3D/视频）生成 skills，走 Scenario SaaS | 低 | 需 Scenario MCP + **付费 SaaS** | 中-高（平台绑定+费用） |

### B. MCP server 类

| 项目 | star | 最近推送 | 能力一句话 | 适配度 | 接入成本 | 风险 |
|---|---|---|---|---|---|---|
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | 38,154 | 2026-10-08 | 官方 Playwright MCP：截图 / 点击 / 读 console / 无头浏览 | **高** | `npx @playwright/mcp@latest`，无 key | 极低 |
| [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP)（Framelink；旧地址 framelink/figma-developer-mcp 已 404） | 15,988 | 2026-10-14 | 把 Figma 设计稿的布局/样式数据喂给编码 Agent | 中（**前提是得先有 Figma 稿**） | 需 Figma 个人 access token（免费档可用） | 低 |
| [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp) | 7,054 | 2026-07-26 | 双向读写操作 Figma 画布 | 低-中 | 需 Figma + WebSocket 桥 | 中 |
| [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp)（已并入 21st MCP） | 6,021 | 2026-09-09 | 检索/生成 21st.dev 组件库（**React/Tailwind**） | 低 | 需 21st.dev API key（旧 key 已全部作废重发） | 中（组件生态与 vanilla HTML 不匹配） |
| [Manavarya09/design-extract](https://github.com/Manavarya09/design-extract) | 4,237 | 2026-10-08 | 一条命令抽取任意网站的设计系统（DTCG tokens） | 中 | 零 key | 中（账号历史短，热度型仓库待观察） |
| [Jpisnice/shadcn-ui-mcp-server](https://github.com/Jpisnice/shadcn-ui-mcp-server) | 3,052 | 2026-10-03 | shadcn/ui 组件查询（React 向） | 低 | 零 key | 低 |
| [zhongweili/nanobanana-mcp-server](https://github.com/zhongweili/nanobanana-mcp-server) | 400 | 2026-10-07 | Gemini 图像生成 MCP（可产图标/插画位图） | 中-低 | 需 Gemini API key（有免费层） | 中 |
| [awkoy/replicate-flux-mcp](https://github.com/awkoy/replicate-flux-mcp) | 105 | 2026-10-01 | Replicate Flux 生图 / 生 SVG | 中-低 | 需 Replicate key（**按量付费**） | 中 |
| EverArt 系（[nickbaumann98/everart-forge-mcp](https://github.com/nickbaumann98/everart-forge-mcp) 等） | 10 | 2025-03-02 | EverArt 图像生成 MCP | 低 | 需 EverArt key | **高（一年多未更新，事实弃维护）** |
| [willibrandon/pixel-plugin](https://github.com/willibrandon/pixel-plugin) | 363 | 2025-10-19 | Claude Code 像素画插件，驱动 Aseprite | 低 | 需本机装 Aseprite（付费软件） | 中 |

### C. Awesome 入口（检索用，不直接接入）

| 列表 | star | 最近推送 | 用途 |
|---|---|---|---|
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 96,349 | 2026-10-09 | MCP 总目录 |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | 77,129 | 2026-09-18 | skills 总目录 |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | 55,707 | 2026-10-15 | Claude Code 生态资源 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 35,728 | 2026-10-13 | 1000+ 跨工具 skills 目录 |
| [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | 15,407 | 2026-04-28 | skills 目录（更新较慢） |

---

## 三、逐项详评（前 3 名 + 反例）

### 1. anthropics/skills —— 🥇 首选，三件套组合拳

- **一手来源**：<https://github.com/anthropics/skills>（API 实测 181,187 star，pushed 2026-10-09，active）
- **能力**：官方 Agent Skills 库。已逐目录核实（`skills/` 下 19 个），与本场景直接相关的四个：
  - `frontend-design`：SKILL.md 全文读过——定位是「做有辨识度、不落模板默认脸的视觉设计」：要求从题材本身（儿童教育玩具 vs 金融仪表盘美感完全不同）推导配色/字体/布局，明确列了「生成感网页的常见坏味道」清单（标题里单独高亮一个词、无意义全大写 label、装饰性 01/02 编号等）。这正是「美化探险岛而不把它改成通用 SaaS 脸」需要的那类指导。
  - `webapp-testing`：基于 Python Playwright 测本地 web 应用，含截图、console 读取、`with_server.py` 生命周期管理脚本。对静态 HTML（本仓就是）直接读选择器写脚本即可。
  - `theme-factory`：10 套预设「色板+字体对」主题，可整套套到 HTML 产物上，也可现场生成新主题——适合先给棋盘主页试 2-3 套儿童向主题色。
  - `canvas-design` / `brand-guidelines` / `algorithmic-art`：视觉方向备查。
- **适配度：高**。理由：① 本仓规则就是「AI Agent 用 SKILL.md 形式的技能」，格式天然兼容；② 美化只落在 HTML/CSS，这些 skill 全部面向 HTML/web 产物，零概念移植；③ 免费、离线、无外部服务，不碰数据管线和 Swift 红线。
- **接入成本**：拷贝 skill 目录即用；`webapp-testing` 需本机 `pip install playwright && playwright install chromium`（一次性）。
- **风险**：极低。官方仓库、高频维护。License 见仓库内各 skill 的 LICENSE.txt。

### 2. microsoft/playwright-mcp —— 🥈 视觉迭代闭环的「眼睛」

- **一手来源**：<https://github.com/microsoft/playwright-mcp>（API 实测 38,154 star，pushed 2026-10-08，active）
- **能力**：微软官方 Playwright MCP server。给 Agent 结构化的浏览器操作工具：打开页面、截图、点击、填表、读 console 与网络日志、无头运行。
- **适配度：高**。理由：本仓现状是 `preview_sweep.py` 做**静态**渲染质检（弹回/越界/长文字/缺图四类全 0），但「好不好看」没有任何反馈通道——Agent 改 CSS 是盲改。有了截图工具就能跑「改 → 截图 → 看图评审 → 再改」的真闭环，而且 iPad Safari 的目标 viewport 可以用 Playwright 的 viewport 模拟近似（如 1024×768 / 1180×820）。index.html 是自包含单文件，`file://` 直开即可测。
- **接入成本**：MCP 配置加一条 `npx @playwright/mcp@latest`；无 API key、无付费。与推荐 1 的 `webapp-testing` 二选一即可起步（skill 形式更轻，MCP 形式更顺手，可先 skill 后 MCP）。
- **风险**：极低。微软官方、持续活跃。注意模拟 Safari 与真机 Safari 仍有渲染差异，终验还是要 iPad 过一遍。

### 3. ConardLi/garden-skills（web-design-engineer 子 skill）—— 🥉 中文的高标准评审员

- **一手来源**：<https://github.com/ConardLi/garden-skills>（API 实测 12,902 star，pushed 2026-10-11，active；`skills/` 下已核实含 web-design-engineer / motion-showreel / gpt-image-2 / beautiful-article 等 6 个）
- **能力**：`web-design-engineer` 的 SKILL.md 已全文读过：定位「视觉前端交付物（页面/仪表盘/原型/动画/UI mockup/设计系统）的构建与重设计 + 浏览器验收评审」，核心理念原话是 **"The bar is 'stunning,' not 'functional.'"**，输出介质就是 HTML/CSS/JS，自带 design critique 工作流。
- **适配度：中高**。理由：中文（对本仓中文文档习惯友好）、纯 web 输出、critique 工作流适合先做「体检报告」再挑着落地；`motion-showreel` 与学一学动画舞台的 CSS 动效打磨也对口。作为个人仓库，长期维护确定性弱于官方库，但单个 skill 目录可独立拷贝、无锁定。
- **接入成本**：零 key；拷 `skills/web-design-engineer` 单目录即用。备选同路线：xiaopu-ai/web-design（787 star，中文，先出 DESIGN.md 规范再改码的两阶段流，但 2026-06 后未推送）。
- **风险**：低-中（个人维护；缓解：只用其 skill 文本，不依赖其任何运行时）。

### 反例：为什么不推荐追 Unity / Godot / 游戏资产类 MCP

- [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp)（14,955 star）、[Coding-Solo/godot-mcp](https://github.com/Coding-Solo/godot-mcp)（6,090 star）、[IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP)（4,459 star）：都是「AI ↔ 游戏引擎编辑器」的桥，前提是项目活在 Unity/Godot 里。探险岛是零依赖 DOM+CSS 单文件，AGENTS.md 明确不新增 Swift 更不会引入引擎——这些 MCP 装上后**没有任何可操作对象**，star 再高也与本仓无关。
- [scenario-labs/skills](https://github.com/scenario-labs/skills)（1,005 star）：产出贴图/精灵/3D 资产，需接 Scenario 付费 SaaS；与探险岛 Emoji+内联 SVG 的轻量风格、离线包体积敏感（zip 已 9.1MB）都冲突。
- 像素画类（Gamezxz/pixel-art-studio 83、willibrandon/pixel-plugin 363）：风格（像素）与受众（低幼儿童需要圆润明快）不符，且多数要求本机 Aseprite。

### 图像生成类 MCP 的定位（中-低，二期可选）

nanobanana-mcp-server（Gemini 生图，400 star，需 Gemini key）/ replicate-flux-mcp（105 star，按量付费）：理论上可为关卡生成定制插画，替换部分 Emoji 图标。但① 位图会显著膨胀离线包；② 多关之间风格一致性难保证（儿童产品对形象一致性敏感）；③ 现有内联 SVG 图标管线（`sync_assets.py` + manifest + Emoji 兜底）刚理顺。建议只在某一两个「门面」位置（如主页横幅）试点，不作为首选投入。

---

## 四、接入建议（哪个先试、怎么接）

**顺序：先 1 后 2，3 按需。** 全程不碰 Swift、不碰数据管线（若只改 CSS/布局不动 DATA 段，双闸门照跑即可）。

**第一步（半天内见效）：装 anthropics/skills 三件套**

```bash
# 方式：sparse-checkout 只取需要的 skill 目录
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/anthropics/skills /tmp/anthropic-skills
cd /tmp/anthropic-skills && git sparse-checkout init --no-cone \
  && git sparse-checkout set "skills/frontend-design" "skills/theme-factory" "skills/webapp-testing" \
  && git checkout
# 拷到 Agent 技能目录（ZCode 个人技能目录 ~/.zcode/skills/，或项目级 .zcode/skills/）
```

**第二步：跑一轮「截图 → critique → 只改 CSS」的最小闭环**

1. 用 `webapp-testing`（或直接 playwright-mcp）以 iPad 尺寸 viewport 打开 `ios/preview/index.html`，对**棋盘主页、星区选关、任一题型关、任一学一学动画**各截一张现状图；
2. 让 Agent 按 `frontend-design` 的清单（或 garden-skills 的 critique 流）出书面评审：配色、字号阶梯、间距节奏、圆角/阴影一致性、动效节奏，**只输出问题清单不动手**；
3. 第一轮只改 CSS 变量层（色板、圆角、阴影、间距）与最多 2-3 处布局——index.html 视觉几乎全由 CSS 承担，改动面可控；
4. 复跑闸门与质检：`python3 ios/tools/validate.py` → `audit_preview.py` → `preview_sweep.py`，iPad Safari 真机过一遍；
5. 满意后按收尾口径重打离线包并逐字节核对，更新工作进展文档。

**第三步（可选）**：对第 2 步的评审结果不满意，再引入 garden-skills/web-design-engineer 做第二轮深度 critique；想试主题先让 theme-factory 出 2-3 套儿童向色板对比。

---

## 五、检索方法附注（复现用）

- 时间：2026-10-15；工具：`gh api`（已认证，限额远高于匿名 curl 的 60 次/小时）。
- 仓库元数据：`gh api repos/<owner>/<repo> --jq '[.full_name,.stargazers_count,.pushed_at,.archived]'`。
- 搜索（各取 star 序前 5-6 名）：`gh api "search/repositories?q=<query>&sort=stars&per_page=6"`。
  实际使用的检索词：`mcp figma`、`mcp ui component`、`mcp design`、`mcp game`、`mcp image generation`、`mcp sprite`、`mcp pixel art`、`mcp godot`、`mcp unity`、`awesome claude skills`、`mcp svg`、`everart mcp`、`replicate mcp`、`mcp screenshot ui`、`claude skill web design`。
- 内容核实：SKILL.md / README 一律走 `gh api repos/<owner>/<repo>/contents/<path>` 或 `/readme`（raw.githubusercontent 在本环境拿不到内容，故未用）。
- 关键发现：任务给定的已知地址 `framelink/figma-developer-mcp` 经 API 实测为 **404**（2026-10-15），Framelink Figma MCP 现落在 `GLips/Figma-Context-MCP`（README 自证「Framelink MCP for Figma」、npm 包名仍为 `figma-developer-mcp`）；`21st-dev/magic-mcp` README 自证已并入统一的「21st MCP」且旧 API key 全部作废。
- 局限：star 数是热度不是质量；搜索按相关度+star 排序，可能漏掉 star 低但更贴合的小项目；未实测任何 MCP 的运行效果（本仓未安装），适配度判断基于 README/SKILL.md 文本与仓库现状比对。
