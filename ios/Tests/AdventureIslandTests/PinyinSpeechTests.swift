import XCTest
@testable import AdventureIsland

/// 拼音朗读转换：确保拼音字母/音节被转成中文同音字，
/// 避免 zh-CN 语音把 b 读成英文字母名 "bee"。
final class PinyinSpeechTests: XCTestCase {

    // MARK: 声母呼读音

    func testSingleInitials() {
        XCTAssertEqual(PinyinSpeech.convert("b"), "玻")
        XCTAssertEqual(PinyinSpeech.convert("p"), "坡")
        XCTAssertEqual(PinyinSpeech.convert("m"), "摸")
        XCTAssertEqual(PinyinSpeech.convert("d"), "得")
        // 双字母声母
        XCTAssertEqual(PinyinSpeech.convert("zh"), "知")
        XCTAssertEqual(PinyinSpeech.convert("ch"), "吃")
        XCTAssertEqual(PinyinSpeech.convert("sh"), "诗")
        // 大写同样处理
        XCTAssertEqual(PinyinSpeech.convert("B"), "玻")
        XCTAssertEqual(PinyinSpeech.convert("ZH"), "知")
    }

    // MARK: 单韵母

    func testSingleFinals() {
        XCTAssertEqual(PinyinSpeech.convert("a"), "啊")
        XCTAssertEqual(PinyinSpeech.convert("o"), "喔")
        XCTAssertEqual(PinyinSpeech.convert("e"), "鹅")
        XCTAssertEqual(PinyinSpeech.convert("i"), "衣")
        XCTAssertEqual(PinyinSpeech.convert("u"), "乌")
        XCTAssertEqual(PinyinSpeech.convert("ü"), "迂")
        XCTAssertEqual(PinyinSpeech.convert("ai"), "哀")
        XCTAssertEqual(PinyinSpeech.convert("ing"), "英")
    }

    // MARK: 完整音节

    func testWholeSyllables() {
        XCTAssertEqual(PinyinSpeech.convert("ba"), "八")
        XCTAssertEqual(PinyinSpeech.convert("ma"), "妈")
        XCTAssertEqual(PinyinSpeech.convert("zhi"), "知")
        XCTAssertEqual(PinyinSpeech.convert("zi"), "字")
        XCTAssertEqual(PinyinSpeech.convert("chi"), "吃")
        // ü 的两种拼写：nv/lv 与 nü/lǜ
        XCTAssertEqual(PinyinSpeech.convert("nv"), "女")
        XCTAssertEqual(PinyinSpeech.convert("nü"), "女")
        XCTAssertEqual(PinyinSpeech.convert("lv"), "绿")
        XCTAssertEqual(PinyinSpeech.convert("lǜ"), "绿")
    }

    // MARK: 带调音节

    func testAccentedSyllables() {
        XCTAssertEqual(PinyinSpeech.convert("bà"), "爸")
        XCTAssertEqual(PinyinSpeech.convert("mā"), "妈")
        XCTAssertEqual(PinyinSpeech.convert("bái"), "白")
        XCTAssertEqual(PinyinSpeech.convert("ā"), "啊")
        XCTAssertEqual(PinyinSpeech.convert("á"), "啊")
        XCTAssertEqual(PinyinSpeech.convert("ǎ"), "啊")
        XCTAssertEqual(PinyinSpeech.convert("à"), "啊")
        // 连续带调单韵母（听力题可能出现 ā á ǎ à）
        XCTAssertEqual(PinyinSpeech.convert("āāā"), "啊啊啊")
    }

    // MARK: 混排文本：只替换拉丁拼音片段，中文原样保留

    func testMixedText() {
        XCTAssertEqual(PinyinSpeech.convert("拼对了，ba！"), "拼对了，八！")
        XCTAssertEqual(PinyinSpeech.convert("b—a"), "玻—啊")
        XCTAssertEqual(PinyinSpeech.convert("声母 b"), "声母 玻")
        // 汉字在前、拼音在后
        XCTAssertEqual(PinyinSpeech.convert("爸爸 bà"), "爸爸 爸")
    }

    // MARK: 英语章节分段：拉丁段 en-US，中文段 zh-CN

    func testEnglishSegments() {
        let segs = SpeechService.segments("Apple 苹果", lang: .english)
        XCTAssertEqual(segs.count, 2)
        XCTAssertEqual(segs[0].text, "Apple")
        XCTAssertEqual(segs[0].language, "en-US")
        XCTAssertEqual(segs[1].text, " 苹果")
        XCTAssertEqual(segs[1].language, "zh-CN")
    }

    func testEnglishSegmentsPureLatin() {
        let segs = SpeechService.segments("Bb", lang: .english)
        XCTAssertEqual(segs.count, 1)
        XCTAssertEqual(segs[0].language, "en-US")
    }

    func testChineseSegmentsKeepChineseVoice() {
        let segs = SpeechService.segments("找一找", lang: .chinese)
        XCTAssertEqual(segs.count, 1)
        XCTAssertEqual(segs[0].language, "zh-CN")
    }
}
