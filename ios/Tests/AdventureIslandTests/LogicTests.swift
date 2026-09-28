import XCTest
@testable import AdventureIsland

/// 护眼时长管理：单次限制 / 休息 / 每日上限 / 跨天重置
final class TimeManagerTests: XCTestCase {

    private func makeManager(once: Int = 15, daily: Int = 45, rest: Int = 15) -> (TimeManager, UnsafeMutablePointer<Date>, SettingsStore) {
        let settings = SettingsStore(fileName: "test-\(UUID().uuidString).json")
        settings.settings.onceMinutes = once
        settings.settings.dailyMinutes = daily
        settings.settings.restIntervalMinutes = rest
        let holder = UnsafeMutablePointer<Date>.allocate(capacity: 1)
        holder.initialize(to: Self.date("2026-09-29 09:00:00")!)
        let store = ProgressStore(now: { holder.pointee }, fileName: "test-\(UUID().uuidString).json")
        let manager = TimeManager(settings: settings, store: store, now: { holder.pointee })
        return (manager, holder, settings)
    }

    static func date(_ s: String) -> Date? {
        let df = DateFormatter()
        df.dateFormat = "yyyy-MM-dd HH:mm:ss"
        df.timeZone = TimeZone(identifier: "Asia/Shanghai")
        return df.date(from: s)
    }

    func testRestTriggersAfterSessionLimit() {
        let (manager, holder, _) = makeManager(once: 15, rest: 0)   // 关闭间隔提醒，仅测单次限制
        // 推进 14 分钟 59 秒：仍在玩
        for _ in 0..<(14 * 60 + 59) { manager.tick(); holder.pointee += 1 }
        XCTAssertEqual(manager.phase, .playing)
        manager.tick()
        holder.pointee += 1
        if case .resting(let left) = manager.phase {
            XCTAssertEqual(left, TimeManager.restDurationSeconds)
        } else {
            XCTFail("达到单次时长后应进入休息")
        }
        // 休息 20 秒后恢复，且计时段清零
        for _ in 0..<TimeManager.restDurationSeconds {
            manager.tick(); holder.pointee += 1
        }
        XCTAssertEqual(manager.phase, .playing)
        XCTAssertEqual(manager.segmentSeconds, 1)
    }

    func testDayOverAtDailyLimit() {
        let (manager, holder, _) = makeManager(daily: 45)
        for _ in 0..<(45 * 60) {
            manager.tick()
            holder.pointee += 1
            if case .dayOver = manager.phase { return }
        }
        XCTFail("达到每日上限后应进入 dayOver")
    }

    func testRestInterval() {
        let (manager, holder, _) = makeManager(once: 25, rest: 15)
        for _ in 0..<(15 * 60) {
            manager.tick(); holder.pointee += 1
        }
        if case .resting = manager.phase {
            // OK
        } else {
            XCTFail("休息间隔 15 分钟后应进入休息")
        }
    }

    func testNewDayResetsUsage() {
        let (manager, holder, _) = makeManager(daily: 45)
        for _ in 0..<600 { manager.tick(); holder.pointee += 1 }
        XCTAssertEqual(manager.todaySeconds, 600)
        // 跨天
        holder.pointee = Self.date("2026-09-30 08:00:00")!
        manager.tick()
        XCTAssertEqual(manager.todaySeconds, 1, "跨天应清零当日累计")
        XCTAssertEqual(manager.phase, .playing)
    }

    func testParentResetToday() {
        let (manager, holder, _) = makeManager(daily: 1)
        for _ in 0..<(1 * 60) { manager.tick(); holder.pointee += 1 }
        if case .dayOver = manager.phase {} else { XCTFail("应 dayOver") }
        manager.resetToday()
        XCTAssertEqual(manager.todaySeconds, 0)
        XCTAssertEqual(manager.phase, .playing)
    }
}

/// 浮沉物理模型
final class BuoyancyModelTests: XCTestCase {

    func testFloatItemConvergesToSurface() {
        let final = BuoyancyModel.simulate(BuoyancyState(y: -80, velocity: 0), isFloat: true, steps: 900)
        XCTAssertTrue(abs(final.y) < 60, "漂浮物应稳定在水面附近，实际 y=\(final.y)")
        XCTAssertTrue(abs(final.velocity) < 60, "漂浮物最终速度应很小，实际 v=\(final.velocity)")
    }

    func testFloatItemDroppedFromAboveAlsoFloats() {
        let final = BuoyancyModel.simulate(BuoyancyState(y: 250, velocity: 0), isFloat: true, steps: 900)
        XCTAssertTrue(final.y > -60 && final.y < 70, "从上方投入的漂浮物最终应回到水面附近，实际 y=\(final.y)")
    }

    func testSinkItemReachesFloor() {
        let floor: Double = -400
        let final = BuoyancyModel.simulate(BuoyancyState(y: -80, velocity: 0), isFloat: false, steps: 900, floorY: floor)
        XCTAssertEqual(final.y, floor, accuracy: 0.001)
        XCTAssertEqual(final.velocity, 0, accuracy: 0.001)
    }

    func testStepIsDeterministic() {
        let a = BuoyancyModel.step(BuoyancyState(y: -50, velocity: 0), isFloat: true)
        let b = BuoyancyModel.step(BuoyancyState(y: -50, velocity: 0), isFloat: true)
        XCTAssertEqual(a, b, "物理步进必须确定性（同一输入同输出）")
    }
}

/// 语音配置
final class SpeechConfigTests: XCTestCase {
    func testBuilderDefaults() {
        let cfg = SpeechBuilder.utteranceConfig(text: "你好")
        XCTAssertEqual(cfg.language, "zh-CN")
        XCTAssertEqual(cfg.rate, 0.45, accuracy: 0.001)
        XCTAssertEqual(cfg.text, "你好")
    }
}
