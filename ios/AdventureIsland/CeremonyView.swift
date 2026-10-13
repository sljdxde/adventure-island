import SwiftUI

// MARK: - 通关结算卡（v0.10：替代原马里奥仪式动画）
// 答完最后一步即时弹出的静态卡片：星级 + 本次入账金币 + 文案 + 按钮组，无逐拍动画。
// 记账与原仪式 record() 同源：星级金币 + 可能的蘑菇 +2，经 completeLevel/recordCoin 入账。

struct LevelSettleCard: View {
    let subject: String
    let index: Int
    let levelId: String
    let totalLevels: Int
    let stars: Int
    let wrongCount: Int
    let onNext: () -> Void
    let onReplay: () -> Void
    @Binding var route: Route

    @EnvironmentObject var store: ProgressStore
    @Environment(\.soundService) private var sound
    @State private var settled = false
    @State private var coinsGained = 0

    private var hasNext: Bool { index + 1 < totalLevels }

    var body: some View {
        ZStack {
            Color.black.opacity(0.45).ignoresSafeArea()

            VStack(spacing: 13) {
                Text(hasNext ? "本关完成！" : "🎉 \(SubjectConfig.map[subject]?.title ?? "本学科")全部通关啦！")
                    .font(.kidTitle(29))
                    .foregroundColor(.ink)
                    .multilineTextAlignment(.center)

                HStack(spacing: 10) {
                    ForEach(0..<3, id: \.self) { i in
                        IconView(name: "starface", size: 52)
                            .opacity(i < stars ? 1 : 0.22)
                            .scaleEffect(i < stars ? 1 : 0.78)
                    }
                }

                if coinsGained > 0 {
                    GoldChip(icon: "coin", text: "+\(coinsGained)")
                }

                Text(wrongCount == 0 ? "一次没错，完美通关！" : "答错了 \(wrongCount) 次也没关系，你已经学会啦")
                    .font(.kidBody(15))
                    .foregroundColor(.inkSoft)
                    .multilineTextAlignment(.center)

                HStack(spacing: 12) {
                    if hasNext {
                        Button(action: onNext) {
                            Label("下一关", systemImage: "arrow.right").font(.kidHead(19))
                        }.buttonStyle(.jellyGreen)
                    } else {
                        // 最终关通关：一键清空本学科关卡星数，从第 1 关重新探险
                        Button {
                            store.resetSubject(subject)
                            route = .level(subject: subject, index: 0)
                        } label: {
                            Label("从头再玩一次", systemImage: "arrow.counterclockwise").font(.kidHead(19))
                        }.buttonStyle(.jellyGreen)
                    }
                    Button { route = backRoute(subject: subject, index: index) } label: {
                        Label(LevelCatalog.hasZones(subject) ? "返回星区" : "返回地图", systemImage: "map").font(.kidHead(19))
                    }.buttonStyle(.jellyOrange)
                    Button(action: onReplay) {
                        Label("再玩本关", systemImage: "arrow.clockwise").font(.kidHead(19))
                    }.buttonStyle(.jellyCream)
                }
            }
            .padding(.horizontal, 46).padding(.vertical, 30)
            .background(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(LinearGradient(colors: [Color(hex: 0xFFFBF0), Color(hex: 0xFFF4E2)],
                                         startPoint: .top, endPoint: .bottom))
            )
            .overlay(RoundedRectangle(cornerRadius: 34, style: .continuous).stroke(.white, lineWidth: 5))
            .shadow(color: .black.opacity(0.28), radius: 26)
            .padding(.horizontal, 70)
        }
        .onAppear {
            guard !settled else { return }
            settled = true
            coinsGained = record()
            sound.fanfare()
        }
    }

    /// 记账（与原仪式同源）：星级提升才入账星级金币；3 星首次达成附蘑菇 +2。
    /// 返回本次实际入账，供「+N 金币」展示。
    private func record() -> Int {
        let previousStars = store.stars(for: subject, levelId: levelId)
        var gained = 0
        if stars > previousStars || previousStars == 0 { gained += stars }
        store.completeLevel(subject: subject, levelId: levelId, stars: stars)
        if stars == 3 && previousStars < 3 {
            store.recordCoin(.mushroomBonus, amount: 2)
            gained += 2
        }
        return gained
    }
}
