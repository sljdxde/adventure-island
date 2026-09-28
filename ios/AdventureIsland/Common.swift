import SwiftUI
import UIKit

// MARK: - 图标加载（资源缺失时回退到 Emoji，保证任何环境可运行）

enum IconEmoji {
    static let map: [String: String] = [
        "girl": "🧒", "panda": "🐼", "fox": "🦊", "robot": "🤖", "duck": "🦆",
        "school": "🏫", "ferris": "🎡", "volcano": "🌋", "castle": "🏰",
        "apple": "🍎", "banana": "🍌", "rock": "🪨", "wood": "🪵", "key": "🔑",
        "sponge": "🧽", "balloon": "🎈", "ice": "🧊", "magnet": "🧲",
        "rainbow": "🌈", "sprout": "🌱", "sun": "☀️", "sunrays": "🌞",
        "sunface": "😊", "moon": "🌙", "wave": "🌊", "sunrise": "🌅",
        "cake": "🎂", "calendar": "📅", "star": "⭐", "medal": "🏅",
        "gift": "🎁", "clip": "📋", "lock": "🔒", "speaker": "🔊",
        "home": "🏠", "back": "🔙", "fire": "🔥", "goggles": "🥽",
        "flask": "🧪", "book": "📖", "sparkle": "✨", "crystal": "💎",
        "flower": "🌸", "leaf": "🍃", "rocket": "🚀", "party": "🎉",
        "question": "❓", "clock": "⏰", "shield": "🛡", "chart": "📈",
        "slider": "🎚", "bulb": "💡", "heart": "❤️", "equal": "🟰",
        "hanzi": "🈶", "block": "🟨", "blockok": "✅", "blocklock": "🔒",
        "coin": "🪙", "dice": "🎲", "pipe-red": "🟥", "pipe-blue": "🟦",
        "pipe-purple": "🟪", "flag": "🏁", "starface": "🌟", "brick": "🧱",
        "hills-back": "⛰", "hills-front": "🏞"
    ]
}

struct IconView: View {
    let name: String
    var size: CGFloat = 40
    var body: some View {
        if let ui = UIImage(named: name) {
            Image(uiImage: ui)
                .resizable()
                .interpolation(.medium)
                .scaledToFit()
                .frame(width: size, height: size)
        } else {
            Text(IconEmoji.map[name] ?? "❓")
                .font(.system(size: size * 0.82))
        }
    }
}

// MARK: - 果冻按钮

