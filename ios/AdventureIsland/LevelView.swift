import SwiftUI

// MARK: - 关卡页：步骤引擎（认一认 / 答题 / 点数 / 比多少）+ 结算

struct LevelView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var settings: SettingsStore
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @Binding var route: Route
    @Binding var confetti: Int

    let subject: String
    let index: Int

    @State private var content: SubjectFile?
    @State private var stepIndex = 0
    @State private var wrongCount = 0
    @State private var finished = false
    @State private var earnedCoins = 0

    private var level: Level? { content?.levels[safe: index] }
    private var step: Step? { level?.steps[safe: stepIndex] }
    private var theme: AppTheme { subject == "cn" ? .cn : .math }
    private var subjectTitle: String { content?.title ?? "" }

    var body: some View {
        ZStack {
            SceneBackground(theme: theme)

            VStack(spacing: 10) {
                header
                if let step {
                    ZStack {
                        switch step.kind {
                        case "teach": TeachStepView(step: step, onNext: advanceStep)
                        case "quiz": QuizStepView(step: step, onWrong: { wrongCount += 1 }) { confetti += 1 }
                        case "count": CountStepView(step: step) { confetti += 1 }
                        case "compare": CompareStepView(step: step) { confetti += 1 }
                        default: EmptyView()
                        }
                    }
                    .id(step.id)
                    .transition(.asymmetric(insertion: .move(edge: .trailing).combined(with: .opacity),
                                            removal: .move(edge: .leading).combined(with: .opacity)))
                    .animation(.easeInOut(duration: 0.3), value: stepIndex)
                }
            }
            .padding(.horizontal, 22)
            .padding(.top, 8)

            if finished { finishCard }
        }
        .onAppear {
            if content == nil {
                content = ContentLoader.load(SubjectFile.self, subject == "cn" ? "cn_levels" : "math_levels")
            }
            if subject == "cn" {
                // 学过的字进收集册
                if let char = level?.steps.first(where: { $0.kind == "teach" })?.char {
                    store.learnHanzi(char)
                }
            }
            speech.speak(level?.steps.first?.kind == "teach" ? "欢迎来到\(subjectTitle)！\(level?.subtitle ?? "")" : "欢迎来到\(subjectTitle)！\(level?.subtitle ?? "")")
        }
    }

    // MARK: 顶部

    private var header: some View {
        HStack(spacing: 14) {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            VStack(alignment: .leading, spacing: 1) {
                Text("\(subjectTitle) · \(level?.title ?? "")")
                    .font(.kidHead(22))
                    .foregroundColor(theme.titleStroke)
                Text("关卡进度 \(index + 1) / \(content?.levels.count ?? 0) · \(level?.subtitle ?? "")")
                    .font(.kidBody(14))
                    .foregroundColor(.inkSoft)
            }
            Spacer()
            StepChips(chips: stepChips)
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    private var stepChips: [StepChipState] {
        guard let steps = level?.steps else { return [] }
        return steps.enumerated().map { i, s in
            let name: String
            switch s.kind {
            case "teach": name = "认一认"
            case "quiz": name = "练一练"
            case "count": name = "数一数"
            default: name = "比一比"
            }
            return StepChipState(title: name, state: i < stepIndex ? .done : (i == stepIndex ? .now : .todo))
        }
    }

    // MARK: 步骤推进（认一认完成后手动进入下一步）

    private func advanceStep() {
        guard let total = level?.steps.count, stepIndex < total - 1 else { return }
        withAnimation(.easeInOut(duration: 0.3)) { stepIndex += 1 }
        Haptics.tap()
    }

    // MARK: 结算

    private var stars: Int {
        switch wrongCount {
        case 0: return 3
        case 1: return 2
        default: return 1
        }
    }

    private var finishCard: some View {
        ZStack {
            Color.black.opacity(0.4).ignoresSafeArea()
            VStack(spacing: 12) {
                Text("🎉").font(.system(size: 64))
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
                Text(wrongCount == 0 ? "一次没错，完美通关！" : "答错了 \(wrongCount) 次也没关系，你已经学会啦")
                    .font(.kidBody(16))
                    .foregroundColor(.inkSoft)
                HStack(spacing: 16) {
                    Button {
                        route = .map
                    } label: {
                        Label("返回地图", systemImage: "map")
                            .font(.kidHead(19))
                    }
                    .buttonStyle(.jellyOrange)
                    Button {
                        // 重玩本关
                        stepIndex = 0
                        wrongCount = 0
                        finished = false
                    } label: {
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
            store.completeLevel(subject: subject, index: index, stars: stars)
            earnedCoins = stars
        }
    }
}

// MARK: - 认一认（象形字演变）

struct TeachStepView: View {
    let step: Step
    let onNext: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @State private var showingChar = false

    var body: some View {
        HStack(spacing: 22) {
            // 左：演变卡
            VStack(spacing: 12) {
                Text("看一看：\(step.char ?? "") 是怎么变来的？")
                    .font(.kidHead(17))
                    .foregroundColor(.brandOrangeDdk)
                    .padding(.horizontal, 22)
                    .padding(.vertical, 8)
                    .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFE7A8), .brandYellow], startPoint: .top, endPoint: .bottom)))
                    .shadow(color: .goldDdk.opacity(0.5), radius: 0, x: 0, y: 3)

                ZStack {
                    IconView(name: step.morphFrom ?? "sunface", size: 210)
                        .opacity(showingChar ? 0 : 1)
                        .scaleEffect(showingChar ? 0.4 : 1)
                        .rotationEffect(.degrees(showingChar ? 30 : 0))
                    Text(step.char ?? "")
                        .font(.hanzi(170))
                        .foregroundColor(Color(hex: 0xE2582A))
                        .shadow(color: Color(hex: 0xFFD9A0), radius: 0, x: 0, y: 5)
                        .opacity(showingChar ? 1 : 0)
                        .scaleEffect(showingChar ? 1 : 0.4)
                }
                .frame(height: 260)
                .onReceive(Timer.publish(every: 2.6, on: .main, in: .common).autoconnect()) { _ in
                    withAnimation(.spring(response: 0.5, dampingFraction: 0.75)) {
                        showingChar.toggle()
                    }
                }

                HStack(spacing: 12) {
                    Text(step.pinyin ?? "")
                        .font(.kidTitle(34))
                        .foregroundColor(.white)
                        .padding(.horizontal, 26)
                        .padding(.vertical, 8)
                        .background(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .fill(LinearGradient(colors: [.brandCoral, .brandCoralDk], startPoint: .top, endPoint: .bottom))
                        )
                        .shadow(color: .brandCoralDdk, radius: 0, x: 0, y: 4)
                    Button {
                        speech.speak("\(step.pinyin ?? "")。\(step.char ?? "")。\(step.words?.first?.say ?? "")")
                        toast.show("🔊 播放读音")
                    } label: {
                        ZStack {
                            Circle().fill(LinearGradient(colors: [Color(hex: 0xFFDD7A), .brandYellowDk], startPoint: .top, endPoint: .bottom))
                            IconView(name: "speaker", size: 26)
                        }
                        .frame(width: 58, height: 58)
                        .shadow(color: .brandYellowDdk, radius: 0, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)
                }

                HStack(spacing: 10) {
                    ForEach(step.words ?? [], id: \.text) { w in
                        Button {
                            speech.speak(w.say ?? w.text)
                            toast.show("词卡：\(w.text)")
                        } label: {
                            HStack(spacing: 6) {
                                if let icon = w.icon { IconView(name: icon, size: 22) }
                                Text(w.text).font(.kidHead(18)).foregroundColor(Color(hex: 0xB06A00))
                            }
                            .padding(.horizontal, 15)
                            .padding(.vertical, 9)
                            .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(.white))
                            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(Color(hex: 0xFFE3B3), lineWidth: 2.5))
                            .shadow(color: Color(hex: 0xF2E2C4), radius: 0, x: 0, y: 3)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .frame(maxWidth: 470)
            .frame(maxHeight: .infinity)
            .modifier(StickerCardModifier())

            // 右：提示语与引导
            VStack(spacing: 14) {
                Text("点一点下面的语音喇叭，跟读两遍～")
                    .font(.kidHead(24))
                    .foregroundColor(.ink)
                Text("看太阳变成了什么字？盯住它 3 秒！")
                    .font(.kidBody(17))
                    .foregroundColor(.inkSoft)
                IconView(name: "panda", size: 110)
                    .offset(y: 8)
                Button {
                    onNext()
                } label: {
                    Label("练一练", systemImage: "arrow.right")
                        .font(.kidHead(20))
                }
                .buttonStyle(.jellyGreen)
                .padding(.top, 2)
            }
            .frame(maxWidth: .infinity)
            .frame(maxHeight: .infinity)
            .modifier(StickerCardModifier())
        }
    }
}

// MARK: - 答题

struct QuizStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongIndex: Int?
    @State private var dimOthers = false

    var body: some View {
        VStack(spacing: 22) {
            Text(step.question ?? "")
                .font(.kidHead(26))
                .foregroundColor(.ink)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
                .padding(.vertical, 13)
                .background(
                    Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFF3D8), Color(hex: 0xFFE9BC)], startPoint: .top, endPoint: .bottom))
                )
                .shadow(color: Color(hex: 0xF0DCAC), radius: 0, x: 0, y: 4)

            HStack(spacing: 26) {
                ForEach((step.options ?? []).indices, id: \.self) { i in
                    optionCard(i)
                }
            }

            if solved {
                Text(step.praise ?? "答对啦！")
                    .font(.kidHead(22))
                    .foregroundColor(.brandGreenDk)
            } else {
                Text("答错不扣分，大胆试！")
                    .font(.kidBody(15))
                    .foregroundColor(.inkSoft)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .onAppear { speech.speak(step.question ?? "") }
    }

    @ViewBuilder
    private func optionCard(_ i: Int) -> some View {
        let opt = step.options![i]
        Button {
            guard !solved else { return }
            if i == step.answer {
                solved = true
                sound.correct()
                speech.speak(step.praise ?? "答对啦！")
                onCorrectCelebrate()
            } else {
                wrongIndex = i
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "再想一想哦", seconds: 2.2)
                speech.speak(step.hint ?? "再想一想哦")
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
            }
        } label: {
            optionContent(opt)
        }
        .buttonStyle(.plain)
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(outlineColor(i), lineWidth: 5)
        )
        .background(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(bgColor(i))
        )
        .scaleEffect(solved && i == step.answer ? 1.06 : 1)
        .modifier(ShakeModifier(shake: wrongIndex == i))
        .opacity(dimOthers && i != step.answer && solved ? 0.4 : 1)
        .animation(.spring(response: 0.35, dampingFraction: 0.7), value: solved)
    }

    @ViewBuilder
    private func optionContent(_ opt: QuizOption) -> some View {
        if let text = opt.text {
            Text(text)
                .font(.hanzi(86))
                .foregroundColor(.ink)
                .frame(width: 165, height: 165)
        } else {
            IconView(name: opt.icon ?? "", size: 116)
                .frame(width: 165, height: 165)
        }
    }

    private func outlineColor(_ i: Int) -> Color {
        if solved && i == step.answer { return .brandGreen }
        if wrongIndex == i { return .brandCoral }
        return Color(hex: 0xF2E2C4)
    }
    private func bgColor(_ i: Int) -> Color {
        if solved && i == step.answer { return Color(hex: 0xEDFBF0) }
        return .white
    }
}

