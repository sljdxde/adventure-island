# 探险岛 · 幼小衔接 iPad App（v0.1）

面向自家 3-6 岁孩子的幼小衔接 App，**仅个人使用、不上架**。马里奥风设计稿（`design/shots/final-*.png`）的 SwiftUI + SpriteKit 实现。

- 学科：语文（识字村 10 关）· 数学（思维镇 10 关）· 科学实验室（浮与沉）
- 激励：金币 + 收集册（图鉴/贴纸/汉字卡），无分数无排名
- 家长中心：算术家长门 / 护眼时长 / 进度 / 难度
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
│  └─ Assets.xcassets/            # 由设计稿 assets 生成的 68 个 SVG 图标
├─ Tests/AdventureIslandTests/    # XCTest 测试套件
└─ tools/validate.py              # 本机静态验证脚本（已执行通过）
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

编辑 `AdventureIsland/Resources/` 下的 JSON 后重新 Run：

- `cn_levels.json` / `math_levels.json`：加关卡。四种步骤：`teach`（认一认）/ `quiz`（答题）/ `count`（点数）/ `compare`（比多少）
- `experiments.json`：加实验（目前浮沉物理引擎通用，可扩展磁性/光影实验需新增场景）
- `collection.json`：加图鉴/贴纸/汉字卡/徽章

图标可用 `design/assets/icons/` 里的 68 个 SVG（加新图 = 拷入 `Assets.xcassets` 仿照现有 imageset 结构）。
改完在 Mac 上跑一次 `Cmd+U`，内容校验测试会自动检查答案正确性和图标引用。

## 常见问题

| 现象 | 处理 |
|---|---|
| 图标显示为 ❓ | 该图标没进 Assets.xcassets（代码会自动用 Emoji 兜底，不会崩） |
| 没有声音 | 检查 iPad 静音键；音效为程序生成蜂鸣，音量偏小是正常的 |
| 7 天后 App 打不开 | 免费签名过期，连 Mac 重新 Cmd+R |
| 想重置孩子进度 | 家长中心 → 重置全部进度 |
| 每日到点被锁 | 设计如此（护眼）；家长中心可调每日上限，跨天自动恢复 |