struct JellyButtonStyle: ButtonStyle {
    var base: Color
    var dark: Color
    var edge: Color
    var textColor: Color = .white
    var fontSize: CGFloat = 22

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.kidHead(fontSize))
            .foregroundColor(textColor)
            .padding(.horizontal, 26)
            .padding(.vertical, 13)
            .background(
                Capsule().fill(
                    LinearGradient(
                        colors: [base.opacity(0.88), base, dark],
                        startPoint: .top, endPoint: .bottom
                    )
                )
            )
            .overlay(
                Capsule()
                    .fill(
                        LinearGradient(
                            colors: [.white.opacity(0.42), .white.opacity(0.05)],
                            startPoint: .top, endPoint: .bottom
                        )
                    )
                    .padding(2.5)
                    .blendMode(.plusLighter)
                    .allowsHitTesting(false)
            )
            .overlay(Capsule().stroke(edge, lineWidth: 1))
            .shadow(color: edge.opacity(0.9), radius: 0, x: 0, y: 5)
            .shadow(color: .ink.opacity(0.14), radius: 10, x: 0, y: 6)
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
            .offset(y: configuration.isPressed ? 3 : 0)
            .animation(.easeOut(duration: 0.08), value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == JellyButtonStyle {
    static var jellyOrange: JellyButtonStyle {
        JellyButtonStyle(base: .brandOrange, dark: .brandOrangeDk, edge: .brandOrangeDdk)
    }
    static var jellyYellow: JellyButtonStyle {
        JellyButtonStyle(base: .brandYellow, dark: .brandYellowDk, edge: .brandYellowDdk, textColor: Color(hex: 0x7A4A00))
    }
    static var jellyGreen: JellyButtonStyle {
        JellyButtonStyle(base: .brandGreen, dark: .brandGreenDk, edge: .brandGreenDdk)
    }
    static var jellyBlue: JellyButtonStyle {
        JellyButtonStyle(base: .brandBlue, dark: .brandBlueDk, edge: .brandBlueDdk)
    }
    static var jellyPurple: JellyButtonStyle {
        JellyButtonStyle(base: .brandPurple, dark: .brandPurpleDk, edge: .brandPurpleDdk)
    }
    static var jellyCream: JellyButtonStyle {
        JellyButtonStyle(
            base: Color(hex: 0xFFFDF6), dark: Color(hex: 0xFFF1D6),
            edge: Color(hex: 0xE4D2AC), textColor: .ink
        )
    }
}

// MARK: - 圆角方图标按钮

struct SquareIconButton: View {
    let icon: String
    var label: String? = nil
    var size: CGFloat = 62
    var action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: -2) {
                IconView(name: icon, size: size * 0.5)
                if let label {
                    Text(label)
                        .font(.system(size: 10.5, weight: .heavy))
                        .foregroundColor(.brandOrangeDk)
                }
            }
            .frame(width: size, height: label == nil ? size : size + 12)
            .background(
                RoundedRectangle(cornerRadius: size * 0.33, style: .continuous)
                    .fill(LinearGradient(colors: [Color(hex: 0xFFFDF6), Color(hex: 0xFFF3DC)], startPoint: .top, endPoint: .bottom))
            )
            .overlay(
                RoundedRectangle(cornerRadius: size * 0.33, style: .continuous)
                    .stroke(Color(hex: 0xE8D5AE), lineWidth: 1.5)
            )
            .shadow(color: Color(hex: 0xE8D5AE), radius: 0, x: 0, y: 4)
            .shadow(color: .ink.opacity(0.10), radius: 8, y: 6)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - 金色徽章（星星/金币计数）

struct GoldChip: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 8) {
            ZStack {
                Circle().fill(
                    RadialGradient(
                        colors: [Color(hex: 0xFFE68A), .gold, .goldDk],
                        center: UnitPoint(x: 0.35, y: 0.3), radius: 0.9
                    )
                )
                IconView(name: icon, size: 19)
            }
            .frame(width: 33, height: 33)
            Text(text)
                .font(.kidHead(21))
                .foregroundStyle(
                    LinearGradient(colors: [Color(hex: 0x8A5B00), Color(hex: 0x6B4500)], startPoint: .top, endPoint: .bottom)
                )
        }
        .padding(.leading, 6)
        .padding(.trailing, 18)
        .padding(.vertical, 7)
        .background(Capsule().fill(LinearGradient(colors: [Color(hex: 0xFFFDF4), Color(hex: 0xFFF2CE)], startPoint: .top, endPoint: .bottom)))
        .overlay(Capsule().stroke(Color(hex: 0xEBD9A8), lineWidth: 1.5))
        .shadow(color: Color(hex: 0xEBD9A8), radius: 0, x: 0, y: 4)
        .shadow(color: .ink.opacity(0.10), radius: 8, y: 5)
    }
}

// MARK: - 贴纸卡容器

struct StickerCard<Content: View>: View {
    var corner: CGFloat = 30
    var stroke: Color = .clear
    @ViewBuilder var content: Content

    var body: some View {
        content
            .background(
                RoundedRectangle(cornerRadius: corner, style: .continuous)
                    .fill(LinearGradient(colors: [.white, .cream], startPoint: .top, endPoint: .bottom))
            )
            .overlay(
                RoundedRectangle(cornerRadius: corner, style: .continuous)
                    .stroke(.white, lineWidth: 5)
            )
            .overlay(
                RoundedRectangle(cornerRadius: corner + 2, style: .continuous)
                    .stroke(stroke == .clear ? Color.ink.opacity(0.07) : stroke.opacity(0.35), lineWidth: 2)
            )
            .shadow(color: .ink.opacity(0.15), radius: 18, x: 0, y: 10)
    }
}

// MARK: - 金色进度条

struct GoldTrack: View {
    var ratio: Double
    var height: CGFloat = 12

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule().fill(Color.white.opacity(0.75))
                Capsule()
                    .fill(LinearGradient(colors: [Color(hex: 0xFFE58A), .gold], startPoint: .top, endPoint: .bottom))
                    .frame(width: max(0, min(1, ratio)) * geo.size.width)
                    .overlay(Capsule().stroke(.black.opacity(0.06), lineWidth: 1))
            }
        }
        .frame(height: height)
        .animation(.easeOut(duration: 0.4), value: ratio)
    }
}

// MARK: - 环节步骤条（斑马式高亮）

struct StepChipState: Equatable {
    var title: String
    var state: State
    enum State { case done, now, todo }
}

struct StepChips: View {
    let chips: [StepChipState]

    var body: some View {
        HStack(spacing: 6) {
            ForEach(chips.indices, id: \.self) { i in
                if i > 0 { DashSeparator() }
                chip(chips[i], number: i + 1)
            }
        }
    }

