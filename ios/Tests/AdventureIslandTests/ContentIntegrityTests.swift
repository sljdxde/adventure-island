import XCTest
@testable import AdventureIsland

/// 内容数据完整性：JSON 结构、题目正确性、资产名一致性
final class ContentIntegrityTests: XCTestCase {

    private var iconNames: Set<String> = []

    override func setUpWithError() throws {
        let url = Bundle(for: ContentIntegrityTests.self).url(forResource: "icon_names", withExtension: "json")
        XCTAssertNotNil(url, "测试夹具 icon_names.json 缺失")
        let data = try Data(contentsOf: url!)
        let decoded = try JSONDecoder().decode(Fixture.self, from: data)
        iconNames = Set(decoded.icons)
    }

    struct Fixture: Codable { let icons: [String] }

    func testSubjectFilesDecodeAndValid() throws {
        for (name, subject, expected) in [("cn_levels", "cn", 15), ("math_levels", "math", 15),
                                          ("pinyin_levels", "pinyin", 12), ("english_levels", "english", 12),
                                          ("astro_levels", "astro", 10)] {
            let file = ContentLoader.load(SubjectFile.self, name)
            XCTAssertEqual(file.subject, subject)
            XCTAssertEqual(file.levels.count, expected, "\(name) 应有 \(expected) 关")
            XCTAssertEqual(Set(file.levels.map(\.id)).count, expected, "\(name) 关卡 id 必须唯一")

            for (li, level) in file.levels.enumerated() {
                XCTAssertFalse(level.steps.isEmpty, "\(name) 第\(li)关没有步骤")

                // v0.8 迷你棋盘（工单02）：8-10 格、题目格占比 ≥ 60%、题目引用存在且不重复（规格实现决策 2）
                if let board = level.board {
                    let spaces = board.spaces
                    XCTAssertTrue((8...10).contains(spaces.count),
                                  "\(name)/\(level.id) 棋盘应 8-10 格，实际 \(spaces.count)")
                    let questionCount = spaces.filter { $0.type == "question" }.count
                    let ratio = Double(questionCount) / Double(spaces.count)
                    XCTAssertGreaterThanOrEqual(ratio, 0.6,
                                  "\(name)/\(level.id) 题目格占比 \(ratio) 低于 60% 红线")
                    let stepIds = Set(level.steps.map(\.id))
                    var referenced = Set<String>()
                    for sp in spaces {
                        XCTAssertTrue(["question", "coin"].contains(sp.type),
                                      "\(name)/\(level.id) 未知格子类型 \(sp.type)")
                        if sp.type == "question" {
                            let sid = try XCTUnwrap(sp.step, "\(name)/\(level.id) 题目格缺 step 引用")
                            XCTAssertTrue(stepIds.contains(sid), "\(name)/\(level.id) 引用了不存在的 step \(sid)")
                            XCTAssertFalse(referenced.contains(sid), "\(name)/\(level.id) 重复引用 step \(sid)")
                            referenced.insert(sid)
                        } else {
                            XCTAssertNil(sp.step, "\(name)/\(level.id) 非题目格不应带 step")
                        }
                    }
                }

                for step in level.steps {
                    switch step.kind {
                    case "teach":
                        XCTAssertNotNil(step.char)
                        XCTAssertNotNil(step.pinyin)
                        XCTAssertNotNil(step.morphFrom)
                    case "letter":
                        XCTAssertFalse((step.letters ?? []).isEmpty, "\(step.id) letter 缺 letters")
                        XCTAssertNotNil(step.display)
                        XCTAssertFalse((step.examples ?? []).isEmpty, "\(step.id) letter 缺例词")
                    case "listen":
                        // 视觉化找一找：目标大卡为 prompt 文字或 promptIcon 图片（无声音也能作答）
                        XCTAssertTrue(step.prompt != nil || step.promptIcon != nil,
                                      "\(step.id) listen 缺视觉目标 prompt/promptIcon")
                        XCTAssertNotNil(step.speakText, "\(step.id) listen 缺 speakText")
                        if let pi = step.promptIcon { XCTAssertTrue(iconNames.contains(pi), "\(step.id) promptIcon 不在资产清单") }
                        XCTAssertEqual(step.options?.count, 3, "\(step.id) listen 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                    case "pattern":
                        XCTAssertGreaterThanOrEqual(step.seq?.count ?? 0, 3, "\(step.id) pattern 序列过短")
                        XCTAssertEqual(step.options?.count, 3, "\(step.id) pattern 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                        for opt in step.options ?? [] {
                            let icon = try XCTUnwrap(opt.icon, "\(step.id) pattern 选项缺 icon")
                            XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单")
                        }
                    case "split":
                        let t = try XCTUnwrap(step.total, "\(step.id) split 缺 total")
                        let p = try XCTUnwrap(step.part, "\(step.id) split 缺 part")
                        XCTAssertTrue(p >= 1 && p < t && t <= 10, "\(step.id) split total/part 非法")
                        let rest = t - p
                        XCTAssertTrue((step.arithOptions ?? []).contains(rest), "\(step.id) split 选项应含 \(rest)")
                    case "order":
                        let nums = try XCTUnwrap(step.nums, "\(step.id) order 缺 nums")
                        XCTAssertEqual(nums.count, 3, "\(step.id) order 应 3 个数字")
                        XCTAssertEqual(Set(nums).count, 3, "\(step.id) order 数字应互不相同")
                        XCTAssertTrue(["up", "down"].contains(step.dir ?? ""), "\(step.id) order dir 非法")
                    case "neighbor":
                        let nums = try XCTUnwrap(step.nums, "\(step.id) neighbor 缺 nums")
                        XCTAssertEqual(nums, [nums[0], 0, nums[0] + 2], "\(step.id) neighbor 应为 [a,0,a+2]")
                        let correct = nums[0] + 1
                        let opts = try XCTUnwrap(step.arithOptions, "\(step.id) neighbor 缺选项")
                        XCTAssertTrue(opts.contains(correct), "\(step.id) neighbor 选项应含 \(correct)")
                        let nans = try XCTUnwrap(step.answer, "\(step.id) neighbor 缺 answer")
                        XCTAssertEqual(opts[nans], correct, "\(step.id) neighbor answer 指向错误")
                    case "memory":
                        let cards = try XCTUnwrap(step.cards, "\(step.id) memory 缺 cards")
                        XCTAssertEqual(cards.count, 6, "\(step.id) memory 应为 6 张牌")
                        let keys = cards.map(\.key)
                        XCTAssertEqual(Set(keys).count, 3, "\(step.id) memory 应为 3 对")
                        XCTAssertTrue(keys.allSatisfy { key in keys.filter { $0 == key }.count == 2 },
                                      "\(step.id) memory 牌必须两两同 key")
                        for card in cards {
                            XCTAssertTrue(card.icon != nil || card.text != nil, "\(step.id) memory 牌缺内容")
                            if let icon = card.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                    case "dice":
                        let n = try XCTUnwrap(step.count, "\(step.id) dice 缺 count")
                        XCTAssertTrue((1...6).contains(n), "\(step.id) dice 点数超范围")
                        let opts = try XCTUnwrap(step.countOptions, "\(step.id) dice 缺选项")
                        XCTAssertTrue(opts.contains(n), "\(step.id) dice 选项应含 \(n)")
                    case "blend":
                        XCTAssertEqual(step.parts?.count, 2, "\(step.id) blend 应为 声母+韵母")
                        XCTAssertEqual(step.options?.count, 3, "\(step.id) blend 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        let expected = (step.parts?[0] ?? "") + (step.parts?[1] ?? "")
                        XCTAssertEqual(step.options?[safe: ans]?.text, expected,
                                       "\(step.id) 拼读答案应为 \(expected)")
                    case "arith":
                        XCTAssertTrue(step.op == "+" || step.op == "-", "\(step.id) op 非法")
                        let l = try XCTUnwrap(step.leftCount), r = try XCTUnwrap(step.rightCount)
                        let correct = step.op == "+" ? l + r : l - r
                        XCTAssertTrue((step.arithOptions ?? []).contains(correct),
                                      "\(step.id) 选项应含正确答案 \(correct)")
                        XCTAssertTrue(correct >= 0 && correct <= 10, "\(step.id) 结果应在 0-10")
                    case "quiz":
                        XCTAssertEqual(step.options?.count, 3, "\(name)/\(step.id) 选项应为 3 个")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                        for opt in step.options ?? [] {
                            XCTAssertTrue(opt.icon != nil || opt.text != nil, "\(step.id) 选项缺少内容")
                            if let icon = opt.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                    case "count":
                        let n = try XCTUnwrap(step.count, "\(step.id) 缺 count")
                        XCTAssertGreaterThanOrEqual(n, 3)
                        XCTAssertLessThanOrEqual(n, 10)
                        let opts = try XCTUnwrap(step.countOptions, "\(step.id) 缺 countOptions")
                        XCTAssertTrue(opts.contains(n), "\(step.id) 选项必须包含正确数量")
                        XCTAssertNotNil(step.duckIcon)
                        XCTAssertTrue(["pond", "sky", "night", "grass"].contains(step.backdrop ?? ""),
                                      "\(step.id) 点数场景非法")
                        XCTAssertNotNil(step.unit, "\(step.id) 缺量词")
                    case "compare":
                        let keys = Set((step.compareOptions ?? []).map(\.key))
                        XCTAssertEqual(keys, ["left", "right", "same"], "\(step.id) 比较选项不完整")
                        let left = try XCTUnwrap(step.leftCount)
                        let right = try XCTUnwrap(step.rightCount)
                        let expected = left == right ? "same" : (left > right ? "left" : "right")
                        XCTAssertEqual(step.answerKey, expected, "\(step.id) 答案与数量不符")
                        XCTAssertTrue(iconNames.contains(step.leftIcon ?? ""), "\(step.id) 左盘图标缺失")
                        XCTAssertTrue(iconNames.contains(step.rightIcon ?? ""), "\(step.id) 右盘图标缺失")
                    default:
                        XCTFail("\(step.id) 未知步骤类型 \(step.kind)")
                    }
                    // 词卡图标校验
                    for w in step.words ?? [] {
                        if let icon = w.icon { XCTAssertTrue(iconNames.contains(icon), "词卡图标 \(icon) 不在资产清单") }
                    }
                }
            }
        }
    }

    /// 关卡 id 全局唯一是 v0.8 进度迁移（工单05：id 平移插入新关）的前提
    func testLevelIdsGloballyUnique() throws {
        var seen = Set<String>()
        for name in ["cn_levels", "math_levels", "pinyin_levels", "english_levels", "astro_levels"] {
            let file = ContentLoader.load(SubjectFile.self, name)
            for level in file.levels {
                XCTAssertFalse(seen.contains(level.id), "关卡 id \(level.id) 跨文件重复（\(name)）")
                seen.insert(level.id)
            }
        }
    }

    func testExperimentsDecodeAndValid() throws {
        let file = ContentLoader.load(ExperimentFile.self, "experiments")
        XCTAssertGreaterThanOrEqual(file.experiments.count, 1)
        for exp in file.experiments {
            XCTAssertGreaterThanOrEqual(exp.items.count, 3)
            XCTAssertTrue(exp.items.contains { $0.id == exp.guessItem })
            for item in exp.items {
                XCTAssertFalse(item.fact.isEmpty, "\(item.id) 缺小知识")
                XCTAssertTrue(iconNames.contains(item.icon), "实验图标 \(item.icon) 不在资产清单")
            }
        }
    }

    func testCollectionDecodeAndValid() throws {
        let file = ContentLoader.load(CollectionFile.self, "collection")
        let ids = file.groups.map(\.id)
        XCTAssertEqual(ids, ["science", "sticker", "hanzi", "pinyin", "english", "astro", "badge"])
        for group in file.groups {
            XCTAssertGreaterThanOrEqual(group.items.count, 10, "\(group.id) 条目过少")
            for item in group.items {
                if let icon = item.icon { XCTAssertTrue(iconNames.contains(icon), "收集册图标 \(icon) 不在资产清单") }
            }
        }
    }

    func testEmojiFallbackCoversAllIcons() throws {
        // 每个资产都应有 Emoji 兜底，保证资产缺失时 UI 仍可理解
        for icon in iconNames {
            XCTAssertNotNil(IconEmoji.map[icon], "图标 \(icon) 缺少 Emoji 兜底")
        }
    }
}
