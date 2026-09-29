# 探险岛 · 幼小衔接 iPad App（v0.4）

面向自家 3-6 岁孩子的幼小衔接 App，**仅个人使用、不上架**。马里奥风设计稿（`design/shots/final-*.png`）的 SwiftUI + SpriteKit 实现。

- 学科（6 水管）：识字村 15 关 · 思维镇 15 关（8 种题型：点数/比多少/加减/找规律/分一分/排一排/填一填/归类）· 拼音谷 12 关 · 英语王国 12 关 · 天文台 10 关 · 科学岛（浮沉实验）
- 飞机模式友好：所有题型纯视觉作答，朗读全部改为手动可选，不点喇叭也能通关
- 激励：金币 + 收集册（图鉴/贴纸/汉字卡/拼音卡/单词卡/星空卡/徽章），无分数无排名
- 家长中心：算术家长门 / 护眼时长 / 6 学科进度 / 难度
- 数据全部存本机（Documents 下 JSON），无网络、无广告、无内购

---

## 目录结构

```
ios/
├─ project.yml                    # XcodeGen 工程定义（可选，见方法B）
├─ AdventureIsland/               # App 源码（SwiftUI + SpriteKit）
│  ├─ AdventureIsland 入口/主题/通用组件/模型/存储/服务
│  ├─ RootView / MapView / LevelView / LabView / CollectionView / ParentView
│  ├─ Resources/*.json            # 关卡与收集内容（加内容=加JSON）
│  └─ Assets.xcassets/            # 82 个 SVG 图标（含矢量保留，可直接替换高清图）
├─ Tests/AdventureIslandTests/    # XCTest 测试套件
├─ preview/index.html             # 浏览器模拟器（1:1 预览，见 docs §5）
└─ tools/
   ├─ validate.py                 # 本机静态验证（18 项）
   ├─ gen_content.py              # 内容生成器：改完重跑 → Resources/*.json
   └─ gen_preview_data.py         # 把 Resources JSON 注入模拟器（改内容后必跑）
```

源码文件说明见 `docs/开发与测试记录.md`。

---

## 构建（需要一台 Mac + Xcode 15+）

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
# Cmd+R 运行 · Cmd+U 跑测试
```

工程已配置好：iPad only / iOS 16 / 仅横屏 / 测试目标 / Scheme。

---

## 运行测试

**XCTest（在 Mac 上）**：`Cmd+U` 或
```bash
xcodebuild test -project AdventureIsland.xcodeproj -scheme AdventureIsland -destination 'platform=iOS Simulator,name=iPad (10th generation)'
```
覆盖：内容完整性（题目答案/资产引用）· 进度存储 · 连击/每日任务 · 护眼时长状态机 · 浮沉物理模型 · 家长门。共 6 个测试类 20 个用例。

**静态验证（本 Windows 机已执行，12 项全过）**：
```bash
python tools/validate.py
```

---

## 给孩子加新内容（不用写代码）

推荐走内容生成器：编辑 `tools/gen_content.py`（Python 数据表，注释齐全）→ 跑 `python tools/gen_content.py` 生成 JSON → 跑 `python tools/gen_preview_data.py` 同步模拟器 → Mac 上 `Cmd+U` 验证。

也可以直接编辑 `AdventureIsland/Resources/` 下的 JSON：

- `cn_levels / math_levels / pinyin_levels / english_levels / astro_levels .json`：加关卡。12 种步骤：
  `teach`（认一认）`letter`（学一学）`listen`（找一找，视觉匹配）`quiz`（练一练）
  `count`（点数）`compare`（比多少）`arith`（加减法）`pattern`（找规律）
  `split`（分一分）`order`（排一排）`neighbor`（填一填）`blend`（拼读）
- `experiments.json`：加实验（浮沉物理引擎通用，磁性/光影需新场景）
- `collection.json`：图鉴/贴纸/汉字卡/拼音卡/单词卡/星空卡/徽章

图标可用 `design/assets/icons/` 里的 82 个 SVG（加新图 = 拷入 `Assets.xcassets` 仿照现有 imageset 结构，并在 `Common.swift` 的 IconEmoji.map 加 Emoji 兜底）。
改完跑 `python tools/validate.py`（本机）+ `Cmd+U`（Mac），会自动检查答案正确性和图标引用。

## 常见问题

| 现象 | 处理 |
|---|---|
| 图标显示为 ❓ | 该图标没进 Assets.xcassets（代码会自动用 Emoji 兜底，不会崩） |
| 没有声音 | 检查 iPad 静音键；音效为程序生成蜂鸣，音量偏小是正常的 |
| 7 天后 App 打不开 | 免费签名过期，连 Mac 重新 Cmd+R |
| 想重置孩子进度 | 家长中心 → 重置全部进度 |
| 每日到点被锁 | 设计如此（护眼）；家长中心可调每日上限，跨天自动恢复 |