    @ViewBuilder
    private func chip(_ c: StepChipState, number: Int) -> some View {
        HStack(spacing: 6) {
            ZStack {
                switch c.state {
                case .done:
                    Circle().fill(.brandGreen)
                    Image(systemName: "checkmark").font(.system(size: 11, weight: .black)).foregroundColor(.white)
                case .now:
                    Circle().fill(.white.opacity(0.3))
                    Text("\(number)")
                        .font(.system(size: 12, weight: .black)).foregroundColor(.white)
                case .todo:
                    Circle().fill(Color(hex: 0xEFE6D2))
                    Text("\(number)")
                        .font(.system(size: 12, weight: .black)).foregroundColor(Color(hex: 0xB7A88F))
                }
            }
            .frame(width: 20, height: 20)
            Text(c.title).font(.kidBody(16))
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 7)
        .background(Capsule().fill(capsuleFill(c.state)))
        .shadow(color: shadowColor(c.state), radius: 0, x: 0, y: 3)
    }

    private func capsuleFill(_ s: StepChipState.State) -> Color {
        switch s {
        case .done: return Color(hex: 0xEFFBEF)
        case .now: return .brandOrange
        case .todo: return .white.opacity(0.94)
        }
    }
    private func shadowColor(_ s: StepChipState.State) -> Color {
        switch s {
        case .done: return .brandGreenDdk.opacity(0.5)
        case .now: return .brandOrangeDdk
        case .todo: return .ink.opacity(0.12)
        }
    }
}

struct DashSeparator: View {
    var body: some View {
        Rectangle()
            .fill(Color.clear)
            .frame(width: 15, height: 3)
            .overlay(
                Rectangle()
                    .fill(Color.ink.opacity(0.22))
                    .frame(width: 3)
                    .frame(maxWidth: .infinity, alignment: .leading)
            )
            .mask(
                HStack(spacing: 4) {
                    Rectangle(); Rectangle()
                }
            )
    }
}

// MARK: - 场景背景（天空+光晕+云+远山）

struct SceneBackground: View {
    let theme: AppTheme

    var body: some View {
        ZStack {
            LinearGradient(colors: theme.sky, startPoint: .top, endPoint: .bottom)
            Circle()
                .fill(
                    RadialGradient(colors: [Color(hex: 0xFFF6C9).opacity(0.95), Color(hex: 0xFFE28A).opacity(0.35), .clear],
                                   center: .center, startRadius: 0, endRadius: 150)
                )
                .frame(width: 320, height: 320)
                .offset(x: -180, y: -180)
            CloudShape()
                .fill(.white.opacity(0.92))
                .frame(width: 150, height: 40)
                .offset(x: -240, y: -270)
                .modifier(DriftModifier(duration: 38))
            CloudShape()
                .fill(.white.opacity(0.8))
                .frame(width: 100, height: 30)
                .offset(x: 100, y: -190)
                .modifier(DriftModifier(duration: 28, reverse: true))
            CloudShape()
                .fill(.white.opacity(0.85))
                .frame(width: 180, height: 46)
                .offset(x: 60, y: -310)
                .modifier(DriftModifier(duration: 46))
            HillLayer(asset: "hills-back", tint: Color(hex: 0xB9E88C), fallback: .brandGreen.opacity(0.45))
                .frame(height: 300)
                .frame(maxHeight: .infinity, alignment: .bottom)
                .opacity(theme.hillOpacity)
            HillLayer(asset: "hills-front", tint: .brandGreen, fallback: .brandGreen)
                .frame(height: 250)
                .frame(maxHeight: .infinity, alignment: .bottom)
        }
        .ignoresSafeArea()
    }
}

struct CloudShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let h = rect.height
        p.addEllipse(in: CGRect(x: 0, y: h * 0.35, width: rect.width * 0.5, height: h * 0.65))
        p.addEllipse(in: CGRect(x: rect.width * 0.22, y: 0, width: rect.width * 0.45, height: h))
        p.addEllipse(in: CGRect(x: rect.width * 0.52, y: h * 0.28, width: rect.width * 0.48, height: h * 0.72))
        return p
    }
}

struct HillLayer: View {
    let asset: String
    let tint: Color
    let fallback: Color

    var body: some View {
        GeometryReader { geo in
            if UIImage(named: asset) != nil {
                Image(uiImage: UIImage(named: asset)!)
                    .resizable()
                    .scaledToFit()
                    .frame(width: geo.size.width, height: geo.size.height, alignment: .bottom)
                    .foregroundStyle(tint)
            } else {
                HillShape()
                    .fill(fallback)
            }
        }
    }
}

