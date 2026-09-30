import Foundation

// MARK: - 关卡数据模型（JSON 驱动，加内容不改代码）

struct WordChip: Codable, Equatable {
    var icon: String?
    var text: String
    var say: String?
}

struct QuizOption: Codable, Equatable {
    var icon: String?   // 资源图标名
    var emoji: String?  // 无资源时的兜底
    var text: String?   // 文字选项（找字/数字题）
}

struct CompareOption: Codable, Equatable {
    var key: String     // "left" / "right" / "same"
    var label: String
}

struct MemoryCard: Codable, Equatable {
    var key: String     // 配对键：相同 key 的两张牌是一对
    var icon: String?
    var text: String?
}

struct Step: Codable, Equatable, Identifiable {
    var id: String
    /// teach | quiz | count | compare | letter | listen | blend | arith | pattern | split | order | neighbor
    var kind: String

    // teach（认一认：象形演变）
    var morphFrom: String?
    var char: String?
    var pinyin: String?
    var words: [WordChip]?

    // letter（认字母：拼音声母/韵母、英语字母）
    var letters: [String]?
    var display: String?
    var examples: [WordChip]?

    // listen（找一找：目标大卡，prompt 文字或 promptIcon 图片；朗读可选）
    var speakText: String?
    var prompt: String?
    var promptIcon: String?

    // pattern（找规律：序列 + 选项）
    var seq: [String]?

    // split（分一分：数的组成）total = part + 剩余
    var total: Int?
    var part: Int?

    // order（排一排）/ neighbor（填一填：nums[1]==0 为空位）
    var nums: [Int]?
    var dir: String?   // up | down

    // memory（翻牌配对：扑克牌翻牌，cards 两两同 key 配对）
    var cards: [MemoryCard]?

    // blend（拼一拼：声母+韵母）
    var parts: [String]?

    // arith（加减法：op + 数量即等式）
    var op: String?
    var arithOptions: [Int]?

    // quiz
    var question: String?
    var options: [QuizOption]?
    var answer: Int?
    var hint: String?
    var praise: String?

    // count（点数：duckIcon 为本关情境道具，backdrop 池塘/夜空/白天场景）
    var duckIcon: String?
    var count: Int?
    var countOptions: [Int]?
    var backdrop: String?   // pond | sky | night | grass
    var unit: String?       // 只 / 颗 / 朵 / 个 / 辆 / 枚

    // compare（比多少）
    var leftIcon: String?
    var rightIcon: String?
    var leftCount: Int?
    var rightCount: Int?
    var compareOptions: [CompareOption]?
    var answerKey: String?
}

struct Level: Codable, Equatable, Identifiable {
    var id: String
    var title: String
    var subtitle: String?
    var steps: [Step]
    var board: Board?          // v0.8 迷你棋盘；nil = 线性步骤关
}

// MARK: - 迷你棋盘（v0.8 工单02：识字村试点）

/// 棋盘格子：question 引用本关 step id；coin 为金币格（宝箱/蘑菇/休息站由工单03扩充）
struct BoardSpace: Codable, Equatable {
    var type: String           // question | coin
    var step: String?
}

struct Board: Codable, Equatable {
    var spaces: [BoardSpace]
}

/// 星级映射（规格 v0.8）：错 0 题 3 星、错 1 题 2 星、错 ≥2 题 1 星。线性关与棋盘关共用
enum StarRule {
    static func stars(wrongCount: Int) -> Int {
        switch wrongCount {
        case 0: return 3
        case 1: return 2
        default: return 1
        }
    }
}

/// 棋盘推进状态（纯逻辑，测试缝在领域层）：掷骰逐格前进，超出停在城堡；
/// 语义与浏览器模拟器 hopBoard/arriveBoard 同源
struct BoardFlow: Equatable {
    /// -1 起点；0..<spaceCount 落在格上；spaceCount 到达城堡
    private(set) var position: Int = -1
    private(set) var wrongCount: Int = 0
    private(set) var finished: Bool = false

    var stars: Int { StarRule.stars(wrongCount: wrongCount) }

