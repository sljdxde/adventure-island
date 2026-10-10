import Foundation

/// 拼音朗读工具：把拉丁字母拼写的拼音（声母/韵母/音节，可带声调）转成中文同音字，
/// 再交给中文语音合成朗读，避免 zh-CN 语音把拼音字母按英文字母名读出
/// （例如 b 读成英文 "bee"）。
///
/// 设计要点：
/// - 单个声母 -> 教学呼读音汉字（b->玻、p->坡、zh->知 …）
/// - 单个韵母 -> 韵母名称汉字（a->啊、o->喔、ü->迂 …）
/// - 完整音节 -> 常用同音汉字（ba->八、zhi->知 …）
/// - 带声调的音节优先按声调选字（bà->爸、mā->妈 …）
/// - 中文与拼音混排的句子（如「拼对了，ba！」）只替换其中的拉丁片段
enum PinyinSpeech {

    /// 对外入口：把文本中的拼音片段替换为中文同音字，其余内容原样保留
    static func convert(_ raw: String) -> String {
        let chars = Array(raw)
        var out = ""
        var i = 0
        while i < chars.count {
            if isPinyinChar(chars[i]) {
                var j = i
                while j < chars.count && isPinyinChar(chars[j]) { j += 1 }
                out += convertRun(String(chars[i..<j]))
                i = j
            } else {
                out.append(chars[i])
                i += 1
            }
        }
        return out
    }

    // MARK: - 单个拼音片段（连续拉丁字母）转换

    private static func convertRun(_ run: String) -> String {
        let lower = run.lowercased()
        var result = ""
        var index = lower.startIndex

        while index < lower.endIndex {
            var matched: String?
            var matchedEnd = index

            // 1) 优先匹配带调音节（保留声调信息，如 bà、mā、āāā）
            // 2) 再匹配无声调完整音节；3) 复韵母（ai/ing 等，避免被拆成 a+i）
            // 按最长前缀贪心切分
            for len in stride(from: 6, through: 1, by: -1) {
                guard let end = lower.index(index, offsetBy: len, limitedBy: lower.endIndex) else { continue }
                let piece = String(lower[index..<end])
                let plain = stripTones(piece)
                if let word = accentedSyllables[piece] ?? syllables[plain] ?? finals[plain] {
                    matched = word
                    matchedEnd = end
                    break
                }
            }

            if let word = matched {
                result += word
                index = matchedEnd
                continue
            }

            // 3) 退化为声母呼读音（zh/ch/sh 双字母优先）
            let remaining = String(lower[index...])
            let two = String(remaining.prefix(2))
            if ["zh", "ch", "sh"].contains(two) {
                result += initials[two] ?? two
                index = lower.index(index, offsetBy: 2)
                continue
            }
            let one = String(remaining.prefix(1))
            let oneKey = stripTones(one)   // ü / ǖ 等先归一化为 v 再查韵母表
            if let word = initials[oneKey] ?? finals[oneKey] {
                result += word
                index = lower.index(after: index)
                continue
            }

            // 4) 无法识别，原样保留（避免吞字符）
            result.append(contentsOf: one)
            index = lower.index(after: index)
        }
        return result
    }

    private static func isPinyinChar(_ ch: Character) -> Bool {
        if ch.isLetter {
            guard let s = ch.asciiValue else { return true } // ü、声调字母等非 ASCII 字母
            return (0x61...0x7A).contains(s) || (0x41...0x5A).contains(s)
        }
        return false
    }

    // MARK: - 声调符号去除

    private static let toneMap: [Character: Character] = [
        "ā": "a", "á": "a", "ǎ": "a", "à": "a",
        "ē": "e", "é": "e", "ě": "e", "è": "e",
        "ī": "i", "í": "i", "ǐ": "i", "ì": "i",
        "ō": "o", "ó": "o", "ǒ": "o", "ò": "o",
        "ū": "u", "ú": "u", "ǔ": "u", "ù": "u",
        "ǖ": "v", "ǘ": "v", "ǚ": "v", "ǜ": "v", "ü": "v",
        "ḿ": "m", "ń": "n", "ň": "n", "ǹ": "n"
    ]

    static func stripTones(_ s: String) -> String {
        var out = ""
        for ch in s {
            if let m = toneMap[ch] { out.append(m) } else { out.append(ch) }
        }
        return out
    }

    // MARK: - 声母呼读音（教材常用近似呼读音）

    static let initials: [String: String] = [
        "b": "玻", "p": "坡", "m": "摸", "f": "佛",
        "d": "得", "t": "特", "n": "讷", "l": "勒",
        "g": "哥", "k": "科", "h": "喝",
        "j": "基", "q": "欺", "x": "希",
        "zh": "知", "ch": "吃", "sh": "诗", "r": "日",
        "z": "资", "c": "雌", "s": "思",
        "y": "衣", "w": "乌"
    ]

