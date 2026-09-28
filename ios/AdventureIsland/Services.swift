import Foundation
import Combine
import AVFoundation

// MARK: - 用时管理（护眼：单次时长 / 每日上限 / 休息提醒）
// 逻辑与 UI 分离，秒级推进函数可注入测试。

final class TimeManager: ObservableObject {
    enum Phase: Equatable {
        case playing
        case resting(secondsLeft: Int)
        case dayOver
    }

    @Published private(set) var phase: Phase = .playing
    @Published private(set) var todaySeconds: Int = 0
    @Published private(set) var segmentSeconds: Int = 0   // 距上次休息的使用秒数

    private(set) var dayKey: String = ""
    var now: () -> Date
    private let settings: SettingsStore
    private let store: ProgressStore
    private let fileURL: URL
    private let dayFormatter: DateFormatter

    static let restDurationSeconds = 20

    init(settings: SettingsStore, store: ProgressStore, now: @escaping () -> Date = Date.init) {
        self.settings = settings
        self.store = store
        self.now = now
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        self.fileURL = docs.appendingPathComponent("usage.json")
        self.dayFormatter = DateFormatter()
        dayFormatter.dateFormat = "yyyy-MM-dd"
        dayFormatter.timeZone = TimeZone(identifier: "Asia/Shanghai")
        dayKey = dayFormatter.string(from: now())
        loadUsage()
    }

    var dailyLimitSeconds: Int { settings.settings.dailyMinutes * 60 }
    var sessionLimitSeconds: Int { settings.settings.onceMinutes * 60 }
    var restIntervalSeconds: Int { settings.settings.restIntervalMinutes * 60 }
    var remainingTodaySeconds: Int { max(0, dailyLimitSeconds - todaySeconds) }

    // MARK: 每秒推进（RootView 的 Timer 驱动；测试可批量推进）

    func tick() {
        advance(seconds: 1)
    }

    func advance(seconds: Int) {
        guard seconds > 0 else { return }
        let newDay = dayFormatter.string(from: now())
        if newDay != dayKey {
            dayKey = newDay
            todaySeconds = 0
            saveUsage()
        }

        switch phase {
        case .resting(let left):
            let next = left - seconds
            if next <= 0 {
                phase = .playing
                segmentSeconds = 0
            } else {
                phase = .resting(secondsLeft: next)
            }

        case .dayOver:
            break

        case .playing:
            todaySeconds += seconds
            segmentSeconds += seconds
            saveUsage()
            if todaySeconds >= dailyLimitSeconds {
                phase = .dayOver
            } else if restIntervalSeconds > 0, segmentSeconds >= restIntervalSeconds {
                phase = .resting(secondsLeft: Self.restDurationSeconds)
            } else if segmentSeconds >= sessionLimitSeconds {
                phase = .resting(secondsLeft: Self.restDurationSeconds)
            }
        }
    }

    /// 家长手动"再玩一次"：清除当日累计
    func resetToday() {
        todaySeconds = 0
        segmentSeconds = 0
        phase = .playing
        saveUsage()
    }

    // MARK: 持久化（跨启动保留当日用量）

    private struct UsageRecord: Codable {
        var day: String
        var seconds: Int
    }

    private func loadUsage() {
        guard let data = try? Data(contentsOf: fileURL),
              let rec = try? JSONDecoder().decode(UsageRecord.self, from: data),
              rec.day == dayKey else {
            todaySeconds = 0
            return
        }
        todaySeconds = rec.seconds
        if todaySeconds >= dailyLimitSeconds { phase = .dayOver }
    }

    private func saveUsage() {
        let rec = UsageRecord(day: dayKey, seconds: todaySeconds)
        if let data = try? JSONEncoder().encode(rec) {
            try? data.write(to: fileURL, options: .atomic)
        }
    }
}

// MARK: - 语音朗读（系统 TTS，zh-CN 慢速）

struct SpeechConfig: Equatable {
    var text: String
    var language: String = "zh-CN"
    var rate: Float = 0.45
    var pitch: Float = 1.15
    var volume: Float = 1.0
}

enum SpeechBuilder {
    static func utteranceConfig(text: String) -> SpeechConfig {
        SpeechConfig(text: text)
    }
}

final class SpeechService: NSObject, ObservableObject, AVSpeechSynthesizerDelegate {
    private let synth = AVSpeechSynthesizer()
    @Published var isSpeaking = false

    override init() {
        super.init()
        synth.delegate = self
    }

