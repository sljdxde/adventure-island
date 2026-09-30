import SwiftUI

// MARK: - 马里奥式结算仪式（v0.8 工单07）
// 滑旗杆（按星级决定抓位）→ 跑进城堡、门开 → 本次所得金币逐枚掉落并计数
// → 星星逐颗点亮 → 按钮组浮现。约 4 秒，点按任意处可跳过。
// 金币雨数量 = 本次账本实际入账（星级金币 + 可能的蘑菇 +2），与 settleLevel 同源。

struct CeremonyView: View {
    let subject: String
    let index: Int
    let levelId: String
    let totalLevels: Int
    let stars: Int
    let wrongCount: Int
    var mascot: String = ""
    let onNext: () -> Void
    let onReplay: () -> Void
    @Binding var route: Route

    @EnvironmentObject var store: ProgressStore
    @Environment(\.soundService) private var sound

    private var hasNext: Bool { index + 1 < totalLevels }
    private var mascotName: String { mascot.isEmpty ? (index % 2 == 0 ? "mario" : "dino") : mascot }
    // 旗杆抓位按星级（3 星最高）
    private var gripHeight: CGFloat { stars == 3 ? 232 : (stars == 2 ? 178 : 124) }

    @State private var mascotDown = false
    @State private var mascotAtCastle = false
    @State private var doorOpen = false
    @State private var coinCount = 0
    @State private var coinIds: [Int] = []
    @State private var litStars = 0
    @State private var showSummary = false
    @State private var showButtons = false
    @State private var rainTotal = 0
    @State private var runTask: Task<Void, Never>?
    @State private var settled = false

    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(hex: 0x5A8CD2).opacity(0.22),
                                    Color(hex: 0x281E14).opacity(0.46)],
                           startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()

            VStack {
                Spacer()
                scene
                bottomGroup
            }

            // 标题与跳过
            VStack {
                HStack {
                    Spacer()
                    Text("本关完成！")
                        .font(.kidTitle(34))
                        .foregroundColor(.white)
                        .shadow(color: .black.opacity(0.35), radius: 4, y: 3)
                    Spacer()
                    Button {
                        skip()
                    } label: {
                        Text("跳过 ▶").font(.kidHead(17))
                            .foregroundColor(Color(hex: 0x8A5B00))
                            .padding(.horizontal, 18).padding(.vertical, 10)
                            .background(Capsule().fill(.white))
                            .shadow(color: .black.opacity(0.2), radius: 4, y: 3)
                    }
                }
                .padding(.horizontal, 34)
                .padding(.top, 26)
                Spacer()
            }
        }
        .contentShape(Rectangle())
        .onTapGesture { skip() }
        .onAppear { run() }
        .onDisappear { runTask?.cancel() }
    }

    // MARK: 场景（旗杆 / 角色 / 城堡）

    private var scene: some View {
        ZStack(alignment: .bottom) {
            // 地面
            VStack(spacing: 0) {
                Rectangle()
                    .fill(LinearGradient(colors: [Color(hex: 0x86C856), Color(hex: 0x57A23E)],
                                         startPoint: .top, endPoint: .bottom))
                    .frame(height: 22)
                    .overlay(Rectangle().fill(Color(hex: 0x478C36)).frame(height: 6),
                             alignment: .top)
            }

            HStack(alignment: .bottom, spacing: 0) {
                // 旗杆 + 角色
                ZStack(alignment: .top) {
                    Rectangle()
                        .fill(LinearGradient(colors: [Color(hex: 0xCFC8B6), Color(hex: 0xF6F1E4)],
                                             startPoint: .leading, endPoint: .trailing))
                        .frame(width: 10, height: 268)
                        .cornerRadius(5)
                    Circle().fill(Color(hex: 0x6FC93D)).frame(width: 22, height: 22)
                        .offset(x: -6, y: -8)
                    // 小旗（原创三角旗，非任天堂造型）
                    Image(systemName: "flag.fill")
                        .font(.system(size: 20))
                        .foregroundColor(Color(hex: 0xE84838))
                        .rotationEffect(.degrees(0))
                        .scaleEffect(x: 1, y: doorOpen ? 0.35 : 1, anchor: .center)
                        .offset(x: 14, y: 2)
                        .animation(.easeInOut(duration: 0.4), value: doorOpen)
                    // 角色：抓位 → 滑下 → 跑向城堡
                    IconView(name: mascotName, size: 52)
                        .offset(x: 26, y: mascotDown ? 268 - 52 : -(gripHeight))
                        .animation(.easeInOut(duration: 0.82), value: mascotDown)
                        .opacity(mascotAtCastle ? 0 : 1)
                        .offset(x: mascotAtCastle ? 280 : 26)
                        .animation(.easeInOut(duration: 0.8), value: mascotAtCastle)
                }
                .frame(width: 120, height: 280, alignment: .bottom)

                Spacer().frame(width: 180)

                // 城堡 + 开门 + 金币
                ZStack(alignment: .bottom) {
                    IconView(name: "castle", size: 128)
                    // 门洞（门打开后露出）
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Color(hex: 0x5B4A8C))
                        .frame(width: 44, height: 62)
                        .offset(y: -8)
                    // 双扇门
                    Group {
                        Rectangle().fill(Color(hex: 0xF7B7C4))
                            .frame(width: 22, height: 62)
                            .overlay(Rectangle().fill(Color(hex: 0xE892A6)).frame(width: 4),
                                     alignment: .trailing)
                            .rotation3DEffect(.degrees(doorOpen ? -78 : 0),
                                              axis: (x: 0, y: 1, z: 0),
                                              anchor: .leading, perspective: 0.4)
                            .offset(x: -22, y: -8)
                        Rectangle().fill(Color(hex: 0xF7B7C4))
                            .frame(width: 22, height: 62)
                            .overlay(Rectangle().fill(Color(hex: 0xE892A6)).frame(width: 4),
                                     alignment: .leading)
                            .rotation3DEffect(.degrees(doorOpen ? 78 : 0),
                                              axis: (x: 0, y: 1, z: 0),
                                              anchor: .trailing, perspective: 0.4)
                            .offset(x: 22, y: -8)
                    }
                    // 金币（逐枚出现，向上弹后落）
                    ForEach(coinIds, id: \.self) { i in
                        IconView(name: "coin", size: 30)
                            .offset(x: CGFloat(-60 + (i % 3) * 52),
                                    y: CGFloat(-78 - (i % 2) * 18))
                    }
                    // 计数牌
                    if coinCount > 0 || !showButtons {
                        HStack(spacing: 6) {
                            IconView(name: "coin", size: 24)
                            Text("\(coinCount)").font(.kidHead(20))
                                .foregroundColor(Color(hex: 0x8A5B00))
                        }
                        .padding(.horizontal, 14).padding(.vertical, 7)
                        .background(Capsule().fill(.white))
                        .shadow(color: .black.opacity(0.2), radius: 4, y: 3)
                        .offset(y: -150)
                        .opacity(coinIds.isEmpty && coinCount == 0 ? 0 : 1)
                    }
                }
                .frame(width: 128, height: 160, alignment: .bottom)
            }
        }
        .frame(height: 300)
    }

    // MARK: 底部（星星 / 文案 / 按钮）

    private var bottomGroup: some View {
        VStack(spacing: 14) {
            HStack(spacing: 18) {
                ForEach(0..<3, id: \.self) { i in
                    IconView(name: "starface", size: 56)
                        .opacity(i < litStars ? 1 : 0.2)
                        .scaleEffect(i < litStars ? 1 : 0.5)
                        .animation(.spring(response: 0.4, dampingFraction: 0.5), value: litStars)
                }
            }
            if showSummary {
                Text(wrongCount == 0 ? "一次没错，完美通关！" : "答错了 \(wrongCount) 次也没关系，你已经学会啦")
                    .font(.kidHead(17))
                    .foregroundColor(Color(hex: 0xFFF6E0))
                    .shadow(color: .black.opacity(0.4), radius: 3, y: 2)
                    .transition(.opacity)
            }
            if showButtons {
                HStack(spacing: 14) {
                    if hasNext {
                        Button(action: onNext) {
                            Label("下一关", systemImage: "arrow.right").font(.kidHead(19))
                        }.buttonStyle(.jellyGreen)
                    }
                    Button { route = .map } label: {
                        Label("返回地图", systemImage: "map").font(.kidHead(19))
                    }.buttonStyle(.jellyOrange)
                    Button(action: onReplay) {
                        Label("再玩一次", systemImage: "arrow.counterclockwise").font(.kidHead(19))
                    }.buttonStyle(.jellyCream)
                }
                .transition(.move(edge: .bottom).combined(with: .opacity))
            } else {
                Color.clear.frame(height: 56)
            }
        }
        .padding(.bottom, 20)
    }

    // MARK: 驱动

    private func record() -> Int {
        let previousStars = store.stars(for: subject, levelId: levelId)
        var rain = 0
        if stars > previousStars || previousStars == 0 { rain += stars }
        let mushroom = stars == 3 && previousStars < 3
        if mushroom { rain += 2 }
        store.completeLevel(subject: subject, levelId: levelId, stars: stars)
        if mushroom { store.recordCoin(.mushroomBonus, amount: 2) }
        return rain
    }

    private func run() {
        guard !settled else { return }
        settled = true
        rainTotal = record()
        sound.fanfare()
        runTask = Task { @MainActor in
            // beat 1：滑下旗杆
            try? await Task.sleep(nanoseconds: 200_000_000)
            mascotDown = true
            doorOpen = true   // 落旗
            // beat 2：跑进城堡、门开
            try? await Task.sleep(nanoseconds: 850_000_000)
            mascotAtCastle = true
            try? await Task.sleep(nanoseconds: 450_000_000)
            doorOpen = true
            // beat 3：金币逐枚计数
            for i in 0..<max(rainTotal, 1) {
                if Task.isCancelled { return }
                coinIds.append(i)
                coinCount = min(coinCount + 1, rainTotal)
                try? await Task.sleep(nanoseconds: 190_000_000)
            }
            if Task.isCancelled { return }
            // beat 4：星星逐颗点亮
            for _ in 0..<stars {
                litStars += 1
                try? await Task.sleep(nanoseconds: 340_000_000)
            }
            if Task.isCancelled { return }
            // beat 5：文案 + 按钮浮现
            withAnimation { showSummary = true }
            try? await Task.sleep(nanoseconds: 200_000_000)
            withAnimation(.spring(response: 0.5, dampingFraction: 0.6)) { showButtons = true }
        }
    }

    private func skip() {
        runTask?.cancel()
        mascotDown = true
        mascotAtCastle = true
        doorOpen = true
        coinCount = rainTotal
        coinIds = Array(0..<max(rainTotal, 1))
        litStars = stars
        showSummary = true
        showButtons = true
    }
}
