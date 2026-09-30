import Foundation
import Combine

// MARK: - 进度存储（Documents/progress.json，可注入时钟便于测试）

struct ProgressSnapshot: Codable, Equatable {
    var coins: Int = 0
    var levelStars: [String: Int] = [:]          // "cn-0": 3
    var testedItems: [String] = []               // 实验物品 id
    var collectedScience: [String] = []
    var stickers: [String] = []
    var learnedHanzi: [String] = []
    var learnedPinyin: [String] = []
    var learnedEnglish: [String] = []
    var learnedAstro: [String] = []
    var dailyDone: [String: Int] = [:]           // "2026-09-29|cn": 2
    var streak: Int = 0
    var lastPlayDay: String?
}

final class ProgressStore: ObservableObject {
    @Published var snapshot: ProgressSnapshot
    /// 可注入时钟（测试用）；生产为系统时间
    var now: () -> Date

    private let fileURL: URL
    private let calendar = Calendar(identifier: .gregorian)
    private let dayFormatter: DateFormatter

    init(now: @escaping () -> Date = Date.init, fileName: String = "progress.json") {
        self.now = now
        self.snapshot = ProgressSnapshot()
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        self.fileURL = docs.appendingPathComponent(fileName)
        self.dayFormatter = DateFormatter()
        dayFormatter.dateFormat = "yyyy-MM-dd"
        dayFormatter.timeZone = TimeZone(identifier: "Asia/Shanghai")
        load()
    }

    var todayKey: String { dayFormatter.string(from: now()) }

    // MARK: 读写

    func load() {
        guard let data = try? Data(contentsOf: fileURL),
              let decoded = try? JSONDecoder().decode(ProgressSnapshot.self, from: data) else { return }
        snapshot = decoded
    }

    func save() {
        if let data = try? JSONEncoder().encode(snapshot) {
            try? data.write(to: fileURL, options: .atomic)
        }
    }

    func resetAll() {
        snapshot = ProgressSnapshot()
        save()
    }

    // MARK: 关卡

    func stars(for subject: String, index: Int) -> Int {
        snapshot.levelStars["\(subject)-\(index)"] ?? 0
    }

    /// 完成关卡：累计最高星级、加金币、连击天数、每日任务
    func completeLevel(subject: String, index: Int, stars: Int) {
        let key = "\(subject)-\(index)"
        let old = snapshot.levelStars[key] ?? 0
        if stars > old { snapshot.levelStars[key] = stars }
        if stars > old || old == 0 { snapshot.coins += stars }
        bumpDaily(subject: subject)
        updateStreak()
        save()
    }

    func totalStars(subject: String, total: Int) -> Int {
        (0..<total).reduce(0) { $0 + stars(for: subject, index: $1) }
    }

    func doneCount(subject: String, total: Int) -> Int {
        (0..<total).filter { stars(for: subject, index: $0) > 0 }.count
    }

    /// 地图节点状态：done / current(第一个未完成的) / locked
    func nodeState(subject: String, index: Int, total: Int) -> MapNodeState {
        if stars(for: subject, index: index) > 0 { return .done }
        if index == 0 { return .current }
        return stars(for: subject, index: index - 1) > 0 ? .current : .locked
    }

    // MARK: 每日任务与连击

    func dailyDone(subject: String) -> Int {
        snapshot.dailyDone["\(todayKey)|\(subject)"] ?? 0
    }

    func bumpDaily(subject: String) {
        let key = "\(todayKey)|\(subject)"
        snapshot.dailyDone[key, default: 0] += 1
        pruneOldDaily()
    }

    /// 跨天时清掉历史任务记录（保留最近 7 天）
    func pruneOldDaily() {
        let keys = snapshot.dailyDone.keys.filter {
            guard let dayPart = $0.split(separator: "|").first else { return false }
            return todayKey > String(dayPart) &&
                calendar.date(byAdding: .day, value: -7, to: now())!.timeIntervalSince1970
                    > (dayFormatter.date(from: String(dayPart))?.timeIntervalSince1970 ?? 0)
        }
        keys.forEach { snapshot.dailyDone.removeValue(forKey: $0) }
    }

