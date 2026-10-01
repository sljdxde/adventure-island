# 探险岛 · 幼小衔接 iPad App

面向自家 3-6 岁孩子的幼小衔接 App，**仅个人使用、不上架**。马里奥风迷你棋盘玩法：掷骰走格、答题冒险、金币商店、通关仪式。

> **⚠️ 当前实施口径（ADR-0003，2026-09-30 起）**：Swift 原生端**冻结中**。唯一实现与验收载体是浏览器模拟器 `preview/index.html`（由内容生成器注入数据），新功能与修复只落模拟器端；`AdventureIsland/` 下的 Swift 代码会逐渐落后于模拟器行为，追平前不要把它当作现状参照。解除冻结时应按最新 `docs/specs/` + 模拟器实际行为重建，而非在旧 Swift 上增量修改。

- 学科（6 水管）：识字村 18 关 · 思维镇 18 关 · 拼音谷 15 关 · 英语王国 15 关 · 天文台 13 关（每学科 = 普通关 + 2 复习关 + 1 boss 关）· 科学岛（浮沉实验，自由重玩）
- 迷你棋盘（v0.8）：每关 8-10 格，掷骰前进，途经题目格逐格必答；金币格 +5 / 宝箱 3-8 / 幸运蘑菇（挡一次答错）/ 休息站；走到城堡结算（旗杆 → 金币雨 → 星星点亮）
- 金币经济：答对 +2、3 星通关 +5、boss +15，金币只经账本变动；商店卖角色与称号（买不到任何学习内容），衣橱切换
- 题型（14 种步骤 kind）：`teach` 认一认 · `letter` 学一学 · `listen` 找一找 · `quiz` 练一练 · `count` 点数 · `compare` 比多少 · `arith` 加减 · `pattern` 找规律 · `split` 分一分 · `order` 排一排 · `neighbor` 填一填 · `blend` 拼读 · `memory` 翻翻牌 · `dice` 掷骰数点
- 飞机模式友好：所有题型纯视觉作答，朗读全部为手动可选；静音也能完整游玩
- 家长中心：算术家长门 / 护眼时长（单次+每日，结算断点不打断一局）/ 金币收支只读统计 / 进度 / 重置
- 数据全部存本机，无网络、无广告、无内购

---

## 目录结构

```
ios/
├─ project.yml                    # XcodeGen 工程定义（Swift 冻结中，见 ADR-0003）
├─ AdventureIsland/               # App 源码（SwiftUI + SpriteKit，冻结中）
│  ├─ AdventureIsland 入口/主题/通用组件/模型/存储/服务
│  ├─ RootView / MapView / LevelView / LabView / CollectionView / ParentView
│  ├─ Resources/*.json            # 关卡/收集/实验/商店内容（加内容=改生成器重跑）
│  └─ Assets.xcassets/            # 94 个 SVG 图标（含矢量保留，可直接替换高清图）
├─ Tests/AdventureIslandTests/    # XCTest 测试套件（冻结中，现状红，见下）
├─ preview/index.html             # ★ 浏览器模拟器——唯一实现与验收载体
└─ tools/
   ├─ validate.py                 # 本机静态验证（内容规则/商店闸门/资产一致性/兼容性）
   ├─ gen_content.py              # 内容生成器：改完重跑 → Resources/*.json
   └─ gen_preview_data.py         # 把 Resources JSON 注入模拟器（改内容后必跑）
```

源码文件说明见 `docs/开发与测试记录.md`。

---

## 改内容 / 日常验证（不碰 Swift）

```bash
# 1. 编辑 tools/gen_content.py（Python 数据表，注释齐全）
python tools/gen_content.py         # 2. 生成 Resources/*.json
python tools/gen_preview_data.py    # 3. 注入模拟器（改内容后必跑）
python tools/validate.py            # 4. 本机静态验证（答案/棋盘结构/商店/图标）
```

`validate.py` 当前覆盖：关卡数与 id 全局唯一、棋盘格数与题目占比 ≥60%、题目格引用存在且不重复、金币格 1-2（决策 2）、每关题库 ≥5 道变体（修订）、boss 关 8 题全题目、商店 id 唯一与定价区间（决策 14）、JSON↔资产清单↔xcassets 一致、Emoji 兜底全覆盖、iOS 16 兼容性扫描、project.yml 关键配置。

## 运行测试

**静态验证（本机即可）**：`python tools/validate.py`