    // MARK: - 单韵母名称

    static let finals: [String: String] = [
        "a": "啊", "o": "喔", "e": "鹅", "i": "衣", "u": "乌", "v": "迂",
        "ai": "哀", "ei": "诶", "ui": "威",
        "ao": "熬", "ou": "欧", "iu": "优",
        "ie": "耶", "ve": "约", "er": "儿",
        "an": "安", "en": "恩", "in": "因", "un": "温", "vn": "晕",
        "ang": "昂", "eng": "鞥", "ing": "英", "ong": "翁"
    ]

    // MARK: - 带调音节（按声调选字，仅覆盖教学内容中出现的带调形式）

    static let accentedSyllables: [String: String] = [
        "ā": "啊", "á": "啊", "ǎ": "啊", "à": "啊", "ó": "噢",
        "bà": "爸", "bái": "白",
        "dì": "地", "dāo": "刀",
        "fā": "发", "fēi": "飞",
        "gù": "故", "gē": "哥",
        "kàn": "看", "kāi": "开",
        "lā": "拉", "lǎo": "老",
        "mā": "妈", "mǐ": "米",
        "ná": "拿", "nǐ": "你",
        "pō": "坡", "pǎo": "跑",
        "tài": "太", "tiào": "跳",
        "zhī": "知"
    ]

    // MARK: - 完整音节 -> 常用同音汉字（无声调，取该音节最常用字）

