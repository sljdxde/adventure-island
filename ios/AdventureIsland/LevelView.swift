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
    private var config: SubjectConfig { SubjectConfig.map[subject] ?? SubjectConfig.map["cn"]! }
    private var theme: AppTheme { config.theme }
    private var subjectTitle: String { config.title }

    var body: some View {
        ZStack {
            // 相邻关卡轮换 白天/黄昏/星夜，场景有区别
            SceneBackground(theme: theme, variant: index % 3)

            VStack(spacing: 10) {
                header
                if let step {
                    ZStack {
                        switch step.kind {
                        case "teach": TeachStepView(step: step, onNext: advanceStep)
                        case "letter": LetterStepView(step: step, subject: subject, onNext: advanceStep)
                        case "listen": ListenStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "blend": BlendStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "arith": ArithStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "pattern": PatternStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "split": SplitStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "neighbor": NeighborStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "order": OrderStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "quiz": QuizStepView(step: step, onWrong: { wrongCount += 1 }, onNext: advanceStep) { confetti += 1 }
                        case "count": CountStepView(step: step, onNext: advanceStep) { confetti += 1 }
                        case "compare": CompareStepView(step: step, onNext: advanceStep) { confetti += 1 }
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
                content = ContentLoader.load(SubjectFile.self, config.file)
            }
            // 学过的内容进收集册
            if let teach = level?.steps.first(where: { $0.kind == "teach" }), let ch = teach.char {
                store.learnHanzi(ch)
            }
            if let letter = level?.steps.first(where: { $0.kind == "letter" }) {
                if subject == "pinyin", let l = letter.letters?.first { store.learnPinyin(l) }
                if subject == "english",
                   let word = letter.examples?.first?.text.components(separatedBy: " ").first {
                    store.learnEnglish(word)
                }
                if subject == "astro", let name = letter.display { store.learnAstro(name) }
            }
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
            case "letter": name = "学一学"
            case "listen": name = "找一找"
            case "quiz": name = "练一练"
            case "count": name = "数一数"
            case "blend": name = "拼一拼"
            case "arith": name = "算一算"
            case "pattern": name = "找规律"
            case "split": name = "分一分"
            case "order": name = "排一排"
            case "neighbor": name = "填一填"
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
        let total = content?.levels.count ?? 0
        let hasNext = index + 1 < total
        return ZStack {
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
                    if hasNext {
                        Button {
                            goNextLevel()
                        } label: {
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

    /// 直接进入下一关（通关卡按钮）
    private func goNextLevel() {
        stepIndex = 0
        wrongCount = 0
        finished = false
        route = .level(subject: subject, index: index + 1)
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
                Text("看一看：图片变成了什么字？")
                    .font(.kidHead(24))
                    .foregroundColor(.ink)
                Text("想听读音可以点小喇叭哦（不出声也可以）")
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
    let onNext: () -> Void
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
    }

    @ViewBuilder
    private func optionCard(_ i: Int) -> some View {
        let opt = step.options![i]
        Button {
            guard !solved else { return }
            if i == step.answer {
                solved = true
                sound.correct()
                onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
            } else {
                wrongIndex = i
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "再想一想哦", seconds: 2.2)
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
        if let icon = opt.icon {
            VStack(spacing: 4) {
                IconView(name: icon, size: 100)
                if let text = opt.text {
                    Text(text)
                        .font(.kidHead(16))
                        .foregroundColor(.inkSoft)
                        .lineLimit(1)
                        .minimumScaleFactor(0.7)
                }
            }
            .frame(width: 165, height: 165)
        } else if let text = opt.text {
            Text(text)
                .font(.hanzi(86))
                .foregroundColor(.ink)
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
    let onNext: () -> Void
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
        .id(duckSeed)
    }

    // 点数场景：pond 池塘 / sky 白天 / night 星夜 / grass 草地（与关卡情境配套）
    private var backdropColors: (Color, Color, Color) {
        switch step.backdrop {
        case "night": return (Color(hex: 0x2E3A87), Color(hex: 0x4A5AB8), Color(hex: 0x8C9BE8))
        case "sky": return (Color(hex: 0xE0F4FF), Color(hex: 0xA6DBF8), Color(hex: 0x8FC9EC))
        case "grass": return (Color(hex: 0xE8F6CF), Color(hex: 0xB4E18E), Color(hex: 0x8FC96B))
        default: return (Color(hex: 0xC9EFFB), Color(hex: 0x6FC9EE), Color(hex: 0xBFE4F7))
        }
    }

    private var backdropDecor: some View {
        switch step.backdrop {
        case "night":
            return AnyView(ZStack {
                ForEach(0..<8, id: \.self) { i in
                    Circle()
                        .fill(.white.opacity(0.85))
                        .frame(width: 4, height: 4)
                        .position(x: CGFloat([0.08, 0.2, 0.33, 0.46, 0.58, 0.71, 0.84, 0.95][i]) * 760,
                                  y: CGFloat([0.14, 0.3, 0.1, 0.26, 0.12, 0.32, 0.16, 0.28][i]) * 205)
                }
                IconView(name: "moon", size: 30).position(x: 690, y: 34)
            })
        case "sky":
            return AnyView(ZStack {
                CloudShape().fill(.white.opacity(0.75)).frame(width: 90, height: 26).position(x: 110, y: 40)
                CloudShape().fill(.white.opacity(0.65)).frame(width: 64, height: 20).position(x: 640, y: 28)
            })
        case "grass":
            return AnyView(ZStack {
                IconView(name: "flower", size: 26).position(x: 52, y: 160)
                IconView(name: "sprout", size: 24).position(x: 700, y: 168)
                IconView(name: "tree", size: 34).position(x: 726, y: 52)
            })
        default:
            return AnyView(ZStack {
                WaveShape().fill(.white.opacity(0.4)).frame(height: 46).frame(maxHeight: .infinity, alignment: .bottom)
                IconView(name: "flower", size: 30).offset(x: -400, y: -60)
            })
        }
    }

    private var unitWord: String { step.unit ?? "个" }

    private var pond: some View {
        let (top, bottom, stroke) = backdropColors
        return ZStack(alignment: .topTrailing) {
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .fill(LinearGradient(colors: [top, bottom], startPoint: .top, endPoint: .bottom))
            backdropDecor
            HStack(spacing: 5) {
                Text("已数").font(.kidBody(15)).foregroundColor(.inkSoft)
                Text("\(counted.count)").font(.kidTitle(24)).foregroundColor(.brandBlueDk)
                Text(unitWord).font(.kidBody(15)).foregroundColor(.inkSoft)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 7)
            .background(Capsule().fill(.white))
            .padding(12)

            // 情境道具排布（两行）
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
        .overlay(RoundedRectangle(cornerRadius: 24, style: .continuous).stroke(stroke, lineWidth: 5))
    }

    private func duck(at i: Int) -> some View {
        Button {
            guard !counted.contains(i), !solved else { return }
            counted.append(i)
            let n = counted.count
            Haptics.tap()
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
                onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
            } else {
                wrongValue = n
                sound.wrong()
                toast.show("再数一数：点一个数一个数", seconds: 2.0)
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
    let onNext: () -> Void
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
                            onCorrectCelebrate()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
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

// MARK: - 认字母（拼音声母/韵母、英语字母）

struct LetterStepView: View {
    let step: Step
    let subject: String
    let onNext: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @State private var bounce = false

    private var isEnglish: Bool { subject == "english" }
    private var isAstro: Bool { subject == "astro" }
    private var accent: Color {
        if isEnglish { return .brandGreenDk }
        if isAstro { return Color(hex: 0x4A5AB8) }
        return .brandOrangeDdk
    }
    private var guideIcon: String { isEnglish || isAstro ? "robot" : "panda" }

    var body: some View {
        HStack(spacing: 22) {
            VStack(spacing: 14) {
                Text(step.question ?? "学一学")
                    .font(.kidHead(17))
                    .foregroundColor(accent)
                    .padding(.horizontal, 22)
                    .padding(.vertical, 8)
                    .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFE7A8), .brandYellow], startPoint: .top, endPoint: .bottom)))
                    .shadow(color: .goldDdk.opacity(0.5), radius: 0, x: 0, y: 3)

                // 大字母卡
                ZStack {
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .fill(LinearGradient(colors: [.white, Color(hex: 0xFFF6E0)], startPoint: .top, endPoint: .bottom))
                        .frame(width: 250, height: 250)
                        .overlay(RoundedRectangle(cornerRadius: 28, style: .continuous).stroke(.brandYellow, lineWidth: 5))
                        .shadow(color: .goldDdk.opacity(0.35), radius: 0, x: 0, y: 6)
                    VStack(spacing: 2) {
                        let disp = step.display ?? step.letters?.first ?? "?"
                        Text(disp)
                            .font(.system(size: disp.count >= 3 ? 62 : (disp.count == 2 ? 88 : 140),
                                          weight: .heavy,
                                          design: isEnglish ? .rounded : .default))
                            .foregroundStyle(
                                LinearGradient(colors: [accent, accent.opacity(0.75)], startPoint: .top, endPoint: .bottom)
                            )
                            .shadow(color: accent.opacity(0.25), radius: 0, y: 3)
                        if let extra = step.letters, extra.count > 1 {
                            Text("本关字母：" + extra.joined(separator: " "))
                                .font(.kidBody(14))
                                .foregroundColor(.inkSoft)
                        }
                    }
                }
                .scaleEffect(bounce ? 1.05 : 1)
                .onAppear {
                    withAnimation(.spring(response: 0.5, dampingFraction: 0.5).repeatForever(autoreverses: true)) {
                        bounce = true
                    }
                }

                HStack(spacing: 12) {
                    Button {
                        speech.speak(isEnglish ? (step.display ?? "A") : (step.display ?? "a"))
                        toast.show("🔊 播放读音")
                    } label: {
                        HStack(spacing: 8) {
                            IconView(name: "speaker", size: 22)
                            Text(isEnglish ? "Listen" : "读一读").font(.kidHead(19))
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 11)
                        .background(Capsule().fill(LinearGradient(colors: [.brandCoral, .brandCoralDk], startPoint: .top, endPoint: .bottom)))
                        .shadow(color: .brandCoralDdk, radius: 0, x: 0, y: 4)
                    }
                    .buttonStyle(.plain)
                }

                HStack(spacing: 10) {
                    ForEach(step.examples ?? [], id: \.text) { ex in
                        Button {
                            speech.speak(ex.say ?? ex.text)
                            toast.show("例词：\(ex.text)")
                        } label: {
                            HStack(spacing: 6) {
                                if let icon = ex.icon { IconView(name: icon, size: 24) }
                                Text(ex.text).font(.kidHead(17)).foregroundColor(Color(hex: 0xB06A00))
                            }
                            .padding(.horizontal, 14)
                            .padding(.vertical, 9)
                            .background(RoundedRectangle(cornerRadius: 14, style: .continuous).fill(.white))
                            .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(Color(hex: 0xFFE3B3), lineWidth: 2.5))
                            .shadow(color: Color(hex: 0xF2E2C4), radius: 0, x: 0, y: 3)
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .frame(maxWidth: 460)
            .frame(maxHeight: .infinity)
            .modifier(StickerCardModifier())

            // 右：引导
            VStack(spacing: 12) {
                Text(isEnglish ? "Look and say!\n看一看，读一读～" : (isAstro ? "认识新朋友啦！\n看一看，读一读～" : "看卡片，读一读～（不出声也可以）"))
                    .font(.kidHead(22))
                    .multilineTextAlignment(.center)
                IconView(name: guideIcon, size: 100)
                Text(isEnglish ? "Then tap the green button!" : "认完了？点下面的绿色按钮继续")
                    .font(.kidBody(15))
                    .foregroundColor(.inkSoft)
                Button {
                    onNext()
                } label: {
                    Label(isEnglish ? "Next" : "下一步", systemImage: "arrow.right")
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

// MARK: - 找一找（listen：视觉匹配，朗读可选 —— 适配无声音环境）

struct ListenStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongIndex: Int?

    var body: some View {
        VStack(spacing: 18) {
            Text(step.question ?? "找一找，选一选")
                .font(.kidHead(25))
                .foregroundColor(.ink)

            // 目标大卡：题目直接展示要找的字/字母，不依赖声音
            ZStack {
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                    .frame(width: 168, height: 118)
                    .shadow(color: Color(hex: 0xB8770A).opacity(0.55), radius: 0, x: 0, y: 6)
                Text(step.prompt ?? step.speakText ?? "?")
                    .font(.system(size: promptSize, weight: .heavy))
                    .foregroundColor(.white)
                    .shadow(color: Color(hex: 0xB8770A), radius: 0, x: 1, y: 3)
            }

            HStack(spacing: 26) {
                ForEach((step.options ?? []).indices, id: \.self) { i in
                    let opt = step.options![i]
                    Button {
                        guard !solved else { return }
                        if i == step.answer {
                            solved = true
                            sound.correct()
                            onCorrectCelebrate()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
                        } else {
                            wrongIndex = i
                            sound.wrong()
                            onWrong()
                            toast.show(step.hint ?? "再找一找哦", seconds: 2.2)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
                        }
                    } label: {
                        Group {
                            if let icon = opt.icon {
                                VStack(spacing: 4) {
                                    IconView(name: icon, size: 96)
                                    if let text = opt.text {
                                        Text(text)
                                            .font(.kidHead(17))
                                            .foregroundColor(.inkSoft)
                                    }
                                }
                            } else if let text = opt.text {
                                Text(text)
                                    .font(.hanzi(isEnglishLetter(text) ? 76 : 72))
                                    .foregroundColor(.ink)
                            }
                        }
                        .frame(width: 158, height: 158)
                    }
                    .buttonStyle(.plain)
                    .background(
                        RoundedRectangle(cornerRadius: 28, style: .continuous)
                            .fill((solved && i == step.answer) ? Color(hex: 0xEDFBF0) : .white)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 28, style: .continuous)
                            .stroke(outline(i), lineWidth: 5)
                    )
                    .modifier(ShakeModifier(shake: wrongIndex == i))
                    .opacity(solved && i != step.answer ? 0.4 : 1)
                    .animation(.spring(response: 0.35, dampingFraction: 0.7), value: solved)
                }
            }

            if solved {
                Text(step.praise ?? "找对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            } else {
                // 朗读完全可选：想听再点，不做题的必要条件
                Button {
                    speech.speak(step.speakText ?? "")
                    toast.show("🔊 朗读：\(step.speakText ?? "")")
                } label: {
                    HStack(spacing: 8) {
                        IconView(name: "speaker", size: 20)
                        Text("想听点这里").font(.kidBody(15))
                    }
                    .foregroundColor(.inkSoft)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 8)
                    .background(Capsule().fill(.white.opacity(0.85)))
                    .overlay(Capsule().stroke(Color(hex: 0xF2E2C4), lineWidth: 2.5))
                }
                .buttonStyle(.plain)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private var promptSize: CGFloat {
        let p = step.prompt ?? ""
        if p.count <= 1 { return 74 }
        if p.count == 2 { return 54 }
        return 40
    }

    private func outline(_ i: Int) -> Color {
        if solved && i == step.answer { return .brandGreen }
        if wrongIndex == i { return .brandCoral }
        return Color(hex: 0xF2E2C4)
    }

    private func isEnglishLetter(_ t: String) -> Bool { t.count <= 3 && t.first?.isASCII == true }
}

// MARK: - 拼一拼（blend：声母+韵母）

struct BlendStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongIndex: Int?

    private var parts: [String] { step.parts ?? [] }

    var body: some View {
        VStack(spacing: 22) {
            Text(step.question ?? "拼一拼")
                .font(.kidHead(26))

            HStack(spacing: 16) {
                partCard(parts.first ?? "b")
                Text("—").font(.kidTitle(40)).foregroundColor(.inkSoft)
                partCard(parts.count > 1 ? parts[1] : "a")
                Text("=").font(.kidTitle(40)).foregroundColor(.inkSoft)
                ZStack {
                    RoundedRectangle(cornerRadius: 22, style: .continuous)
                        .fill(resultCardFill)
                    Text(solved ? (step.options?[safe: step.answer ?? 0]?.text ?? "?") : "?")
                        .font(.system(size: 64, weight: .heavy))
                        .foregroundColor(solved ? Color(hex: 0x2F6B22) : .inkSoft)
                }
                .frame(width: 130, height: 130)
                .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(.white, lineWidth: 4))
                .animation(.spring(response: 0.4, dampingFraction: 0.7), value: solved)
            }

            HStack(spacing: 20) {
                ForEach((step.options ?? []).indices, id: \.self) { i in
                    let opt = step.options![i]
                    Button {
                        guard !solved else { return }
                        if i == step.answer {
                            solved = true
                            sound.correct()
                            if let t = opt.text { speech.speak(step.praise ?? "拼对了！\(t)") }
                            onCorrectCelebrate()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
                        } else {
                            wrongIndex = i
                            sound.wrong()
                            onWrong()
                            toast.show(step.hint ?? "再拼一拼", seconds: 2.2)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
                        }
                    } label: {
                        Text(opt.text ?? "?")
                            .font(.system(size: 38, weight: .heavy, design: .rounded))
                            .foregroundColor(.ink)
                            .frame(width: 140, height: 84)
                            .background(
                                RoundedRectangle(cornerRadius: 20, style: .continuous)
                                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                            )
                            .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
                            .shadow(color: Color(hex: 0xB8770A).opacity(0.6), radius: 0, x: 0, y: 5)
                    }
                    .buttonStyle(.plain)
                    .modifier(ShakeModifier(shake: wrongIndex == i))
                }
            }

            if solved {
                Text(step.praise ?? "拼对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func partCard(_ t: String) -> some View {
        VStack {
            Text(t)
                .font(.system(size: 72, weight: .heavy, design: .rounded))
                .foregroundStyle(LinearGradient(colors: [.brandOrangeDk, .brandCoralDk], startPoint: .top, endPoint: .bottom))
        }
        .frame(width: 130, height: 130)
        .background(RoundedRectangle(cornerRadius: 22, style: .continuous).fill(.white))
        .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Color(hex: 0xFFE3B3), lineWidth: 4))
        .shadow(color: Color(hex: 0xF2E2C4), radius: 0, x: 0, y: 4)
    }
}

private let resultCardFill = LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom)

// MARK: - 算一算（arith：图示加减法）

struct ArithStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongValue: Int?

    private var isAdd: Bool { step.op != "-" }
    private var left: Int { step.leftCount ?? 0 }
    private var right: Int { step.rightCount ?? 0 }
    private var correct: Int { isAdd ? left + right : left - right }

    var body: some View {
        VStack(spacing: 18) {
            // 情境题干（如「3 个气球飞走 1 个，还剩几个？」）
            Text(step.question ?? (isAdd ? "合起来一共有多少？" : "走了一些后，还剩多少？"))
                .font(.kidHead(24))
                .foregroundColor(.ink)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 30)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xFFF3D8)))
                .overlay(Capsule().stroke(Color(hex: 0xF0DCAC), lineWidth: 2))

            // 图示等式
            HStack(alignment: .center, spacing: 14) {
                equationGroup
                Text(isAdd ? "+" : "−")
                    .font(.kidTitle(44))
                    .foregroundColor(.brandOrangeDdk)
                if isAdd {
                    VStack {
                        ForEach(0..<right, id: \.self) { _ in
                            IconView(name: step.leftIcon ?? "duck", size: 44)
                        }
                    }
                } else {
                    // 减法：右边显示被划掉的
                    VStack {
                        ForEach(0..<right, id: \.self) { _ in
                            IconView(name: step.leftIcon ?? "duck", size: 44)
                                .overlay(
                                    Rectangle()
                                        .fill(Color.clear)
                                        .overlay(
                                            GeometryReader { geo in
                                                Path { p in
                                                    p.move(to: CGPoint(x: 6, y: geo.size.height / 2))
                                                    p.addLine(to: CGPoint(x: geo.size.width - 6, y: geo.size.height / 2))
                                                }
                                                .stroke(.brandCoralDk, style: StrokeStyle(lineWidth: 5, lineCap: .round))
                                            }
                                        )
                                )
                                .opacity(0.55)
                        }
                    }
                }
                Text("=").font(.kidTitle(44)).foregroundColor(.inkSoft)
                ZStack {
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                    Text(solved ? "\(correct)" : "?")
                        .font(.kidTitle(46))
                        .foregroundColor(Color(hex: 0x8A5B00))
                }
                .frame(width: 92, height: 84)
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
                .shadow(color: Color(hex: 0xB8770A).opacity(0.5), radius: 0, x: 0, y: 5)
            }
            .padding(.vertical, 10)

            HStack(spacing: 26) {
                ForEach(step.arithOptions ?? [], id: \.self) { n in
                    numberBlock(n)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    @ViewBuilder
    private var equationGroup: some View {
        VStack {
            ForEach(0..<left, id: \.self) { _ in
                IconView(name: step.leftIcon ?? "duck", size: 44)
            }
        }
    }

    private func numberBlock(_ n: Int) -> some View {
        Button {
            guard !solved else { return }
            if n == correct {
                solved = true
                sound.correct()
                onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
            } else {
                wrongValue = n
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "数一数图里的东西", seconds: 2.0)
                speech.speak(step.hint ?? "数一数图里的东西")
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
        .scaleEffect(solved && n == correct ? 1.1 : 1)
        .modifier(ShakeModifier(shake: wrongValue == n))
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: solved)
    }
}

// MARK: - 找规律（pattern：序列观察 + 下一个是谁）

struct PatternStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongIndex: Int?

    private var seq: [String] { step.seq ?? [] }

    var body: some View {
        VStack(spacing: 24) {
            Text(step.question ?? "找规律：下一个是哪个？")
                .font(.kidHead(25))
                .foregroundColor(.ink)
                .padding(.horizontal, 30)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xF3EDFF)))
                .overlay(Capsule().stroke(Color(hex: 0xD9CCF5), lineWidth: 2))

            // 规律序列（最后一个是问号）
            HStack(spacing: 12) {
                ForEach(seq.indices, id: \.self) { i in
                    seqCard(seq[i])
                    if i < seq.count - 1 {
                        Text("→").font(.kidTitle(20)).foregroundColor(.inkSoft.opacity(0.6))
                    }
                }
                ZStack {
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .fill(LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom))
                    Text("?")
                        .font(.system(size: 44, weight: .heavy, design: .rounded))
                        .foregroundColor(.brandOrangeDdk)
                }
                .frame(width: 86, height: 86)
                .overlay(
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .stroke(Color(hex: 0xE8B54A), lineWidth: 4)
                )
                .shadow(color: Color(hex: 0xE8B54A).opacity(0.4), radius: 0, x: 0, y: 4)
            }

            HStack(spacing: 26) {
                ForEach((step.options ?? []).indices, id: \.self) { i in
                    let opt = step.options![i]
                    Button {
                        guard !solved else { return }
                        if i == step.answer {
                            solved = true
                            sound.correct()
                            onCorrectCelebrate()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.15) { onNext() }
                        } else {
                            wrongIndex = i
                            sound.wrong()
                            onWrong()
                            toast.show(step.hint ?? "读一读前面几个，找找谁在轮流出现", seconds: 2.4)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
                        }
                    } label: {
                        IconView(name: opt.icon ?? "question", size: 74)
                            .frame(width: 118, height: 118)
                    }
                    .buttonStyle(.plain)
                    .background(
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .fill((solved && i == step.answer) ? Color(hex: 0xEDFBF0) : .white)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .stroke(solved && i == step.answer ? .brandGreen : Color(hex: 0xF2E2C4),
                                    lineWidth: solved && i == step.answer ? 5 : 4)
                    )
                    .modifier(ShakeModifier(shake: wrongIndex == i))
                    .opacity(solved && i != step.answer ? 0.4 : 1)
                    .animation(.spring(response: 0.35, dampingFraction: 0.7), value: solved)
                }
            }

            if solved {
                Text(step.praise ?? "规律找对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func seqCard(_ icon: String) -> some View {
        ZStack {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(.white)
            IconView(name: icon, size: 58)
        }
        .frame(width: 86, height: 86)
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color(hex: 0xF2E2C4), lineWidth: 4))
        .shadow(color: Color(hex: 0xF2E2C4), radius: 0, x: 0, y: 4)
    }
}

// MARK: - 分一分（split：数的组成，total = part + ?）

struct SplitStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongValue: Int?

    private var total: Int { step.total ?? 0 }
    private var part: Int { step.part ?? 0 }
    private var rest: Int { total - part }
    private var unit: String { step.unit ?? "个" }

    var body: some View {
        VStack(spacing: 20) {
            Text(step.question ?? "分一分，另一边有几个？")
                .font(.kidHead(23))
                .foregroundColor(.ink)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 28)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xFFF3D8)))
                .overlay(Capsule().stroke(Color(hex: 0xF0DCAC), lineWidth: 2))

            // 总数徽章
            HStack(spacing: 8) {
                Text("一共").font(.kidBody(16)).foregroundColor(.inkSoft)
                Text("\(total)")
                    .font(.kidTitle(30))
                    .foregroundColor(Color(hex: 0x8A5B00))
                    .padding(.horizontal, 16)
                    .padding(.vertical, 3)
                    .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom)))
                    .overlay(Capsule().stroke(Color(hex: 0xB8770A), lineWidth: 2.5))
                Text(unit).font(.kidBody(16)).foregroundColor(.inkSoft)
            }

            // 两个盘：左边 part 个 + 右边 ?
            HStack(spacing: 22) {
                VStack(spacing: 6) {
                    ZStack {
                        Ellipse()
                            .fill(LinearGradient(colors: [.white, Color(hex: 0xF2EDDF)], startPoint: .top, endPoint: .bottom))
                            .frame(width: 220, height: 130)
                            .overlay(Ellipse().stroke(.white, lineWidth: 5))
                            .shadow(color: Color(hex: 0xE4D9C2), radius: 0, x: 0, y: 6)
                        PlateGrid(icon: step.leftIcon ?? "apple", count: part)
                            .frame(width: 170, height: 86)
                    }
                    Text("\(part)")
                        .font(.kidTitle(28))
                        .foregroundColor(.ink)
                }
                Text("+").font(.kidTitle(40)).foregroundColor(.inkSoft)
                VStack(spacing: 6) {
                    ZStack {
                        Ellipse()
                            .fill(LinearGradient(colors: [Color(hex: 0xFFFBF0), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom))
                            .frame(width: 220, height: 130)
                        if solved {
                            PlateGrid(icon: step.leftIcon ?? "apple", count: rest)
                                .frame(width: 170, height: 86)
                        } else {
                            Text("?")
                                .font(.kidTitle(52))
                                .foregroundColor(Color(hex: 0xC9BBA0))
                        }
                    }
                    .overlay(
                        Ellipse().stroke(
                            solved ? Color(hex: 0xBFE8C9) : Color(hex: 0xE0D2B6),
                            style: StrokeStyle(lineWidth: 4, dash: solved ? [] : [8, 6])
                        )
                    )
                    Text(solved ? "\(rest)" : "?")
                        .font(.kidTitle(28))
                        .foregroundColor(solved ? .brandGreenDk : Color(hex: 0xC9BBA0))
                }
            }

            HStack(spacing: 26) {
                ForEach(step.arithOptions ?? [], id: \.self) { n in
                    numberBlock(n)
                }
            }

            if solved {
                Text(step.praise ?? "分对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func numberBlock(_ n: Int) -> some View {
        Button {
            guard !solved else { return }
            if n == rest {
                solved = true
                sound.correct()
                onCorrectCelebrate()
                DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
            } else {
                wrongValue = n
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "数一数两边合起来", seconds: 2.2)
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
        .scaleEffect(solved && n == rest ? 1.1 : 1)
        .modifier(ShakeModifier(shake: wrongValue == n))
        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: solved)
    }
}

// MARK: - 排一排（order：按大小顺序依次点数字）

struct OrderStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var progress = 0
    @State private var doneIdx: Set<Int> = []
    @State private var wrongIndex: Int?
    @State private var solved = false

    private var nums: [Int] { step.nums ?? [] }
    private var ascending: Bool { (step.dir ?? "up") == "up" }
    private var target: [Int] { ascending ? nums.sorted() : nums.sorted().reversed() }
    private var dirLabel: String { ascending ? "从小到大" : "从大到小" }

    var body: some View {
        VStack(spacing: 24) {
            Text(step.question ?? "\(dirLabel)，依次点一点")
                .font(.kidHead(25))
                .foregroundColor(.ink)
                .padding(.horizontal, 30)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xE7F6FF)))
                .overlay(Capsule().stroke(Color(hex: 0xBFE4F7), lineWidth: 2))

            // 顺序提示槽
            HStack(spacing: 14) {
                ForEach(target.indices, id: \.self) { i in
                    ZStack {
                        RoundedRectangle(cornerRadius: 16, style: .continuous)
                            .fill(i < progress ? Color(hex: 0xEDFBF0) : Color(hex: 0xF5F0E4))
                        if i < progress {
                            Text("\(target[i])")
                                .font(.kidTitle(30))
                                .foregroundColor(.brandGreenDk)
                        } else {
                            Image(systemName: "\(i + 1).circle")
                                .font(.system(size: 24, weight: .bold))
                                .foregroundColor(Color(hex: 0xC9BBA0))
                        }
                    }
                    .frame(width: 76, height: 66)
                    .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(i < progress ? .brandGreen : Color(hex: 0xE0D2B6), lineWidth: 3))
                }
            }

            // 打乱的数字块
            HStack(spacing: 24) {
                ForEach(nums.indices, id: \.self) { i in
                    numberBlock(i)
                }
            }

            if solved {
                Text(step.praise ?? "排队排好啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            } else {
                Text(step.hint ?? "先想清楚谁排第一").font(.kidBody(15)).foregroundColor(.inkSoft)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func numberBlock(_ i: Int) -> some View {
        Button {
            guard !solved, !doneIdx.contains(i) else { return }
            if nums[i] == target[progress] {
                withAnimation(.spring(response: 0.3, dampingFraction: 0.6)) {
                    doneIdx.insert(i)
                    progress += 1
                }
                sound.correct()
                if progress == nums.count {
                    solved = true
                    onCorrectCelebrate()
                    DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
                }
            } else {
                wrongIndex = i
                sound.wrong()
                onWrong()
                toast.show(step.hint ?? "想一想顺序哦", seconds: 2.0)
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
            }
        } label: {
            Text("\(nums[i])")
                .font(.kidTitle(44))
                .foregroundColor(doneIdx.contains(i) ? .white : Color(hex: 0x8A5B00))
                .frame(width: 104, height: 96)
                .background(
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(doneIdx.contains(i)
                              ? AnyShapeStyle(LinearGradient(colors: [Color(hex: 0xC6F0A0), .brandGreen], startPoint: .top, endPoint: .bottom))
                              : AnyShapeStyle(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom)))
                )
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(doneIdx.contains(i) ? .brandGreenDk : Color(hex: 0xB8770A), lineWidth: 3.5))
                .shadow(color: Color(hex: 0xB8770A).opacity(0.6), radius: 0, x: 0, y: 6)
                .overlay(alignment: .topTrailing) {
                    if doneIdx.contains(i) {
                        Text("\(target.firstIndex(of: nums[i])! + 1)")
                            .font(.system(size: 15, weight: .heavy, design: .rounded))
                            .foregroundColor(.white)
                            .padding(6)
                            .background(Circle().fill(.brandGreenDk))
                            .offset(x: 8, y: -8)
                    }
                }
        }
        .buttonStyle(.plain)
        .modifier(ShakeModifier(shake: wrongIndex == i))
    }
}

// MARK: - 填一填（neighbor：相邻数，a ? a+2）

struct NeighborStepView: View {
    let step: Step
    let onWrong: () -> Void
    let onNext: () -> Void
    let onCorrectCelebrate: () -> Void
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @State private var solved = false
    @State private var wrongIndex: Int?

    private var nums: [Int] { step.nums ?? [] }
    private var correct: Int { (nums.first ?? 0) + 1 }

    var body: some View {
        VStack(spacing: 24) {
            Text(step.question ?? "想一想：藏起来的数字是几？")
                .font(.kidHead(25))
                .foregroundColor(.ink)
                .padding(.horizontal, 30)
                .padding(.vertical, 11)
                .background(Capsule().fill(Color(hex: 0xF3EDFF)))
                .overlay(Capsule().stroke(Color(hex: 0xD9CCF5), lineWidth: 2))

            // 数字列车：a ? a+2
            HStack(spacing: 10) {
                numCard("\(nums.first ?? 0)")
                ZStack {
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .fill(LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom))
                    if solved {
                        Text("\(correct)")
                            .font(.kidTitle(46))
                            .foregroundColor(.brandGreenDk)
                    } else {
                        Text("?")
                            .font(.kidTitle(46))
                            .foregroundColor(Color(hex: 0xC9BBA0))
                    }
                }
                .frame(width: 92, height: 92)
                .overlay(
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .stroke(solved ? .brandGreen : Color(hex: 0xE8B54A),
                                style: StrokeStyle(lineWidth: 4, dash: solved ? [] : [8, 6]))
                )
                .shadow(color: Color(hex: 0xE8B54A).opacity(0.4), radius: 0, x: 0, y: 4)
                numCard("\(nums.last ?? 0)")
            }

            HStack(spacing: 26) {
                ForEach((step.arithOptions ?? []).indices, id: \.self) { i in
                    let n = step.arithOptions![i]
                    Button {
                        guard !solved else { return }
                        if n == correct {
                            solved = true
                            sound.correct()
                            onCorrectCelebrate()
                            DispatchQueue.main.asyncAfter(deadline: .now() + 1.3) { onNext() }
                        } else {
                            wrongIndex = i
                            sound.wrong()
                            onWrong()
                            toast.show(step.hint ?? "看看两边的数字", seconds: 2.2)
                            DispatchQueue.main.asyncAfter(deadline: .now() + 0.45) { wrongIndex = nil }
                        }
                    } label: {
                        Text("\(n)")
                            .font(.kidTitle(40))
                            .foregroundColor(Color(hex: 0x8A5B00))
                            .frame(width: 92, height: 84)
                            .background(
                                RoundedRectangle(cornerRadius: 18, style: .continuous)
                                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), Color(hex: 0xF7B32B)], startPoint: .top, endPoint: .bottom))
                            )
                            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Color(hex: 0xB8770A), lineWidth: 3.5))
                            .shadow(color: Color(hex: 0xB8770A).opacity(0.6), radius: 0, x: 0, y: 6)
                    }
                    .buttonStyle(.plain)
                    .scaleEffect(solved && n == correct ? 1.1 : 1)
                    .modifier(ShakeModifier(shake: wrongIndex == i))
                    .animation(.spring(response: 0.3, dampingFraction: 0.6), value: solved)
                }
            }

            if solved {
                Text(step.praise ?? "填对啦！").font(.kidHead(20)).foregroundColor(.brandGreenDk)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func numCard(_ t: String) -> some View {
        ZStack {
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(.white)
            Text(t)
                .font(.kidTitle(46))
                .foregroundColor(.ink)
        }
        .frame(width: 92, height: 92)
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color(hex: 0xF2E2C4), lineWidth: 4))
        .shadow(color: Color(hex: 0xF2E2C4), radius: 0, x: 0, y: 4)
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