struct HillShape: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        let w = rect.width, h = rect.height
        p.move(to: CGPoint(x: 0, y: h))
        p.addLine(to: CGPoint(x: 0, y: h * 0.5))
        p.addQuadCurve(to: CGPoint(x: w * 0.3, y: h * 0.42), control: CGPoint(x: w * 0.12, y: h * 0.12))
        p.addQuadCurve(to: CGPoint(x: w * 0.62, y: h * 0.38), control: CGPoint(x: w * 0.45, y: h * 0.6))
        p.addQuadCurve(to: CGPoint(x: w, y: h * 0.34), control: CGPoint(x: w * 0.8, y: h * 0.08))
        p.addLine(to: CGPoint(x: w, y: h))
        p.closeSubpath()
        return p
    }
}

struct DriftModifier: ViewModifier {
    var duration: Double
    var reverse = false

    func body(content: Content) -> some View {
        content
            .onAppear {
                withAnimation(.linear(duration: duration).repeatForever(autoreverses: false)) {
                    // 通过 phase 驱动位移
                }
            }
            .modifier(DriftOffset(reverse: reverse, duration: duration))
    }
}

private struct DriftOffset: ViewModifier {
    @State private var go = false
    var reverse: Bool
    var duration: Double

    func body(content: Content) -> some View {
        content
            .offset(x: go ? 900 : -900)
            .onAppear {
                withAnimation(.linear(duration: duration).repeatForever(autoreverses: false)) {
                    go.toggle()
                }
            }
    }
}

// MARK: - 彩带庆祝

struct ConfettiLayer: View {
    let trigger: Int
    @State private var pieces: [ConfettiPiece] = []

    struct ConfettiPiece: Identifiable {
        let id = UUID()
        let emoji: String
        let x: CGFloat
        let delay: Double
        let scale: CGFloat
    }

    var body: some View {
        ZStack {
            ForEach(pieces) { p in
                Text(p.emoji)
                    .font(.system(size: 30 * p.scale))
                    .offset(x: p.x - 512, y: -420)
                    .transition(.asymmetric(insertion: .identity, removal: .opacity))
                    .modifier(FallModifier(delay: p.delay))
            }
        }
        .allowsHitTesting(false)
        .onChange(of: trigger) { _ in
            guard trigger > 0 else { return }
            let icons = ["⭐", "🎉", "✨", "🌟", "🎊", "💛"]
            pieces = (0..<24).map { i in
                ConfettiPiece(
                    emoji: icons[i % icons.count],
                    x: CGFloat.random(in: 60...960),
                    delay: Double.random(in: 0...0.4),
                    scale: CGFloat.random(in: 0.7...1.4)
                )
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                pieces = []
            }
        }
    }
}

private struct FallModifier: ViewModifier {
    @State private var fallen = false
    let delay: Double

    func body(content: Content) -> some View {
        content
            .onAppear {
                DispatchQueue.main.asyncAfter(deadline: .now() + delay) {
                    withAnimation(.easeIn(duration: 1.5)) { fallen = true }
                }
            }
            .offset(y: fallen ? 900 : 0)
            .opacity(fallen ? 0 : 1)
            .rotationEffect(.degrees(fallen ? 320 : 0))
    }
}

// MARK: - Toast

@MainActor
final class ToastCenter: ObservableObject {
    @Published var message: String = ""
    @Published var visible = false
    private var hideTask: DispatchWorkItem?

    func show(_ text: String, seconds: Double = 1.8) {
        message = text
        withAnimation(.spring(response: 0.35, dampingFraction: 0.8)) { visible = true }
        hideTask?.cancel()
        let task = DispatchWorkItem { [weak self] in
            withAnimation(.easeIn(duration: 0.25)) { self?.visible = false }
        }
        hideTask = task
        DispatchQueue.main.asyncAfter(deadline: .now() + seconds, execute: task)
    }
}

struct ToastOverlay: View {
    @EnvironmentObject var toast: ToastCenter

    var body: some View {
        VStack {
            Spacer()
            Text(toast.message)
                .font(.kidHead(19))
                .foregroundColor(.cream)
                .padding(.horizontal, 28)
                .padding(.vertical, 14)
                .background(Capsule().fill(Color.ink.opacity(0.9)))
                .shadow(color: .ink.opacity(0.3), radius: 14, y: 8)
                .opacity(toast.visible ? 1 : 0)
                .scaleEffect(toast.visible ? 1 : 0.9)
                .padding(.bottom, 66)
        }
        .allowsHitTesting(false)
    }
}

// MARK: - 振动反馈

enum Haptics {
    static func tap() {
        UIImpactFeedbackGenerator(style: .light).impactOccurred()
    }
    static func success() {
        UINotificationFeedbackGenerator().notificationOccurred(.success)
    }
}
