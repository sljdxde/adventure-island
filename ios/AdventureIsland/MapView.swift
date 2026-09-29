import SwiftUI

// MARK: - 主页：马里奥风探险岛地图（水管入口 + 圆点关卡路径 + 终点旗）

struct MapView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var settings: SettingsStore
    @EnvironmentObject var toast: ToastCenter
    @EnvironmentObject var speech: SpeechService
    @Environment(\.soundService) private var sound
    @Binding var route: Route
    @Binding var confetti: Int

    @State private var cnContent: SubjectFile?
    @State private var mathContent: SubjectFile?

    private let zones: [(icon: String, label: String, meta: String, pipe: String, subject: String, unit: String, total: Int)] = [
        ("panda", "识字村", "象形字 · 认读", "pipe-red", "cn", "关", 15),
        ("fox", "思维镇", "数感 · 加减法", "pipe-blue", "math", "关", 15),
        ("robot", "科学岛", "动手做实验", "pipe-purple", "lab", "项已点亮", 12),
        ("panda", "拼音谷", "声母 · 韵母 · 拼读", "pipe-orange", "pinyin", "关", 12),
        ("robot", "英语王国", "ABC · 单词", "pipe-green", "english", "关", 12),
        ("robot", "天文台", "太阳 · 月亮 · 星星", "pipe-indigo", "astro", "关", 10)
    ]

    var body: some View {
        ZStack {
            SceneBackground(theme: .home)

            VStack(spacing: 0) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                titleBanner
                    .padding(.top, 2)

                pipesRow
                    .padding(.top, 6)

                Spacer(minLength: 4)

                levelPath

                Spacer(minLength: 0)

                bottomDock
                    .padding(.bottom, 10)
            }

            // 天空装饰：砖块 + 无敌旋转金币
            VStack {
                HStack {
                    ImageDecor(icon: "brick", size: 44).padding(.leading, 26)
                    ImageDecor(icon: "brick", size: 44).padding(.leading, -8)
                    Spacer()
                    SpinCoin(size: 30)
                    SpinCoin(size: 38, delay: 0.4).padding(.leading, -6).offset(y: 14)
                    SpinCoin(size: 30, delay: 0.8).padding(.leading, -6)
                }
                .padding(.top, 96)
                Spacer()
            }
            .allowsHitTesting(false)

            // 马里奥灌木丛（路径两端）
            HStack {
                IconView(name: "bush", size: 96)
                    .padding(.leading, 8)
                Spacer()
                IconView(name: "bush", size: 72)
                    .padding(.trailing, 18)
            }
            .frame(maxHeight: .infinity, alignment: .bottom)
            .padding(.bottom, 130)
            .allowsHitTesting(false)
            .zIndex(11)
        }
        .onAppear {
            if cnContent == nil { cnContent = ContentLoader.load(SubjectFile.self, "cn_levels") }
            if mathContent == nil { mathContent = ContentLoader.load(SubjectFile.self, "math_levels") }
        }
    }

    // MARK: 顶部 HUD

    private var header: some View {
        HStack {
            SquareIconButton(icon: "home", action: { speech.speak("我在探险岛，点水管开始闯关吧！") })
            HStack(spacing: 0) {
                ZStack {
                    Circle().fill(LinearGradient(colors: [Color(hex: 0xFFE29A), .brandYellow], startPoint: .topLeading, endPoint: .bottomTrailing))
                    IconView(name: settings.settings.avatar, size: 34)
                }
                .frame(width: 54, height: 54)
                .overlay(Circle().stroke(.white, lineWidth: 4))
                Text("\(settings.settings.childName) · Lv.\(level)")
                    .font(.kidHead(19))
                    .foregroundColor(.white)
                    .padding(.horizontal, 20)
                    .padding(.vertical, 12)
                    .background(Capsule().fill(LinearGradient(colors: [.brandOrange, .brandOrangeDk], startPoint: .top, endPoint: .bottom)))
                    .padding(.leading, -16)
            }
            .shadow(color: .ink.opacity(0.2), radius: 8, y: 5)

            Spacer()

            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
            SquareIconButton(icon: "medal", action: { route = .collection })
            SquareIconButton(icon: "lock", action: { route = .parent })
        }
    }

    private var level: Int {
        let done = store.doneCount(subject: "cn", total: 15) + store.doneCount(subject: "math", total: 15)
        return max(1, done / 4 + 1)
    }

    // MARK: 红色标题横幅

    private var titleBanner: some View {
        VStack(spacing: 2) {
            Text("探 险 岛")
                .font(.kidTitle(40))
                .foregroundColor(.white)
                .shadow(color: .black.opacity(0.25), radius: 0, x: 0, y: 3)
            Text("每天玩一小会儿 · 养成好习惯")
                .font(.kidBody(15))
                .foregroundColor(.white.opacity(0.95))
        }
        .padding(.horizontal, 60)
        .padding(.vertical, 16)
        .background(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(LinearGradient(colors: [Color(hex: 0xFF8A70), .brandCoralDk], startPoint: .top, endPoint: .bottom))
                .overlay(
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .stroke(Color(hex: 0xB8493A), lineWidth: 4)
                )
        )
        .overlay(
            // 砖块四角钉
            HStack {
                ForEach(0..<2, id: \.self) { _ in EmptyView() }
            }
        )
        .shadow(color: .black.opacity(0.22), radius: 14, y: 8)
        .overlay(alignment: .topLeading) { BannerStud().offset(x: -8, y: -8) }
        .overlay(alignment: .topTrailing) { BannerStud().offset(x: 8, y: -8) }
        .overlay(alignment: .bottomLeading) { BannerStud().offset(x: -8, y: 8) }
        .overlay(alignment: .bottomTrailing) { BannerStud().offset(x: 8, y: 8) }
    }

    // MARK: 三个水管入口

    private var pipesRow: some View {
        HStack(alignment: .bottom, spacing: 2) {
            zonePipe(zones[0], done: store.doneCount(subject: "cn", total: zones[0].total), total: zones[0].total, isNew: false)
            zonePipe(zones[1], done: store.doneCount(subject: "math", total: zones[1].total), total: zones[1].total, isNew: false)
            zonePipe(zones[2], done: store.snapshot.collectedScience.count, total: zones[2].total, isNew: false)
            zonePipe(zones[3], done: store.doneCount(subject: "pinyin", total: zones[3].total), total: zones[3].total, isNew: false)
            zonePipe(zones[4], done: store.doneCount(subject: "english", total: zones[4].total), total: zones[4].total, isNew: false)
            zonePipe(zones[5], done: store.doneCount(subject: "astro", total: zones[5].total), total: zones[5].total, isNew: true)
        }
    }

    private func zonePipe(_ zone: (icon: String, label: String, meta: String, pipe: String, subject: String, unit: String, total: Int),
                          done: Int, total: Int, isNew: Bool) -> some View {
        VStack(spacing: 0) {
                ZStack {
                    IconView(name: zone.pipe, size: 84)
                    VStack {
                        Text("") // 占位
                    }
                    VStack {
                        QuestionBlock(onTap: {
                            // 顶砖块出金币（马里奥手感彩蛋）
                            sound.systemTap()
                            store.snapshot.coins += 1
                            store.save()
                            toast.show("🪙 +1", seconds: 1.0)
                        })
                            .offset(y: -42)
                    }
                    IconView(name: zone.icon, size: 30)
                        .offset(x: 36, y: 24)
                }
                .frame(height: 116)
                .overlay(alignment: .topTrailing) {
                    if isNew {
                        Text("NEW ✦")
                            .font(.system(size: 13, weight: .heavy, design: .rounded))
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 5)
                            .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFF9068), .brandCoralDk], startPoint: .top, endPoint: .bottom)))
                            .rotationEffect(.degrees(8))
                            .offset(x: 10, y: 2)
                    }
                }

                Text(zone.label)
                    .font(.kidHead(19))
                    .foregroundColor(Color(hex: 0x8A5B00))
                    .padding(.horizontal, 20)
                    .padding(.vertical, 7)
                    .background(
                        Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFE58A), .brandYellowDk], startPoint: .top, endPoint: .bottom))
                    )
                    .overlay(Capsule().stroke(Color(hex: 0xB8770A), lineWidth: 2.5))
                    .shadow(color: .black.opacity(0.14), radius: 6, y: 4)
                    .padding(.top, 2)

                Text("\(zone.meta) ｜ \(done)/\(total) \(zone.unit)")
                    .font(.kidBody(12.5))
                    .foregroundColor(.brandGreenDdk)
                    .padding(.top, 4)
                    .lineLimit(1)
                    .minimumScaleFactor(0.8)

                GoldTrack(ratio: total == 0 ? 0 : Double(done) / Double(total), height: 9)
                    .frame(width: 138)
                    .padding(.top, 4)
            }
            .contentShape(Rectangle())
            .onTapGesture {
                sound.systemTap()
                if zone.subject == "lab" {
                    route = .lab
                } else {
                    // 进入该学科当前关卡
                    var index = 0
                    while index < total, store.nodeState(subject: zone.subject, index: index, total: total) == .done {
                        index += 1
                    }
                    route = .level(subject: zone.subject, index: min(index, total - 1))
                }
            }
            .frame(maxWidth: .infinity)
    }

    // MARK: 关卡路径（圆点 + 关卡节点 + 终点旗）

    private var levelPath: some View {
        GeometryReader { geo in
            let path = Path { p in
                p.move(to: CGPoint(x: 30, y: geo.size.height * 0.75))
                p.addCurve(to: CGPoint(x: geo.size.width * 0.5, y: geo.size.height * 0.35),
                           control1: CGPoint(x: geo.size.width * 0.2, y: geo.size.height * 0.1),
                           control2: CGPoint(x: geo.size.width * 0.35, y: geo.size.height * 0.62))
                p.addCurve(to: CGPoint(x: geo.size.width - 40, y: geo.size.height * 0.5),
                           control1: CGPoint(x: geo.size.width * 0.65, y: geo.size.height * 0.1),
                           control2: CGPoint(x: geo.size.width * 0.8, y: geo.size.height * 0.72))
            }
            ZStack {
                path
                    .stroke(.white.opacity(0.95), style: StrokeStyle(lineWidth: 9, dash: [1, 26], lineCap: .round))
                path
                    .stroke(.black.opacity(0.08), style: StrokeStyle(lineWidth: 9, dash: [1, 26], lineCap: .round))
                    .offset(y: 3)
                    .blendMode(.multiply)

                PathDots(width: geo.size.width, height: geo.size.height)
                PathLevelNodes(width: geo.size.width, height: geo.size.height, route: $route)

                // 终点：马里奥城堡（旗杆插在城堡上）
                VStack(spacing: 0) {
                    IconView(name: "flag", size: 26)
                        .offset(y: 6)
                    IconView(name: "castle", size: 62)
                    Text("终点")
                        .font(.kidHead(13))
                        .foregroundColor(.white)
                        .shadow(color: .ink, radius: 0, y: 2)
                }
                .position(x: geo.size.width - 40, y: geo.size.height * 0.44)
            }
        }
        .frame(height: 118)
        .padding(.horizontal, 6)
    }

    // MARK: 底部弧形面板

    private var bottomDock: some View {
        ZStack(alignment: .bottom) {
            ArcCreamPanel()
                .frame(height: 96)
            HStack(spacing: 64) {
                dockItem(icon: "medal", badge: "\(store.snapshot.collectedScience.count + store.snapshot.stickers.count)/34", title: "收集册") {
                    route = .collection
                }
                dockItem(icon: "clip", badge: "\(dailyTotal())/3", title: "今日任务") {
                    toast.show(dailyTotal() >= 3 ? "今日任务全部完成，明天见 🎉" : "六个学科任玩三个就达标啦")
                }
                dockItem(icon: "clock", badge: nil, title: "休息一下") {
                    toast.show("👀 看看窗外最远的地方，数 20 个数～")
                }
            }
            .padding(.bottom, 8)

            HStack {
                Button {
                    rollDice()
                } label: {
                    ZStack {
                        Circle().fill(LinearGradient(colors: [Color(hex: 0xFFDD7A), .brandYellowDk], startPoint: .top, endPoint: .bottom))
                        IconView(name: "dice", size: 34)
                    }
                    .frame(width: 64, height: 64)
                    .overlay(Circle().stroke(.white, lineWidth: 4))
                    .shadow(color: .brandYellowDdk.opacity(0.5), radius: 10, y: 5)
                }
                .buttonStyle(.plain)
                Spacer()
            }
            .padding(.leading, 26)
            .padding(.bottom, 26)
        }
    }

    private func dockItem(icon: String, badge: String?, title: String, locked: Bool = false, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: 3) {
                ZStack(alignment: .topTrailing) {
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .fill(LinearGradient(colors: [Color(hex: 0xFFFDF6), Color(hex: 0xFFF0D2)], startPoint: .top, endPoint: .bottom))
                        .frame(width: 58, height: 58)
                        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color(hex: 0xE8D5AE), lineWidth: 1.5))
                        .shadow(color: .ink.opacity(0.12), radius: 6, y: 4)
                    IconView(name: icon, size: 32)
                        .padding(13)
                    if let badge {
                        Text(badge)
                            .font(.system(size: 12, weight: .heavy, design: .rounded))
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 3)
                            .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFF9068), .brandCoralDk], startPoint: .top, endPoint: .bottom)))
                            .offset(x: 16, y: -8)
                    }
                }
                Text(title)
                    .font(.kidBody(14))
                    .foregroundColor(locked ? .inkSoft : .ink)
            }
        }
        .buttonStyle(.plain)
        .opacity(locked ? 0.65 : 1)
    }

    // MARK: 行为

    private func dailyTotal() -> Int {
        ["cn", "math", "lab", "pinyin", "english", "astro"].reduce(0) { $0 + (store.dailyDone(subject: $1) > 0 ? 1 : 0) }
    }

    private func rollDice() {
        let subjects = ["cn", "math", "pinyin", "english", "astro"]
        let subject = subjects.randomElement()!
        let total = zones.first(where: { $0.subject == subject })?.total ?? 10
        var index = 0
        while index < total, store.nodeState(subject: subject, index: index, total: total) == .done {
            index += 1
        }
        route = .level(subject: subject, index: min(index, total - 1))
        toast.show("🎲 命运骰子：出发！")
    }
}