**XCTest（在 Mac 上；⚠️ 冻结中，现状为红）**：
```bash
xcodebuild test -project AdventureIsland.xcodeproj -scheme AdventureIsland -destination 'platform=iOS Simulator,name=iPad (10th generation)'
```
共 4 个测试类 59 个用例（内容完整性 / 存储 / 逻辑 / Boss 流程）。其中 `ContentIntegrityTests` 的关卡数期望（17/17/14/14/12）落后于已发布内容（18/18/15/15/13），按 ADR-0003 此差异**挂起到解冻时随原生端一并重建**，不在冻结期修改 Swift。

---

## 构建（需要一台 Mac + Xcode 15+；Swift 冻结中，仅解冻后相关）

### 方法 A：手动建工程（无需装任何工具）

1. Mac 上打开 Xcode → **Create New Project → iOS → App**
   - Product Name：`AdventureIsland`；Interface 选 **SwiftUI**；Language **Swift**；不勾选 Core Data / Tests 复选框
   - 保存到任意目录（建议和本文件夹同级）
2. 在 Xcode 左侧文件树里，**删除**模板生成的 `ContentView.swift` 和 `AdventureIslandApp.swift`
3. 把本目录 `AdventureIsland/` 下的**全部内容**（Swift 文件 + Resources 文件夹 + Assets.xcassets）拖进 Xcode 项目导航器（拖到蓝色工程图标下的 `AdventureIsland` 组上）：
   - 弹窗勾选 **"Copy items if needed"**、**"Create groups"**，Targets 勾选 `AdventureIsland`
4. 设置 Target（选中蓝色工程图标 → TARGETS → AdventureIsland）：
   - **Signing & Capabilities**：Team 选你的 Apple ID（Personal Team）
   - **General → Minimum Deployments**：iOS 16.0；勾选 **iPad** 支持（取消 iPhone）
   - Deployment Info 勾选方向：只留 **Landscape Left / Landscape Right**
   - **Info** 标签：确认有 `UILaunchScreen`（空字典）、`UIRequiresFullScreen = YES`、`UIStatusBarHidden = YES`，没有就手动加
5. iPad 上开启开发者模式：设置 → 隐私与安全性 → 开发者模式 → 打开（需重启 iPad）
6. iPad 用数据线连 Mac，Xcode 顶部设备选你的 iPad → **Cmd+R** 运行
   - 首次运行若提示"不受信任的开发者"：iPad 设置 → 通用 → VPN与设备管理 → 信任你的开发者证书
7. 装好后拔线即可离线玩

> 免费Apple ID 签名 **7 天有效**，到期重新连 Mac Cmd+R 即可；付费开发者账号（$99/年）签名 1 年有效。

### 方法 B：XcodeGen 一键生成（推荐顺手）

```bash
brew install xcodegen
cd ios
xcodegen          # 生成 AdventureIsland.xcodeproj（含测试 target）
open AdventureIsland.xcodeproj
# Cmd+R 运行 · Cmd+U 跑测试（见上：冻结期为红）
```

工程已配置好：iPad only / iOS 16 / 仅横屏 / 测试目标 / Scheme。

---

## 给孩子加新内容（不用写代码）

推荐走内容生成器：编辑 `tools/gen_content.py` → `python tools/gen_content.py` 生成 JSON → `python tools/gen_preview_data.py` 同步模拟器 → `python tools/validate.py` 验证。

内容分布在 `AdventureIsland/Resources/`：

- `cn_levels / math_levels / pinyin_levels / english_levels / astro_levels .json`：关卡（普通/复习/boss）与棋盘格序列
- `shop.json`：角色与称号两品类（非默认件定价 40-120，validate 闸门把关）
- `experiments.json`：科学岛实验（浮沉物理引擎通用，磁性/光影需新场景）
- `collection.json`：图鉴/贴纸/汉字卡/拼音卡/单词卡/星空卡/徽章 + 衣橱分区

图标在 `design/assets/icons/`（94 个 SVG；加新图 = 拷入 `Assets.xcassets` 仿照现有 imageset 结构，并在 `Common.swift` 的 IconEmoji.map 加 Emoji 兜底——后者涉及冻结中的 Swift，建议攒到解冻一起做）。

## 常见问题

| 现象 | 处理 |
|---|---|
| 图标显示为 ❓ | 该图标没进 Assets.xcassets（代码会自动用 Emoji 兜底，不会崩） |
| 没有声音 | 检查 iPad 静音键；音效为程序生成蜂鸣，音量偏小是正常的 |
| 7 天后 App 打不开 | 免费签名过期，连 Mac 重新 Cmd+R（Swift 冻结期用模拟器离线包则无此问题） |
| 想重置孩子进度 | 家长中心 → 重置全部进度 |
| 每日到点被锁 | 设计如此（护眼）；家长中心可调每日上限，跨天自动恢复 |
| 刷新/重进后计时还在 | v0.8 评审修复后护眼时长随存档持久化，刷新不再重置每日计时 |
