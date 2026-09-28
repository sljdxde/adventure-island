import SwiftUI
import SpriteKit

// MARK: - SpriteKit 浮沉实验场景（物理模型见 BuoyancyModel）

final class FloatSinkScene: SKScene {
    var onSettled: ((String, Bool) -> Void)?          // (itemId, isFloat)
    var waterTopY: CGFloat { size.height * 0.42 }     // SK 坐标：底部为 0

    private var items: [String: ItemState] = [:]
    private var lastTime: TimeInterval = 0
    private let floorPadding: CGFloat = 34

    struct ItemState {
        let node: SKNode
        let isFloat: Bool
        let itemId: String
        var buoyancy = BuoyancyState(y: 0, velocity: 0)   // y 相对水面
        var settled = false
        var settleTimer: TimeInterval = 0
        var age: TimeInterval = 0
    }

    override func didMove(to view: SKView) {
        backgroundColor = .clear
        buildWater()
    }

    private func buildWater() {
        let waterRect = CGRect(x: 0, y: 0, width: size.width, height: waterTopY)
        let water = SKShapeNode(rect: waterRect, cornerRadius: 18)
        water.fillColor = UIColor(red: 0.50, green: 0.83, blue: 0.97, alpha: 0.92)
        water.strokeColor = .clear
        water.zPosition = 1
        addChild(water)

        // 水面高光线
        let line = SKShapeNode(rect: CGRect(x: 0, y: waterTopY - 6, width: size.width, height: 6), cornerRadius: 3)
        line.fillColor = UIColor(white: 1, alpha: 0.6)
        line.strokeColor = .clear
        line.zPosition = 2
        addChild(line)

        // 缓慢移动的光斑
        for (i, x) in [0.2, 0.55, 0.8].enumerated() {
            let spot = SKShapeNode(circleOfRadius: CGFloat(24 + i * 10))
            spot.fillColor = UIColor(white: 1, alpha: 0.18)
            spot.strokeColor = .clear
            spot.position = CGPoint(x: size.width * x, y: waterTopY * 0.5)
            spot.zPosition = 2
            spot.run(.repeatForever(.sequence([
                .moveBy(x: 30, y: 10, duration: 3 + Double(i)),
                .moveBy(x: -30, y: -10, duration: 3 + Double(i))
            ])))
            addChild(spot)
        }
    }

    /// 从顶部投放物品
    func dropItem(_ item: ExperimentItem, atX x: CGFloat) {
        guard items[item.id] == nil else { return }
        let node = SKSpriteNode(imageNamed: item.icon)
        if node.texture == nil {
            node.texture = SKTexture(image: UIImage())
            node.color = .lightGray
            node.size = CGSize(width: 56, height: 56)
        } else {
            node.size = CGSize(width: 74, height: 74)
        }
        node.zPosition = 5
        node.position = CGPoint(x: min(max(x, 70), size.width - 70), y: size.height + 40)
        addChild(node)
        items[item.id] = ItemState(
            node: node, isFloat: item.isFloat, itemId: item.id,
            buoyancy: BuoyancyState(y: (size.height + 40 - waterTopY), velocity: 0)
        )
        spawnSplashBubbles(at: node.position.x, top: true)
    }

