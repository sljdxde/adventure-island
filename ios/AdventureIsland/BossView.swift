import SwiftUI

// MARK: - Boss 大挑战关（v0.8 工单06）
// 双方各 3 心：答对打 boss 掉一心，答错被撞掉一心（幸运蘑菇可豁免一次）；
// boss 先空 → 胜利 +15 金币（走账本），玩家先空 → 友好失败、零损失可重试。
// 纯逻辑在 BossFlow（Models.swift），本视图只渲染。

struct BossLevelView: View {
    let subject: String
    let index: Int
    let levelId: String
    let totalLevels: Int
    let title: String
    let subtitle: String?
    let steps: [Step]
    @Binding var route: Route
    @Binding var confetti: Int

    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound

    @State private var flow = BossFlow()
    @State private var started = false
    @State private var rewardGiven = false
    // 受击演出
    @State private var bossKnock = CGFloat.zero
    @State private var playerBump = CGFloat.zero
    @State private var playerFlash = false

    private var config: SubjectConfig { SubjectConfig.map[subject] ?? SubjectConfig.map["cn"]! }
    private var theme: AppTheme { config.theme }
    private var questionCount: Int { steps.count }
    private var currentStep: Step? { steps[safe: flow.questionIndex] }

    var body: some View {
        ZStack {
            VStack(spacing: 8) {
                header
                bossZone
                questionZone
                playerZone
                Spacer(minLength: 0)
            }
            .padding(.horizontal, 22)
            .padding(.top, 8)

            if flow.outcome == .won { winCard }
            if flow.outcome == .lost { loseCard }
        }
        .onAppear {
            if !started { started = true }
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
            if store.snapshot.mushroomBuff {
                IconView(name: "mushroom", size: 30)
                    .modifier(NodePulse(active: true))
            }
            Text("第 \(min(flow.questionIndex + 1, questionCount)) / \(questionCount) 题")
                .font(.kidBody(15))
                .foregroundColor(.inkSoft)
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    // MARK: Boss 区（心条 + 大壳壳兽）

    private var bossZone: some View {
        VStack(spacing: 2) {
            HStack(spacing: 10) {
                Text("大壳壳兽")
                    .font(.kidHead(18))
                    .foregroundColor(Color(hex: 0x35623A))
                HeartBar(remaining: flow.bossHearts, size: 30)
                Spacer()
            }
            .padding(.leading, 120)
            IconView(name: "boss", size: 158)
                .shadow(color: .black.opacity(0.22), radius: 10, y: 7)
                .offset(x: bossKnock)
                .rotationEffect(.degrees(bossKnock == 0 ? 0 : -8))
                .allowsHitTesting(false)
        }
    }

    // MARK: 题目区（卡片内嵌一题，不做全屏遮罩，避免遮挡双方心条）

    private var questionZone: some View {
        StickerCard(corner: 26) {
            Group {
                if let step = currentStep {
                    StepContainerView(step: step,
                                      subject: subject,
                                      onWrong: handleWrong,
                                      onNext: handleCorrect,
                                      onCorrectCelebrate: { confetti += 1 })
                } else {
                    Text("…").font(.kidHead(28))
                }
            }
            .frame(maxWidth: .infinity)
            .frame(height: 236)
            .padding(.horizontal, 26)
            .padding(.vertical, 12)
        }
        .padding(.horizontal, 30)
    }

    // MARK: 玩家区（头像 + 心条）

    private var playerZone: some View {
        HStack(spacing: 10) {
            IconView(name: store.snapshot.mushroomBuff ? "mushroom" : "girl", size: 52)
                .shadow(color: .black.opacity(0.2), radius: 4, y: 3)
                .offset(y: playerBump)
                .overlay(
                    Circle()
                        .fill(Color(hex: 0xE84838))
                        .opacity(playerFlash ? 0.45 : 0)
                )
            Text("我")
                .font(.kidHead(18))
                .foregroundColor(.ink)
            HeartBar(remaining: flow.playerHearts, size: 30)
            Spacer()
        }
        .padding(.leading, 120)
    }

    // MARK: 判题

    private func handleWrong() {
        // 幸运蘑菇（决策 8）：持有则消耗一朵，本次不掉心
        if store.consumeMushroomIfHeld() {
            toast.show("🍄 幸运蘑菇挡了一下：这次不掉心！", seconds: 2.0)
            return
        }
        sound.wrong()
        withAnimation(.spring(response: 0.25, dampingFraction: 0.4)) { playerBump = -16; playerFlash = true }
        flow.answerWrong(questionCount: questionCount)
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: 280_000_000)
            withAnimation(.spring(response: 0.35, dampingFraction: 0.55)) { playerBump = 0; playerFlash = false }
        }
    }