// 路径上的小圆点装饰
private struct PathDots: View {
    let width: CGFloat
    let height: CGFloat
    var body: some View {
        ForEach(0..<16, id: \.self) { i in
            Circle()
                .fill(.white.opacity(0.9))
                .frame(width: 7, height: 7)
                .position(
                    x: 40 + CGFloat(i) * (width - 80) / 15,
                    y: height * 0.62 + sin(Double(i) * 0.9) * height * 0.16
                )
        }
    }
}

// 关卡节点（识字村 10 关沿路径排布）
private struct PathLevelNodes: View {
    let width: CGFloat
    let height: CGFloat
    @Binding var route: Route
    @EnvironmentObject var store: ProgressStore

    var body: some View {
        let total = 15   // 识字村 v0.2 起为 15 关，节点随内容数自适应
        ForEach(0..<total, id: \.self) { i in
            let state = store.nodeState(subject: "cn", index: i, total: total)
            let x = width * 0.07 + CGFloat(i) * (width * 0.88) / CGFloat(total - 1)
            let y = height * 0.58 + sin(Double(i) * 0.85) * height * 0.14
            ZStack(alignment: .bottom) {
                nodeCircle(state)
                if state == .current {
                    Text("下一关 ▶")
                        .font(.system(size: 12, weight: .heavy, design: .rounded))
                        .foregroundColor(.white)
                        .shadow(color: .brandGreenDdk, radius: 0, y: 2)
                        .offset(y: 24)
                }
            }
            .position(x: x, y: y)
            .onTapGesture {
                if state != .locked { route = .level(subject: "cn", index: i) }
            }
        }
    }

