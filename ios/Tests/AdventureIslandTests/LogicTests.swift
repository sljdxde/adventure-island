import XCTest
@testable import AdventureIsland

/// 护眼时长管理：单次限制 / 休息 / 每日上限 / 跨天重置
final class TimeManagerTests: XCTestCase {

    // TimeManager 的 usage.json 固定写在 Documents 下，用例间共享会互相污染 → 每个用例前清掉重来
    override func setUp() {
        super.setUp()
        let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("usage.json")
        try? FileManager.default.removeItem(at: url)
    }

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
        // 休息 20 秒后恢复，且计时段清零（恢复当下尚未使用，须再 tick 才会 +1）
        for _ in 0..<TimeManager.restDurationSeconds {
            manager.tick(); holder.pointee += 1
        }
        XCTAssertEqual(manager.phase, .playing)
        XCTAssertEqual(manager.segmentSeconds, 0)
    }

    func testDayOverAtDailyLimit() {
        let (manager, holder, _) = makeManager(daily: 45)
        // 休息不占当日额度但消耗推进次数 → 在 45 分钟之外多留几次 20s 休息的余量
        let budget = 45 * 60 + 10 * TimeManager.restDurationSeconds
        for _ in 0..<budget {
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

/// 关卡流程状态机：最后一步结算置位 + 星级映射
/// （规格 v0.8 实现决策 22「修复原生端结算不可达」、测试决策「星级映射不变」的回归守卫）
final class LevelFlowTests: XCTestCase {

    // MARK: 星级映射（错 0 题 3 星 / 错 1 题 2 星 / 错 ≥2 题 1 星 —— 规格 US13）

    func testStarsPerfectRun() {
        var flow = LevelFlow()
        flow.advance(stepCount: 3)
        flow.advance(stepCount: 3)
        flow.advance(stepCount: 3)
        XCTAssertEqual(flow.stars, 3, "错 0 题应得 3 星")
    }

    func testStarsOneWrong() {
        var flow = LevelFlow()
        flow.registerWrong()
        XCTAssertEqual(flow.stars, 2, "错 1 题应得 2 星")
    }

    func testStarsTwoOrMoreWrong() {
        var flow = LevelFlow()
        flow.registerWrong()
        flow.registerWrong()
        XCTAssertEqual(flow.stars, 1, "错 2 题应得 1 星")

        var many = LevelFlow()
        for _ in 0..<5 { many.registerWrong() }
        XCTAssertEqual(many.stars, 1, "错 5 题仍为 1 星（保底不再降）")
    }

    // MARK: 最后一步答完 finished 置真（原生端曾永不置真 → 结算卡不可达）

    func testLastStepAdvanceFinishesLevel() {
        var flow = LevelFlow()
        // 三步关：前两步答完只前进，不结算
        flow.advance(stepCount: 3)
        XCTAssertEqual(flow.stepIndex, 1)
        XCTAssertFalse(flow.finished)
        flow.advance(stepCount: 3)
        XCTAssertEqual(flow.stepIndex, 2)
        XCTAssertFalse(flow.finished, "中间步骤不应触发结算")
        // 最后一步答完：必须置 finished 进入结算卡
        flow.advance(stepCount: 3)
        XCTAssertTrue(flow.finished, "最后一步答完 finished 必须置真（原生端结算不可达缺陷的回归守卫）")
    }

    func testSingleStepLevelFinishesOnFirstAdvance() {
        var flow = LevelFlow()
        flow.advance(stepCount: 1)
        XCTAssertTrue(flow.finished, "单步关第一步答完即结算")
    }

    // MARK: 非法输入设防（结算后重复推进 / 空关卡）

    func testAdvanceAfterFinishedIsNoOp() {
        var flow = LevelFlow()
        flow.advance(stepCount: 2)
        flow.advance(stepCount: 2)
        XCTAssertTrue(flow.finished)
        flow.advance(stepCount: 2)
        XCTAssertEqual(flow.stepIndex, 1, "结算后重复 advance 应为无操作")
        XCTAssertTrue(flow.finished)
    }

    func testAdvanceWithEmptyLevelDoesNotFinish() {
        var flow = LevelFlow()
        flow.advance(stepCount: 0)
        XCTAssertFalse(flow.finished, "空关卡（无步骤）不应直接进入结算")
        XCTAssertEqual(flow.stepIndex, 0)
    }

    func testWrongCountAccumulatesAcrossSteps() {
        var flow = LevelFlow()
        flow.registerWrong()
        flow.advance(stepCount: 3)
        flow.registerWrong()
        XCTAssertEqual(flow.wrongCount, 2)
        XCTAssertEqual(flow.stars, 1)
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