    override func update(_ currentTime: TimeInterval) {
        if lastTime == 0 { lastTime = currentTime }
        let dt = min(currentTime - lastTime, 1.0 / 30.0)
        lastTime = currentTime

        let floorY = floorPadding
        for key in Array(items.keys) {
            guard items[key] != nil else { continue }
            var state = items[key]!
            guard !state.settled else { continue }

            // 以固定步长推进物理（与单元测试同一模型）
            var steps = Int(dt / BuoyancyModel.dt)
            steps = max(steps, 1)
            for _ in 0..<steps {
                state.buoyancy = BuoyancyModel.step(state.buoyancy, isFloat: state.isFloat)
            }

            // 世界坐标：水面 y = waterTopY；模型 y>0 在水上
            let worldY = waterTopY + CGFloat(state.buoyancy.y)
            if worldY <= floorY {
                state.buoyancy.y = Double(floorY - waterTopY)
                state.buoyancy.velocity = 0
                state.node.position.y = floorY
            } else {
                state.node.position.y = worldY
            }

            // 沉底 / 漂浮稳定判定（最迟 2.6s 强制结算，避免软木塞弹跳过久）
            state.age += dt
            let nearRest = abs(state.buoyancy.velocity) < 45 &&
                (state.isFloat ? abs(state.buoyancy.y) < 90 : worldY <= floorY + 1)
            if nearRest {
                state.settleTimer += dt
                if state.settleTimer > 0.3 || state.age > 2.6 {
                    state.settled = true
                    // 漂浮物轻微上下浮动动画
                    if state.isFloat {
                        state.node.run(.repeatForever(.sequence([
                            .moveBy(x: 0, y: 5, duration: 1.2),
                            .moveBy(x: 0, y: -5, duration: 1.2)
                        ])))
                    }
                    onSettled?(state.itemId, state.isFloat)
                    items[state.itemId] = state
                    continue
                }
            } else {
                state.settleTimer = 0
            }

            // 水中冒泡
            if state.buoyancy.y < 0, Int.random(in: 0...14) == 0 {
                spawnBubble(at: state.node.position)
            }

            items[state.itemId] = state
        }
    }

    private func spawnSplashBubbles(at x: CGFloat, top: Bool) {
        for _ in 0..<6 {
            spawnBubble(at: CGPoint(x: x + CGFloat.random(in: -26...26), y: waterTopY))
        }
    }

    private func spawnBubble(at position: CGPoint) {
        let r = CGFloat.random(in: 4...9)
        let b = SKShapeNode(circleOfRadius: r)
        b.fillColor = UIColor(white: 1, alpha: 0.75)
        b.strokeColor = UIColor(red: 0.63, green: 0.86, blue: 0.98, alpha: 1)
        b.lineWidth = 2
        b.position = CGPoint(x: position.x + CGFloat.random(in: -20...20), y: max(position.y, 10))
        b.zPosition = 3
        addChild(b)
        b.run(.sequence([
            .group([.moveBy(x: CGFloat.random(in: -14...14), y: waterTopY - b.position.y + 8, duration: 0.9),
                    .fadeAlpha(to: 0, duration: 0.9)]),
            .removeFromParent()
        ]))
    }

    func resetAll() {
        items.values.forEach { $0.node.removeFromParent() }
        items.removeAll()
    }
}

// MARK: - 实验室页面（四步探究法）

