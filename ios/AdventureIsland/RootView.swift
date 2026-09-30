import SwiftUI
import SpriteKit

@main
struct AdventureIslandApp: App {
    @StateObject private var settings = SettingsStore()
    @StateObject private var store = ProgressStore()
    @StateObject private var timeManager: TimeManager
    @StateObject private var speech = SpeechService()
    @StateObject private var toast = ToastCenter()
    @State private var sound = SoundService()

    init() {
        let s = SettingsStore()
        let p = ProgressStore()
        _settings = StateObject(wrappedValue: s)
        _store = StateObject(wrappedValue: p)
        _timeManager = StateObject(wrappedValue: TimeManager(settings: s, store: p))
    }

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(settings)
                .environmentObject(store)
                .environmentObject(timeManager)
                .environmentObject(speech)
                .environmentObject(toast)
                .environment(\.soundService, sound)
                .statusBarHidden(true)
                .onAppear { sound.muted = { settings.settings.muted } }
        }
    }
}

// MARK: - 音效环境注入

private struct SoundServiceKey: EnvironmentKey {
    static let defaultValue = SoundService()
}

extension EnvironmentValues {
    var soundService: SoundService {
        get { self[SoundServiceKey.self] }
        set { self[SoundServiceKey.self] = newValue }
    }
}

// MARK: - 路由

enum Route: Equatable {
    case map
    case level(subject: String, index: Int)
    case lab
    case collection
    case parent
}

struct RootView: View {
    @EnvironmentObject var store: ProgressStore
    @EnvironmentObject var settings: SettingsStore
    @EnvironmentObject var timeManager: TimeManager
    @EnvironmentObject var speech: SpeechService
    @EnvironmentObject var toast: ToastCenter
    @State private var route: Route = .map
    @State private var confettiTrigger = 0
    @State private var showResetConfirm = false

    private let timer = Timer.publish(every: 1, on: .main, in: .common).autoconnect()

    var body: some View {
        ZStack {
            switch route {
            case .map:
                MapView(route: $route, confetti: $confettiTrigger)
            case .level(let subject, let index):
                LevelView(route: $route, confetti: $confettiTrigger, subject: subject, index: index)
            case .lab:
                LabView(route: $route, confetti: $confettiTrigger)
            case .collection:
                CollectionView(route: $route)
            case .parent:
                ParentView(route: $route)
            }

            ToastOverlay()
            ConfettiLayer(trigger: confettiTrigger)
            RestOverlay()
        }
        .onReceive(timer) { _ in
            timeManager.tick()
            if case .resting = timeManager.phase { speech.stop() }
        }
        .animation(.easeInOut(duration: 0.25), value: route)
    }
}

// MARK: - 休息/护眼遮罩

struct RestOverlay: View {
    @EnvironmentObject var timeManager: TimeManager

    var body: some View {
        switch timeManager.phase {
        case .resting(let left):
            restCard(title: "👀 小眼睛休息一下",
                     subtitle: "看看窗外最远的地方，数 \(left) 秒就回来",
                     accent: .brandBlueDk)
        case .dayOver:
            restCard(title: "🌙 今天的探险结束啦",
                     subtitle: "明天再来玩，明天有新关卡等你哦",
                     accent: .brandPurpleDk)
        case .playing:
            EmptyView()
        }
    }

    private func restCard(title: String, subtitle: String, accent: Color) -> some View {
        ZStack {
            Color.black.opacity(0.55).ignoresSafeArea()
            VStack(spacing: 18) {
                if case .resting(let left) = timeManager.phase {
                    ZStack {
                        Circle().stroke(.white.opacity(0.25), lineWidth: 10)
                        Circle()
                            .trim(from: 0, to: Double(left) / Double(TimeManager.restDurationSeconds))
                            .stroke(.brandYellow, style: StrokeStyle(lineWidth: 10, lineCap: .round))
                            .rotationEffect(.degrees(-90))
                        Text("\(left)")
                            .font(.kidTitle(44))
                            .foregroundColor(.white)
                    }
                    .frame(width: 110, height: 110)
                } else {
                    Text("🌟")
                        .font(.system(size: 72))
                }
                Text(title)
                    .font(.kidTitle(32))
                    .foregroundColor(.white)
                Text(subtitle)
                    .font(.kidBody(19))
                    .foregroundColor(.white.opacity(0.9))
                    .multilineTextAlignment(.center)
                if case .dayOver = timeManager.phase {
                    Text("（想继续玩？请爸爸妈妈在家长中心调整）")
                        .font(.kidBody(14))
                        .foregroundColor(.white.opacity(0.65))
                }
            }
            .padding(40)
            .background(
                RoundedRectangle(cornerRadius: 34, style: .continuous)
                    .fill(accent)
            )
            .overlay(RoundedRectangle(cornerRadius: 34, style: .continuous).stroke(.white, lineWidth: 5))
            .shadow(color: .black.opacity(0.3), radius: 30)
        }
        .transition(.opacity)
    }
}