    private func handleCorrect() {
        sound.correct()
        withAnimation(.spring(response: 0.22, dampingFraction: 0.35)) { bossKnock = 34 }
        flow.answerCorrect(questionCount: questionCount)
        Task { @MainActor in
            try? await Task.sleep(nanoseconds: 260_000_000)
            withAnimation(.spring(response: 0.35, dampingFraction: 0.55)) { bossKnock = 0 }
        }
    }

    // MARK: 胜利结算

    private var winCard: some View {
        ZStack {
            Color.black.opacity(0.42).ignoresSafeArea()
            VStack(spacing: 12) {
                HStack(spacing: 18) {
                    IconView(name: "star", size: 56)
                    IconView(name: "boss", size: 92)
                        .rotationEffect(.degrees(180))
                        .opacity(0.85)
                    IconView(name: "party", size: 56)
                }
                Text("打败大壳壳兽啦！")
                    .font(.kidTitle(30))
                    .foregroundColor(.ink)
                HStack(spacing: 10) {
                    ForEach(0..<3, id: \.self) { i in
                        IconView(name: "starface", size: 42)
                            .opacity(i < flow.stars ? 1 : 0.25)
                            .scaleEffect(i < flow.stars ? 1 : 0.8)
                    }
                }
                GoldChip(icon: "coin", text: "Boss 奖励 +15 金币！")
                Text("星星和金币都收好啦，你是学科小勇士～")
                    .font(.kidBody(15))
                    .foregroundColor(.inkSoft)
                HStack(spacing: 16) {
                    Button {
                        route = .map
                    } label: {
                        Label("返回地图", systemImage: "map").font(.kidHead(19))
                    }
                    .buttonStyle(.jellyGreen)
                    Button(action: replay) {
                        Label("再玩一次", systemImage: "arrow.counterclockwise").font(.kidHead(19))
                    }
                    .buttonStyle(.jellyCream)
                }
            }
            .padding(40)
            .background(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(LinearGradient(colors: [.white, .creamDk], startPoint: .top, endPoint: .bottom))
            )
            .overlay(RoundedRectangle(cornerRadius: 34, style: .continuous).stroke(.brandYellow, lineWidth: 5))
            .shadow(color: .black.opacity(0.3), radius: 26)
        }
        .onAppear {
            guard !rewardGiven else { return }
            rewardGiven = true
            // 星级记账（地图展示）+ boss 奖励 15 金币走账本；答对不另发 +2
            store.completeLevel(subject: subject, levelId: levelId, stars: flow.stars)
            store.recordCoin(.boss, amount: 15)
            confetti += 1
        }
    }

    // MARK: 失败（零损失重试）

    private var loseCard: some View {
        ZStack {
            Color.black.opacity(0.42).ignoresSafeArea()
            VStack(spacing: 12) {
                HStack(spacing: 14) {
                    IconView(name: "girl", size: 64)
                        .rotationEffect(.degrees(-18))
                    IconView(name: "boss", size: 96)
                }
                Text("哎呀，被撞飞啦！")
                    .font(.kidTitle(28))
                    .foregroundColor(.ink)
                Text("没关系，星星和金币都还在，\n再挑战一次吧～")
                    .font(.kidBody(16))
                    .foregroundColor(.inkSoft)
                    .multilineTextAlignment(.center)
                HStack(spacing: 16) {
                    Button(action: retry) {
                        Label("再来一次", systemImage: "arrow.counterclockwise").font(.kidHead(19))
                    }
                    .buttonStyle(.jellyGreen)
                    Button {
                        route = .map
                    } label: {
                        Label("返回地图", systemImage: "map").font(.kidHead(19))
                    }
                    .buttonStyle(.jellyOrange)
                }
            }
            .padding(40)
            .background(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(LinearGradient(colors: [.white, .creamDk], startPoint: .top, endPoint: .bottom))
            )
            .overlay(RoundedRectangle(cornerRadius: 34, style: .continuous).stroke(.brandYellow, lineWidth: 5))
            .shadow(color: .black.opacity(0.3), radius: 26)
        }
    }

    // MARK: 复位

    private func replay() {
        flow.retry()
        rewardGiven = false
    }

    private func retry() {
        flow.retry()
    }
}

// MARK: - 心条（剩余红心 / 失去空心灰）

struct HeartBar: View {
    let remaining: Int
    var size: CGFloat = 28

    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<BossFlow.maxHearts, id: \.self) { i in
                IconView(name: "heart", size: size)
                    .grayscale(i < remaining ? 0 : 1)
                    .opacity(i < remaining ? 1 : 0.28)
                    .scaleEffect(i < remaining ? 1 : 0.82)
            }
        }
        .animation(.spring(response: 0.3, dampingFraction: 0.5), value: remaining)
    }
}
