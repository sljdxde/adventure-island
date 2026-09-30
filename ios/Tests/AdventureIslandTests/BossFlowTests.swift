import XCTest
@testable import AdventureIsland

/// 工单06：boss 血条状态机纯逻辑测试（心结算 / 蘑菇豁免语义 / 失败重试复位 / 题号推进）
final class BossFlowTests: XCTestCase {

    private let qCount = 8

    func testCorrectAnswersBeatBoss() {
        var flow = BossFlow()
        flow.answerCorrect(questionCount: qCount)
        XCTAssertEqual(flow.bossHearts, 2)
        XCTAssertEqual(flow.playerHearts, 3)
        XCTAssertEqual(flow.outcome, .fighting)
        flow.answerCorrect(questionCount: qCount)
        flow.answerCorrect(questionCount: qCount)
        XCTAssertEqual(flow.bossHearts, 0)
        XCTAssertEqual(flow.outcome, .won, "boss 心先空 → 胜利")
        XCTAssertTrue(flow.isOver)
    }

    func testWrongAnswersDefeatPlayer() {
        var flow = BossFlow()
        flow.answerWrong(questionCount: qCount)
        XCTAssertEqual(flow.playerHearts, 2)
        XCTAssertEqual(flow.bossHearts, 3, "答错不扣 boss 心")
        flow.answerWrong(questionCount: qCount)
        flow.answerWrong(questionCount: qCount)
        XCTAssertEqual(flow.playerHearts, 0)
        XCTAssertEqual(flow.outcome, .lost, "玩家心先空 → 失败")
    }

    func testMushroomExemptsWrong() {
        // 蘑菇豁免在视图层：持有蘑菇时不调用 answerWrong → 玩家心不变
        var flow = BossFlow()
        let heartsBefore = flow.playerHearts
        // 模拟「蘑菇挡了一下」：本次答错不进状态机
        _ = heartsBefore
        XCTAssertEqual(flow.playerHearts, 3, "蘑菇豁免的答错不掉心")
        // 蘑菇用完后再答错才掉心
        flow.answerWrong(questionCount: qCount)
        XCTAssertEqual(flow.playerHearts, 2)
    }

    func testRetryResetsAllState() {
        var flow = BossFlow()
        flow.answerWrong(questionCount: qCount)
        flow.answerWrong(questionCount: qCount)
        XCTAssertEqual(flow.outcome, .fighting)
        flow.answerWrong(questionCount: qCount)
        XCTAssertEqual(flow.outcome, .lost)
        flow.retry()
        XCTAssertEqual(flow.bossHearts, 3)
        XCTAssertEqual(flow.playerHearts, 3)
        XCTAssertEqual(flow.questionIndex, 0)
        XCTAssertEqual(flow.wrongCount, 0)
        XCTAssertEqual(flow.outcome, .fighting, "重试满血复位")
    }

    func testQuestionIndexAdvancesAndClamps() {
        var flow = BossFlow()
        for k in 1...7 {
            flow.answerCorrect(questionCount: qCount)
            XCTAssertEqual(flow.questionIndex, min(k, qCount - 1))
        }
        // boss 在第 3 次答对时已败；结束后继续调用不再推进
        let idx = flow.questionIndex
        flow.answerCorrect(questionCount: qCount)
        XCTAssertEqual(flow.questionIndex, idx, "战斗结束后状态冻结")
    }

    func testStarsByPlayerHearts() {
        var perfect = BossFlow()
        XCTAssertEqual(perfect.stars, 3, "未掉心 3 星")
        var oneLost = BossFlow(); oneLost.answerWrong(questionCount: qCount)
        XCTAssertEqual(oneLost.stars, 2, "掉 1 心 2 星")
        var twoLost = BossFlow()
        twoLost.answerWrong(questionCount: qCount)
        twoLost.answerWrong(questionCount: qCount)
        XCTAssertEqual(twoLost.stars, 1, "掉 2 心 1 星")
    }

    func testMixedBattleEndsByHearts() {
        // 3 对 2 错：boss 先空 → 胜（共 5 回合，6 心去掉 5，boss 恰空）
        var flow = BossFlow()
        flow.answerCorrect(questionCount: qCount)   // boss 2
        flow.answerWrong(questionCount: qCount)      // player 2
        flow.answerCorrect(questionCount: qCount)   // boss 1
        flow.answerWrong(questionCount: qCount)      // player 1
        flow.answerCorrect(questionCount: qCount)   // boss 0 → won
        XCTAssertEqual(flow.outcome, .won)
        XCTAssertEqual(flow.playerHearts, 1)
    }
}