struct LabView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @Environment(\.soundService) private var sound
    @Binding var route: Route
    @Binding var confetti: Int

    @State private var experiment: Experiment?
    @State private var phase: Phase = .guess
    @State private var guess: String?          // "float" / "sink"
    @State private var selectedItemId: String?
    @State private var resultChip: String?
    @State private var collectedCount = 0

    enum Phase: Equatable { case guess, play, done }

    private var exp: Experiment? { experiment }
    private var scene: FloatSinkScene {
        let s = FloatSinkScene()
        s.size = CGSize(width: 470, height: 440)
        s.scaleMode = .fill
        s.onSettled = { itemId, isFloat in
            handleSettled(itemId: itemId, isFloat: isFloat)
        }
        return s
    }
    @State private var skScene: FloatSinkScene?

    var body: some View {
        ZStack {
            SceneBackground(theme: .lab)

            VStack(spacing: 8) {
                header
                flowBar

                HStack(spacing: 16) {
                    shelf
                    tank
                    codex
                }
                .padding(.horizontal, 24)

                HStack {
                    Button {
                        skScene?.resetAll()
                        resetRound()
                    } label: {
                        Label(" 重新实验", systemImage: "arrow.counterclockwise")
                            .font(.kidHead(17))
                    }
                    .buttonStyle(.jellyCream)
                    Spacer()
                }
                .padding(.horizontal, 26)
                .padding(.bottom, 4)
            }
            .padding(.top, 6)
        }
        .onAppear {
            if experiment == nil {
                let file = ContentLoader.load(ExperimentFile.self, "experiments")
                experiment = file.experiments.first
                skScene = scene
            }
            speech.speak("欢迎来到科学实验室！\(exp?.guessQuestion ?? "")")
        }
    }

    // MARK: 顶部

    private var header: some View {
        HStack(spacing: 14) {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            VStack(alignment: .leading, spacing: 1) {
                Text("🔬 科学实验室 · \(exp?.title ?? "")")
                    .font(.kidHead(22))
                    .foregroundColor(.brandPurpleDk)
                Text("实验 1 / 1 · 向导闪闪")
                    .font(.kidBody(14))
                    .foregroundColor(.inkSoft)
            }
            Spacer()
            GoldChip(icon: "goggles", text: "已戴好")
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    private var flowBar: some View {
        HStack(spacing: 8) {
            flowStep(num: 1, title: "猜一猜", state: phase == .guess ? .now : .done)
            arrow
            flowStep(num: 2, title: "动手做", state: phase == .play ? .now : (phase == .guess ? .todo : .done))
            arrow
            flowStep(num: 3, title: "看现象", state: resultChip != nil ? .now : .todo)
            arrow
            flowStep(num: 4, title: "收进图鉴", state: collectedCount >= 3 ? .now : (phase == .done ? .done : .todo))
        }
    }

    private var arrow: some View {
        Image(systemName: "arrow.right")
            .font(.system(size: 16, weight: .black))
            .foregroundColor(.white.opacity(0.95))
    }

    private func flowStep(num: Int, title: String, state: StepChipState.State) -> some View {
        HStack(spacing: 7) {
            ZStack {
                switch state {
                case .done:
                    Circle().fill(.brandGreen)
                    Image(systemName: "checkmark").font(.system(size: 12, weight: .black)).foregroundColor(.white)
                case .now:
                    Circle().fill(.white.opacity(0.3))
                    Text("\(num)").font(.system(size: 13, weight: .black)).foregroundColor(.white)
                case .todo:
                    Circle().fill(.brandPurple.opacity(0.35))
                    Text("\(num)").font(.system(size: 13, weight: .black)).foregroundColor(.white)
                }
            }
            .frame(width: 24, height: 24)
            Text(title).font(.kidHead(17))
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 8)
        .background(
            Capsule().fill(state == .now
                           ? AnyShapeStyle(LinearGradient(colors: [.brandPurple, .brandPurpleDk], startPoint: .top, endPoint: .bottom))
                           : AnyShapeStyle(.white.opacity(0.94)))
        )
        .foregroundColor(state == .now ? .white : .brandPurpleDk)
        .shadow(color: state == .now ? .brandPurpleDdk : Color.ink.opacity(0.12), radius: 0, x: 0, y: 3)
    }

    // MARK: 工具箱

    private var shelf: some View {
        VStack(spacing: 10) {
            Text("🧰 工具箱")
                .font(.kidHead(17))
                .foregroundColor(.brandOrangeDdk)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 7)
                .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFE7A8), .brandYellow], startPoint: .top, endPoint: .bottom)))
                .shadow(color: .goldDdk.opacity(0.5), radius: 0, x: 0, y: 3)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 10) {
                ForEach(exp?.items ?? []) { item in
                    shelfItem(item)
                }
            }

            Text("点选物品\n再点水箱放进去")
                .font(.kidBody(13))
                .foregroundColor(.inkSoft)
                .multilineTextAlignment(.center)
        }
        .padding(14)
        .frame(width: 214)
        .frame(maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func shelfItem(_ item: ExperimentItem) -> some View {
        let tested = store.hasTested(itemId: item.id)
        let isSelected = selectedItemId == item.id
        return Button {
            guard phase == .play, !tested else { return }
            selectedItemId = item.id
            sound.systemTap()
            speech.speak(item.name)
            toast.show("已选中 \(item.name)，现在点水箱放进去！")
        } label: {
            ZStack(alignment: .topTrailing) {
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(isSelected ? Color(hex: 0xF5F0FF) : .white)
                    .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(isSelected ? .brandPurple : Color(hex: 0xF2E2C4), lineWidth: 3.5))
                    .shadow(color: Color(hex: 0xEFE3C8), radius: 0, x: 0, y: 3)
                IconView(name: item.icon, size: 46)
                    .opacity(tested ? 0.35 : 1)
                if tested {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 18, weight: .black))
                        .foregroundColor(.brandGreen)
                        .offset(x: 8, y: -8)
                }
            }
            .frame(height: 86)
        }
        .buttonStyle(.plain)
    }

    // MARK: 水箱

    private var tank: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .fill(Color.white.opacity(0.55))
            SpriteView(scene: skScene ?? scene, options: [.allowsTransparency])
                .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(.white, lineWidth: 9))
                .shadow(color: .black.opacity(0.18), radius: 16, y: 8)

            if let chip = resultChip {
                Text(chip)
                    .font(.kidHead(19))
                    .foregroundColor(.ink)
                    .padding(.horizontal, 22)
                    .padding(.vertical, 10)
                    .background(Capsule().fill(.white.opacity(0.97)))
                    .shadow(color: .ink.opacity(0.15), radius: 6, y: 3)
                    .frame(maxHeight: .infinity, alignment: .top)
                    .padding(.top, 18)
                    .transition(.move(edge: .top).combined(with: .opacity))
            }

            if phase == .guess {
                guessCard
            }
        }
        .frame(width: 470, height: 440)
        .contentShape(RoundedRectangle(cornerRadius: 26))
        .gesture(
            SpatialTapGesture().onEnded { value in
                handleTankTap(at: value.location)
            }
        )
    }

    private var guessCard: some View {
        VStack(spacing: 10) {
            Text("猜一猜 🔮")
                .font(.kidTitle(26))
                .foregroundColor(.brandPurpleDk)
            IconView(name: exp?.guessIcon ?? "apple", size: 88)
            Text(exp?.guessQuestion ?? "")
                .font(.kidHead(19))
                .foregroundColor(.inkSoft)
                .multilineTextAlignment(.center)
            HStack(spacing: 16) {
                Button {
                    makeGuess("float")
                } label: {
                    Label(" 浮起来", systemImage: "arrow.up")
                        .font(.kidHead(20))
                }
                .buttonStyle(.jellyYellow)
                Button {
                    makeGuess("sink")
                } label: {
                    Label(" 沉下去", systemImage: "arrow.down")
                        .font(.kidHead(20))
                }
                .buttonStyle(.jellyBlue)
            }
            .padding(.top, 4)
        }
        .padding(30)
        .background(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF3D8)], startPoint: .top, endPoint: .bottom))
        )
        .overlay(RoundedRectangle(cornerRadius: 28, style: .continuous).stroke(.white, lineWidth: 5))
        .shadow(color: .black.opacity(0.25), radius: 22)
    }

    // MARK: 图鉴

    private var codex: some View {
        VStack(spacing: 8) {
            Text("📓 现象图鉴")
                .font(.kidHead(17))
                .foregroundColor(.brandPurpleDk)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 7)
                .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xE4D6FF), Color(hex: 0xD0BCFF)], startPoint: .top, endPoint: .bottom)))
                .shadow(color: .brandPurple.opacity(0.5), radius: 0, x: 0, y: 3)

            codexList(title: "↑ 浮起来", color: .brandBlueDk, isFloat: true)
            codexList(title: "↓ 沉下去", color: .brandCoralDk, isFloat: false)

            Text("已测试 \(store.snapshot.testedItems.count) / \(exp?.items.count ?? 0)")
                .font(.kidHead(15))
                .foregroundColor(.brandPurpleDk)

            Button {
                collect()
            } label: {
                Label("⭐ 收进图鉴", systemImage: "star.fill")
                    .font(.kidHead(18))
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.jellyPurple)
            .disabled(store.snapshot.testedItems.count < 3)
            .opacity(store.snapshot.testedItems.count < 3 ? 0.55 : 1)
        }
        .padding(14)
        .frame(width: 226)
        .frame(maxHeight: .infinity)
        .modifier(StickerCardModifier())
    }

    private func codexList(title: String, color: Color, isFloat: Bool) -> some View {
        VStack(alignment: .leading, spacing: 5) {
            Text(title)
                .font(.kidHead(16))
                .foregroundColor(color)
            let found = (exp?.items ?? []).filter { store.hasTested(itemId: $0.id) && $0.isFloat == isFloat }
            if found.isEmpty {
                Text("还没有发现…")
                    .font(.kidBody(13.5))
                    .foregroundColor(Color(hex: 0xC6BADF))
            } else {
                FlexibleChips(items: found)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(8)
        .background(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .fill(.white)
                .overlay(RoundedRectangle(cornerRadius: 14, style: .continuous).stroke(Color(hex: 0xF2E2C4), lineWidth: 2))
        )
    }

    // MARK: 行为

    private func makeGuess(_ g: String) {
        guess = g
        phase = .play
        sound.systemTap()
        speech.speak("好，记下你的猜想啦，动手试试看！")
        toast.show("🔮 猜想已记录！把物品放进水箱验证吧")
    }

    private func handleTankTap(at location: CGPoint) {
        guard phase == .play else {
            if phase == .guess { toast.show("先完成猜一猜哦 🔮") }
            return
        }
        guard let id = selectedItemId,
              let item = exp?.items.first(where: { $0.id == id }),
              !store.hasTested(itemId: id) else {
            toast.show("先在左边工具箱里选一个物品哦 🧰")
            return
        }
        let local = CGPoint(x: location.x, y: location.y)
        skScene?.dropItem(item, atX: local.x)
        selectedItemId = nil
    }

    private func handleSettled(itemId: String, isFloat: Bool) {
        guard let item = exp?.items.first(where: { $0.id == itemId }) else { return }
        store.markTested(itemId: itemId)
        resultChip = "\(item.name) \(isFloat ? "浮起来了 ⬆" : "沉下去了 ⬇")"
        speech.speak("\(item.name)\(isFloat ? "浮起来了" : "沉下去了")")
        sound.coin()

        // 苹果验证猜想
        if itemId == exp?.guessItem {
            let guessedFloat = (guess == "float")
            if guessedFloat == isFloat {
                confetti += 1
                toast.show("🔮 猜对啦！加一颗智慧星 ⭐")
                store.snapshot.coins += 1
            } else {
                toast.show("没关系～科学家就是靠不断试错发现规律的 🔬")
            }
        }

        withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {}
    }

    private func resetRound() {
        phase = .guess
        guess = nil
        selectedItemId = nil
        resultChip = nil
        speech.speak("重新开始实验！\(exp?.guessQuestion ?? "")")
    }

    private func collect() {
        confetti += 1
        sound.correct()
        speech.speak("太棒了，实验记录收进图鉴！")
        if store.addSticker("st-fuchen") {
            toast.show("📓 图鉴 +1 · 获得「浮沉小侦探」贴纸 🏅", seconds: 2.2)
        } else {
            toast.show("这个实验已经收进图鉴啦")
        }
        store.collectScience(id: "sci-apple")
        collectedCount = store.snapshot.testedItems.count
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.4) {
            route = .collection
        }
    }
}

// 简易流式换行小胶囊
struct FlexibleChips: View {
    let items: [ExperimentItem]
    var body: some View {
        LazyVGrid(columns: [GridItem(.adaptive(minimum: 58), spacing: 4)], alignment: .leading, spacing: 4) {
            ForEach(items) { item in
                HStack(spacing: 3) {
                    IconView(name: item.icon, size: 16)
                    Text(item.name).font(.system(size: 12.5, weight: .heavy))
                }
                .padding(.horizontal, 7)
                .padding(.vertical, 4)
                .background(Capsule().fill(Color(hex: 0xFFFDF4)))
                .overlay(Capsule().stroke(Color(hex: 0xF0DCAC), lineWidth: 1.5))
            }
        }
    }
}