    func speak(_ text: String) {
        guard !text.isEmpty else { return }
        let cfg = SpeechBuilder.utteranceConfig(text: text)
        let u = AVSpeechUtterance(string: cfg.text)
        u.voice = AVSpeechSynthesisVoice(language: cfg.language)
        u.rate = cfg.rate
        u.pitchMultiplier = cfg.pitch
        u.volume = cfg.volume
        u.postUtteranceDelay = 0.05
        stop()
        synth.speak(u)
    }

    func stop() {
        synth.stopSpeaking(at: .immediate)
        isSpeaking = false
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didFinish utterance: AVSpeechUtterance) {
        isSpeaking = false
    }

    func speechSynthesizer(_ synthesizer: AVSpeechSynthesizer, didStart utterance: AVSpeechUtterance) {
        isSpeaking = true
    }
}

// MARK: - 音效（正弦波蜂鸣，无需音频素材）

import AudioToolbox

final class SoundService {
    var muted: () -> Bool

    init(muted: @escaping () -> Bool = { false }) {
        self.muted = muted
    }

    private var engine: AVAudioEngine?
    private var player: AVAudioPlayerNode?

    /// 播放一段频率序列 [(频率Hz, 开始秒, 时长秒)]
    func playTones(_ tones: [(freq: Double, at: Double, dur: Double)]) {
        guard !muted() else { return }
        do {
            let eng = engine ?? AVAudioEngine()
            let ply = player ?? AVAudioPlayerNode()
            if engine == nil {
                engine = eng
                player = ply
                eng.attach(ply)
                ply.volume = 0.16
                eng.connect(ply, to: eng.mainMixerNode, format: nil)
                try eng.start()
            }
            guard eng.isRunning else { return }
            let format = AVAudioFormat(standardFormatWithSampleRate: 44100, channels: 1)!

            for t in tones {
                let frames = AVAudioFrameCount(44100 * t.dur)
                guard let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frames) else { continue }
                buffer.frameLength = frames
                let data = buffer.floatChannelData![0]
                for i in 0..<Int(frames) {
                    let sec = Double(i) / 44100
                    // 淡入淡出防爆音
                    let env = min(1, sec / 0.01) * min(1, (t.dur - sec) / 0.03)
                    data[i] = Float(sin(2 * .pi * t.freq * sec) * env)
                }
                // 绝对主机时间 = 现在 + 偏移
                let when = AVAudioTime(hostTime: mach_absolute_time() + AVAudioTime.hostTime(forSeconds: t.at))
                ply.scheduleBuffer(buffer, at: when, options: [], completionHandler: nil)
            }
            if !ply.isPlaying { ply.play() }
        } catch {
            // 音频失败不影响功能
        }
    }

    func correct() { playTones([(523, 0, 0.16), (784, 0.12, 0.22)]) }
    func wrong() { playTones([(240, 0, 0.2)]) }
    func coin() { playTones([(988, 0, 0.08), (1319, 0.07, 0.18)]) }

    static func systemTap() {
        AudioServicesPlaySystemSound(1104)
    }
}

// MARK: - 浮沉物理模型（纯函数，供 SpriteKit 与单元测试共用）
// 坐标：水面 = 0，向上为正。漂浮物入水后受浮力+阻尼，最终在水面附近收敛；
// 沉物持续下落，由场景钳制在水底。

struct BuoyancyState: Equatable {
    var y: Double        // 相对水面的高度
    var velocity: Double
}

enum BuoyancyModel {
    static let gravity: Double = -980        // pt/s²
    static let buoyantAccel: Double = 1400   // 水中向上加速度
    static let waterDamping: Double = 6.0    // 水中线性阻尼
    static let dt: Double = 1.0 / 60.0

    /// 推进一步
    static func step(_ state: BuoyancyState, isFloat: Bool) -> BuoyancyState {
        var v = state.velocity
        if state.y <= 0 {
            let a = isFloat ? buoyantAccel : gravity
            v += a * dt
            v -= v * waterDamping * dt
        } else {
            v += gravity * dt
        }
        return BuoyancyState(y: state.y + v * dt, velocity: v)
    }

    /// 模拟 n 步（测试用）；沉物到达水底即停
    static func simulate(_ state: BuoyancyState, isFloat: Bool, steps: Int, floorY: Double = -400) -> BuoyancyState {
        var s = state
        for _ in 0..<steps {
            s = step(s, isFloat: isFloat)
            if s.y < floorY {
                s.y = floorY
                s.velocity = 0
                break
            }
        }
        return s
    }
}
