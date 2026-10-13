import SwiftUI

// MARK: - 学一学动画（v0.10.1）
// letter 步骤可选 anim 字段 → 循环播放主题动画；未配置的关回落静态大字卡。
// 每个 anim 用 TimelineView 驱动 0..<1 相位，纯 Shape + 设计图标绘制，与 HTML 端 CSS 动画观感对齐。
// 动画只做演示，朗读仍由「读一读」按钮触发（可全程静音）。

struct AstroAnimView: View {
    let anim: String

    /// 动画 id 全集（validate/测试与 JSON `letter.anim` 枚举同源）。
    /// v0.11 学科专属动画（pydraw/tone/merge/walk/rainbow/countpop/fall/heartbeat/train/river/wall/mountain/panda/drift/windmill）
    /// 当前仅 HTML 端实现（用户指示 HTML 先行）；Swift 端渲染后续补齐，届时 letter 步的 isAstro 门槛一并放开。
    static let animIds: Set<String> = ["sunrise", "daynight", "orbit", "satellite", "moonphases",
                                       "rocket", "float", "meteor", "bigdipper", "blackhole",
                                       "galaxy", "bigbang", "tide",
                                       "pydraw", "tone", "merge",
                                       "walk", "rainbow", "countpop", "fall", "heartbeat", "train",
                                       "river", "wall", "mountain", "panda", "drift", "windmill"]

    private static let periods: [String: Double] = [
        "sunrise": 6, "daynight": 5, "orbit": 6, "satellite": 5, "moonphases": 8,
        "rocket": 4.5, "float": 5, "meteor": 4, "bigdipper": 6, "blackhole": 6,
        "galaxy": 12, "bigbang": 5, "tide": 5,
    ]

