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
        for (name, subject) in [("cn_levels", "cn"), ("math_levels", "math")] {
            let file = ContentLoader.load(SubjectFile.self, name)
            XCTAssertEqual(file.subject, subject)
            XCTAssertEqual(file.levels.count, 10, "\(name) 应有 10 关")
            XCTAssertEqual(Set(file.levels.map(\.id)).count, 10, "\(name) 关卡 id 必须唯一")

            for (li, level) in file.levels.enumerated() {
                XCTAssertFalse(level.steps.isEmpty, "\(name) 第\(li)关没有步骤")
                for step in level.steps {
                    switch step.kind {
                    case "teach":
                        XCTAssertNotNil(step.char)
                        XCTAssertNotNil(step.pinyin)
                        XCTAssertNotNil(step.morphFrom)
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
        XCTAssertEqual(ids, ["science", "sticker", "hanzi", "badge"])
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