// MARK: - 点数（数鸭子）

struct CountStepView: View {
    let step: Step
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var counted: [Int] = []
    @State private var bubbles: [Int: Int] = [:]
    @State private var solved = false
    @State private var wrongValue: Int?
    @State private var duckSeed = UUID()

    private var total: Int { step.count ?? 0 }

    var body: some View {
        VStack(spacing: 20) {
            Text(step.question ?? "")
                .font(.kidHead(24))
                .foregroundColor(.ink)
                .padding(.horizontal, 26)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xE7F6FF)))
                .overlay(Capsule().stroke(Color(hex: 0xBFE4F7), lineWidth: 2))

            pond

            HStack(spacing: 26) {
                ForEach(step.countOptions ?? [], id: \.self) { n in
                    numberBlock(n)
                }
            }
        }
        .frame(maxWidth: 780)
        .frame(maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .onAppear { speech.speak(step.question ?? "") }
        .id(duckSeed)
    }

    private var pond: some View {
        ZStack(alignment: .topTrailing) {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(LinearGradient(colors: [Color(hex: 0xC9EFFB), Color(hex: 0x6FC9EE)], startPoint: .top, endPoint: .bottom))
            WaveShape()
                .fill(.white.opacity(0.4))
                .frame(height: 46)
                .frame(maxHeight: .infinity, alignment: .bottom)
            IconView(name: "flower", size: 30)
                .offset(x: -400, y: -60)
            HStack(spacing: 5) {
                Text("已数").font(.kidBody(15)).foregroundColor(.inkSoft)
                Text("\(counted.count)").font(.kidTitle(24)).foregroundColor(.brandBlueDk)
                Text("只").font(.kidBody(15)).foregroundColor(.inkSoft)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 7)
            .background(Capsule().fill(.white))
            .padding(12)

            // 小鸭排布（两行）
            GeometryReader { geo in
                let cols = min(total, 5)
                let rows = (total + cols - 1) / cols
                ForEach(0..<total, id: \.self) { i in
                    let row = i / cols
                    let col = i % cols
                    let inRow = min(cols, total - row * cols)
                    let x = (geo.size.width / CGFloat(inRow + 1)) * CGFloat(col + 1)
                    let y = (geo.size.height * 0.62) + CGFloat(row) * (geo.size.height * 0.28) - 20
                    duck(at: i)
                        .position(x: x, y: y)
                    if let n = bubbles[i] {
                        CountBubble(number: n)
                            .position(x: x, y: y - 58)
                    }
                }
            }
        }
        .frame(height: 205)
        .overlay(RoundedRectangle(cornerRadius: 24, style: .continuous).stroke(.white, lineWidth: 5))
    }

    private func duck(at i: Int) -> some View {
        Button {
            guard !counted.contains(i), !solved else { return }
            counted.append(i)
            let n = counted.count
            speech.speak("\(n)")
            withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                bubbles[i] = n
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) { bubbles[i] = nil }
        } label: {
            IconView(name: step.duckIcon ?? "duck", size: 56)
                .shadow(color: .black.opacity(0.18), radius: 4, y: 3)
                .opacity(counted.contains(i) ? 1 : 0.92)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(.brandYellow, lineWidth: counted.contains(i) ? 3 : 0)
                )
        }
        .buttonStyle(.plain)
    }

    private func numberBlock(_ n: Int) -> some View {
        Button {
            guard !solved else { return }
            if n == total {
                solved = true
                sound.correct()
                speech.speak("答对啦，一共\(n)只！")
                onCorrectCelebrate()
            } else {
                wrongValue = n
                sound.wrong()
                toast.show("再数一数：点一只小鸭数一个数", seconds: 2.0)
                speech.speak("再数一数：点一只小鸭数一个数")
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongValue = nil }
            }
        } label: {
            Text("\(n)")
                .font(.kidTitle(44))
                .foregroundColor(Color(hex: 0x8A5B00))
                .frame(width: 100, height: 92)
                .background(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                )
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
                .shadow(color: Color(hex: 0xB8770A).opacity(0.6), radius: 0, x: 0, y: 6)
        }
        .buttonStyle(.plain)
        .scaleEffect(solved && n == total ? 1.1 : 1)
        .modifier(ShakeModifier(shake: wrongValue == n))
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: solved)
    }
}