    static let syllables: [String: String] = [
        // 单韵母自成音节
        "a": "啊", "o": "喔", "e": "鹅", "er": "儿",
        // b
        "ba": "八", "bo": "波", "bi": "比", "bu": "不",
        "bai": "白", "bao": "包", "ban": "班", "ben": "本",
        "bang": "帮", "beng": "蹦", "bie": "别", "biao": "标",
        "bian": "边", "bin": "宾", "bing": "兵",
        // p
        "pa": "趴", "po": "坡", "pi": "皮", "pu": "扑",
        "pai": "拍", "pao": "跑", "pou": "剖", "pan": "潘",
        "pen": "喷", "pang": "旁", "peng": "朋", "pie": "撇",
        "piao": "飘", "pian": "片", "pin": "拼", "ping": "平",
        // m
        "ma": "妈", "mo": "摸", "me": "么", "mi": "米", "mu": "木",
        "mai": "买", "mao": "猫", "mou": "谋", "man": "满", "men": "门",
        "mang": "忙", "meng": "蒙", "mie": "灭", "miao": "苗", "miu": "谬",
        "mian": "面", "min": "民", "ming": "明",
        // f
        "fa": "发", "fo": "佛", "fu": "福", "fei": "飞",
        "fou": "否", "fan": "饭", "fen": "分", "fang": "方", "feng": "风",
        // d
        "da": "大", "de": "的", "di": "地", "du": "读",
        "dai": "带", "dei": "得", "dao": "到", "dou": "豆",
        "dan": "但", "dang": "当", "deng": "灯", "dong": "东",
        "die": "爹", "diu": "丢", "diao": "掉", "dian": "点",
        "ding": "丁", "dui": "对", "duan": "段", "dun": "蹲", "duo": "多",
        // t
        "ta": "他", "te": "特", "ti": "踢", "tu": "土",
        "tai": "太", "tao": "桃", "tou": "头", "tan": "谈",
        "tang": "汤", "teng": "疼", "tong": "通", "tie": "贴",
        "tiao": "跳", "tian": "天", "ting": "听", "tui": "推",
        "tuan": "团", "tun": "吞", "tuo": "托",
        // n
        "na": "拿", "ne": "呢", "ni": "你", "nu": "奴", "nv": "女",
        "nai": "奶", "nao": "脑", "nou": "耨", "nan": "南", "nen": "嫩",
        "nang": "囊", "neng": "能", "nong": "农", "nie": "捏", "niu": "牛",
        "niao": "鸟", "nian": "年", "nin": "您", "niang": "娘",
        "ning": "宁", "nve": "虐", "nuo": "糯", "nuan": "暖",
        // l
        "la": "拉", "lo": "咯", "le": "乐", "li": "里", "lu": "路", "lv": "绿",
        "lai": "来", "lei": "类", "lao": "老", "lou": "楼", "lan": "蓝",
        "lang": "狼", "leng": "冷", "long": "龙", "lia": "俩", "lie": "列",
        "liu": "六", "liao": "了", "lian": "连", "lin": "林", "liang": "亮",
        "ling": "零", "lve": "略", "luo": "罗", "luan": "乱", "lun": "轮",
        // g
        "ga": "嘎", "ge": "哥", "gu": "古", "gai": "该", "gei": "给",
        "gao": "高", "gou": "狗", "gan": "干", "gen": "跟", "gang": "刚",
        "geng": "更", "gong": "工", "gua": "瓜", "guo": "国", "gui": "贵",
        "guai": "怪", "guan": "关", "gun": "滚", "guang": "光",
        // k
        "ka": "咖", "ke": "科", "ku": "哭", "kai": "开", "kao": "考",
        "kou": "口", "kan": "看", "ken": "肯", "kang": "康", "keng": "坑",
        "kong": "空", "kua": "夸", "kuo": "阔", "kui": "亏", "kuai": "快",
        "kuan": "宽", "kun": "困", "kuang": "筐",
        // h
        "ha": "哈", "he": "喝", "hu": "虎", "hai": "海", "hei": "黑",
        "hao": "好", "hou": "后", "han": "汉", "hen": "很", "hang": "航",
        "heng": "横", "hong": "红", "hua": "花", "huo": "火", "hui": "会",
        "huai": "坏", "huan": "欢", "hun": "婚", "huang": "黄",
        // j q x
        "ji": "机", "ju": "居", "jia": "家", "jie": "接", "jiao": "交",
        "jiu": "九", "jian": "见", "jin": "金", "jiang": "江", "jing": "京",
        "jiong": "窘", "jun": "军", "juan": "娟", "jue": "决",
        "qi": "七", "qu": "区", "qia": "恰", "qie": "切", "qiao": "桥",
        "qiu": "秋", "qian": "千", "qin": "亲", "qiang": "强", "qing": "青",
        "qiong": "穷", "qun": "群", "quan": "全", "que": "确",
        "xi": "西", "xu": "需", "xia": "下", "xie": "写", "xiao": "小",
        "xiu": "休", "xian": "先", "xin": "心", "xiang": "想", "xing": "星",
        "xiong": "熊", "xun": "寻", "xuan": "宣", "xue": "学",
        // 翘舌整体认读音节
        "zhi": "知", "chi": "吃", "shi": "十", "ri": "日",
        "zi": "字", "ci": "次", "si": "四",
        // zh
        "zha": "扎", "zhe": "这", "zhu": "猪", "zhai": "摘", "zhao": "找",
        "zhou": "周", "zhan": "站", "zhen": "真", "zhang": "张", "zheng": "正",
        "zhong": "中", "zhua": "抓", "zhuo": "桌", "zhui": "追", "zhuai": "拽",
        "zhuan": "转", "zhun": "准", "zhuang": "装",
        // ch
        "cha": "茶", "che": "车", "chu": "出", "chai": "拆", "chao": "超",
        "chou": "抽", "chan": "产", "chen": "陈", "chang": "长", "cheng": "成",
        "chong": "虫", "chuo": "戳", "chui": "吹", "chuai": "揣",
        "chuan": "船", "chun": "春", "chuang": "窗",
        // sh
        "sha": "沙", "she": "蛇", "shu": "书", "shai": "晒", "shao": "少",
        "shou": "手", "shan": "山", "shen": "身", "shang": "上", "sheng": "生",
        "shua": "刷", "shuo": "说", "shui": "水", "shuai": "帅",
        "shuan": "拴", "shun": "顺", "shuang": "双",
        // r
        "re": "热", "ru": "如", "rao": "绕", "rou": "肉", "ran": "然",
        "ren": "人", "rang": "让", "reng": "仍", "rong": "容",
        "ruo": "若", "rui": "瑞", "ruan": "软", "run": "润",
        // z
        "za": "杂", "ze": "则", "zu": "足", "zai": "在", "zao": "早",
        "zou": "走", "zan": "咱", "zen": "怎", "zang": "脏", "zeng": "增",
        "zong": "宗", "zuo": "昨", "zui": "最", "zuan": "钻", "zun": "尊",
        // c
        "ca": "擦", "ce": "册", "cu": "粗", "cai": "菜", "cao": "草",
        "cou": "凑", "can": "餐", "cen": "岑", "cang": "仓", "ceng": "层",
        "cong": "从", "cuo": "错", "cui": "催", "cuan": "窜", "cun": "村",
        // s
        "sa": "撒", "se": "色", "su": "苏", "sai": "赛", "sao": "扫",
        "sou": "搜", "san": "三", "sen": "森", "sang": "桑", "seng": "僧",
        "song": "送", "suo": "所", "sui": "岁", "suan": "算", "sun": "孙",
        // y w 整体认读
        "ya": "呀", "yo": "哟", "ye": "爷", "yi": "一", "yao": "要",
        "you": "有", "yan": "眼", "yin": "音", "yang": "羊", "ying": "英",
        "yong": "用", "yu": "鱼", "yue": "月", "yuan": "圆", "yun": "云",
        "wa": "挖", "wo": "我", "wu": "五", "wai": "外", "wei": "为",
        "wan": "完", "wen": "文", "wang": "王", "weng": "翁"
    ]
}