    func updateStreak() {
        let today = todayKey
        guard snapshot.lastPlayDay != today else { return }
        if let last = snapshot.lastPlayDay,
           let lastDate = dayFormatter.date(from: last),
           let yesterday = calendar.date(byAdding: .day, value: -1, to: now()),
           dayFormatter.string(from: yesterday) == last {
            snapshot.streak += 1
        } else if snapshot.lastPlayDay == nil {
            snapshot.streak = 1
        } else {
            snapshot.streak = 1
        }
        snapshot.lastPlayDay = today
    }

    // MARK: 实验与收集

    func markTested(itemId: String) {
        if !snapshot.testedItems.contains(itemId) {
            snapshot.testedItems.append(itemId)
            save()
        }
    }

    func hasTested(itemId: String) -> Bool {
        snapshot.testedItems.contains(itemId)
    }

    func collectScience(id: String) {
        if !snapshot.collectedScience.contains(id) {
            snapshot.collectedScience.append(id)
            snapshot.coins += 1
            save()
        }
    }

    func addSticker(_ id: String) -> Bool {
        if snapshot.stickers.contains(id) { return false }
        snapshot.stickers.append(id)
        save()
        return true
    }

    func learnHanzi(_ char: String) {
        if !snapshot.learnedHanzi.contains(char) {
            snapshot.learnedHanzi.append(char)
            save()
        }
    }

    func learnPinyin(_ letter: String) {
        if !snapshot.learnedPinyin.contains(letter) {
            snapshot.learnedPinyin.append(letter)
            save()
        }
    }

    func learnEnglish(_ word: String) {
        if !snapshot.learnedEnglish.contains(word) {
            snapshot.learnedEnglish.append(word)
            save()
        }
    }

    func learnAstro(_ name: String) {
        if !snapshot.learnedAstro.contains(name) {
            snapshot.learnedAstro.append(name)
            save()
        }
    }
}

enum MapNodeState: Equatable {
    case done, current, locked
}

// MARK: - 设置存储

struct AppSettings: Codable, Equatable {
    var childName: String = "糖糖"
    var avatar: String = "girl"
    var onceMinutes: Int = 15        // 10/15/20/25
    var dailyMinutes: Int = 45       // 30/45/60
    var restIntervalMinutes: Int = 15 // 15/30/0(关)
    var difficulty: String = "auto"  // easy | auto | normal
    var unlockAll: Bool = false
    var muted: Bool = false
}

final class SettingsStore: ObservableObject {
    @Published var settings: AppSettings
    private let fileURL: URL

    init(fileName: String = "settings.json") {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        self.fileURL = docs.appendingPathComponent(fileName)
        if let data = try? Data(contentsOf: fileURL),
           let decoded = try? JSONDecoder().decode(AppSettings.self, from: data) {
            settings = decoded
        } else {
            settings = AppSettings()
        }
    }

    func save() {
        if let data = try? JSONEncoder().encode(settings) {
            try? data.write(to: fileURL, options: .atomic)
        }
    }
}

// MARK: - 家长门（随机两位数加法）

enum ParentGate {
    static func makeQuestion(seed: UInt64? = nil) -> (text: String, answer: Int) {
        let a: Int, b: Int
        if let s = seed {
            var gen = SeededGenerator(seed: s)
            a = Int.random(in: 6...9, using: &gen)
            b = Int.random(in: 6...9, using: &gen)
        } else {
            a = Int.random(in: 6...9)
            b = Int.random(in: 6...9)
        }
        return ("\(a) + \(b) = ?", a + b)
    }

    static func check(_ input: String, answer: Int) -> Bool {
        Int(input.trimmingCharacters(in: .whitespaces)) == answer
    }
}

struct SeededGenerator: RandomNumberGenerator {
    var state: UInt64
    init(seed: UInt64) { state = seed &+ 0x9E3779B97F4A7C15 }
    mutating func next() -> UInt64 {
        state ^= state << 13
        state ^= state >> 7
        state ^= state << 17
        return state
    }
}
