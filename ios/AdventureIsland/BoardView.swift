import SwiftUI

// MARK: - 迷你棋盘关（v0.8 工单02：识字村试点）
// 掷骰 → 蛇形路径逐格蹦跳 → 题目格出题（答对 +2 金币、答错可重答）→ 金币格 +5
// → 到城堡走结算卡。路径形状按格数由渲染层计算，不进 JSON（规格实现决策 4）。

/// 骰子点面（1-6 点）：掷骰步骤与棋盘掷骰共用
struct DieFaceView: View {
    let face: Int
    var size: CGFloat = 64

    /// 1-6 点的骰子点位坐标（0-1 比例）
    static let pips: [Int: [(Double, Double)]] = [
        1: [(0.5, 0.5)],
        2: [(0.28, 0.28), (0.72, 0.72)],
        3: [(0.26, 0.26), (0.5, 0.5), (0.74, 0.74)],
        4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
        5: [(0.26, 0.26), (0.74, 0.26), (0.5, 0.5), (0.26, 0.74), (0.74, 0.74)],
        6: [(0.28, 0.22), (0.72, 0.22), (0.28, 0.5), (0.72, 0.5), (0.28, 0.78), (0.72, 0.78)],
    ]

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: size * 0.19, style: .continuous)
                .fill(LinearGradient(colors: [.white, Color(hex: 0xF2EDDF)], startPoint: .top, endPoint: .bottom))
                .overlay(RoundedRectangle(cornerRadius: size * 0.19, style: .continuous)
                    .stroke(Color(hex: 0xD8CBAF), lineWidth: size * 0.05))
                .shadow(color: .ink.opacity(0.16), radius: 6, y: 4)
            ForEach(Array((Self.pips[face] ?? []).enumerated()), id: \.offset) { _, p in
                Circle()
                    .fill(RadialGradient(colors: [Color(hex: 0xE84838), Color(hex: 0xC24836)],
                                         center: .center, startRadius: 0, endRadius: size * 0.11))
                    .frame(width: size * 0.17, height: size * 0.17)
                    .position(x: size * p.0, y: size * p.1)
            }
        }
        .frame(width: size, height: size)
    }
}

/// step.kind 分发渲染：线性关卡与棋盘题目覆盖层共用同一份
struct StepContainerView: View {
    let step: Step
    let subject: String
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void