    /// 答错一题：不后退不惩罚（防挫败铁律），只计入星级
    mutating func registerWrong() { wrongCount += 1 }

    /// 掷得 roll 点前进，超出部分停在城堡（min 钳制）；返回落点。已结算/非正点数/空棋盘为非法输入，忽略
    @discardableResult
    mutating func advance(roll: Int, spaceCount: Int) -> Int {
        guard !finished, roll > 0, spaceCount > 0 else { return position }
        position = min(position + roll, spaceCount)
        if position == spaceCount { finished = true }
        return position
    }

    /// 前进一格（蹦跳动画逐格驱动）；到达城堡置 finished
    mutating func advanceOne(spaceCount: Int) {
        guard !finished, spaceCount > 0 else { return }
        position = min(position + 1, spaceCount)
        if position == spaceCount { finished = true }
    }

    /// 落点对应格子（城堡返回 nil）
    func space(at spaceCount: Int) -> Int? {
        position >= 0 && position < spaceCount ? position : nil
    }
}

// MARK: - 关卡流程状态机（步骤推进 / 最后一步结算置位 / 星级映射）

/// 一关的推进状态（纯逻辑，测试缝在领域层；LevelView 只做渲染委托）。
/// 语义与浏览器模拟器 nextStep 同源：非最后一步 → 前进；最后一步答完 → finished 置真进入结算卡。
struct LevelFlow: Equatable {
    private(set) var stepIndex = 0
    private(set) var wrongCount = 0
    private(set) var finished = false

    /// 答错一题：不后退不惩罚（防挫败铁律），只计入星级
    mutating func registerWrong() { wrongCount += 1 }

    /// 答完当前步骤推进：还有下一步则前进，已是最后一步则置 finished 进入通关结算；
    /// 已结算或空关卡（stepCount ≤ 0）为非法输入，忽略不改变状态
    mutating func advance(stepCount: Int) {
        guard !finished, stepCount > 0 else { return }
        if stepIndex < stepCount - 1 {
            stepIndex += 1
        } else {
            finished = true
        }
    }

    /// 星级映射（规格 v0.8）：错 0 题 3 星、错 1 题 2 星、错 ≥2 题 1 星
    var stars: Int {
        StarRule.stars(wrongCount: wrongCount)
    }
}

struct SubjectFile: Codable {
    var subject: String   // cn | math
    var title: String
    var guide: String
    var levels: [Level]
}

// MARK: - 实验模型

struct ExperimentItem: Codable, Equatable, Identifiable {
    var id: String
    var name: String
    var icon: String
    var isFloat: Bool
    var fact: String
}

struct Experiment: Codable, Equatable, Identifiable {
    var id: String
    var title: String
    var guide: String
    var guessItem: String     // 猜一猜的物品 id
    var guessIcon: String
    var guessQuestion: String
    var items: [ExperimentItem]
}

struct ExperimentFile: Codable {
    var experiments: [Experiment]
}

// MARK: - 收集册模型

struct CollectionItem: Codable, Equatable, Identifiable {
    var id: String
    var name: String
    var icon: String?
    var text: String?      // 汉字卡等文字内容
    var pinyin: String?
    var fact: String?
    var tag: String?       // 浮/沉 等角标
    var tagColor: String?  // blue | coral | gold
}

struct CollectionGroup: Codable, Equatable, Identifiable {
    var id: String         // science | sticker | hanzi | badge
    var title: String
    var icon: String
    var lockedLabel: String
    var items: [CollectionItem]
}

struct CollectionFile: Codable {
    var groups: [CollectionGroup]
}

// MARK: - 解码

enum ContentLoader {
    static func load<T: Decodable>(_ type: T.Type, _ name: String) -> T {
        guard let url = Bundle.main.url(forResource: name, withExtension: "json") else {
            fatalError("缺少内容文件 \(name).json —— 请确认 Resources 已加入 target")
        }
        do {
            return try JSONDecoder().decode(T.self, from: Data(contentsOf: url))
        } catch {
            fatalError("内容文件 \(name).json 解码失败: \(error)")
        }
    }
}
