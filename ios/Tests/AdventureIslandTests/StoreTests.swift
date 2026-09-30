import XCTest
@testable import AdventureIsland

/// 进度存储：星级/金币/地图状态/每日任务/连击
final class ProgressStoreTests: XCTestCase {

    private func makeStore(day: String) -> (ProgressStore, Date) {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        df.timeZone = TimeZone(identifier: "Asia/Shanghai")
        let date = df.date(from: day)!
        let store = ProgressStore(now: { date }, fileName: "test-\(UUID().uuidString).json")
        return (store, date)
    }

    func testCompleteLevelAddsStarsAndCoins() {
        let (store, _) = makeStore(day: "2026-09-29")
        store.completeLevel(subject: "cn", index: 0, stars: 3)
        XCTAssertEqual(store.stars(for: "cn", index: 0), 3)
        XCTAssertEqual(store.snapshot.coins, 3)

        // 重玩低星不倒扣
        store.completeLevel(subject: "cn", index: 0, stars: 1)
        XCTAssertEqual(store.stars(for: "cn", index: 0), 3)
        XCTAssertEqual(store.snapshot.coins, 3, "重玩不重复加金币")
    }

    func testNodeStates() {
        let (store, _) = makeStore(day: "2026-09-29")
        XCTAssertEqual(store.nodeState(subject: "cn", index: 0, total: 10), .current)
        XCTAssertEqual(store.nodeState(subject: "cn", index: 1, total: 10), .locked)
        store.completeLevel(subject: "cn", index: 0, stars: 2)
        XCTAssertEqual(store.nodeState(subject: "cn", index: 0, total: 10), .done)
        XCTAssertEqual(store.nodeState(subject: "cn", index: 1, total: 10), .current)
        XCTAssertEqual(store.nodeState(subject: "cn", index: 2, total: 10), .locked)
    }

    func testDailyTasksPerDay() {
        let (store, _) = makeStore(day: "2026-09-29")
        store.bumpDaily(subject: "cn")
        store.bumpDaily(subject: "cn")
        XCTAssertEqual(store.dailyDone(subject: "cn"), 2)
        XCTAssertEqual(store.dailyDone(subject: "math"), 0)
    }

    func testStreakAcrossConsecutiveDays() {
        var date = Self.date("2026-09-28")!
        let store = ProgressStore(now: { date }, fileName: "test-\(UUID().uuidString).json")
        store.updateStreak()
        XCTAssertEqual(store.snapshot.streak, 1)

        date = Self.date("2026-09-29")!   // 连续第二天
        store.updateStreak()
        XCTAssertEqual(store.snapshot.streak, 2)

        date = Self.date("2026-09-29")!   // 同日重复不叠加
        store.updateStreak()
        XCTAssertEqual(store.snapshot.streak, 2)

        date = Self.date("2026-10-01")!   // 断签重置
        store.updateStreak()
        XCTAssertEqual(store.snapshot.streak, 1)
    }

    func testPersistenceRoundTrip() {
        let name = "test-\(UUID().uuidString).json"
        let store1 = ProgressStore(now: { Self.date("2026-09-29")! }, fileName: name)
        store1.completeLevel(subject: "math", index: 3, stars: 2)
        store1.collectScience(id: "sci-apple")
        store1.addSticker("st-fuchen")
        store1.learnHanzi("日")

        let store2 = ProgressStore(now: { Self.date("2026-09-29")! }, fileName: name)
        XCTAssertEqual(store2.stars(for: "math", index: 3), 2)
        XCTAssertEqual(store2.snapshot.coins, 3)   // 2 星 + 1 图鉴
        XCTAssertTrue(store2.snapshot.collectedScience.contains("sci-apple"))
        XCTAssertTrue(store2.snapshot.stickers.contains("st-fuchen"))
        XCTAssertTrue(store2.snapshot.learnedHanzi.contains("日"))
    }

    func testExperimentTestedAndScienceCollect() {
        let (store, _) = makeStore(day: "2026-09-29")
        XCTAssertFalse(store.hasTested(itemId: "rock"))
        store.markTested(itemId: "rock")
        XCTAssertTrue(store.hasTested(itemId: "rock"))
        store.markTested(itemId: "rock")   // 重复
        XCTAssertEqual(store.snapshot.testedItems.count, 1)

        store.collectScience(id: "sci-apple")
        store.collectScience(id: "sci-apple")  // 重复不重复加分
        XCTAssertEqual(store.snapshot.coins, 1)
    }

    static func date(_ s: String) -> Date? {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd"
        df.timeZone = TimeZone(identifier: "Asia/Shanghai")
        return df.date(from: s)
    }
}

/// 设置存储与家长门
final class SettingsAndGateTests: XCTestCase {

    func testSettingsDefaultsAndPersist() {
        let name = "test-\(UUID().uuidString).json"
        let s1 = SettingsStore(fileName: name)
        XCTAssertEqual(s1.settings.onceMinutes, 15)
        XCTAssertEqual(s1.settings.dailyMinutes, 45)
        s1.settings.onceMinutes = 25
        s1.save()
        let s2 = SettingsStore(fileName: name)
        XCTAssertEqual(s2.settings.onceMinutes, 25)
    }

    func testGateQuestionDeterministicWithSeed() {
        let q1 = ParentGate.makeQuestion(seed: 42)
        let q2 = ParentGate.makeQuestion(seed: 42)
        XCTAssertEqual(q1.text, q2.text)
        XCTAssertEqual(q1.answer, q2.answer)
        // 答案范围：两位 6..9 相加
        XCTAssertTrue((12...18).contains(q1.answer))
    }

