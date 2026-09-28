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