    @ViewBuilder
    private func nodeCircle(_ state: MapNodeState) -> some View {
        ZStack {
            switch state {
            case .done:
                Circle()
                    .fill(LinearGradient(colors: [Color(hex: 0x7FD98A), .brandGreen], startPoint: .top, endPoint: .bottom))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: .brandGreenDdk, radius: 0, y: 4)
                Image(systemName: "checkmark")
                    .font(.system(size: 19, weight: .black))
                    .foregroundColor(.white)
            case .current:
                Circle()
                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), .gold], startPoint: .top, endPoint: .bottom))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: .goldDdk.opacity(0.65), radius: 0, y: 4)
                    .shadow(color: .gold.opacity(0.45), radius: 10)
                IconView(name: "starface", size: 26)
            case .locked:
                Circle()
                    .fill(Color(hex: 0xC9CFD6))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: Color(hex: 0x9AA1A9), radius: 0, y: 4)
            }
        }
        .frame(width: 38, height: 38)
        .modifier(NodePulse(active: state == .current))
    }
}

private struct NodePulse: ViewModifier {
    let active: Bool
    @State private var up = false
    func body(content: Content) -> some View {
        content
            .scaleEffect(active && up ? 1.09 : 1)
            .onAppear {
                guard active else { return }
                withAnimation(.easeInOut(duration: 1.2).repeatForever(autoreverses: true)) { up = true }
            }
    }
}

