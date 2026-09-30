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
    var coinLedger: [CoinEntry] = []             // v0.8 金币账本：每笔来源/数额/时间（决策 12）
    var brickClaims: [String] = []               // 问号砖已领日期："2026-09-30|brick-cn"（决策 13）
    var mushroomBuff: Bool = false               // 幸运蘑菇：持有一次答错豁免（决策 8，工单03）

    init() {}

    private enum CodingKeys: String, CodingKey {
        case coins, levelStars, testedItems, collectedScience, stickers
        case learnedHanzi, learnedPinyin, learnedEnglish, learnedAstro
        case dailyDone, streak, lastPlayDay, coinLedger, brickClaims, mushroomBuff
    }

    /// 字段全部 decodeIfPresent + 默认值：旧版本 progress.json（无账本/砖块字段）解码不失败，
    /// 否则 load() 的 try? 会静默清空孩子全部进度（规格 US26 升级不丢进度）
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        coins = try c.decodeIfPresent(Int.self, forKey: .coins) ?? 0
        levelStars = try c.decodeIfPresent([String: Int].self, forKey: .levelStars) ?? [:]
        testedItems = try c.decodeIfPresent([String].self, forKey: .testedItems) ?? []
        collectedScience = try c.decodeIfPresent([String].self, forKey: .collectedScience) ?? []
        stickers = try c.decodeIfPresent([String].self, forKey: .stickers) ?? []
        learnedHanzi = try c.decodeIfPresent([String].self, forKey: .learnedHanzi) ?? []
        learnedPinyin = try c.decodeIfPresent([String].self, forKey: .learnedPinyin) ?? []
        learnedEnglish = try c.decodeIfPresent([String].self, forKey: .learnedEnglish) ?? []
        learnedAstro = try c.decodeIfPresent([String].self, forKey: .learnedAstro) ?? []
        dailyDone = try c.decodeIfPresent([String: Int].self, forKey: .dailyDone) ?? [:]
        streak = try c.decodeIfPresent(Int.self, forKey: .streak) ?? 0
        lastPlayDay = try c.decodeIfPresent(String.self, forKey: .lastPlayDay)
        coinLedger = try c.decodeIfPresent([CoinEntry].self, forKey: .coinLedger) ?? []
        brickClaims = try c.decodeIfPresent([String].self, forKey: .brickClaims) ?? []
        mushroomBuff = try c.decodeIfPresent(Bool.self, forKey: .mushroomBuff) ?? false
    }
}

// MARK: - 金币账本（v0.8 决策 12：金币只经账本变动，HUD 余额读账本口径）

/// 记账来源（口径见规格决策 11；商店消费在工单08 增加 .shop）
enum CoinSource: String, Codable {
    case levelStars = "level-stars"        // 通关星级奖励
    case mushroomBonus = "mushroom-bonus"  // 3 星通关蘑菇
    case answer = "answer"                 // 题目格答对 +2
    case coinSpace = "coin-space"          // 金币格 +5
    case chest = "chest"                   // 宝箱格 +3~8 随机（决策 11，工单03）
    case brick = "brick"                   // 地图问号砖（每根水管每天一次）
    case labReward = "lab-reward"          // 实验猜对
    case collection = "collection"         // 图鉴收集奖励
}

struct CoinEntry: Codable, Equatable, Identifiable {
    var id = UUID()
    var source: String
    var amount: Int        // 正入负出
    var at: Date
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

    // MARK: 金币账本（只经此路变动；余额永不为负）

    /// 账本条目上限：只留最近 N 笔，防止进度文件无限膨胀（家长统计只看近期口径）
    static let coinLedgerLimit = 1000

    /// 入账/扣款 + 记账 + 落盘。视图层所有金币变动走这里
    func recordCoin(_ source: CoinSource, amount: Int) {
        guard amount != 0 else { return }
        mutateCoin(source: source, amount: amount)
        save()
    }

    /// 记账 + 更新余额（不落盘，供 completeLevel 等已统一 save 的存储方法复用）
    private func mutateCoin(source: CoinSource, amount: Int) {
        snapshot.coins = max(0, snapshot.coins + amount)
        snapshot.coinLedger.append(CoinEntry(source: source.rawValue, amount: amount, at: now()))
        if snapshot.coinLedger.count > Self.coinLedgerLimit {
            snapshot.coinLedger.removeFirst(snapshot.coinLedger.count - Self.coinLedgerLimit)
        }
    }

    /// 账本回放：按来源汇总（家长中心「金币哪来的」统计口径，工单09 消费侧接入）
    func coinTotal(source: CoinSource? = nil) -> Int {
        let target = source?.rawValue
        return snapshot.coinLedger
            .filter { target == nil || $0.source == target }
            .reduce(0) { $0 + $1.amount }
    }

    /// 问号砖：每根水管每天限领一次（决策 13）；当日已领返回 false 不入账
    @discardableResult
    func claimBrick(subject: String) -> Bool {
        let key = "\(todayKey)|brick-\(subject)"
        guard !snapshot.brickClaims.contains(key) else { return false }
        snapshot.brickClaims.append(key)
        mutateCoin(source: .brick, amount: 1)
        save()
        return true
    }

    // MARK: 幸运蘑菇 buff（决策 8：吃到持有，下一次答错不计数，用完即消失；不可重复持有）

    /// 吃到蘑菇格：已持有时不叠加（返回 false）
    @discardableResult
    func grantMushroom() -> Bool {
        guard !snapshot.mushroomBuff else { return false }
        snapshot.mushroomBuff = true
        save()
        return true
    }

    /// 答错时调用：持有则消耗一朵并豁免本次（返回 true = 不计入星级）
    @discardableResult
    func consumeMushroomIfHeld() -> Bool {
        guard snapshot.mushroomBuff else { return false }
        snapshot.mushroomBuff = false
        save()
        return true
    }

    /// 宝箱格金币：3~8 枚随机（决策 11）
    func chestAmount() -> Int {
        Int.random(in: 3...8)
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
        if stars > old || old == 0 { mutateCoin(source: .levelStars, amount: stars) }
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
        // 问号砖已领记录同款剪枝（保留最近 7 天）
        snapshot.brickClaims.removeAll { key in
            guard let dayPart = key.split(separator: "|").first else { return true }
            return todayKey > String(dayPart) &&
                calendar.date(byAdding: .day, value: -7, to: now())!.timeIntervalSince1970
                    > (dayFormatter.date(from: String(dayPart))?.timeIntervalSince1970 ?? 0)
        }
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
            mutateCoin(source: .collection, amount: 1)
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