    var body: some View {
        switch step.kind {
        case "teach": TeachStepView(step: step, onNext: onNext)
        case "letter": LetterStepView(step: step, subject: subject, onNext: onNext)
        case "listen": ListenStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "blend": BlendStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "arith": ArithStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "pattern": PatternStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "split": SplitStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "neighbor": NeighborStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "order": OrderStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "memory": MemoryStepView(step: step, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "dice": DiceStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "quiz": QuizStepView(step: step, onWrong: onWrong, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "count": CountStepView(step: step, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        case "compare": CompareStepView(step: step, onNext: onNext, onCorrectCelebrate: onCorrectCelebrate)
        default: EmptyView()
        }
    }
}

/// 通关结算卡：星级、3 星蘑菇 +2、按钮组（线性关与棋盘关共用，结算语义与模拟器 settleLevel 同源）
struct FinishCardView: View {
    let subject: String
    let index: Int
    let totalLevels: Int
    let stars: Int
    let wrongCount: Int
    let onNext: () -> Void
    let onReplay: () -> Void
    @EnvironmentObject var store: ProgressStore
    @Binding var route: Route

    private var hasNext: Bool { index + 1 < totalLevels }

    var body: some View {
        ZStack {
            Color.black.opacity(0.4).ignoresSafeArea()
            VStack(spacing: 12) {
                // 马里奥通关：小人 + 城堡 + 旗杆 + 庆典
                ZStack(alignment: .bottom) {
                    HStack(spacing: 14) {
                        VStack(spacing: -4) {
                            IconView(name: "flag", size: 30)
                            IconView(name: "castle", size: 66)
                        }
                        IconView(name: index % 2 == 0 ? "mario" : "dino", size: 58)
                            .modifier(NodePulse(active: true))
                        Text("🎉").font(.system(size: 52))
                        IconView(name: "mushroom", size: 52)
                            .opacity(stars == 3 ? 1 : 0.3)
                            .scaleEffect(stars == 3 ? 1 : 0.85)
                    }
                }
                Text("本关完成！")
                    .font(.kidTitle(30))
                    .foregroundColor(.ink)
                HStack(spacing: 10) {
                    ForEach(0..<3, id: \.self) { i in
                        IconView(name: "starface", size: 44)
                            .opacity(i < stars ? 1 : 0.25)
                            .scaleEffect(i < stars ? 1 : 0.8)
                    }
                }
                if stars == 3 {
                    Text("🍄 幸运蘑菇奖励 +2 金币！")
                        .font(.kidHead(17))
                        .foregroundColor(Color(hex: 0xC24836))
                        .padding(.horizontal, 16)
                        .padding(.vertical, 6)
                        .background(Capsule().fill(Color(hex: 0xFFEFE6)))
                }
                Text(wrongCount == 0 ? "一次没错，完美通关！" : "答错了 \(wrongCount) 次也没关系，你已经学会啦")
                    .font(.kidBody(16))
                    .foregroundColor(.inkSoft)
                HStack(spacing: 16) {
                    if hasNext {
                        Button(action: onNext) {
                            Label("下一关", systemImage: "arrow.right")
                                .font(.kidHead(19))
                        }
                        .buttonStyle(.jellyGreen)
                    }
                    Button {
                        route = .map
                    } label: {
                        Label("返回地图", systemImage: "map")
                            .font(.kidHead(19))
                    }
                    .buttonStyle(.jellyOrange)
                    Button(action: onReplay) {
                        Label("再玩一次", systemImage: "arrow.counterclockwise")
                            .font(.kidHead(19))
                    }
                    .buttonStyle(.jellyCream)
                }
            }
            .padding(44)
            .background(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(LinearGradient(colors: [.white, .creamDk], startPoint: .top, endPoint: .bottom))
            )
            .overlay(RoundedRectangle(cornerRadius: 34, style: .continuous).stroke(.brandYellow, lineWidth: 5))
            .shadow(color: .black.opacity(0.3), radius: 26)
        }
        .onAppear {
            // 蘑菇 +2 只发给此前从未拿过 3 星的关：旧星级须在 completeLevel 改写前取
            // （判据与模拟器 old<3 同源，跨启动持久防重发；经金币账本入账——工单04）
            let previousStars = store.stars(for: subject, index: index)
            store.completeLevel(subject: subject, index: index, stars: stars)
            if stars == 3, previousStars < 3 {
                store.recordCoin(.mushroomBonus, amount: 2)
            }
        }
    }
}

/// 蹦跳弹跳：tick 每前进一格 +1，弹簧跳一下
private struct HopBounceModifier: ViewModifier {
    let tick: Int
    @State private var up = false

    func body(content: Content) -> some View {
        content
            .offset(y: up ? -26 : 0)
            .animation(.spring(response: 0.32, dampingFraction: 0.5), value: up)
            .onChange(of: tick) { _ in up.toggle() }
    }
}

/// 金币格爆金币：3 枚金币弹出淡出
private struct CoinBurstView: View {
    @State private var fired = false

    var body: some View {
        Group {
            ForEach(0..<3, id: \.self) { i in
                IconView(name: "coin", size: 30)
                    .offset(x: fired ? CGFloat([-52, 0, 52][i]) : 0,
                            y: fired ? -64 : 0)
                    .opacity(fired ? 0 : 1)
                    .animation(.easeOut(duration: 0.7).delay(Double(i) * 0.08), value: fired)
            }
        }
        .onAppear { fired = true }
        .allowsHitTesting(false)
    }
}

/// 迷你棋盘关整屏：头部进度 + 棋盘 + 掷骰坞 + 题目覆盖层 + 结算卡
struct BoardLevelView: View {
    let subject: String
    let index: Int
    let totalLevels: Int
    let title: String
    let subtitle: String?
    let board: Board
    let steps: [Step]
    @Binding var route: Route
    @Binding var confetti: Int

    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound

    private enum Phase: Equatable {
        case intro       // teach 开场卡
        case roll        // 等待掷骰
        case moving      // 蹦跳中
        case question    // 题目覆盖层
    }

    @State private var flow = BoardFlow()
    @State private var phase: Phase = .roll
    @State private var started = false
    @State private var dieFace = 6
    @State private var rolling = false
    @State private var hopTick = 0
    @State private var questionStep: Step?
    @State private var coinBurstSpace: Int?

    private var config: SubjectConfig { SubjectConfig.map[subject] ?? SubjectConfig.map["cn"]! }
    private var theme: AppTheme { config.theme }
    private var n: Int { board.spaces.count }
    private var initialPhase: Phase { steps.first?.kind == "teach" ? .intro : .roll }

    var body: some View {
        ZStack {
            VStack(spacing: 10) {
                header
                boardArea
            }
            .padding(.horizontal, 22)
            .padding(.top, 8)

            if phase == .intro, let teach = steps.first {
                StepContainerView(step: teach,
                                  subject: subject,
                                  onWrong: {},
                                  onNext: { phase = .roll },
                                  onCorrectCelebrate: {})
                    .padding(.horizontal, 22)
                    .padding(.top, 8)
                    .transition(.opacity)
            }

            if phase == .question, let step = questionStep {
                questionOverlay(step)
            }

            if flow.finished {
                FinishCardView(subject: subject,
                               index: index,
                               totalLevels: totalLevels,
                               stars: flow.stars,
                               wrongCount: flow.wrongCount,
                               onNext: goNext,
                               onReplay: replay,
                               route: $route)
            }
        }
        .onAppear {
            if !started {
                started = true
                phase = initialPhase
            }
        }
    }

    // MARK: 头部

    private var header: some View {
        HStack(spacing: 14) {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            VStack(alignment: .leading, spacing: 1) {
                Text("\(config.title) · \(title)")
                    .font(.kidHead(22))
                    .foregroundColor(theme.titleStroke)
                Text("关卡进度 \(index + 1) / \(totalLevels) · \(subtitle ?? "")")
                    .font(.kidBody(14))
                    .foregroundColor(.inkSoft)
            }
            Spacer()
            Text("格子 \(min(max(flow.position + 1, 0), n)) / \(n)")
                .font(.kidBody(15))
                .foregroundColor(.inkSoft)
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    // MARK: 棋盘布局（蛇形两行：上行左→右、下行右→左；起点在首格上方、城堡在末格左下）

    private static func point(_ pos: Int, n: Int, in size: CGSize) -> CGPoint {
        let x0 = 0.18 * size.width, x1 = 0.86 * size.width
        let yT = 0.26 * size.height, yB = 0.64 * size.height
        if pos == -1 { return CGPoint(x: x0, y: yT - 0.26 * size.height) }
        if pos == n { return CGPoint(x: x0 - 0.07 * size.width, y: yB + 0.2 * size.height) }
        let top = Int(ceil(Double(n) / 2.0))
        if pos < top {
            let t = top == 1 ? 0.0 : Double(pos) / Double(top - 1)
            return CGPoint(x: x0 + (x1 - x0) * t,
                           y: yT + sin(t * 4.4) * 0.045 * size.height)
        }
        let bot = n - top
        let t = bot == 1 ? 0.0 : Double(pos - top) / Double(bot - 1)
        return CGPoint(x: x1 - (x1 - x0) * t,
                       y: yB + sin(t * 4.4) * 0.045 * size.height)
    }

    private func path(in size: CGSize) -> Path {
        var path = Path()
        path.move(to: Self.point(-1, n: n, in: size))
        for i in 0...n {
            path.addLine(to: Self.point(i, n: n, in: size))
        }
        return path
    }

    private var boardArea: some View {
        GeometryReader { geo in
            let size = geo.size
            ZStack {
                path(in: size)
                    .stroke(.white, style: StrokeStyle(lineWidth: 8, lineCap: .round, dash: [1, 20]))
                    .opacity(0.92)

                let startP = Self.point(-1, n: n, in: size)
                IconView(name: "flag", size: 30)
                    .position(x: startP.x - 46, y: startP.y - 4)

                ForEach(0..<n, id: \.self) { i in
                    spaceView(i)
                        .position(Self.point(i, n: n, in: size))
                }

                IconView(name: "castle", size: 60)
                    .position(Self.point(n, n: n, in: size))

                IconView(name: index % 2 == 0 ? "mario" : "dino", size: 54)
                    .shadow(color: .black.opacity(0.25), radius: 4, y: 3)
                    .modifier(HopBounceModifier(tick: hopTick))
                    .position(Self.point(flow.position, n: n, in: size))
                    .animation(.easeInOut(duration: 0.3), value: flow.position)
                    .allowsHitTesting(false)

                if let cs = coinBurstSpace {
                    CoinBurstView()
                        .position(Self.point(cs, n: n, in: size))
                }

                if phase == .roll {
                    diceDock
                        .position(x: size.width / 2, y: size.height - 56)
                }
            }
        }
    }

    @ViewBuilder
    private func spaceView(_ i: Int) -> some View {
        let sp = board.spaces[i]
        ZStack {
            Circle()
                .fill(LinearGradient(colors: sp.type == "coin"
                                     ? [Color(hex: 0xC9EFFB), Color(hex: 0x6FC9EE)]
                                     : [Color(hex: 0xFFE9AE), Color(hex: 0xF5B93B)],
                                     startPoint: .top, endPoint: .bottom))
                .frame(width: 64, height: 64)
                .overlay(Circle().stroke(.white, lineWidth: 4))
                .shadow(color: .black.opacity(0.16), radius: 5, y: 4)
            IconView(name: sp.type == "coin" ? "coin" : "question", size: 34)
        }
        .opacity(i < flow.position ? 0.55 : 1)
        .scaleEffect(i == flow.position ? 1.12 : 1)
        .modifier(NodePulse(active: i == flow.position && !flow.finished))
    }

    private var diceDock: some View {
        VStack(spacing: 8) {
            Button {
                rollDice()
            } label: {
                HStack(spacing: 14) {
                    DieFaceView(face: dieFace, size: 64)
                        .rotation3DEffect(.degrees(rolling ? 10 : 0), axis: (x: 1, y: 1, z: 0))
                    Text("掷骰子，前进！")
                        .font(.kidHead(23))
                        .foregroundColor(Color(hex: 0x7A4A00))
                }
                .padding(.horizontal, 28)
                .padding(.vertical, 10)
                .background(
                    Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFDD7A), .brandYellow, .brandYellowDk],
                                                  startPoint: .top, endPoint: .bottom))
                )
                .overlay(Capsule().stroke(.white, lineWidth: 3))
                .shadow(color: .brandYellowDk.opacity(0.55), radius: 0, y: 5)
            }
            .buttonStyle(.plain)
            .disabled(rolling)

            Text("掷到几就走几格，答对题目 +2 金币")
                .font(.kidBody(14))
                .foregroundColor(.ink)
                .padding(.horizontal, 16)
                .padding(.vertical, 5)
                .background(Capsule().fill(Color(hex: 0xFFFDF6).opacity(0.9)))
                .shadow(color: .black.opacity(0.12), radius: 3, y: 2)
        }
    }

    // MARK: 玩法推进

    private func rollDice() {
        guard phase == .roll, !rolling else { return }
        rolling = true
        Task { @MainActor in
            // 复用既有 0.8s 滚动落定手感（与 DiceStepView/模拟器 rollDie 同源）
            for _ in 0..<10 {
                dieFace = Int.random(in: 1...6)
                try? await Task.sleep(nanoseconds: 80_000_000)
            }
            let r = Int.random(in: 1...6)
            dieFace = r
            rolling = false
            toast.show("掷出 \(r) 点！", seconds: 1.4)
            phase = .moving
            hop(by: r)
        }
    }

    private func hop(by r: Int) {
        let target = min(flow.position + r, n)
        Task { @MainActor in
            while flow.position < target {
                flow.advanceOne(spaceCount: n)
                hopTick += 1
                sound.systemTap()
                try? await Task.sleep(nanoseconds: 360_000_000)
            }
            arrive()
        }
    }

    private func arrive() {
        if flow.finished { return }   // 到城堡 → FinishCardView 浮现
        let sp = board.spaces[flow.position]
        switch sp.type {
        case "question":
            questionStep = steps.first { $0.id == sp.step }
            phase = .question
        case "coin":
            sound.coin()
            withAnimation(.spring(response: 0.4, dampingFraction: 0.6)) { coinBurstSpace = flow.position }
            store.recordCoin(.coinSpace, amount: 5)   // 金币格 +5 经账本（工单04）
            toast.show("金币格 +5 金币！", seconds: 1.6)
            Task { @MainActor in
                try? await Task.sleep(nanoseconds: 900_000_000)
                withAnimation { coinBurstSpace = nil }
                phase = .roll
            }
        default:
            phase = .roll
        }
    }

    private func questionOverlay(_ step: Step) -> some View {
        ZStack {
            Color.black.opacity(0.42).ignoresSafeArea()
            StepContainerView(step: step,
                              subject: subject,
                              onWrong: { flow.registerWrong() },
                              onNext: {
                store.recordCoin(.answer, amount: 2)   // 题目格答对 +2 经账本（工单04）
                sound.coin()
                toast.show("答对啦 +2 金币！", seconds: 1.4)
                questionStep = nil
                phase = .roll
                              },
                              onCorrectCelebrate: { confetti += 1 })
                .frame(maxWidth: 940, maxHeight: 560)
        }
        .transition(.opacity)
    }

    private func replay() {
        flow = BoardFlow()
        questionStep = nil
        coinBurstSpace = nil
        phase = initialPhase
    }

    private func goNext() {
        // 同分支路由切换不销毁视图身份，@State 会残留 → 逐关复位
        flow = BoardFlow()
        questionStep = nil
        coinBurstSpace = nil
        route = .level(subject: subject, index: index + 1)
    }
}
