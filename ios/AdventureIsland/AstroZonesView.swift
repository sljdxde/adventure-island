import SwiftUI

// MARK: - 星区选关（v0.10，保卫萝卜式分章）
// 星区图（10 个星区沿星空路径排布）→ 单星区关卡路径（一屏只展示本星区 10 关）→ 关卡。
// 数据驱动：SubjectFile.zones + Level.zone（非天文台学科无 zones，不进本视图）。

/// 每个星区的代表图标（与星区主题呼应；ContentIntegrityTests 钉住其资产存在性，防漂移）
enum AstroZoneIcons {
    static let all = ["sun", "earth", "rocket", "mercury", "jupiter",
                      "sunrays", "moon", "star", "milkyway", "telescope"]
    static func icon(_ n: Int) -> String { all[min(n - 1, all.count - 1)] }
}

/// 星区图：每星区一个节点，前一星区正式关推进到才解锁后续星区
struct ZoneGalaxyView: View {
    let subject: String
    @Binding var route: Route
    @EnvironmentObject var store: ProgressStore

    @State private var content: SubjectFile?

    private var config: SubjectConfig { SubjectConfig.map[subject] ?? SubjectConfig.map["astro"]! }
    private var ids: [String] { content?.levels.map(\.id) ?? [] }
    private var reviews: [Bool] { content?.levels.map { $0.review ?? false } ?? [] }
    private var bosses: [Bool] { content?.levels.map { $0.boss ?? false } ?? [] }
    private var zones: [SubjectZone] { content?.zones ?? [] }

    /// 当前进度关（第一个未通关的节点）
    private var currentIndex: Int {
        var i = 0
        while i < ids.count,
              store.nodeState(subject: subject, index: i, ids: ids, reviews: reviews, bosses: bosses) == .done {
            i += 1
        }
        return min(i, max(ids.count - 1, 0))
    }

