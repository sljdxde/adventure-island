import XCTest
@testable import AdventureIsland

/// 内容数据完整性：JSON 结构、题目正确性、资产名一致性（v0.9：六学科 + 7 种新题型）
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
        // v0.11：五科各 50 关（5 星区）、天文 100 关（10 星区），末关均为 boss
        for (name, subject, expected) in [("cn_levels", "cn", 50), ("math_levels", "math", 50),
                                          ("pinyin_levels", "pinyin", 50), ("english_levels", "english", 50),
                                          ("astro_levels", "astro", 100), ("geo_levels", "geo", 50)] {
            let file = ContentLoader.load(SubjectFile.self, name)
            XCTAssertEqual(file.subject, subject)
            XCTAssertEqual(file.levels.count, expected, "\(name) 应有 \(expected) 关")
            XCTAssertEqual(Set(file.levels.map(\.id)).count, expected, "\(name) 关卡 id 必须唯一")
            XCTAssertEqual(file.levels.last?.boss, true, "\(name) 末关应为 boss")

            for (li, level) in file.levels.enumerated() {
                XCTAssertFalse(level.steps.isEmpty, "\(name) 第\(li)关没有步骤")

                // v0.8 迷你棋盘（工单02/03/05）：题目格占比 ≥ 60%、题目引用存在且不重复；
                // 普通关 8-10 格、事件格 1-2；复习关 10-12 格、事件格加倍 ≥2 且标记 review
                if let board = level.board {
                    let spaces = board.spaces
                    let isReview = level.review == true
                    let isBoss = level.boss == true
                    if isBoss {
                        // boss 战斗棋盘：8 格全题目，无宝箱/蘑菇/休息事件格
                        XCTAssertEqual(spaces.count, 8, "\(name)/\(level.id) boss 棋盘应为 8 格")
                        XCTAssertTrue(spaces.allSatisfy { $0.type == "question" },
                                      "\(name)/\(level.id) boss 棋盘必须全部为题目格")
                    } else {
                        XCTAssertTrue(isReview ? (10...12).contains(spaces.count) : (8...10).contains(spaces.count),
                                      "\(name)/\(level.id) 棋盘格数 \(spaces.count) 与\(isReview ? "复习关" : "普通关")规格不符")
                    }
                    let questionCount = spaces.filter { $0.type == "question" }.count
                    let ratio = Double(questionCount) / Double(spaces.count)
                    XCTAssertGreaterThanOrEqual(ratio, 0.6,
                                  "\(name)/\(level.id) 题目格占比 \(ratio) 低于 60% 红线")
                    let eventCount = spaces.filter { ["chest", "mushroom", "rest"].contains($0.type) }.count
                    if !isBoss {
                        XCTAssertTrue(isReview ? (2...4).contains(eventCount) : (1...2).contains(eventCount),
                                      "\(name)/\(level.id) 事件格 \(eventCount) 个与\(isReview ? "复习关(加倍)" : "普通关")规格不符")
                    }
                    let stepIds = Set(level.steps.map(\.id))
                    var referenced = Set<String>()
                    for sp in spaces {
                        XCTAssertTrue(["question", "coin", "chest", "mushroom", "rest"].contains(sp.type),
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
                        if let anim = step.anim {
                            XCTAssertTrue(AstroAnimView.animIds.contains(anim), "\(step.id) anim 非法 \(anim)")
                        }
                    case "listen":
                        // 视觉化找一找：目标大卡为 prompt 文字或 promptIcon 图片（无声音也能作答）
                        XCTAssertTrue(step.prompt != nil || step.promptIcon != nil,
                                      "\(step.id) listen 缺视觉目标 prompt/promptIcon")
                        XCTAssertNotNil(step.speakText, "\(step.id) listen 缺 speakText")
                        if let pi = step.promptIcon { XCTAssertTrue(iconNames.contains(pi), "\(step.id) promptIcon 不在资产清单") }
                        XCTAssertEqual(step.options?.quizList.count, 3, "\(step.id) listen 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                    case "pattern":
                        XCTAssertGreaterThanOrEqual(step.seq?.count ?? 0, 3, "\(step.id) pattern 序列过短")
                        XCTAssertEqual(step.options?.quizList.count, 3, "\(step.id) pattern 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                        for opt in step.options?.quizList ?? [] {
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
                        guard case .memory(let cards)? = step.cards else {
                            XCTFail("\(step.id) memory 缺 cards"); continue
                        }
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
                        XCTAssertEqual(step.options?.quizList.count, 3, "\(step.id) blend 选项应为 3")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        let expected = (step.parts?[0] ?? "") + (step.parts?[1] ?? "")
                        XCTAssertEqual(step.options?.quizList[safe: ans]?.text, expected,
                                       "\(step.id) 拼读答案应为 \(expected)")
                    case "arith":
                        XCTAssertTrue(step.op == "+" || step.op == "-", "\(step.id) op 非法")
                        let l = try XCTUnwrap(step.leftCount), r = try XCTUnwrap(step.rightCount)
                        let correct = step.op == "+" ? l + r : l - r
                        XCTAssertTrue((step.arithOptions ?? []).contains(correct),
                                      "\(step.id) 选项应含正确答案 \(correct)")
                        XCTAssertTrue(correct >= 0 && correct <= 200, "\(step.id) 结果超范围 \(correct)")
                    case "quiz":
                        XCTAssertEqual(step.options?.quizList.count, 3, "\(name)/\(step.id) 选项应为 3 个")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) answer 越界")
                        for opt in step.options?.quizList ?? [] {
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
                    // MARK: v0.9 新题型（规则与 tools/validate.py 同源）
                    case "write":
                        XCTAssertNotNil(step.char, "\(step.id) write 缺 char")
                        XCTAssertNotNil(step.pinyin, "\(step.id) write 缺 pinyin")
                        let strokes = try XCTUnwrap(step.strokes, "\(step.id) write 缺笔画序列")
                        XCTAssertFalse(strokes.isEmpty, "\(step.id) write 笔画为空")
                        for sk in strokes {
                            XCTAssertFalse(sk.d.isEmpty, "\(step.id) write 笔画缺 d")
                        }
                    case "muldiv":
                        let opts = step.options?.intList ?? []
                        let ans = try XCTUnwrap(step.answer, "\(step.id) muldiv 缺 answer")
                        let op = try XCTUnwrap(step.op, "\(step.id) muldiv 缺 op")
                        var correct: Int?
                        if op == "×" {
                            correct = try XCTUnwrap(step.groups) * XCTUnwrap(step.per, "\(step.id) muldiv× 缺 per")
                        } else {
                            let mode = try XCTUnwrap(step.mode, "\(step.id) muldiv÷ 缺 mode")
                            let t = try XCTUnwrap(step.total, "\(step.id) muldiv÷ 缺 total")
                            if mode == "average" {
                                let g = try XCTUnwrap(step.groups, "\(step.id) 平均分缺 groups")
                                XCTAssertEqual(t % g, 0, "\(step.id) 平均分不整除")
                                correct = t / g
                            } else {
                                let p = try XCTUnwrap(step.per, "\(step.id) 包含除缺 per")
                                XCTAssertEqual(t % p, 0, "\(step.id) 包含除不整除")
                                correct = t / p
                            }
                        }
                        XCTAssertTrue(opts.contains(try XCTUnwrap(correct)), "\(step.id) muldiv 选项不含 \(String(describing: correct))")
                        XCTAssertEqual(opts[ans], correct, "\(step.id) muldiv answer 指向错误")
                    case "cards":
                        guard case .values(let cardVals)? = step.cards else {
                            XCTFail("\(step.id) cards 缺 cards"); continue
                        }
                        let target = try XCTUnwrap(step.target, "\(step.id) cards 缺 target")
                        let pick = try XCTUnwrap(step.pick, "\(step.id) cards 缺 pick")
                        XCTAssertTrue(cardVals.allSatisfy { (1...10).contains($0) }, "\(step.id) cards 牌面超 1-10")
                        if step.mode == "make10" {
                            XCTAssertEqual(pick, 2, "\(step.id) make10 pick 应为 2")
                            let sums = cardVals.combinationsPairs().map { $0.0 + $0.1 }
                            XCTAssertTrue(sums.contains(target), "\(step.id) make10 无解凑 \(target)")
                        } else {
                            XCTAssertEqual(pick, 3, "\(step.id) target pick 应为 3")
                            XCTAssertTrue(try cardVals.hasTriple(target: target), "\(step.id) cards 无解凑 \(target)")
                        }
                    case "sudoku":
                        XCTAssertEqual(step.size, 4, "\(step.id) sudoku size 应为 4")
                        let sol = try XCTUnwrap(step.solution, "\(step.id) sudoku 缺 solution")
                        let givens = try XCTUnwrap(step.givens, "\(step.id) sudoku 缺 givens")
                        XCTAssertEqual(step.symbols?.count, 4, "\(step.id) sudoku symbols 应 4 个")
                        XCTAssertEqual(sol.count, 4, "\(step.id) solution 应 4 行")
                        XCTAssertTrue(sol.allSatisfy { $0.count == 4 }, "\(step.id) solution 应 4 列")
                        for r in 0..<4 { XCTAssertEqual(Set(sol[r]).count, 4, "\(step.id) sudoku 第\(r)行重复") }
                        for c in 0..<4 { XCTAssertEqual(Set(sol.map { $0[c] }).count, 4, "\(step.id) sudoku 第\(c)列重复") }
                        for g in givens { XCTAssertEqual(sol[g.r][g.c], g.v, "\(step.id) given 与 solution 不一致") }
                    case "clock":
                        let h = try XCTUnwrap(step.hour, "\(step.id) clock 缺 hour")
                        let m = try XCTUnwrap(step.minute, "\(step.id) clock 缺 minute")
                        XCTAssertTrue((1...12).contains(h), "\(step.id) clock hour 越界")
                        XCTAssertTrue(m == 0 || m == 30, "\(step.id) clock minute 应为整/半点")
                        if step.mode == "read" {
                            let opts = step.options?.stringList ?? []
                            let ans = try XCTUnwrap(step.answer, "\(step.id) clock read 缺 answer")
                            XCTAssertEqual(opts.count, 3, "\(step.id) clock read 选项应 3 个")
                            XCTAssertEqual(opts[ans], String(format: "%d:%02d", h, m), "\(step.id) clock read 答案与钟面不符")
                        } else {
                            XCTAssertEqual(step.mode, "set", "\(step.id) clock mode 非法")
                        }
                    case "money":
                        let price = try XCTUnwrap(step.price, "\(step.id) money 缺 price")
                        let denoms = try XCTUnwrap(step.denominations, "\(step.id) money 缺 denominations")
                        let vals = denoms.map(\.value)
                        XCTAssertTrue(vals.allSatisfy { [1, 5, 10, 50, 100].contains($0) }, "\(step.id) money 面额非法 \(vals)")
                        XCTAssertGreaterThan(price, 0, "\(step.id) money price 非法")
                        var dp = [Bool](repeating: false, count: price + 1)
                        dp[0] = true
                        for v in vals where v <= price {
                            for x in v...price where dp[x - v] { dp[x] = true }
                        }
                        XCTAssertTrue(dp[price], "\(step.id) money 无法恰好付清 \(price)")
                    case "mappuzzle":
                        let regions = try XCTUnwrap(step.regions, "\(step.id) mappuzzle 缺 regions")
                        XCTAssertFalse(regions.isEmpty, "\(step.id) mappuzzle regions 为空")
                        XCTAssertEqual(Set(regions.map(\.id)).count, regions.count, "\(step.id) mappuzzle 块 id 重复")
                        for r in regions {
                            XCTAssertGreaterThanOrEqual(r.points.count, 3, "\(step.id) 块 \(r.id) 多边形点数<3")
                        }
                    // MARK: v0.10 天文台新题型（规则与 tools/validate.py 同源）
                    case "balance":
                        for (key, side) in [("left", step.left), ("right", step.right)] {
                            XCTAssertNotNil(side, "\(step.id) balance 缺 \(key) 侧")
                            XCTAssertTrue(side?.icon != nil || side?.text != nil, "\(step.id) balance \(key) 侧缺 icon/text")
                            if let icon = side?.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                        XCTAssertTrue(["left", "right"].contains(step.answerKey ?? ""), "\(step.id) balance answerKey 非法")
                    case "sort":
                        let bins = try XCTUnwrap(step.bins, "\(step.id) sort 缺 bins")
                        let items = try XCTUnwrap(step.items, "\(step.id) sort 缺 items")
                        XCTAssertEqual(bins.count, 2, "\(step.id) sort 应为 2 个筐")
                        XCTAssertEqual(Set(bins.map(\.id)).count, bins.count, "\(step.id) sort 筐 id 重复")
                        XCTAssertTrue(items.count >= 3 && items.count <= 6, "\(step.id) sort 物品数不在 3-6")
                        XCTAssertEqual(Set(items.map(\.id)).count, items.count, "\(step.id) sort 物品 id 重复")
                        let binIds = Set(bins.map(\.id))
                        for it in items {
                            XCTAssertTrue(it.icon != nil || it.text != nil, "\(step.id) sort 物品 \(it.id) 缺内容")
                            XCTAssertTrue(binIds.contains(it.bin ?? ""), "\(step.id) sort 物品 \(it.id) 指向不存在的筐")
                            if let icon = it.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                        for b in bins {
                            XCTAssertTrue(items.contains { $0.bin == b.id }, "\(step.id) sort 筐 \(b.id) 没有物品")
                            if let icon = b.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                    // MARK: v0.10.1 天文台新题型（规则与 tools/validate.py 同源）
                    case "tapall":
                        let opts = step.options?.quizList ?? []
                        XCTAssertTrue((4...9).contains(opts.count), "\(step.id) tapall 选项数不在 4-9")
                        let correct = opts.filter { $0.correct == true }
                        XCTAssertGreaterThanOrEqual(correct.count, 2, "\(step.id) tapall 正确项应 ≥2")
                        for o in opts {
                            XCTAssertTrue(o.icon != nil || o.text != nil, "\(step.id) tapall 选项缺内容")
                            if let icon = o.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                    case "match":
                        let pairs = try XCTUnwrap(step.pairs, "\(step.id) match 缺 pairs")
                        XCTAssertEqual(pairs.count, 3, "\(step.id) match 应 3 组")
                        let rights = pairs.map { $0.right.text ?? "" }
                        XCTAssertEqual(Set(rights).count, 3, "\(step.id) match 右列文字重复")
                        for p in pairs {
                            XCTAssertFalse((p.left.text ?? "").isEmpty, "\(step.id) match left 缺文字")
                            XCTAssertNotNil(p.left.icon, "\(step.id) match left 缺图标")
                            if let icon = p.left.icon { XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单") }
                        }
                    case "lineup":
                        let items = try XCTUnwrap(step.lineup, "\(step.id) lineup 缺 lineup")
                        XCTAssertTrue((3...4).contains(items.count), "\(step.id) lineup 物品数不在 3-4")
                        XCTAssertEqual(Set(items.map(\.id)).count, items.count, "\(step.id) lineup id 重复")
                        for it in items {
                            let icon = try XCTUnwrap(it.icon, "\(step.id) lineup 物品 \(it.id) 缺 icon")
                            XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单")
                        }
                    case "sequence":
                        let seq = try XCTUnwrap(step.seq, "\(step.id) sequence 缺 seq")
                        XCTAssertTrue((3...5).contains(seq.count), "\(step.id) sequence 长度不在 3-5")
                        XCTAssertEqual(Set(seq).count, seq.count, "\(step.id) sequence token 重复")
                    case "spotlight":
                        let target = try XCTUnwrap(step.targetIcon, "\(step.id) spotlight 缺 targetIcon")
                        XCTAssertTrue(iconNames.contains(target), "\(step.id) 图标 \(target) 不在资产清单")
                        let decoys = try XCTUnwrap(step.decoys, "\(step.id) spotlight 缺 decoys")
                        XCTAssertTrue((3...8).contains(decoys.count), "\(step.id) spotlight 干扰星数不在 3-8")
                        for d in decoys { XCTAssertTrue(iconNames.contains(d), "\(step.id) 图标 \(d) 不在资产清单") }
                    case "shadow":
                        let sil = try XCTUnwrap(step.shadow, "\(step.id) shadow 缺 shadow")
                        XCTAssertTrue(iconNames.contains(sil), "\(step.id) 图标 \(sil) 不在资产清单")
                        let opts = step.options?.quizList ?? []
                        XCTAssertEqual(opts.count, 3, "\(step.id) shadow 选项应 3 个")
                        let ans = try XCTUnwrap(step.answer, "\(step.id) shadow 缺 answer")
                        XCTAssertTrue((0..<3).contains(ans), "\(step.id) shadow answer 越界")
                        for o in opts {
                            let icon = try XCTUnwrap(o.icon, "\(step.id) shadow 选项缺 icon")
                            XCTAssertTrue(iconNames.contains(icon), "\(step.id) 图标 \(icon) 不在资产清单")
                        }
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
        for name in ["cn_levels", "math_levels", "pinyin_levels", "english_levels", "astro_levels", "geo_levels"] {
            let file = ContentLoader.load(SubjectFile.self, name)
            for level in file.levels {
                XCTAssertFalse(seen.contains(level.id), "关卡 id \(level.id) 跨文件重复（\(name)）")
                seen.insert(level.id)
            }
        }
    }

    /// v0.10/v0.11 星区分章：全学科 level.zone 与 zones 对齐，每星区恰好 10 关（保卫萝卜式选关的数据前提）
    func testAstroZones() throws {
        let file = ContentLoader.load(SubjectFile.self, "astro_levels")
        let zones = try XCTUnwrap(file.zones, "astro_levels 缺 zones")
        XCTAssertEqual(zones.count, 10, "天文台应 10 个星区")
        XCTAssertEqual(zones.map(\.n), Array(1...10), "星区编号应 1...10")
        try assertZoneLayout(file)
    }

    /// v0.11 五科 50 关 = 5 星区 × 10 关，星区带学科专属图标
    func testAllSubjectsZoneLayout() throws {
        for name in ["cn_levels", "math_levels", "pinyin_levels", "english_levels", "geo_levels"] {
            let file = ContentLoader.load(SubjectFile.self, name)
            let zones = try XCTUnwrap(file.zones, "\(name) 缺 zones")
            XCTAssertEqual(zones.count, 5, "\(name) 应 5 个星区")
            XCTAssertTrue(zones.allSatisfy { $0.icon != nil }, "\(name) 星区应带代表图标")
            try assertZoneLayout(file)
        }
    }

    private func assertZoneLayout(_ file: SubjectFile) throws {
        let zoneCount = file.zones?.count ?? 0
        var perZone: [Int: Int] = [:]
        for level in file.levels {
            let z = try XCTUnwrap(level.zone, "\(level.id) 缺 zone")
            perZone[z, default: 0] += 1
        }
        XCTAssertEqual(perZone, Dictionary(uniqueKeysWithValues: (1...zoneCount).map { ($0, 10) }),
                       "\(file.subject) 每星区应恰好 10 关")
    }

    /// v0.10 星区节奏：复习关钉在第 3/6/8 星区末（全局第 30/60/80 关），Boss 收官第 100 关
    func testAstroReviewAndBossLayout() throws {
        let levels = ContentLoader.load(SubjectFile.self, "astro_levels").levels
        XCTAssertEqual(levels.count, 100)
        for idx in [29, 59, 79] {
            XCTAssertTrue(levels[idx].review == true, "第 \(idx + 1) 关应为复习关")
            XCTAssertEqual(levels[idx].zone, idx / 10 + 1, "复习关应落在所属星区末位")
            XCTAssertTrue(levels[idx].steps.count == 6, "复习关应混合 6 道旧题")
        }
        for (i, level) in levels.enumerated() where i != 29 && i != 59 && i != 79 {
            XCTAssertFalse(level.review == true, "第 \(i + 1) 关不应标记复习关")
        }
        XCTAssertTrue(levels[99].boss == true, "第 100 关应为 Boss")
    }

    /// v0.10 题型口径：天文台去掉扑克牌翻牌配对，新题型天平/拖一拖必须足量存在
    func testAstroStepMixNoMemory() throws {
        let steps = ContentLoader.load(SubjectFile.self, "astro_levels").levels.flatMap(\.steps)
        let counts = Dictionary(grouping: steps, by: \.kind).mapValues(\.count)
        XCTAssertFalse(counts.keys.contains("memory"), "天文台不应再使用 memory 翻牌配对")
        XCTAssertGreaterThanOrEqual(counts["balance"] ?? 0, 6, "天平比一比应 ≥6 道")
        XCTAssertGreaterThanOrEqual(counts["sort"] ?? 0, 7, "拖一拖分类应 ≥7 道")
        XCTAssertGreaterThanOrEqual(counts["letter"] ?? 0, 30, "学一学单词卡应保持足量")
        // v0.10.1 新题型各 ≥3 道，学一学动画 ≥30 关
        for kind in ["tapall", "match", "lineup", "sequence", "spotlight", "shadow"] {
            XCTAssertGreaterThanOrEqual(counts[kind] ?? 0, 3, "\(kind) 应 ≥3 道")
        }
        let animCount = ContentLoader.load(SubjectFile.self, "astro_levels").levels.flatMap(\.steps).filter { $0.anim != nil }.count
        XCTAssertGreaterThanOrEqual(animCount, 30, "学一学动画应覆盖 ≥30 关")
        for step in steps where step.kind == "balance" {
            XCTAssertNotNil(step.question, "\(step.id) balance 缺题干")
            XCTAssertNotNil(step.hint, "\(step.id) balance 缺提示（答错引导）")
        }
    }

    /// 星区代表图标是视图层硬编码，钉住资产存在性防漂移
    func testAstroZoneIconsInAssets() throws {
        XCTAssertEqual(AstroZoneIcons.all.count, 10, "10 星区应有 10 个代表图标")
        for icon in AstroZoneIcons.all {
            XCTAssertTrue(iconNames.contains(icon), "星区图标 \(icon) 不在资产清单")
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
        XCTAssertEqual(ids, ["science", "sticker", "hanzi", "pinyin", "english", "astro", "geo", "badge"])
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

private extension Array where Element == Int {
    func combinationsPairs() -> [(Int, Int)] {
        var out: [(Int, Int)] = []
        for i in indices { for j in (i + 1)..<count { out.append((self[i], self[j])) } }
        return out
    }
    /// 三张牌用 +/− 凑出目标（与 validate.py cards target 规则同源）
    func hasTriple(target: Int) throws -> Bool {
        for i in indices { for j in (i + 1)..<count { for k in (j + 1)..<count {
            let (a, b, c) = (self[i], self[j], self[k])
            if [a + b + c, a + b - c, a - b + c, -a + b + c, a - b - c].contains(target) { return true }
        } } }
        return false
    }
}