private struct CountBubble: View {
    let number: Int
    @State private var up = false
    var body: some View {
        ZStack {
            Circle()
                .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), .brandYellow], startPoint: .top, endPoint: .bottom))
                .frame(width: 42, height: 42)
                .overlay(Circle().stroke(Color(hex: 0xB8770A), lineWidth: 2.5))
            Text("\(number)")
                .font(.kidTitle(22))
                .foregroundColor(Color(hex: 0x8A5B00))
        }
        .shadow(color: .ink.opacity(0.2), radius: 4, y: 3)
        .onAppear {
            withAnimation(.easeOut(duration: 0.8)) { up = true }
        }
        .offset(y: up ? -34 : 0)
        .opacity(up ? 0 : 1)
    }
}

// MARK: - 比多少

struct CompareStepView: View {
    let step: Step
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongKey: String?

    var body: some View {
        VStack(spacing: 22) {
            Text(step.question ?? "")
                .font(.kidHead(26))
                .foregroundColor(.ink)
                .padding(.horizontal, 30)
                .padding(.vertical, 12)
                .background(Capsule().fill(Color(hex: 0xEAFBEF)))
                .overlay(Capsule().stroke(Color(hex: 0xBFE8C9), lineWidth: 2))

            HStack(spacing: 40) {
                plate(icon: step.leftIcon, count: step.leftCount, label: "左边")
                plate(icon: step.rightIcon, count: step.rightCount, label: "右边")
            }

            HStack(spacing: 20) {
                ForEach(step.compareOptions ?? [], id: \.key) { opt in
                    Button {
                        guard !solved else { return }
                        if opt.key == step.answerKey {
                            solved = true
                            sound.correct()
                            speech.speak(step.praise ?? "答对啦！")
                            onCorrectCelebrate()
                        } else {
                            wrongKey = opt.key
                            sound.wrong()
                            toast.show(step.hint ?? "一一对应比一比", seconds: 2.2)
                            speech.speak(step.hint ?? "一一对应比一比")
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongKey = nil }
                        }
                    } label: {
                        Text(opt.label)
                            .font(.kidHead(22))
                            .foregroundColor(solved && opt.key == step.answerKey ? Color(hex: 0x2F6B22) : .ink)
                            .padding(.horizontal, 28)
                            .padding(.vertical, 14)
                            .background(
                                Capsule().fill(solved && opt.key == step.answerKey
                                               ? AnyShapeStyle(LinearGradient(colors: [Color(hex: 0xC6F0A0), .brandGreen], startPoint: .top, endPoint: .bottom))
                                               : AnyShapeStyle(.white))
                            )
                            .overlay(Capsule().stroke(solved && opt.key == step.answerKey ? .brandGreenDk : Color(hex: 0xF2E2C4), lineWidth: 4))
                            .shadow(color: Color(hex: 0xE4D2AC), radius: 0, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)
                    .modifier(ShakeModifier(shake: wrongKey == opt.key))
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
        .onAppear { speech.speak(step.question ?? "") }
    }

    private func plate(icon: String?, count: Int?, label: String) -> some View {
        VStack(spacing: 8) {
            ZStack {
                Ellipse()
                    .fill(LinearGradient(colors: [.white, Color(hex: 0xF2EDDF)], startPoint: .top, endPoint: .bottom))
                    .frame(width: 270, height: 175)
                    .overlay(Ellipse().stroke(.white, lineWidth: 5))
                    .shadow(color: Color(hex: 0xE4D9C2), radius: 0, x: 0, y: 7)
                PlateGrid(icon: icon ?? "apple", count: count ?? 0)
                    .frame(width: 210, height: 120)
            }
            Text(label)
                .font(.kidBody(16))
                .foregroundColor(.inkSoft)
        }
    }
}

// MARK: - 通用修饰器

struct ShakeModifier: ViewModifier {
    var shake: Bool
    func body(content: Content) -> some View {
        content
            .modifier(ShakeEffect(animatableData: shake ? 1 : 0))
    }
}

struct ShakeEffect: GeometryEffect {
    var animatableData: CGFloat
    func effectValue(size: CGSize) -> ProjectionTransform {
        ProjectionTransform(CGAffineTransform(
            translationX: 12 * sin(animatableData * .pi * 4) * (1 - animatableData),
            y: 0
        ))
    }
}

struct EmojiFallback: ViewModifier {
    let emoji: String
    func body(content: Content) -> some View {
        content
    }
}

struct StickerCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .background(
                RoundedRectangle(cornerRadius: 30, style: .continuous)
                    .fill(LinearGradient(colors: [.white, .cream], startPoint: .top, endPoint: .bottom))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 30, style: .continuous)
                    .stroke(.white, lineWidth: 5)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 32, style: .continuous)
                    .stroke(Color.ink.opacity(0.07), lineWidth: 2)
            )
            .shadow(color: .ink.opacity(0.15), radius: 18, x: 0, y: 10)
    }
}

struct WaveShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let waveH = rect.height * 0.5
        p.move(to: CGPoint(x: 0, y: rect.maxY))
        p.addLine(to: CGPoint(x: 0, y: rect.midY))
        var x: CGFloat = 0
        while x < rect.width {
            p.addQuadCurve(
                to: CGPoint(x: x + rect.width / 8, y: rect.midY),
                control: CGPoint(x: x + rect.width / 16, y: rect.midY - waveH)
            )
            x += rect.width / 8
        }
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        p.closeSubpath()
        return p
    }
}

// 比多少盘子的格子排布
private struct PlateGrid: View {
    let icon: String
    let count: Int
    var body: some View {
        let cols = count <= 4 ? max(count, 1) : 5
        LazyVGrid(columns: Array(repeating: GridItem(.fixed(40), spacing: 4), count: cols), spacing: 3) {
            ForEach(0..<count, id: \.self) { _ in
                IconView(name: icon, size: 38)
            }
        }
    }
}

extension Array {
    subscript(safe index: Int) -> Element? {
        indices.contains(index) ? self[index] : nil
    }
}