    var body: some View {
        ZStack {
            SceneBackground(theme: .astro)

            VStack(spacing: 6) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                if zones.isEmpty {
                    Text("星区内容马上开放～")
                        .font(.kidHead(20)).foregroundColor(.white)
                    Spacer()
                } else {
                    zonePath
                    Spacer(minLength: 0)
                }
            }

            // 星空装饰
            VStack {
                HStack {
                    IconView(name: "starface", size: 30).padding(.leading, 34).offset(y: 12)
                    Spacer()
                    IconView(name: "rocket", size: 40).padding(.trailing, 46)
                }
                .padding(.top, 90)
                Spacer()
            }
            .allowsHitTesting(false)
        }
        .onAppear {
            if content == nil { content = ContentLoader.load(SubjectFile.self, config.file) }
        }
    }

    private var header: some View {
        HStack(spacing: 14) {
            SquareIconButton(icon: "back", size: 56, action: { route = .map })
            VStack(alignment: .leading, spacing: 1) {
                Text("\(config.title) · 星区图")
                    .font(.kidHead(23))
                    .foregroundColor(.white)
                Text("点亮一个星区，解锁下一片星空 · 已通关 \(store.doneCount(subject: subject, ids: ids))/\(ids.count) 关")
                    .font(.kidBody(13.5))
                    .foregroundColor(.white.opacity(0.85))
            }
            Spacer()
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    private var zonePath: some View {
        GeometryReader { geo in
            let path = Path { p in
                p.move(to: CGPoint(x: 46, y: geo.size.height * 0.72))
                p.addCurve(to: CGPoint(x: geo.size.width * 0.5, y: geo.size.height * 0.34),
                           control1: CGPoint(x: geo.size.width * 0.22, y: geo.size.height * 0.08),
                           control2: CGPoint(x: geo.size.width * 0.34, y: geo.size.height * 0.66))
                p.addCurve(to: CGPoint(x: geo.size.width - 46, y: geo.size.height * 0.5),
                           control1: CGPoint(x: geo.size.width * 0.66, y: geo.size.height * 0.06),
                           control2: CGPoint(x: geo.size.width * 0.78, y: geo.size.height * 0.72))
            }
            ZStack {
                path
                    .stroke(.white.opacity(0.9), style: StrokeStyle(lineWidth: 8, lineCap: .round, dash: [1, 24]))
                path
                    .stroke(.black.opacity(0.1), style: StrokeStyle(lineWidth: 8, lineCap: .round, dash: [1, 24]))
                    .offset(y: 3)
                    .blendMode(.multiply)

                ForEach(zones) { zone in
                    let i = zone.n - 1
                    let x = 46 + CGFloat(i) * (geo.size.width - 92) / CGFloat(max(zones.count - 1, 1))
                    let y = geo.size.height * 0.56 + sin(Double(i) * 0.9) * geo.size.height * 0.16
                    let done = (0..<10).filter { off in
                        let gi = i * 10 + off
                        return gi < ids.count &&
                        store.nodeState(subject: subject, index: gi, ids: ids, reviews: reviews, bosses: bosses) == .done
                    }.count
                    let unlocked = i * 10 <= currentIndex || done > 0
                    let isCurrent = i * 10 <= currentIndex && (i + 1) * 10 > currentIndex

                    zoneNode(zone, done: done, unlocked: unlocked, current: isCurrent)
                        .position(x: x, y: y)
                        .onTapGesture {
                            guard unlocked else { return }
                            Haptics.tap()
                            route = .zoneLevels(subject: subject, zone: zone.n)
                        }
                }

                // 终点：望远镜徽标
                VStack(spacing: 0) {
                    IconView(name: "telescope", size: 44)
                    Text("大探索")
                        .font(.kidHead(12))
                        .foregroundColor(.white)
                        .shadow(color: .black.opacity(0.4), radius: 0, y: 1)
                }
                .position(x: geo.size.width - 46, y: geo.size.height * 0.42)
            }
        }
        .frame(height: 320)
        .padding(.horizontal, 6)
    }

    private func zoneNode(_ zone: SubjectZone, done: Int, unlocked: Bool, current: Bool) -> some View {
        VStack(spacing: 4) {
            ZStack(alignment: .topTrailing) {
                ZStack {
                    Circle()
                        .fill(unlocked
                              ? LinearGradient(colors: [Color(hex: 0xFFE58A), .gold], startPoint: .top, endPoint: .bottom)
                              : LinearGradient(colors: [Color(hex: 0xC9CFD6), Color(hex: 0x9AA1A9)], startPoint: .top, endPoint: .bottom))
                        .overlay(Circle().stroke(.white, lineWidth: 3.5))
                        .shadow(color: unlocked ? .gold.opacity(0.5) : .black.opacity(0.2), radius: unlocked ? 10 : 0, y: 4)
                    IconView(name: unlocked ? (zone.icon ?? AstroZoneIcons.icon(zone.n)) : "lock", size: 30)
                }
                .frame(width: 64, height: 64)
                .modifier(NodePulse(active: current))

                if done == 10 {
                    Text("✓")
                        .font(.system(size: 14, weight: .black))
                        .foregroundColor(.white)
                        .padding(5)
                        .background(Circle().fill(Color.brandGreen))
                        .offset(x: 6, y: -6)
                }
            }

            Text(zone.title)
                .font(.kidHead(14))
                .foregroundColor(unlocked ? .white : .white.opacity(0.6))
                .lineLimit(1)
                .minimumScaleFactor(0.8)
            Text(unlocked ? "\(done)/10" : "未解锁")
                .font(.kidBody(12))
                .foregroundColor(.white.opacity(unlocked ? 0.85 : 0.5))
        }
        .frame(width: 104)
        .contentShape(Rectangle())
    }

    /// 每个星区的代表图标
    private func zoneIcon(_ n: Int) -> String { AstroZoneIcons.icon(n) }
}

/// 单星区关卡路径：只展示本星区 10 关（保卫萝卜式，一屏一区）
struct ZoneLevelsView: View {
    let subject: String
    let zone: Int
    @Binding var route: Route
    @EnvironmentObject var store: ProgressStore

    @State private var content: SubjectFile?

    private var config: SubjectConfig { SubjectConfig.map[subject] ?? SubjectConfig.map["astro"]! }
    private var ids: [String] { content?.levels.map(\.id) ?? [] }
    private var reviews: [Bool] { content?.levels.map { $0.review ?? false } ?? [] }
    private var bosses: [Bool] { content?.levels.map { $0.boss ?? false } ?? [] }
    private var zoneMeta: SubjectZone? { content?.zones?.first { $0.n == zone } }
    private var startIndex: Int { (zone - 1) * 10 }
    private var endIndex: Int { min(startIndex + 10, ids.count) }

    var body: some View {
        ZStack {
            SceneBackground(theme: .astro)

            VStack(spacing: 4) {
                header
                    .padding(.horizontal, 22)
                    .padding(.top, 8)

                levelPath
                Spacer(minLength: 0)
            }

            HStack {
                IconView(name: "starface", size: 34).padding(.leading, 30)
                Spacer()
                IconView(name: "comet", size: 40).padding(.trailing, 40)
            }
            .padding(.top, 96)
            .allowsHitTesting(false)
        }
        .onAppear {
            if content == nil { content = ContentLoader.load(SubjectFile.self, config.file) }
        }
    }

    private var header: some View {
        HStack(spacing: 14) {
            SquareIconButton(icon: "back", size: 56, action: { route = .zones(subject: subject) })
            VStack(alignment: .leading, spacing: 1) {
                Text("第 \(zone) 星区 · \(zoneMeta?.title ?? "")")
                    .font(.kidHead(23))
                    .foregroundColor(.white)
                Text(zoneMeta?.subtitle ?? "仰望星空")
                    .font(.kidBody(13.5))
                    .foregroundColor(.white.opacity(0.85))
            }
            Spacer()
            GoldChip(icon: "coin", text: "\(store.snapshot.coins)")
        }
    }

    private var levelPath: some View {
        GeometryReader { geo in
            let path = Path { p in
                p.move(to: CGPoint(x: 34, y: geo.size.height * 0.74))
                p.addCurve(to: CGPoint(x: geo.size.width * 0.5, y: geo.size.height * 0.36),
                           control1: CGPoint(x: geo.size.width * 0.2, y: geo.size.height * 0.1),
                           control2: CGPoint(x: geo.size.width * 0.35, y: geo.size.height * 0.64))
                p.addCurve(to: CGPoint(x: geo.size.width - 34, y: geo.size.height * 0.52),
                           control1: CGPoint(x: geo.size.width * 0.65, y: geo.size.height * 0.08),
                           control2: CGPoint(x: geo.size.width * 0.8, y: geo.size.height * 0.74))
            }
            ZStack {
                path
                    .stroke(.white.opacity(0.95), style: StrokeStyle(lineWidth: 9, lineCap: .round, dash: [1, 26]))
                path
                    .stroke(.black.opacity(0.08), style: StrokeStyle(lineWidth: 9, lineCap: .round, dash: [1, 26]))
                    .offset(y: 3)
                    .blendMode(.multiply)

                ForEach(startIndex..<endIndex, id: \.self) { gi in
                    let i = gi - startIndex
                    let state = store.nodeState(subject: subject, index: gi, ids: ids,
                                                reviews: reviews, bosses: bosses)
                    let x = 34 + CGFloat(i) * (geo.size.width - 68) / CGFloat(max(endIndex - startIndex - 1, 1))
                    let y = geo.size.height * 0.58 + sin(Double(i) * 0.85) * geo.size.height * 0.15
                    ZStack(alignment: .bottom) {
                        nodeCircle(state, index: gi)
                        if state == .current {
                            Text("下一关 ▶")
                                .font(.system(size: 12, weight: .heavy, design: .rounded))
                                .foregroundColor(.white)
                                .shadow(color: .black.opacity(0.35), radius: 0, y: 1)
                                .offset(y: 26)
                        }
                    }
                    .position(x: x, y: y)
                    .onTapGesture {
                        guard state != .locked else { return }
                        Haptics.tap()
                        route = .level(subject: subject, index: gi)
                    }
                }

                // 星区终点：小旗子
                VStack(spacing: 0) {
                    IconView(name: "flag", size: 24).offset(y: 5)
                    IconView(name: "castle", size: 50)
                }
                .position(x: geo.size.width - 34, y: geo.size.height * 0.44)
            }
        }
        .frame(height: 300)
        .padding(.horizontal, 6)
    }

    @ViewBuilder
    private func nodeCircle(_ state: MapNodeState, index: Int) -> some View {
        ZStack {
            switch state {
            case .done:
                Circle()
                    .fill(LinearGradient(colors: [Color(hex: 0x7FD98A), .brandGreen], startPoint: .top, endPoint: .bottom))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: .brandGreenDdk, radius: 0, y: 4)
                Image(systemName: "checkmark")
                    .font(.system(size: 18, weight: .black))
                    .foregroundColor(.white)
            case .current:
                Circle()
                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), .gold], startPoint: .top, endPoint: .bottom))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: .gold.opacity(0.45), radius: 10)
                    .shadow(color: .goldDdk.opacity(0.6), radius: 0, y: 4)
                IconView(name: "starface", size: 25)
            case .locked:
                Circle()
                    .fill(Color(hex: 0xC9CFD6))
                    .overlay(Circle().stroke(.white, lineWidth: 3.5))
                    .shadow(color: Color(hex: 0x9AA1A9), radius: 0, y: 4)
            }
        }
        .frame(width: 40, height: 40)
        .modifier(NodePulse(active: state == .current))
    }
}