    var body: some View {
        TimelineView(.animation) { tl in
            let period = Self.periods[anim] ?? 5
            let t = tl.date.timeIntervalSinceReferenceDate.truncatingRemainder(dividingBy: period) / period
            content(t).id(anim)
        }
        .frame(width: 244, height: 244)
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 24, style: .continuous).stroke(.brandYellow, lineWidth: 4))
    }

    @ViewBuilder
    private func content(_ t: Double) -> some View {
        switch anim {
        case "sunrise": sunrise(t)
        case "daynight": daynight(t)
        case "orbit": orbit(t)
        case "satellite": satellite(t)
        case "moonphases": moonphases(t)
        case "rocket": rocket(t, tlDate: Date())
        case "float": float(t)
        case "meteor": meteor(t)
        case "bigdipper": bigdipper(t)
        case "blackhole": blackhole(t)
        case "galaxy": galaxy(t)
        case "bigbang": bigbang(t)
        case "tide": tide(t)
        default: starfield()
        }
    }

    // MARK: 公共底景

    /// 夜空 + 随机小星（位置由种子固定，循环间不跳动）
    private func starfield(_ count: Int = 26, seed: Int = 7) -> some View {
        ForEach(0..<count, id: \.self) { i in
            let s = Double((i * 137 + seed * 31) % 100) / 100
            let s2 = Double((i * 61 + seed * 17) % 100) / 100
            Circle()
                .fill(.white.opacity(0.35 + s2 * 0.5))
                .frame(width: 2 + s2 * 2.4, height: 2 + s2 * 2.4)
                .position(x: 12 + s * 220, y: 10 + s2 * 224)
        }
    }

    private func nightSky() -> some View {
        ZStack {
            LinearGradient(colors: [Color(hex: 0x1B2252), Color(hex: 0x3D4CB0)],
                           startPoint: .top, endPoint: .bottom)
            starfield()
        }
    }

    // MARK: 1. 日出日落

    private func sunrise(_ t: Double) -> some View {
        let arc = sin(t * .pi)                    // 0 升起前 → 1 正午 → 0 落下
        let x = -26 + t * (244 + 52)
        let y = 176 - arc * 140
        return ZStack {
            LinearGradient(colors: [Color(hex: 0x2A3170), Color(hex: 0x7B8ADF)],
                           startPoint: .top, endPoint: .bottom)
                .opacity(1 - arc * 0.8)
            LinearGradient(colors: [Color(hex: 0x8FD6FA), Color(hex: 0xFFE29A)],
                           startPoint: .top, endPoint: .bottom)
                .opacity(arc * 0.9)
            starfield(14).opacity(1 - arc)
            Circle()
                .fill(RadialGradient(colors: [Color(hex: 0xFFF3B0), .brandYellowDk],
                                     center: .center, startRadius: 6, endRadius: 34))
                .frame(width: 52, height: 52)
                .shadow(color: .brandYellow.opacity(0.8), radius: arc * 18)
                .position(x: x, y: y)
            // 地面
            VStack(spacing: 0) {
                Spacer()
                Rectangle().fill(LinearGradient(colors: [Color(hex: 0x7FC66A), Color(hex: 0x4E8F3C)],
                                                startPoint: .top, endPoint: .bottom))
                    .frame(height: 46)
            }
            IconView(name: "sprout", size: 26).position(x: 196, y: 186)
        }
    }

    // MARK: 2. 地球自转（昼夜交界线扫过）

    private func daynight(_ t: Double) -> some View {
        ZStack {
            LinearGradient(colors: [Color(hex: 0x1B2252), Color(hex: 0x3D4CB0)],
                           startPoint: .top, endPoint: .bottom)
            starfield(20)
            ZStack {
                Circle().fill(LinearGradient(colors: [Color(hex: 0x7FC66A), Color(hex: 0x4E9FD8)],
                                             startPoint: .topLeading, endPoint: .bottomTrailing))
                // 夜半球：随相位绕地球转
                Rectangle()
                    .fill(LinearGradient(colors: [Color(hex: 0x121A45).opacity(0.92), Color(hex: 0x121A45).opacity(0.55)],
                                         startPoint: .leading, endPoint: .trailing))
                    .rotationEffect(.degrees(t * 360 - 90))
            }
            .frame(width: 148, height: 148)
            .mask(Circle().frame(width: 148, height: 148))
            .overlay(Circle().stroke(.white.opacity(0.7), lineWidth: 4))
            .shadow(color: .black.opacity(0.3), radius: 12)
            // 贴地小屋标记昼夜
            IconView(name: "home", size: 22).position(x: 122, y: 52)
        }
    }

    // MARK: 3. 公转（地球绕太阳 + 月亮绕地球）

    private func orbit(_ t: Double) -> some View {
        let cx: CGFloat = 122, cy: CGFloat = 122
        let angle = t * 2 * .pi
        let ex = cx + cos(angle) * 84
        let ey = cy + sin(angle) * 84
        let mAngle = angle * 2.2
        return ZStack {
            nightSky()
            Circle()
                .stroke(.white.opacity(0.35), style: StrokeStyle(lineWidth: 2, dash: [4, 5]))
                .frame(width: 168, height: 168)
                .position(x: cx, y: cy)
            // 太阳
            Circle()
                .fill(RadialGradient(colors: [Color(hex: 0xFFF6D0), .brandYellowDk],
                                     center: .center, startRadius: 4, endRadius: 30))
                .frame(width: 46, height: 46)
                .shadow(color: .brandYellow.opacity(0.9), radius: 16)
                .position(x: cx, y: cy)
            // 地球 + 月亮
            ZStack {
                Circle()
                    .stroke(.white.opacity(0.3), style: StrokeStyle(lineWidth: 1.4, dash: [3, 4]))
                    .frame(width: 52, height: 52)
                IconView(name: "earth", size: 30)
                IconView(name: "moon", size: 13)
                    .position(x: 26 + cos(mAngle) * 24, y: 26 + sin(mAngle) * 24)
            }
            .frame(width: 52, height: 52)
            .position(x: ex, y: ey)
        }
    }

    // MARK: 4. 卫星绕地

    private func satellite(_ t: Double) -> some View {
        let angle = t * 2 * .pi
        let x = 122 + cos(angle) * 88
        let y = 122 + sin(angle) * 38      // 椭圆轨道
        return ZStack {
            nightSky()
            Ellipse()
                .stroke(.white.opacity(0.35), style: StrokeStyle(lineWidth: 2, dash: [4, 5]))
                .frame(width: 190, height: 84)
                .position(x: 122, y: 122)
            Circle()
                .fill(LinearGradient(colors: [Color(hex: 0x7FC66A), Color(hex: 0x4E9FD8)],
                                     startPoint: .topLeading, endPoint: .bottomTrailing))
                .frame(width: 74, height: 74)
                .overlay(Circle().stroke(.white.opacity(0.5), lineWidth: 3))
                .shadow(color: .black.opacity(0.3), radius: 8)
                .position(x: 122, y: 122)
            IconView(name: "satellite", size: 40)
                .rotationEffect(.degrees(sin(angle) * 12))
                .position(x: x, y: y)
                .shadow(color: .black.opacity(0.35), radius: 3)
        }
    }

    // MARK: 5. 月相轮回（新月→上弦→满月→残月，真实月相图标交叉淡入）

    private func moonphases(_ t: Double) -> some View {
        let icons = ["newmoon", "waxing", "fullmoon", "waning"]
        let idx = Int(t * 4) % 4
        let next = (idx + 1) % 4
        let frac = t * 4 - Double(Int(t * 4))
        let fade = frac > 0.78 ? (frac - 0.78) / 0.22 : 0    // 末段交叉淡入下一相
        return ZStack {
            nightSky()
            ForEach(0..<4, id: \.self) { i in
                IconView(name: icons[i], size: 118)
                    .opacity(i == idx ? (1 - fade) : (i == next && fade > 0 ? fade : 0))
            }
            Text(["新月", "上弦月", "满月", "残月"][idx])
                .font(.kidHead(16))
                .foregroundColor(.white)
                .padding(.horizontal, 14).padding(.vertical, 5)
                .background(Capsule().fill(Color.black.opacity(0.35)))
                .position(x: 122, y: 208)
        }
    }

    // MARK: 6. 火箭发射

    private func rocket(_ t: Double, tlDate: Date) -> some View {
        let shakeAmp = t < 0.32 ? 3.2 : 0
        let flicker = sin(tlDate.timeIntervalSinceReferenceDate * 26)
        let lift = t < 0.32 ? 0 : min(1, (t - 0.32) / 0.6)
        let y = 176 - pow(lift, 1.7) * 330
        let x = 122 + (t < 0.32 ? sin(tlDate.timeIntervalSinceReferenceDate * 38) * shakeAmp : 0)
        return ZStack {
            LinearGradient(colors: [Color(hex: 0x2A3170), Color(hex: 0x4A5AB8)],
                           startPoint: .top, endPoint: .bottom)
            starfield(18)
            VStack(spacing: 0) {
                Spacer()
                Rectangle().fill(LinearGradient(colors: [Color(hex: 0x7FC66A), Color(hex: 0x4E8F3C)],
                                                startPoint: .top, endPoint: .bottom))
                    .frame(height: 40)
            }
            if lift < 0.999 {
                VStack(spacing: -6) {
                    IconView(name: "rocket", size: 62)
                        .scaleEffect(x: -1, y: 1, anchor: .center)   // 朝上
                    // 尾焰
                    Capsule()
                        .fill(LinearGradient(colors: [Color(hex: 0xFFD24D), Color(hex: 0xE84838)],
                                             startPoint: .top, endPoint: .bottom))
                        .frame(width: 13, height: 26 + flicker * 8)
                        .opacity(0.92)
                }
                .position(x: x, y: y - 10)
            }
            if t < 0.32 {
                Text(["3", "2", "1"][min(Int(t / 0.107), 2)])
                    .font(.kidTitle(40))
                    .foregroundColor(.white)
                    .shadow(color: .black.opacity(0.4), radius: 2, y: 2)
                    .position(x: 122, y: 56)
            }
        }
    }

    // MARK: 7. 失重漂浮

    private func float(_ t: Double) -> some View {
        let y = 122 + sin(t * 2 * .pi) * 26
        let rot = sin(t * 4 * .pi) * 12
        return ZStack {
            nightSky()
            starfield(16, seed: 3)
            IconView(name: "sparkle", size: 18)
                .position(x: 60 + sin(t * 2 * .pi + 1) * 8, y: 70 + cos(t * 2 * .pi) * 10)
                .opacity(0.8)
            IconView(name: "astronaut", size: 78)
                .rotationEffect(.degrees(rot))
                .position(x: 122, y: y)
                .shadow(color: .black.opacity(0.3), radius: 6)
            Text("失重啦，飘起来～")
                .font(.kidHead(14))
                .foregroundColor(.white.opacity(0.9))
                .position(x: 122, y: 206)
        }
    }

    // MARK: 8. 流星/彗星划过

    private func meteor(_ t: Double) -> some View {
        ZStack {
            nightSky()
            ForEach(0..<3, id: \.self) { i in
                let p = (t + Double(i) / 3).truncatingRemainder(dividingBy: 1)
                let x = 250 - p * 300
                let y = -10 + p * 200
                ZStack {
                    Capsule()
                        .fill(LinearGradient(colors: [Color(hex: 0xFFE58A).opacity(0.9), .clear],
                                             startPoint: .trailing, endPoint: .leading))
                        .frame(width: 86, height: 5)
                        .offset(x: -46)
                    Circle()
                        .fill(Color(hex: 0xFFF6D0))
                        .frame(width: 11, height: 11)
                        .shadow(color: .brandYellow, radius: 7)
                }
                .rotationEffect(.degrees(33))
                .position(x: x, y: y)
                .opacity(p < 0.06 ? p / 0.06 : (p > 0.82 ? (1 - p) / 0.18 : 1))
            }
        }
    }

    // MARK: 9. 北斗七星连成勺

    private func bigdipper(_ t: Double) -> some View {
        // 与设计稿 bigdipper.svg 同构的 7 星坐标（64 坐标系 × 缩放）
        let pts: [(CGFloat, CGFloat)] = [(26,140),(60,120),(100,133),(133,107),(152,66),(178,50),(190,89)]
        let scale: CGFloat = 1.0
        let starP = pts.map { CGPoint(x: $0.0 * scale + 20, y: $0.1 * scale - 26) }
        let lit = min(Double(starP.count), t * 9)
        let lineT = max(0, min(1, (t - 0.72) / 0.26))
        let fade = t > 0.94 ? (1 - t) / 0.06 : 1
        return ZStack {
            nightSky()
            ForEach(0..<starP.count, id: \.self) { i in
                Circle()
                    .fill(Color(hex: 0xFFE58A))
                    .frame(width: 15, height: 15)
                    .shadow(color: .brandYellow, radius: 8)
                    .position(starP[i])
                    .opacity(Double(i) < lit ? 1 * fade : 0)
            }
            // 连线（星全部亮起后逐段画出）
            Path { p in
                guard let first = starP.first else { return }
                p.move(to: first)
                starP.dropFirst().forEach { p.addLine(to: $0) }
            }
            .trim(from: 0, to: lineT)
            .stroke(Color(hex: 0x9FC1FF), style: StrokeStyle(lineWidth: 2.6, lineCap: .round, dash: [1, 6]))
            .opacity(fade)
        }
    }

    // MARK: 10. 黑洞（吸积盘旋转 + 星被卷入）

    private func blackhole(_ t: Double) -> some View {
        ZStack {
            LinearGradient(colors: [Color(hex: 0x0E1330), Color(hex: 0x252C68)],
                           startPoint: .top, endPoint: .bottom)
            starfield(18)
            // 被卷入的星（三颗，错相螺旋）
            ForEach(0..<3, id: \.self) { i in
                let p = (t + Double(i) / 3).truncatingRemainder(dividingBy: 1)
                let r = 108 * (1 - p) + 34
                let a = Double(i) * 2.1 + p * 5.4
                Circle()
                    .fill(Color(hex: 0xBFD4FF))
                    .frame(width: 6 - p * 3, height: 6 - p * 3)
                    .position(x: 122 + cos(a) * r, y: 122 + sin(a) * r * 0.62)
                    .opacity(p < 0.12 ? p / 0.12 : 1)
            }
            // 吸积盘
            Ellipse()
                .stroke(LinearGradient(colors: [Color(hex: 0xFFD24D), Color(hex: 0xE86A3A)],
                                       startPoint: .leading, endPoint: .trailing),
                        style: StrokeStyle(lineWidth: 7, lineCap: .round))
                .frame(width: 150, height: 52)
                .rotationEffect(.degrees(t * 360))
                .opacity(0.85)
            Ellipse()
                .stroke(Color(hex: 0xFFE9BC).opacity(0.6), style: StrokeStyle(lineWidth: 3, dash: [2, 7]))
                .frame(width: 118, height: 38)
                .rotationEffect(.degrees(-t * 300))
            // 事件视界
            Circle()
                .fill(Color.black)
                .frame(width: 56, height: 56)
                .overlay(Circle().stroke(Color(hex: 0xFFB13B).opacity(0.9), lineWidth: 2.4))
                .shadow(color: Color(hex: 0xE86A3A).opacity(0.7), radius: 14)
                .position(x: 122, y: 122)
        }
    }

    // MARK: 11. 银河系旋转

    private func galaxy(_ t: Double) -> some View {
        ZStack {
            nightSky()
            Circle()
                .fill(RadialGradient(colors: [Color(hex: 0xFFF6D0).opacity(0.95), Color(hex: 0xFFF6D0).opacity(0)],
                                     center: .center, startRadius: 4, endRadius: 60))
                .frame(width: 120, height: 120)
                .position(x: 122, y: 122)
            ForEach(0..<3, id: \.self) { arm in
                ForEach(0..<9, id: \.self) { i in
                    let a = Double(arm) * 2.09 + Double(i) * 0.52 + t * 2 * .pi * 0.35
                    let r = 16 + Double(i) * 11.5
                    Circle()
                        .fill(i % 2 == 0 ? Color(hex: 0xFFE9BC) : Color(hex: 0xBFD4FF))
                        .frame(width: 7 - Double(i) * 0.35, height: 7 - Double(i) * 0.35)
                        .position(x: 122 + cos(a) * r, y: 122 + sin(a) * r * 0.72)
                        .opacity(1 - Double(i) * 0.07)
                }
            }
            IconView(name: "sun", size: 15)
                .position(x: 122 + cos(t * 2 * .pi) * 46, y: 122 + sin(t * 2 * .pi) * 33)
                .opacity(0.9)
        }
    }

    // MARK: 12. 宇宙大爆炸

    private func bigbang(_ t: Double) -> some View {
        let burst = max(0, (t - 0.18) / 0.82)          // 0 点火 → 1 扩散完成
        return ZStack {
            LinearGradient(colors: [Color(hex: 0x0E1330), Color(hex: 0x1B2252)],
                           startPoint: .top, endPoint: .bottom)
            if burst == 0 {
                Circle()
                    .fill(Color.white)
                    .frame(width: 12, height: 12)
                    .shadow(color: .white, radius: 16)
                    .position(x: 122, y: 122)
            } else {
                ForEach(0..<3, id: \.self) { ring in
                    let rp = max(0, burst - Double(ring) * 0.16)
                    Circle()
                        .stroke(Color(hex: 0xFFD24D).opacity((1 - rp) * 0.8),
                                style: StrokeStyle(lineWidth: 3.5 - rp * 2.4))
                        .frame(width: rp * 230, height: rp * 230)
                        .position(x: 122, y: 122)
                }
                ForEach(0..<12, id: \.self) { i in
                    let a = Double(i) / 12 * 2 * .pi + 0.35
                    let r = 14 + burst * 108
                    Circle()
                        .fill(i % 3 == 0 ? Color(hex: 0xFFE58A) : Color(hex: 0xBFD4FF))
                        .frame(width: 6, height: 6)
                        .position(x: 122 + cos(a) * r, y: 122 + sin(a) * r)
                        .opacity(1 - burst * 0.75)
                }
            }
        }
    }

    // MARK: 13. 潮汐（月亮牵引海浪涨落）

    private func tide(_ t: Double) -> some View {
        let moonX = 122 + cos(t * 2 * .pi) * 74
        let pull = cos(t * 2 * .pi)                  // 月亮在正上方时满潮
        let level = 168 - pull * 12
        return ZStack {
            nightSky()
            IconView(name: "moon", size: 40)
                .position(x: moonX, y: 52)
            // 海面（两层波）
            ForEach(0..<2, id: \.self) { layer in
                WavePath(phase: t * 2 * .pi * 3 + Double(layer) * 1.3, level: level + CGFloat(layer) * 9)
                    .fill(Color(hex: layer == 0 ? 0x5FA8E0 : 0x4E8FD0).opacity(layer == 0 ? 0.9 : 0.75))
            }
            IconView(name: "sprout", size: 22).position(x: 30, y: level - 12).opacity(0.9)
        }
    }

    /// 简易正弦波海面
    private struct WavePath: Shape {
        var phase: Double
        var level: CGFloat

        func path(in rect: CGRect) -> Path {
            var p = Path()
            p.move(to: CGPoint(x: 0, y: rect.height))
            p.addLine(to: CGPoint(x: 0, y: level))
            var x: CGFloat = 0
            while x <= rect.width {
                let y = level + sin(Double(x) / 30 + phase) * 5
                p.addLine(to: CGPoint(x: x, y: y))
                x += 8
            }
            p.addLine(to: CGPoint(x: rect.width, y: rect.height))
            p.closeSubpath()
            return p
        }
    }
}