// 问号方块（水管顶，可顶出金币）
private struct QuestionBlock: View {
    var onTap: (() -> Void)? = nil
    @State private var pulse = false
    @State private var bump = false
    @State private var showCoin = false

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 10, style: .continuous)
                .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                .frame(width: 52, height: 52)
                .overlay(RoundedRectangle(cornerRadius: 10, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
            Text("?")
                .font(.system(size: 30, weight: .black, design: .rounded))
                .foregroundColor(.white)
                .shadow(color: Color(hex: 0xB8770A), radius: 0, x: 1, y: 2)
            ForEach(0..<4, id: \.self) { i in
                Circle()
                    .fill(Color(hex: 0xFFF6D0))
                    .frame(width: 4, height: 4)
                    .position(x: i % 2 == 0 ? 10 : 42, y: i < 2 ? 10 : 42)
            }
            if showCoin {
                IconView(name: "coin", size: 26)
                    .offset(y: -44)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
        .scaleEffect(pulse ? 1.07 : 1)
        .offset(y: bump ? -12 : 0)
        .animation(.easeInOut(duration: 1.1).repeatForever(autoreverses: true), value: pulse)
        .onAppear { pulse = true }
        .onTapGesture {
            guard let action = onTap else { return }
            withAnimation(.spring(response: 0.22, dampingFraction: 0.55)) { bump = true; showCoin = true }
            action()
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.24) {
                withAnimation(.easeOut(duration: 0.2)) { bump = false }
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
                withAnimation(.easeOut(duration: 0.25)) { showCoin = false }
            }
        }
    }
}