    func testGateCheck() {
        XCTAssertTrue(ParentGate.check(" 15 ", answer: 15))
        XCTAssertFalse(ParentGate.check("16", answer: 15))
        XCTAssertFalse(ParentGate.check("abc", answer: 15))
    }
}

/// 金币账本（v0.8 工单04）：只经账本变动 / 余额永不透支 / 问号砖每日限次 / 旧进度无损迁移
final class CoinLedgerTests: XCTestCase {

    private func makeStore(start: String = "2026-09-29") -> (ProgressStore, UnsafeMutablePointer<Date>) {
        let holder = UnsafeMutablePointer<Date>.allocate(capacity: 1)
        holder.initialize(to: ProgressStoreTests.date(start)!)
        let store = ProgressStore(now: { holder.pointee }, fileName: "test-\(UUID().uuidString).json")
        return (store, holder)
    }

    func testRecordCoinUpdatesBalanceAndLedger() {
        let (store, _) = makeStore()
        store.recordCoin(.answer, amount: 2)
        store.recordCoin(.answer, amount: 2)
        store.recordCoin(.coinSpace, amount: 5)
        store.recordCoin(.mushroomBonus, amount: 2)
        XCTAssertEqual(store.snapshot.coins, 11)
        XCTAssertEqual(store.coinTotal(), 11, "账本合计必须等于余额")
        XCTAssertEqual(store.coinTotal(source: .answer), 4, "按来源回放：答对收入")
        XCTAssertEqual(store.coinTotal(source: .coinSpace), 5)
        let entries = store.snapshot.coinLedger
        XCTAssertEqual(entries.count, 4)
        XCTAssertEqual(entries.last?.source, CoinSource.mushroomBonus.rawValue)
        XCTAssertEqual(entries.last?.amount, 2)
    }

    func testBalanceNeverGoesNegative() {
        let (store, _) = makeStore()
        store.recordCoin(.answer, amount: 2)
        // 消费侧口径（工单08 商店接入）：扣款超出余额也不透支
        store.recordCoin(.coinSpace, amount: -10)
        XCTAssertEqual(store.snapshot.coins, 0, "余额永不为负")
        XCTAssertEqual(store.coinTotal(), -8, "账本如实记录净额，余额为钳制后的口径")
    }

    func testZeroAmountNotRecorded() {
        let (store, _) = makeStore()
        store.recordCoin(.answer, amount: 0)
        XCTAssertTrue(store.snapshot.coinLedger.isEmpty)
        XCTAssertEqual(store.snapshot.coins, 0)
    }

    func testCompleteLevelAndCollectRecordLedger() {
        let (store, _) = makeStore()
        store.completeLevel(subject: "cn", index: 0, stars: 3)
        store.collectScience(id: "sci-apple")
        XCTAssertEqual(store.coinTotal(source: .levelStars), 3, "通关星级奖励入账本")
        XCTAssertEqual(store.coinTotal(source: .collection), 1, "图鉴收集奖励入账本")
        XCTAssertEqual(store.coinTotal(), store.snapshot.coins)
    }

    func testBrickDailyLimitAndCrossDayReset() {
        let (store, clock) = makeStore(start: "2026-09-29")
        XCTAssertTrue(store.claimBrick(subject: "cn"), "当日首次领取应成功")
        XCTAssertFalse(store.claimBrick(subject: "cn"), "同一根水管当日第二次无金币")
        XCTAssertTrue(store.claimBrick(subject: "math"), "不同水管互不影响")
        XCTAssertEqual(store.coinTotal(source: .brick), 2)

        clock.pointee = ProgressStoreTests.date("2026-09-30")!   // 跨天重置
        XCTAssertTrue(store.claimBrick(subject: "cn"), "跨天后可再领")
        XCTAssertEqual(store.coinTotal(source: .brick), 3)
    }

    func testLegacyProgressDecodesWithoutLedgerFields() throws {
        // v0.7 及以前的 progress.json 没有账本/砖块字段：解码不能失败（否则 load() 会静默清进度）
        let legacy = """
        {"coins":21,"levelStars":{"cn-0":3},"testedItems":["rock"],"collectedScience":[],
         "stickers":[],"learnedHanzi":["日"],"learnedPinyin":[],"learnedEnglish":[],
         "learnedAstro":[],"dailyDone":{"2026-09-29|cn":2},"streak":3,"lastPlayDay":"2026-09-29"}
        """
        let snap = try JSONDecoder().decode(ProgressSnapshot.self, from: Data(legacy.utf8))
        XCTAssertEqual(snap.coins, 21, "旧金币存量无损保留")
        XCTAssertEqual(snap.levelStars["cn-0"], 3)
        XCTAssertTrue(snap.coinLedger.isEmpty)
        XCTAssertTrue(snap.brickClaims.isEmpty)

        // 迁移后正常记账
        let holder = UnsafeMutablePointer<Date>.allocate(capacity: 1)
        holder.initialize(to: ProgressStoreTests.date("2026-09-30")!)
        let store = ProgressStore(now: { holder.pointee }, fileName: "test-\(UUID().uuidString).json")
        store.snapshot = snap
        store.recordCoin(.answer, amount: 2)
        XCTAssertEqual(store.snapshot.coins, 23)
        XCTAssertEqual(store.coinTotal(), 2, "旧余额不计入账本回放，新收入从迁移后起记")
    }

    func testLedgerCappedAtLimit() {
        let (store, _) = makeStore()
        for _ in 0..<(ProgressStore.coinLedgerLimit + 5) {
            store.recordCoin(.answer, amount: 1)
        }
        XCTAssertEqual(store.snapshot.coinLedger.count, ProgressStore.coinLedgerLimit, "账本只留最近 N 笔防膨胀")
        XCTAssertEqual(store.coinTotal(), ProgressStore.coinLedgerLimit)
    }
}