// 无敌旋转金币（SMB 风：绕纵轴转）
private struct SpinCoin: View {
    var size: CGFloat = 30
    var delay: Double = 0
    @State private var spinning = false

    var body: some View {
        IconView(name: "coin", size: size)
            .rotation3DEffect(.degrees(spinning ? 360 : 0), axis: (x: 0, y: 1, z: 0))
            .animation(.linear(duration: 2.4).repeatForever(autoreverses: false).delay(delay), value: spinning)
            .onAppear { spinning = true }
    }
}

private struct BannerStud: View {
    var body: some View {
        ZStack {
            Circle().fill(Color(hex: 0xFFD34D))
            Circle().stroke(Color(hex: 0xC08A0C), lineWidth: 2.5)
            Circle().fill(.white.opacity(0.5)).frame(width: 8, height: 8).offset(x: -3, y: -3)
        }
        .frame(width: 18, height: 18)
    }
}

private struct ImageDecor: View {
    let icon: String
    let size: CGFloat
    var body: some View {
        IconView(name: icon, size: size)
            .opacity(0.9)
    }
}

// 底部奶油弧形面板
private struct ArcCreamPanel: View {
    var body: some View {
        CreamArc()
            .fill(LinearGradient(colors: [Color(hex: 0xFFFBF0), .creamDk], startPoint: .top, endPoint: .bottom))
            .overlay(
                CreamArc().stroke(.white, lineWidth: 4).blur(radius: 0.5)
            )
            .shadow(color: .ink.opacity(0.12), radius: 16, y: -6)
            .ignoresSafeArea(edges: .bottom)
    }
}

private struct CreamArc: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let arcH: CGFloat = 70
        p.move(to: CGPoint(x: 0, y: rect.maxY))
        p.addLine(to: CGPoint(x: 0, y: rect.minY + arcH))
        p.addQuadCurve(
            to: CGPoint(x: rect.maxX, y: rect.minY + arcH * 0.4),
            control: CGPoint(x: rect.midX, y: rect.minY - arcH * 0.5)
        )
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        p.closeSubpath()
        return p
    }
}
