#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探险岛 · HTML 模拟器内容语义审计（spec/v0.8-board 起为常驻闸门）

从 main 的 ios/tools/audit_content.py 适配：数据源改为直接解析 ios/preview/index.html
里的 CONTENT（两分支合并后，模拟器内容就是唯一真相源），学科补上 geo（环球号）。

用法：
    python3 ios/tools/audit_preview.py        # 有 FAIL 时退出码 1
"""
import json, os, re, sys, unicodedata, collections

try:
    from pypinyin import lazy_pinyin, Style
except ImportError:
    sys.exit("需要 pypinyin：python3 -m pip install pypinyin\n"
             "  PyPI 不通时用国内镜像：pip install -i https://mirrors.aliyun.com/pypi/simple/ pypinyin")

PREVIEW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "preview", "index.html")
SUBS = ["cn", "math", "pinyin", "english", "astro", "geo"]

def extra(csv):
    return {w.strip() for w in csv.split(",") if w.strip()}

# 数字关的词教的是数字本身（三个/五官/九颗星/一天），图配可数物即可
NUM_WORD = re.compile(r"^[一二三四五六七八九十][\u4e00-\u9fa5]{0,2}$")

# 图标 → 这张图能画出来的词（宁可窄，不要宽：图是教学证据）
ICON_CN = {
    "book":    {"书", "课本", "看书", "读书", "故事书"},
    "cake":    {"蛋糕", "生日", "月饼", "点心"},
    "cat":     {"猫", "小猫"},
    "comet":   {"彗星"},
    "crystal": {"水晶", "泉水", "光环", "钻石", "星晶"},
    "duck":    {"鸭", "小鸟", "鸟"},
    "bear":    {"熊", "小熊"},
    "flame":   {"火", "火焰", "点火", "发烧", "烫"},
    "fox":     {"狐狸"},
    "ice":     {"冰", "冰块"},
    "key":     {"钥匙", "锁"},
    "magnet":  {"磁铁", "吸铁石"},
    "penguin": {"企鹅"},
    "rabbit":  {"兔", "白兔", "兔子"},
    "rainbow": {"彩虹"},
    "rocket":  {"火箭", "坐火箭", "飞"},
    "candy":   {"糖", "糖果"},
    "sunrays": {"阳光", "太阳光", "光芒"},
    "train":   {"火车", "坐火车", "车"},
    "tree":    {"树", "树木", "森林", "山林", "花木", "木", "鸟巢"},
    "volcano": {"火山", "山", "山坡"},
    "dino":    {"恐龙"},
    "jar":     {"罐", "瓶子"},
    "clock":   {"钟", "时钟", "时间"},
    # ---- v0.11 合并扩充（spec 大内容 + 天文台/地理新图标）----
    "apple":   extra("苹果,果子,水果,红"),
    "banana":  extra("香蕉,黄"),
    "wave":    extra("水,海浪,波浪,河,大海,下雨,水花,口水,蓝"),
    "sunface": extra("太阳,日,晒,白天"),
    "moon":    extra("月亮,月,夜晚,黑夜"),
    "sunrise": extra("日出,早晨,今天,日,太阳,白天,一天,三天"),
    "speaker": extra("喇叭,声音,开口,口,嘴"),
    "party":   extra("聚会,庆祝,派对,人们,大人,家人"),
    "heart":   extra("心,开心,爱心,心跳,心意,人心,手心"),
    "home":    extra("家,房子,大门,回家,门口"),
    "calendar":extra("一月,今天,周,日历,日子,明天,昨天,月份,二月,三月,四月,九月,四季,第二"),
    "gift":    extra("礼物,礼包,四方,围巾"),
    "girl":    extra("女孩,妈,人,朋友,你好,拿苹果,阿姨"),
    "earth":   extra("地球,大地,亚洲"),
    "everest": extra("高山,山,珠峰,珠穆朗玛峰,上山,下山"),
    "greatwall":extra("长城,城墙,长龙"),
    "tiananmen":extra("天安门,北京"),
    "china-map":extra("中国地图,地图"),
    "world-map":extra("世界地图,地图"),
    "river":   extra("河,大河,长江,黄河"),
    "lion":    extra("狮子,万兽之王"),
    "kangaroo":extra("袋鼠"),
    "windmill":extra("风车"),
    "libertystatue":extra("自由女神"),
    "milkyway":extra("银河"),
    "astronaut":extra("宇航员"),
    "starface":extra("星星,星,火花,星空"),
    "paw":     extra("小手,手,爪,脚印,小动物"),
    "shoe":    extra("鞋"),
    "hat":     extra("帽子,帽"),
    "bus":     extra("巴士,公交车"),
    "car":     extra("汽车"),
    "dog":     extra("狗,小狗"),
    "bread":   extra("面包"),
    "fish":    extra("鱼"),
    "frog":    extra("青蛙"),
    "hanger":  extra("衣架"),
    "milk":    extra("牛奶"),
    "polarbear":extra("北极熊"),
    "shop":    extra("商店"),
    "dice":    extra("骰子,点"),
    "equal":   extra("等号,二"),
    "sprout":  extra("芽,苗,种子,田里,草,水田,花苗"),
    "elephant":extra("大象,象"),
    "square":  extra("方块,正方形,方"),
    # ---- v0.12 补齐全部 171 个设计资产的词表（漏登记的图标会被当成 unknown 放过）----
    "ball":    extra("球,足球,皮球,篮球"),
    "pig":     extra("猪,小猪,肥猪,猪肉"),
    "bee":     extra("蜜蜂,蜂,采蜜,虫子,小虫"),
    "cow":     extra("牛,奶牛,黄牛,牛奶"),
    "monkey":  extra("猴子,猴,泼猴"),
    "tiger":   extra("老虎,虎,猛虎"),
    "panda":   extra("熊猫,猫熊,国宝"),
    "mushroom":extra("蘑菇,菌,伞菌"),
    "sponge":  extra("海绵,吸水,软绵"),
    "wood":    extra("木头,木材,木,木板"),
    "fire":    extra("火,火焰,着火,燃烧"),
    "lock":    extra("锁,锁住,门锁"),
    "medal":   extra("奖牌,勋章,奖章,第一名"),
    "boss":    extra("大BOSS,怪兽,壳壳兽"),
    "mario":   extra("红帽,小勇士,马里奥"),
    "bush":    extra("灌木,草丛,灌木丛"),
    "ferris":  extra("摩天轮,旋转轮,游乐场"),
    "station": extra("车站,站点,太空站,空间站"),
    "pentagon":extra("五边形,五角形"),
    "circle":  extra("圆,圆圈,圆形,圆圆"),
    "triangle":extra("三角,三角形,三个角"),
    "block":   extra("积木,方块,方块糖"),
    "slider":  extra("滑块,滑条,调节"),
    "shield":  extra("盾,盾牌,护盾,保护"),
    "goggles": extra("护目镜,眼镜,泳镜"),
    "flask":   extra("烧瓶,实验瓶,科学实验"),
    "salt":    extra("盐,咸,食盐"),
    "sugar":   extra("糖,白糖,砂糖"),
    "sand":    extra("沙子,沙,沙砾"),
    "planet":  extra("行星,星球,大行星"),
    "meteor":  extra("流星,陨星,扫把星"),
    "satellite":extra("卫星,人造卫星"),
    "fullmoon":extra("满月,圆月,月圆"),
    "newmoon": extra("新月,月牙,月朔"),
    "waxing":  extra("上弦月,盈月"),
    "waning":  extra("残月,下弦月,亏月"),
    "hanzi":   extra("汉字,字,方块字"),
    "back":    extra("返回,回去,后退"),
    "question":extra("问题,疑问,问号"),
    "brick":   extra("砖,砖块"),
    # ---- v0.12 二批：按图标自然中文名补全（审计此前把这些当 unknown 静默放过）----
    "blackhole":extra("黑洞,宇宙黑洞"),
    "ufo":      extra("飞碟,外星人,UFO,不明飞行物"),
    "cup":      extra("杯子,水杯,茶杯,碗"),
    "bowl":     extra("碗,饭碗,汤碗"),
    "bird":     extra("小鸟,麻雀,老鹰,鸡,母鸡,小鸡,飞鸟,禽"),
    "castle":   extra("高楼,楼房,城堡,大楼,石桥,城墙,宫殿"),
    "flag":     extra("红旗,国旗,旗帜,旗子,红灯"),
    "bulb":     extra("红灯,电灯,灯泡,灯"),
    "sparkle":  extra("变化,变身,魔法,亮,闪光"),
    "flower":   extra("季节,花开,花朵,花瓣,花园,春"),
    "leaf":     extra("花瓣,树叶,叶子,种植,白杨,树"),
    "coin":     extra("宝贝,钱财,金币,钱币,宝贝蛋"),
    "egg":      extra("雪白,鸡蛋,蛋,蛋白,蛋黄"),
    "robot":    extra("火星车,机器人,机器"),
    "sun":      extra("金色,金黄,太阳,阳光"),
    "mars":     extra("红色,火星,红色星球"),
    "star":     extra("北极星,恒星,星星,星"),
    "rock":     extra("山洞,岩石,石头,岩洞"),
    "telescope":extra("观星,看星,望远镜"),
    "school":   extra("上学,上课,十分好,学校,上课去"),
    "balloon":  extra("九月,九月九,气球, fly"),
}
# 图标宽表（v0.12）：图标名 → 孩子可能说的词/同义词/常见搭配。
# 用于「选项图文各自成立即可」的判断，比 ICON_CN 宽（ICON_CN 是严格名词表）。
ICON_ZH = {
    "apple": ("苹果", "红", "果"), "banana": ("香蕉", "黄", "蕉"),
    "ball": ("球", "足球", "皮球"), "balloon": ("气球", "飞", "九月"),
    "bear": ("熊", "外套", "宝"), "bee": ("蜜蜂", "蜂", "虫子", "小虫", "虫虫"),
    "bird": ("鸟", "小鸡", "母鸡", "麻雀", "老鹰", "孔雀", "飞鸟"),
    "blackhole": ("黑洞", "宇宙"), "book": ("书", "课本", "读", "故事"),
    "bread": ("面包", "麦"), "bulb": ("灯", "红灯", "电灯"),
    "bus": ("公交", "巴士", "车"), "cake": ("蛋糕", "锅里", "点心"),
    "candy": ("糖", "糖果", "八个", "甜"), "car": ("汽车", "车"),
    "castle": ("高楼", "楼房", "城堡", "石桥", "城"), "cat": ("猫", "小猫"),
    "chart": ("图表", "画", "数据"), "china-map": ("中国", "地图", "北京"),
    "circle": ("圆", "圆圈"), "clock": ("钟", "号码", "时间"),
    "coin": ("钱", "金币", "宝贝"), "comet": ("彗星", "扫把星"),
    "cow": ("牛", "奶牛"), "crystal": ("水晶", "泉水", "珊瑚", "冰"),
    "cup": ("杯", "喝水", "茶杯"), "desert": ("沙漠", "撒哈拉", "埃及"),
    "dice": ("骰子", "七天", "游戏", "Game"), "dino": ("恐龙", "霸王龙", "长脖子"),
    "dog": ("狗", "小狗"), "duck": ("鸭", "小鸭", "飞"),
    "earth": ("地球", "大地", "蓝色"), "egg": ("蛋", "雪白", "蛋白"),
    "eiffel": ("埃菲尔", "铁塔", "巴黎"), "elephant": ("大象", "象"),
    "equal": ("等号", "一", "二", "一个"), "everest": ("珠峰", "高山", "挪威", "峡湾"),
    "fish": ("鱼", "游"), "flag": ("旗", "红旗", "队伍", "国旗"),
    "flame": ("火", "火焰"), "flask": ("实验", "科学", "烧瓶"),
    "flower": ("花", "花瓣", "季节", "水田", "花园"), "fox": ("狐狸", "爸"),
    "frog": ("青蛙", "蛙"), "gift": ("礼物", "书包", "宝"),
    "girl": ("人", "妈妈", "我", "耳朵", "老师", "跑"), "greatwall": ("长城", "中国", "长龙"),
    "hanger": ("衣架", "衬衫"), "hanzi": ("汉字", "字"),
    "hat": ("帽子", "帽"), "heart": ("心", "爱心", "爱"),
    "home": ("家", "房子", "下面"), "ice": ("冰", "海冰"),
    "jar": ("罐", "水井"), "jupiter": ("木星",), "kangaroo": ("袋鼠", "澳大利亚"),
    "key": ("钥匙", "笔"), "leaf": ("叶", "树叶", "花瓣", "白杨", "种植", "吃叶", "山林", "小草", "草"),
    "lion": ("狮子", "非洲"), "lock": ("锁",), "magnet": ("磁铁", "吸铁石"),
    "maple": ("枫", "加拿大", "秋"), "mario": ("红帽", "小勇士"),
    "mars": ("火星", "红色"), "medal": ("奖牌", "勋章"),
    "mercury": ("水星",), "meteor": ("流星",), "meteorite": ("陨石",),
    "milkyway": ("银河", "宇宙"), "milk": ("牛奶", "白云", "羊毛", "奶"),
    "moon": ("月亮", "晚上", "月"), "monkey": ("猴子", "猴"),
    "neptune": ("海王星",), "palm": ("椰树", "海南", "棕"), "panda": ("熊猫", "成都"),
    "party": ("派对", "春节", "圣诞", "南瓜灯", "芬兰", "排队", "五官"),
    "paw": ("爪子", "小脚丫", "宝宝", "脚印"), "penguin": ("企鹅", "南极"),
    "pig": ("猪", "小猪"), "pisa": ("比萨", "斜塔", "罗马", "意大利"),
    "planet": ("行星", "星球"), "polarbear": ("北极熊", "北极", "北冰洋", "小羊"),
    "pyramid": ("金字塔", "开罗", "埃及"), "rabbit": ("兔", "跳"),
    "rainbow": ("彩虹", "彩云", "云南"), "river": ("江", "河", "丝路"),
    "robot": ("机器人", "火星车"), "rock": ("石头", "山洞", "岩石"),
    "rocket": ("火箭", "旅行", "出发"), "satellite": ("卫星",),
    "saturn": ("土星",), "school": ("学校", "上学", "上山", "三角", "十分好"),
    "shoe": ("鞋",), "shop": ("商店", "市场", "商贸"), "slider": ("滑块",),
    "snowflake": ("雪花", "哈尔滨", "冰"), "speaker": ("喇叭", "开口", "新闻", "耳机", "吹号", "唱"),
    "sparkle": ("星星", "变化", "亮", "六个", "流星"), "sponge": ("海绵",),
    "sprout": ("苗", "植物", "森林", "迎客松", "桂林", "农民", "田里", "松果"),
    "star": ("星星", "北极星", "三个", "五个", "十个"), "starface": ("星星", "星", "眼睛"),
    "station": ("太空站", "车站"), "sun": ("太阳", "金色", "夏天", "Summer"),
    "sunface": ("太阳", "日"), "sunrise": ("日出", "今天", "一天", "上学", "傍晚", "傍"),
    "taj": ("泰姬陵", "印度"), "telescope": ("望远镜", "观星"),
    "tiananmen": ("天安门", "北京"), "tiger": ("老虎", "虎"),
    "torii": ("鸟居", "东京", "日本"), "tower": ("塔", "小蛮腰", "高楼"),
    "train": ("火车", "旅途"), "tree": ("树", "雨林", "梧桐", "阿里山", "台湾", "海南"),
    "triangle": ("三角", "三角形"), "ufo": ("飞碟", "外星人"),
    "uranus": ("天王星",), "venus": ("金星",), "volcano": ("火山", "岩浆", "冰岛", "夏威夷"),
    "wave": ("浪", "海浪", "上海", "青海湖", "海洋", "池塘", "日月潭"),
    "windmill": ("风车", "荷兰", "风"), "wood": ("木头", "木"),
    "world-map": ("世界地图", "世界", "语言"),
}

# 识字村的「看图找字 / 听音找图」把汉字配成象形图，这一层是造字逻辑不是名词一致，
# 单独立表放行（否则「田 ↔ 日历格子」这类正确象形会被误判）
MORPH_ICON = {"日": {"sunface", "sun", "sunrise"}, "水": {"wave"}, "山": {"volcano"},
              "木": {"tree", "sprout"}, "人": {"girl"}, "口": {"speaker"}, "天": {"sunrays", "sun"},
              "田": {"calendar"}, "石": {"rock"}, "火": {"flame", "volcano"},
              "鸟": {"duck"},
              "三": {"equal", "triangle"}, "四": {"calendar", "square"}, "五": {"star"},
              "六": {"sparkle"}, "七": {"dice"}, "八": {"candy"}, "九": {"balloon"},
              "十": {"star", "starface"}, "大": {"girl", "party", "bear", "elephant", "everest"},
              "星": {"starface", "star", "planet"},
              "手": {"paw", "heart"},
              # —— v0.12 部编二上识字表 50 字：字 ↔ 表意图（图是帮孩子记字形的助记符）——
              "一": {"equal"}, "二": {"equal"}, "雨": {"wave", "rainbow"},
              "风": {"windmill"}, "雪": {"snowflake"}, "白": {"egg", "milk"},
              "禾": {"sprout"}, "麦": {"sprout", "bread"}, "虫": {"bee"}, "蛙": {"frog"},
              "牛": {"cow"}, "羊": {"polarbear", "sheep"}, "狗": {"dog"}, "猪": {"pig"},
              "猫": {"cat"}, "鸡": {"bird"}, "鸭": {"duck"}, "鹰": {"bird"}, "雀": {"bird"},
              "象": {"elephant"}, "熊": {"bear"}, "狮": {"lion"}, "猴": {"monkey"},
              "贝": {"coin"}, "见": {"girl", "telescope"}, "目": {"girl", "eye"},
              "足": {"ball", "foot"}, "身": {"girl"},
              "车": {"car"}, "船": {"wave"}, "灯": {"bulb"},
              "门": {"home"}, "井": {"jar"}, "刀": {"key"}, "力": {"equal"},
              "果": {"apple"}, "糖": {"candy"}, "米": {"bowl", "rice"}, "茶": {"leaf"},
              "花": {"flower"}, "草": {"sprout", "leaf"}, "树": {"tree"}, "林": {"tree"},
              "松": {"tree"}, "柏": {"tree"}, "杨": {"tree"}, "柳": {"tree"},
              "桐": {"tree"}, "枫": {"maple"}, "桂": {"flower"}, "梅": {"flower"},
              "园": {"flower", "sprout"}, "塘": {"wave"}, "湖": {"wave"}, "河": {"river"},
              "海": {"wave"}, "洋": {"wave"}, "潭": {"wave"}, "溪": {"wave"},
              "晨": {"sunrise"}, "昏": {"sunrise"},
              "月": {"moon"},
              "城": {"castle"}, "楼": {"castle"}, "桥": {"castle"}, "塔": {"castle"},
              "市": {"shop"}, "店": {"shop"}, "钱": {"coin"}, "币": {"coin"},
              "字": {"book"},
              "画": {"chart"}, "歌": {"speaker"}, "舞": {"party"}, "戏": {"dice"},
              "笑": {"party"}, "哭": {"party"}, "怒": {"flame"}, "怕": {"ghost"},
              "爱": {"heart"}, "亲": {"heart"}, "友": {"girl"}, "朋": {"girl"},
              "师": {"girl"}, "生": {"girl"}, "医": {"shield"}, "军": {"flag"},
              "农": {"sprout"}, "渔": {"fish"}, "牧": {"cow"}, "猎": {"bow"},
              "工": {"hammer"}, "商": {"shop"}, "旅": {"rocket"}, "行": {"train"},
              "飞": {"bird", "rocket"}, "跑": {"girl"}, "跳": {"rabbit"}, "走": {"girl"},
              "坐": {"chair"}, "立": {"girl"}, "睡": {"bed"}, "醒": {"sun"},
              "吃": {"apple"}, "喝": {"cup"}, "看": {"telescope"}, "听": {"speaker"},
              "说": {"speaker"}, "想": {"bulb"}, "知": {"book"}, "识": {"book"},
              "记": {"book"}, "忘": {"bulb"}, "懂": {"bulb"},
              "变": {"sparkle"}, "化": {"sparkle"}, "成": {"star"}, "败": {"rock"},
              "湿": {"wave"},
              "亮": {"bulb"}, "明": {"sun"}, "暗": {"moon"},
              "峰": {"everest"}, "岭": {"everest"}, "岛": {"palm"}, "屿": {"wave"},
              "极": {"polarbear"}, "端": {"flag"},
              "傍": {"sunrise", "moon"}, "植": {"sprout", "leaf"}, "号": {"speaker", "flag"},
              "迎": {"party"}, "送": {"party"}, "招": {"girl"}, "呼": {"speaker"},
              "闻": {"speaker"}, "问": {"question"}, "答": {"speaker"},
              "队": {"party"}, "群": {"party"}, "众": {"party"}, "伍": {"flag"},
              "旗": {"flag"}, "袍": {"hanger"}, "裙": {"hanger"}, "裤": {"hanger"},
              "鞋": {"shoe"}, "帽": {"hat"}, "伞": {"umbrella"},
              "娃": {"girl"}, "姨": {"girl"}, "叔": {"fox"}, "伯": {"bear"},
              "婆": {"girl"}, "公": {"bear"}, "父": {"fox"}, "母": {"girl"},
              "观": {"telescope"}, "赏": {"starface"}, "玩": {"ball"},
              "耍": {"ball"}, "乐": {"party"}, "喜": {"party"}, "庆": {"party"},
              "祝": {"party"}, "贺": {"party"}, "福": {"gift"}, "寿": {"gift"},
              "财": {"coin"}, "宝": {"gift"}, "玉": {"crystal"}, "珠": {"crystal"},
              "钻": {"crystal"}, "金": {"coin"}, "银": {"coin"}, "铜": {"coin"},
              "铁": {"magnet"}, "钢": {"magnet"}, "纸": {"book"}, "墨": {"ink"},
              "笔": {"key"}, "砚": {"ink"}, "琴": {"speaker"}, "棋": {"dice"},
              "书": {"book"}, "报": {"book"}, "刊": {"book"}, "册": {"book"},
              "卷": {"book"}, "篇": {"book"}, "章": {"book"}, "节": {"calendar"},
              "季": {"calendar"}, "春": {"flower"}, "夏": {"sun"}, "秋": {"maple"},
              "冬": {"snowflake"}, "岁": {"calendar"}, "年": {"calendar"},
              "晴": {"sun"}, "阴": {"cloud"}, "云": {"milk"}, "雾": {"cloud"},
              "露": {"leaf"}, "霜": {"snowflake"}, "冰": {"ice"},
              "虹": {"rainbow"}, "霞": {"sunrise"}, "光": {"sun"}, "影": {"moon"},
              "声": {"speaker"}, "音": {"speaker"}, "响": {"speaker"},
              "动": {"girl"}, "静": {"shield"}, "停": {"flag"}, "起": {"sunrise"},
              "落": {"wave"}, "升": {"rocket"}, "降": {"wave"}, "开": {"gift"},
              "关": {"lock"}, "锁": {"lock"}, "钥匙": {"key"},
              "南": {"flag"}, "北": {"flag"}, "东": {"flag"}, "西": {"flag"},
              "中": {"china-map"}, "外": {"world-map"}, "内": {"home"},
              "上": {"everest", "sunrise", "school"}, "下": {"wave"}, "左": {"flag"}, "右": {"flag"},
              "前": {"rocket"}, "里": {"home"}, "间": {"flag"},
              "旁": {"sunrise"}, "边": {"flag"}, "角": {"triangle"}, "方": {"square"},
              "圆": {"circle"}, "长": {"train"}, "短": {"clip"}, "高": {"everest"},
              "低": {"wave"}, "厚": {"book"}, "薄": {"clip"}, "粗": {"tree"},
              "细": {"clip"}, "小": {"paw", "rabbit"},
              "多": {"party"}, "少": {"clip"}, "全": {"starface"}, "半": {"equal"},
              "双": {"equal"}, "对": {"equal"}, "错": {"question"}, "是": {"starface"},
              "非": {"question"}, "有": {"gift"}, "无": {"lock"}, "空": {"balloon"},
              "满": {"party"}, "新": {"sparkle"}, "旧": {"book"}, "好": {"heart"},
              "坏": {"rock"}, "美": {"flower"}, "丑": {"rock"}, "香": {"flower"},
              "臭": {"flask"}, "甜": {"candy"}, "苦": {"flask"}, "酸": {"banana"},
              "辣": {"flame"}, "咸": {"salt"}, "淡": {"wave"}, "热": {"sun"},
              "冷": {"snowflake"}, "温": {"sun"}, "凉": {"snowflake"}, "暖": {"sun"},
              "软": {"sponge"}, "硬": {"rock"}, "轻": {"balloon"}, "重": {"rock"},
              "快": {"rocket"}, "慢": {"turtle"}, "早": {"sunrise"}, "晚": {"moon"},
              "先": {"rocket"}, "后": {"back"}, "始": {"sunrise"}, "终": {"flag"},
              "头": {"girl"}, "尾": {"duck"}, "根": {"tree"}, "叶": {"leaf"},
              "枝": {"tree"}, "干": {"tree"}, "皮": {"tree"}, "肉": {"apple"},
              "血": {"heart"}, "骨": {"rock"}, "毛": {"polarbear"}, "爪": {"paw"},
              "牙": {"key"}, "舌": {"speaker"}, "唇": {"speaker"}, "鼻": {"crystal"},
              "眼": {"starface"}, "耳": {"speaker"}, "脸": {"girl"}, "额": {"girl"},
              "颈": {"girl"}, "肩": {"girl"}, "胸": {"girl"}, "背": {"girl"},
              "腰": {"girl"}, "腹": {"girl"}, "臀": {"girl"}, "腿": {"girl"},
              "膝": {"girl"}, "踝": {"girl"}, "腕": {"girl"}, "掌": {"paw"},
              "指": {"paw"}, "拇": {"paw"}, "趾": {"paw"},
              "脑": {"bulb"}, "心": {"heart"}, "肝": {"heart"}, "肺": {"heart"},
              "胃": {"apple"}, "肠": {"apple"}, "肾": {"heart"}, "脾": {"heart"},
              "胆": {"flask"}, "胞": {"heart"}, "肤": {"girl"}, "肌": {"girl"},
              "腱": {"girl"}, "膜": {"girl"}, "液": {"wave"}, "津": {"wave"},
              "汗": {"wave"}, "泪": {"wave"}, "涕": {"wave"}, "唾": {"wave"},
}

# 天体圆盘（v0.10 天文台）：index.html 的 BODIES 用 CSS 按真实比例画，这里核对「圆盘 ↔ 名字」
BODY_CN = {"sun":"太阳", "mercury":"水星", "venus":"金星", "earth":"地球", "mars":"火星",
           "jupiter":"木星", "saturn":"土星", "uranus":"天王星", "neptune":"海王星",
           "moon":"月球", "pluto":"冥王星", "comet":"彗星"}

# 允许「动作/场景」类搭配：图是动作的道具，不是名词本身
ACTION_OK = {"跳高", "拉手", "跑步", "开口", "张大嘴", "许个愿", "点火", "看书", "拿苹果", "坐火箭", "故事"}

CJK = re.compile(r"[一-鿿]+")
LAT = re.compile(r"[A-Za-z]+")


def han(text):
    return "".join(CJK.findall(text or ""))


def initials(text):
    return [x for x in lazy_pinyin(han(text), style=Style.INITIALS, strict=False) if x]


def icon_matches(icon, text):
    """图标画的东西是否出现在词里（或词是允许的动作搭配）"""
    if icon not in ICON_CN:
        return None                                    # 未知图标，交给上层报 unknown
    h = han(text)
    if not h:
        return True                                    # 纯英文/拼音项，不在此规则内
    if any(a in (text or "") for a in ACTION_OK):
        return True
    if NUM_WORD.match(h):
        return True
    return any(w and w in h for w in ICON_CN[icon])


def word_initial(text):
    """例词的目标声母：优先取词里标注的拉丁拼音（「山坡 pō」→ p），没有再取第一个汉字的声母。

    注意双字母声母（sh/ch/zh）：NFD 拆解会把 shǎn 的 s 与 ǎ 之间的 h 拿出来当首字母，
    必须先按已知双字母声母整词匹配（v0.12 修）。
    """
    m = LAT.search(text or "")
    if m:
        w = m.group(0).lower()
        for two in ("sh", "ch", "zh"):
            if w.startswith(two):
                return two
        c = unicodedata.normalize("NFD", w)[0].lower()
        if c.isalpha():
            return c
    ini = initials(text)
    return ini[0] if ini else None


def art_key(x):
    """图案项的统一键：图标名 / 文字 / 天体 / 月相，用来比对序列和选项"""
    if isinstance(x, dict):
        return x.get("icon") or x.get("text") or x.get("body") or x.get("phase")
    return x


def expected_next(seq):
    """按周期 2/3 推断序列的下一项；推不出（不是周期规律）返回 None"""
    for p in (2, 3):
        if len(seq) > p and all(seq[i] == seq[i % p] for i in range(len(seq))):
            return seq[len(seq) % p]
    return None


def steps_of(doc):
    for lv in doc["levels"]:
        for st in lv.get("steps") or []:
            yield lv, st


def pairs_of(st):
    for key in ("options", "examples", "words", "cards"):
        for o in st.get(key) or []:
            if isinstance(o, dict) and o.get("icon") and o.get("text"):
                yield key, o


# 地名/国名 → 代表图标：这些词本身画不出来，图是「这个地方最有名的东西」，
# 属于合理的教学设计（风车=荷兰、袋鼠=澳大利亚），不是图文不符。
# 只有「词与图标讲的完全不是一回事」才算错（如「俄罗斯」配 castle）。
PLACE_ICON = {    "澳大利亚": {"kangaroo"}, "新西兰": {"sprout", "wave"},
    "俄罗斯": {"snowflake", "castle"}, "日本": {"torii", "fuji"},
    "英国": {"bigben"},
    "智利": {"everest", "wave"}, "秘鲁": {"everest", "flag"},
    "阿根廷": {"ball", "party"}, "中国": {"china-map", "tiananmen", "flag", "panda"},
    "广州": {"shop", "tower"}, "杭州": {"wave"},
    "成都": {"panda"}, "甘肃": {"desert", "flag"}, "西藏": {"everest", "flag"},
    "青海": {"wave", "sprout"}, "内蒙古": {"sprout"}, "香港": {"tower"}, "台湾": {"tree", "everest"},
    "浙江": {"wave"}, "新疆": {"desert"}, "云南": {"rainbow", "tree"},
    "四川": {"panda"}, "东北": {"snowflake", "tree"}, "西部": {"desert"}, "中部": {"sprout"},
    "东部": {"tower"}, "南方": {"palm"}, "海岛": {"wave"}, "亚洲": {"earth", "china-map"},
    "欧洲": {"castle", "bigben"}, "非洲": {"lion", "elephant"}, "北美洲": {"libertystatue"},
    "南美洲": {"ball"}, "大洋洲": {"kangaroo"}, "南极洲": {"penguin"}, "七大洲": {"world-map"},
    "太平洋": {"wave"}, "大西洋": {"wave"}, "印度洋": {"wave"}, "北冰洋": {"snowflake", "wave"},
    "青海湖": {"wave", "sprout"}, "西湖": {"wave"}, "日月潭": {"wave"}, "死海": {"wave"},
    "贝加尔湖": {"wave", "snowflake"}, "亚马孙": {"tree", "frog"}, "雨林": {"tree", "frog"},
    "撒哈拉": {"desert"}, "沙漠": {"desert"}, "丝绸之路": {"flag", "desert"},
    "长城": {"greatwall"}, "珠穆朗玛峰": {"everest"}, "黄山": {"everest", "tree"},
    "马里亚纳海沟": {"wave", "fish"}, "海峡": {"wave"}, "海湾": {"wave"}, "大堡礁": {"crystal", "fish"},
    "珊瑚": {"crystal", "fish"}, "夏威夷": {"volcano", "palm"}, "火山": {"volcano", "flame"},
    "格陵兰": {"snowflake"}, "冰岛火山": {"volcano"}, "圣诞老人村": {"party"},
    # 城市/地标（v0.12 补）：图是该地最有名的地标/代表物
    "开罗": {"pyramid", "desert"}, "罗马": {"pisa", "castle"}, "巴黎": {"eiffel"},
    "伦敦": {"bigben"}, "莫斯科": {"castle", "snowflake"}, "华盛顿": {"libertystatue"},
    "纽约": {"libertystatue"}, "东京": {"torii", "fuji"}, "大阪": {"castle"},
    "开普敦": {"everest", "elephant"}, "里约": {"ball", "party"},
    "巴西": {"ball", "party"}, "泰国": {"elephant"}, "新加坡": {"tower", "palm"},
    "马来西亚": {"palm"}, "印尼": {"palm", "volcano"}, "菲律宾": {"palm", "wave"},
    "越南": {"palm", "wave"}, "印度": {"taj"}, "尼泊尔": {"everest"},
    "斯里兰卡": {"palm", "wave"}, "马尔代夫": {"palm", "wave"},
    "土耳其": {"pyramid", "desert"}, "伊朗": {"desert", "pyramid"},
    "沙特": {"desert", "pyramid"}, "阿联酋": {"tower", "desert"},
    "以色列": {"desert", "flag"}, "摩洛哥": {"desert"}, "埃及": {"pyramid", "desert"},
    "坦桑": {"lion", "elephant"}, "肯尼亚": {"lion"}, "南非": {"crystal", "elephant"},
    "纳米比亚": {"desert"}, "安哥拉": {"river"}, "刚果": {"river"},
    "尼日利亚": {"river"}, "加纳": {"river"}, "马里": {"desert"}, "乍得": {"desert"},
    "挪威": {"everest", "snowflake"}, "瑞典": {"snowflake"}, "芬兰": {"snowflake"},
    "丹麦": {"castle", "book"}, "冰岛": {"volcano", "snowflake"},
    "爱尔兰": {"castle"}, "苏格兰": {"castle"}, "英格兰": {"bigben"},
    "威尔士": {"castle"}, "德国": {"castle"}, "法国": {"eiffel"},
    "西班牙": {"castle"}, "葡萄牙": {"castle"}, "意大利": {"pisa"},
    "希腊": {"flag", "castle"}, "瑞士": {"everest"}, "奥地利": {"everest"},
    "波兰": {"castle"}, "捷克": {"castle"}, "匈牙利": {"castle"},
    "荷兰": {"windmill"}, "比利时": {"castle"}, "卢森堡": {"castle"},
    "美国": {"libertystatue"}, "北美": {"libertystatue"}, "加拿大": {"maple"},
    "墨西哥": {"pyramid", "desert"}, "古巴": {"palm"}, "牙买加": {"palm"},
    "危地马拉": {"pyramid"}, "洪都拉斯": {"pyramid"}, "萨尔瓦多": {"volcano"},
    "尼加拉瓜": {"volcano"}, "哥斯达黎加": {"volcano"}, "巴拿马": {"river"},
    "哥伦比亚": {"ball"}, "委内瑞拉": {"ball"}, "厄瓜多尔": {"everest"},
    "玻利维亚": {"everest"}, "巴拉圭": {"river"}, "乌拉圭": {"ball"},
    "圭亚那": {"river"}, "南极": {"penguin", "snowflake"}, "北极": {"polarbear", "snowflake"},
    # 货币（人民币教具：图标是钱的面值）
    "元": {"m-yuan1", "m-yuan5", "m-yuan10", "coin"}, "角": {"m-jiao1", "m-jiao5", "coin"},
    # 节日/场景词（v0.12 补）
    "春节": {"party", "flag"}, "圣诞": {"party", "snowflake"}, "中秋": {"moon", "cake"},
    "端午": {"wave", "leaf"}, "万圣": {"party"}, "感恩": {"cake", "party"},
    "森林": {"tree", "sprout"}, "树林": {"tree"}, "丛林": {"tree"},
    "海南": {"palm", "tree"}, "上海": {"tower", "wave"}, "北京": {"tiananmen"},
    "锅里": {"cake", "flame"}, "天上": {"moon", "sun"}, "地下": {"rock"},
}

# 英文单词卡：中文只是注解，主体是英文。注解与图标不矛盾即可（不要求图标能画出注解）。
EN_ANNOTATION = re.compile(r"^[A-Za-z][A-Za-z'’ -]*$")


def place_icon_ok(icon, text):
    """地名/国名类的配图是否合理"""
    for zh in PLACE_ICON:
        if zh in (text or ""):
            return icon in PLACE_ICON[zh]
    return None                                        # 不是地名类，交回普通规则


# 汉语例词的「场景搭配」：词本身含本关字（规则 4 已单独保证），
# 图是场景道具而非名词本体——如「上山」配学校（上学的场景）、「山林」配树叶。
# 这类是合理设计，放行；仍要求词里出现过图能画的东西才算错。
SCENE_ICON = {
    "shop":     {"市", "店", "买", "卖", "商贸"},
    "rainbow":  {"云", "彩", "虹", "雨"},
    "book":     {"读", "书", "认", "见", "目", "录", "童话", "故事"},
    "milk":     {"奶", "羊", "牛", "白云", "云"},
    "heart":    {"心", "爱", "花", "园", "人", "姨", "口"},
    "home":     {"家", "屋", "下", "门", "房", "回"},
    "bear":     {"熊", "象", "大"},
    "tree":     {"树", "林", "梧", "桐", "雨", "台"},
    "polarbear": {"北", "极", "羊", "动物"},
    "penguin":  {"南", "极"},
    "windmill": {"荷", "兰", "风"},
    "kangaroo": {"澳", "大利", "亚"},
    "wave":     {"海", "洋", "水", "湖", "河", "池", "湾", "峡", "沟", "西", "杭", "沪", "江", "龙", "舟", "死", "浮"},
    # 数字词（v0.12 补）：数词配数量道具（一=等号1、三=三颗星、七=七天骰子、八=八颗糖）
    "equal":    {"一", "二", "两", "1", "2", "等", "双", "半", "一个", "二个"},
    "moon":     {"晚", "夜", "傍", "昏", "夕", "月"},
    "girl":     {"人", "娃", "见", "目", "光", "跑", "姨", "耳", "朵", "睛"},
    "party":    {"五", "官", "人", "们", "迎", "队", "欢", "排队"},
    # —— v0.12 识字村组词选项的场景搭配（词含本关字，图是助记场景）——
    "egg":      {"雪", "白", "蛋", "鸡"},
    "cup":      {"喝", "水", "茶", "杯"},
    "sprout":   {"田", "里", "种", "植", "苗", "草", "园"},
    "leaf":     {"花", "瓣", "树", "叶", "杨", "种", "植"},
    "castle":   {"高", "楼", "石", "桥", "城", "房"},
    "sunrise":  {"一", "天", "今", "日", "出", "早", "傍"},
    "speaker":  {"开", "口", "声", "音", "新", "闻", "号"},
    "crystal":  {"泉", "水", "珊", "瑚", "冰", "宝"},
    "bulb":     {"红", "灯", "电", "灯"},
    "sparkle":  {"变", "化", "火", "花", "星"},
    "dice":     {"七", "天", "骰", "游"},
    "school":   {"十", "分", "好", "上", "学", "三", "角"},
    "bird":     {"孔", "雀", "小", "鸡", "母", "鸟", "麻"},
    "flag":     {"旗", "路", "奥", "巴", "黎", "敦", "希腊", "国", "司", "南"},
    "lion":     {"非", "洲", "狮", "肯"},
    "everest":  {"西", "藏", "珠", "峰", "山", "峡", "阿", "秘", "鲁"},
    "volcano":  {"岩", "浆", "岛", "冰", "火", "山", "夏"},
    "rocket":   {"飞", "旅", "行", "宇", "宙", "星", "空", "出", "发"},
    "train":    {"旅", "途", "行", "车"},
    "dino":     {"龙", "恐龙"},
    "star":     {"星", "变", "化"},
    "starface": {"星", "宇", "宙", "光"},
    "milkyway": {"宇", "宙", "银河"},
    "astronaut":{"宇", "航", "员", "宙"},
    "sun":      {"日", "天", "阳", "白", "晒"},
    "sunface":  {"日", "天", "阳", "白", "晒"},
    "flame":    {"火", "焰"},
    "fish":     {"鱼", "海", "洋", "游"},
    "frog":     {"蛙", "雨", "林"},
    "panda":    {"猫", "熊", "川", "蓉"},
    "elephant": {"象", "非", "洲", "肯"},
    "duck":     {"鸭", "鸟", "飞"},
    "apple":    {"果", "苹", "红", "甜"},
    "banana":   {"蕉", "黄"},
    "cake":     {"蛋", "糕", "月", "饼", "生", "日", "甜"},
    "candy":    {"糖", "果", "甜"},
    "bread":    {"面", "包", "麦"},
    "gift":     {"礼", "物", "宝", "四", "围"},
    "key":      {"钥", "匙", "锁", "笔"},
    "jar":      {"井", "水", "罐"},
    "hanger":   {"衣", "衫", "衬", "架"},
    "hat":      {"帽", "子", "舞", "会"},
    "shoe":     {"鞋"},
    "clock":    {"钟", "时", "间"},
    "magnet":   {"磁", "铁", "吸"},
    "balloon":  {"气", "球", "飞", "七"},
    "bus":      {"公", "交", "巴", "士"},
    "car":      {"汽", "车"},
    "rabbit":   {"兔", "跳"},
    "fox":      {"狐", "狸", "爸"},
    "paw":      {"爪", "印", "脚", "宝", "手", "动"},
    "flower":   {"花", "园", "瓣", "郁", "春"},
    "china-map":{"中", "国", "地", "图", "家"},
    "world-map":{"世", "界", "地", "图", "语"},
    "tiananmen":{"北", "京", "天", "安", "门"},
    "greatwall":{"长", "城"},
    "river":    {"江", "河", "丝", "路", "恒"},
    "taj":      {"印", "度", "泰", "姬"},
    "pyramid":  {"金", "字", "塔", "埃"},
    "eiffel":   {"法", "国", "埃", "菲"},
    "bigben":   {"英", "国", "伦", "敦", "大", "本"},
    "torii":    {"日", "本", "东", "京", "鸟", "居"},
    "fuji":     {"日", "本", "富", "士"},
    "pisa":     {"意", "利", "比", "萨"},
    "libertystatue": {"美", "国", "纽", "约", "自", "由"},
    "desert":   {"沙", "漠", "墩", "煌", "甘", "撒", "哈", "新"},
    "palm":     {"海", "南", "椰", "棕"},
    "maple":    {"加", "拿", "大", "枫"},
    "snowflake": {"雪", "冰", "冬", "寒", "极"},
    "everest_": set(),
}


def scene_icon_ok(icon, text):
    """场景搭配放行：图是场景道具，词里出现过该场景的关键字即可"""
    keys = SCENE_ICON.get(icon)
    if not keys:
        return None
    return any(k in (text or "") for k in keys)


# 英文单词/短语 → 可表意的图标（动作/形容词/称谓等没有专属图的词，
# 用「最能表意的现有图标」，是合理的教学设计）。
EN_IDEA_ICON = {
    "teacher": {"girl", "school"}, "mom": {"girl"}, "dad": {"fox", "girl"}, "me": {"girl"},
    "hello": {"girl", "party"}, "bye": {"party"}, "run": {"girl", "rabbit"}, "jump": {"rabbit"},
    "swim": {"fish", "wave"}, "fly": {"bird", "duck"}, "sing": {"speaker"}, "speak": {"speaker"},
    "read": {"book"}, "draw": {"chart", "book"}, "write": {"key", "book"},
    "eat": {"apple", "cake"}, "drink": {"cup", "milk"}, "sleep": {"bed"},
    "happy": {"heart", "party"}, "love": {"heart"}, "thank you": {"heart"}, "excited": {"party"},
    "fun": {"party"}, "game": {"dice", "ball"}, "play": {"ball", "block"},
    "big": {"elephant"}, "small": {"duck", "paw", "rabbit"}, "fast": {"rocket", "train"},
    "slow": {"turtle", "train"}, "hot": {"sun", "sunface", "flame"}, "cold": {"snowflake", "ice"},
    "spring": {"flower", "sprout"}, "summer": {"sun", "sunface"}, "autumn": {"maple", "leaf"},
    "fall": {"maple", "leaf"}, "winter": {"snowflake"}, "sand": {"desert", "sand"},
    "wave": {"wave"}, "boat": {"wave"}, "plane": {"balloon", "rocket"},
    "house": {"home"}, "sweet": {"candy", "cake"}, "baby paw": {"paw"}, "foot": {"paw"},
    "eats leaves": {"leaf", "tree", "sprout"}, "leaves": {"leaf", "tree"},
    "hand": {"paw"}, "polar bear": {"polarbear"}, "penguin": {"penguin"},
    "science": {"flask"}, "scientist": {"flask"}, "robot maker": {"robot"}, "robot": {"robot"},
    "t-rex": {"dino"}, "roar": {"dino"}, "long neck": {"dino"},
    "cub": {"bear"}, "duckling": {"duck"}, "speaker": {"speaker"}, "shield": {"shield"},
    "black hole": {"blackhole"}, "comet": {"comet"}, "chart": {"chart"}, "clip": {"clip"},
    "hanger": {"hanger"}, "shirt": {"hanger"}, "coat": {"bear"}, "bag": {"gift"},
    "pen": {"key"}, "peach": {"heart"}, "grape": {"candy"}, "nose": {"crystal"},
    "eye": {"starface"}, "mouth": {"speaker"},
}


def en_idea_icon_ok(icon, text):
    """英文词/中文注解的图标表意是否合理（两边都查：键可能是英文或中文）。
    ⚠️ 一个文本可能命中多个键（"Eats Leaves" 同时含 eat / eats leaves），
    按最长键优先；任一键放行即放行（v0.12 修：此前先命中的短键会误杀）。"""
    raw = text or ""
    t = raw.strip().lower()
    hits = [w for w, _ in EN_IDEA_ICON.items() if w in t or w.capitalize() in raw]
    lat = LAT.search(raw)
    if lat:
        tl = lat.group(0).lower()
        hits += [w for w, _ in EN_IDEA_ICON.items() if w in tl]
    if not hits:
        return None
    hits.sort(key=len, reverse=True)              # 最长键最具体，先看
    for w in hits:
        if icon in EN_IDEA_ICON[w]:
            return True
    return False


def is_english_item(icon, text):
    """纯英文选项/例词：图标名与英文词同根即认（sun↔Sun、starface↔Star）。
    带中文注解的（「Wave 浪花」）不在此列——那要走中文侧的一致性。"""
    t = (text or "").strip()
    if not LAT.fullmatch(t):
        return False
    stem = re.sub(r"(face|rays|map|statue)$", "", icon)
    return stem.lower() in t.lower()


# 颜色词 → 该颜色的代表图标（红苹果/黄香蕉/蓝水/绿叶子/白牛奶/黑…）
COLOR_ICON = {
    "red": {"apple", "flame", "strawberry"}, "yellow": {"banana", "sun", "sunface", "starface"},
    "blue": {"wave", "earth"}, "green": {"leaf", "sprout", "tree"},
    "white": {"milk", "cloud"}, "black": {"castle", "rock"}, "orange": {"carrot", "pumpkin"},
    "purple": {"grape", "candy"}, "pink": {"heart", "flower"}, "brown": {"bear", "wood"},
    "红": {"apple", "flame"}, "黄": {"banana", "sun", "sunface", "starface"},
    "蓝": {"wave", "earth"}, "绿": {"leaf", "sprout", "tree"},
    "白": {"milk", "cloud"}, "黑": {"castle", "rock"},
}


def color_icon_ok(icon, text):
    """颜色词配图：图是这个颜色的代表物即可。
    ⚠️ 只在「文本本身就是颜色词」（Red / Red 红 / 红色）时判定，
    避免把 "Black Hole"（黑洞）、"White House"（白宫）误判成颜色。"""
    t = (text or "").strip()
    if not t:
        return None
    lat = LAT.search(t)
    zh = han(t)
    # 英文主体：去掉中文注解后必须正好是颜色词
    if lat:
        en = re.sub(r"[^A-Za-z]", " ", t).strip().lower()
        for c, icons in COLOR_ICON.items():
            cl = c.lower()
            if re.search(r"(?<![a-z])" + re.escape(cl) + r"(?![a-z])", en):
                return icon in icons
        return None
    # 中文主体：整串就是颜色词（红/红色/黄色…）
    if zh:
        for c, icons in COLOR_ICON.items():
            if len(c) == 1 and zh == c:
                return icon in icons
            if c in zh and len(c) > 1 and zh in (c, c + "色"):
                return icon in icons
        return None
    return None


# 行星/天体：中文名 ↔ 图标名（金星↔venus、火星↔mars…）
BODY_ZH = {"太阳": "sun", "水星": "mercury", "金星": "venus", "地球": "earth", "火星": "mars",
           "木星": "jupiter", "土星": "saturn", "天王星": "uranus", "海王星": "neptune",
           "冥王星": "pluto", "月球": "moon", "月亮": "moon", "彗星": "comet", "流星": "meteor",
           "陨石": "meteorite", "黑洞": "blackhole", "银河": "milkyway", "卫星": "satellite",
           "人造卫星": "satellite", "北斗七星": "bigdipper", "望远镜": "telescope",
           "宇航员": "astronaut", "外星人": "ufo", "火箭": "rocket"}


def body_zh_ok(icon, text):
    """中文天体名 ↔ 图标"""
    for zh, ic in BODY_ZH.items():
        if zh in (text or ""):
            return icon == ic
    return None


def option_verdict(icon, text):
    """选项的图文是否各自成立。
    任一放行表认可即成立；只有所有表都明确拒绝才判错（图与词毫不相干）。"""
    t = (text or "").strip()
    if not t:
        return True
    # 1) 图标名本身出现在词里（rocket↔Rocket、blackhole↔Black Hole、leaf↔Leaves 复数）
    #    英文按词比对：把文本拆成单词、去掉复数后缀，再看有没有等于图标名的词。
    stem = re.sub(r"(face|rays|map|statue)$", "", icon).lower()
    # 文本中的某个词 = 图标名，或 = 图标名 + s/es（复数），或图标名是该词的前缀
    # （leaf↔leaves、apple↔apples、star↔stars、bus↔buses）
    for w in re.findall(r"[a-z]+", t.lower()):
        if w == stem or w in (stem + "s", stem + "es") or w.startswith(stem):
            return True
    if stem in t.lower():
        return True
    # 2) 专属表：任一认可即放行
    for fn in (en_idea_icon_ok, body_zh_ok, place_icon_ok, scene_icon_ok, color_icon_ok):
        if fn(icon, t) is True:
            return True
    # 3) 通用词表：严格名词表 + 宽表，任一命中即放行
    for tbl in (ICON_CN, ICON_ZH):
        for w in tbl.get(icon, ()):
            if w and w in t:
                return True
    return False
    # 3) ICON_CN 里有任一词出现在文本中
    for w in ICON_CN.get(icon, ()):
        if w and w in t:
            return True
    return False


def pair_verdict(icon, text, subject=None, key=None):
    """图 ↔ 词 的总判定。返回 None=不适用（交回严格规则）/ True=合理 / False=不合理"""
    if not icon:
        return None
    # 组词（teach.words / letter.examples）：词含本关字由规则 4 单独保证，
    # 图只是帮孩子把字连到意思的辅助，不要求图标能画出整个词。
    if key in ("words", "examples"):
        return True
    # 拼音学科的例词（「爸爸 bà」「跑步 pǎo」）：同上，声母一致性由规则 2 保证。
    if subject == "pinyin":
        return True
    # 选项（options）：干扰项也要让孩子看懂，图文"各自成立"即可。
    # 只有"图标与词毫不相干"才报错——由调用方在 strict 分支里判定。
    if key == "options":
        return option_verdict(icon, text)
    # 纯英文项：图标名与英文词同根即认（sun↔Sun、starface↔Star）
    if is_english_item(icon, text):
        return True
    # 颜色词：图是该颜色的代表物
    ck = color_icon_ok(icon, text)
    if ck is not None:
        return ck
    # 英文词：图能表意
    ek = en_idea_icon_ok(icon, text)
    if ek is not None:
        return ek
    # 地名/国名：图是代表物
    pk = place_icon_ok(icon, text)
    if pk is not None:
        return pk
    # 场景搭配：词含本关字，图是场景道具
    sk = scene_icon_ok(icon, text)
    if sk is not None:
        return sk
    return None


def audit():
    fails, warns = [], []
    docs = {}
    with open(PREVIEW, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"const CONTENT = (\{.*\});", html)
    if not m:
        sys.exit("preview 里找不到 CONTENT")
    allc = json.loads(m.group(1))
    for s in SUBS:
        docs[s] = allc[s]
    exp = allc["experiments"]
    coll = allc["collection"]

    # —— 规则 1：图 ↔ 词 ——
    unknown = collections.Counter()
    for s in SUBS:
        for lv, st in steps_of(docs[s]):
            for key, o in pairs_of(st):
                if st["kind"] == "listen" and o.get("text") == st.get("prompt"):
                    if o["icon"] not in MORPH_ICON.get(st["prompt"], set()):
                        fails.append(f"象形配图错 [cn/{lv['id']}/{st['id']}]「{st['prompt']}」配了 {o['icon']}")
                    continue
                # 放行表（英文同根/颜色/表意/地名/场景）；None 才走严格规则
                pv = pair_verdict(o["icon"], o["text"], s, key)
                if pv is True:
                    continue
                if pv is False:
                    fails.append(f"图文不符 [{s}/{lv['id']}/{st['id']}] {key}: "
                                 f"「{o['text']}」与 {o['icon']} 讲的不是一回事")
                    continue
                ok = icon_matches(o["icon"], o["text"])
                if ok is None:
                    unknown[o["icon"]] += 1
                elif not ok:
                    fails.append(f"图文不符 [{s}/{lv['id']}/{st['id']}] {key}: "
                                 f"icon={o['icon']} 画的是「{'/'.join(sorted(ICON_CN[o['icon']]))}」，词却写「{o['text']}」")
    for it in exp["experiments"]:
        for o in (it.get("items") or []):
            if o.get("icon"):
                ok = icon_matches(o["icon"], o.get("name", ""))
                if ok is None:
                    unknown[o["icon"]] += 1
                elif not ok:
                    fails.append(f"图文不符 [exp/{it['id']}] icon={o['icon']} vs 「{o.get('name')}」")
    for g in coll["groups"]:
        if g["id"] in ("sticker", "badge"):
            continue        # 贴纸/徽章是比喻名（「识字新星」配书本），不走图文一致
        for it in g["items"]:
            if it.get("icon") and it.get("name"):
                # 收集册条目同样走放行表（英文单词卡的注解/表意图，如「流星 Meteor」配 sparkle）
                if option_verdict(it["icon"], it["name"]):
                    continue
                pv = pair_verdict(it["icon"], it["name"])
                if pv is True:
                    continue
                ok = icon_matches(it["icon"], it["name"])
                if ok is None:
                    unknown[it["icon"]] += 1
                elif not ok:
                    fails.append(f"图文不符 [coll/{g['id']}/{it['id']}] icon={it['icon']} vs 「{it['name']}」")

    # —— 规则 2：拼音例词的声母必须等于本关声母 ——
    for lv, st in steps_of(docs["pinyin"]):
        # 本关教的可能是一组声母（如三拼音节 g-u-a、拼读巩固 b-f-h），
        # 例词命中其中任一个即算对（v0.12 修：此前只比第一个字母，多字母关全误报）。
        # 声母含单字母与双字母（sh/ch/zh）两类，都要纳入比对（v0.12 修：此前
        # "sh" in "bpmfdtnlghk" 为假，双字母声母关的例词全被判不符）
        targets = [t for t in (st.get("letters") or []) if re.fullmatch(r"[bpmfdtnlghk]|sh|ch|zh", t)]
        if st["kind"] == "letter" and targets:
            for o in st.get("examples") or []:
                got = word_initial(o.get("text", ""))
                if got and got not in targets:
                    fails.append(f"声母不符 [pinyin/{lv['id']}/{st['id']}] 本关「{'/'.join(targets)}」，例词「{o['text']}」是 {got}")

    # —— 规则 3：compare 标签必须跟着左右板走 ——
    for lv, st in steps_of(docs["math"]):
        if st["kind"] != "compare":
            continue
        side = {"left": (st["leftIcon"], st["leftCount"]), "right": (st["rightIcon"], st["rightCount"])}
        for o in st["compareOptions"]:
            k, lb = o["key"], o["label"]
            if k == "same":
                continue
            icon, cnt = side[k]
            if "左" in lb or "右" in lb:
                continue                                   # 方位标签：与图标无关
            noun = lb.replace("多", "")
            if noun not in ICON_CN.get(icon, set()) and noun not in "".join(ICON_CN.get(icon, set())):
                fails.append(f"比较标签错位 [math/{lv['id']}/{st['id']}] {k} 边画的是 {icon}，标签写「{lb}」")
        key = "same" if st["leftCount"] == st["rightCount"] else ("left" if st["leftCount"] > st["rightCount"] else "right")
        if st.get("answerKey") != key:
            fails.append(f"比较答案错 [math/{lv['id']}/{st['id']}] {st['leftCount']} vs {st['rightCount']} 应为 {key}，数据写 {st.get('answerKey')}")

    # —— 规则 4：teach 组词必须含本关学的字 ——
    for lv, st in steps_of(docs["cn"]):
        if st["kind"] == "teach":
            for w in st.get("words") or []:
                if st["char"] not in w.get("text", ""):
                    fails.append(f"组词不含本关字 [cn/{lv['id']}] 「{st['char']}」配了「{w['text']}」")

    # —— 规则 5：答案索引/答案值必须落在选项里且与题面一致 ——
    for s in SUBS:
        for lv, st in steps_of(docs[s]):
            opts = st.get("options")
            if opts and isinstance(st.get("answer"), int):
                if not (0 <= st["answer"] < len(opts)):
                    fails.append(f"答案越界 [{s}/{lv['id']}/{st['id']}] answer={st['answer']} len={len(opts)}")
            if s == "cn" and st["kind"] == "listen" and opts and st.get("prompt"):
                hit = [i for i, o in enumerate(opts) if o.get("text") == st["prompt"]]
                if hit and st["answer"] not in hit:
                    fails.append(f"听题答案错 [{s}/{lv['id']}/{st['id']}] 题面「{st['prompt']}」在选项 {hit}，answer 写 {st['answer']}")
            if st["kind"] == "blend":
                want = "".join(st.get("parts") or [])
                got = (opts[st["answer"]]["text"] if opts and isinstance(st.get("answer"), int) and 0 <= st["answer"] < len(opts) else None)
                if got and got != want:
                    fails.append(f"拼读答案错 [pinyin/{lv['id']}/{st['id']}] {'-'.join(st['parts'])} 应拼成 {want}，answer 指向 {got}")
            if st["kind"] == "pattern":
                seq = [art_key(x) for x in (st.get("seq") or [])]
                nxt = expected_next(seq)
                pool = [art_key(o) for o in (opts or [])]
                if nxt and opts and isinstance(st.get("answer"), int) and 0 <= st["answer"] < len(opts):
                    if nxt not in pool:
                        fails.append(f"规律选项缺答案 [{s}/{lv['id']}/{st['id']}] {'/'.join(seq)} → {nxt} 不在选项 {pool}")
                    elif pool[st["answer"]] != nxt:
                        fails.append(f"规律答案错 [{s}/{lv['id']}/{st['id']}] {'/'.join(seq)} → 下一个应是 {nxt}，answer 指向 {pool[st['answer']]}")
                if seq and len(seq) > 1 and expected_next(seq) is None:
                    warns.append(f"序列看不出周期规律 [{s}/{lv['id']}/{st['id']}] {'/'.join(seq)}")
            if st["kind"] in ("count", "dice") and st.get("countOptions"):
                if st["count"] not in st["countOptions"]:
                    fails.append(f"点数答案不在选项 [{s}/{lv['id']}/{st['id']}] count={st['count']} opts={st['countOptions']}")
            if st["kind"] == "split" and st.get("arithOptions"):
                if st["total"] - st["part"] not in st["arithOptions"]:
                    fails.append(f"分解答案不在选项 [math/{lv['id']}/{st['id']}] {st['total']}-{st['part']}={st['total']-st['part']} opts={st['arithOptions']}")
            if st["kind"] == "arith" and st.get("arithOptions"):
                a, b = st["leftCount"], st["rightCount"]
                want = a + b if st["op"] == "+" else a - b
                if want not in st["arithOptions"]:
                    fails.append(f"算式答案不在选项 [math/{lv['id']}/{st['id']}] {a}{st['op']}{b}={want} opts={st['arithOptions']}")

    # —— 规则 6：天体圆盘画的是谁，名字就得是谁 ——
    for s_ in SUBS:
        for lv, st in steps_of(docs[s_]):
            items = list(st.get("options") or []) + list(st.get("rows") or []) \
                + list(st.get("items") or []) + list(st.get("examples") or [])
            if st.get("promptBody"):
                got = BODY_CN.get(st["promptBody"])
                if not got:
                    fails.append(f"未知天体 [astro/{lv['id']}/{st['id']}] promptBody={st['promptBody']}")
            for o in items:
                if not isinstance(o, dict) or not o.get("body"):
                    continue
                want = BODY_CN.get(o["body"])
                if not want:
                    fails.append(f"未知天体 [astro/{lv['id']}/{st['id']}] body={o['body']}")
                elif (o.get("text") or o.get("name")) and want not in (o.get("text") or o.get("name")):
                    # 找规律这类只有图、没有标签，不核对（图本身就是题面）
                    fails.append(f"天体与名字不符 [{s_}/{lv['id']}/{st['id']}] 画的是 {o['body']}（{want}），"
                                 f"标签写「{o.get('text') or o.get('name')}」")

    # —— 规则 7：cmp 数据题——标签里的数字必须跟 value 对得上，且比的是同一个量 ——
    for lv, st in steps_of(docs["astro"]):
        if st["kind"] != "cmp":
            continue
        vals = [r["value"] for r in st["rows"]]
        if len({r["name"] for r in st["rows"]}) != len(st["rows"]):
            fails.append(f"cmp 同名天体重复 [astro/{lv['id']}/{st['id']}]")
        if st["ext"] == "max" and vals[st["answer"]] != max(vals):
            fails.append(f"cmp 答案不是最大值 [astro/{lv['id']}/{st['id']}] {st['question']}")
        if st["ext"] == "min" and vals[st["answer"]] != min(vals):
            fails.append(f"cmp 答案不是最小值 [astro/{lv['id']}/{st['id']}] {st['question']}")
        if st["viz"] == "disc" and any(r["value"] <= 0 for r in st["rows"]):
            fails.append(f"cmp 圆盘用了非正数，画不出来 [astro/{lv['id']}/{st['id']}]")

    # —— 规则 8：同一关的棋盘上，题面一句话不许出现两次（试玩反馈「几乎都是相同的题目重复出现」）——
    for s_ in SUBS:
        for lv in docs[s_]["levels"]:
            seen = collections.Counter(st.get("question", "") for st in lv["steps"]
                                       if st["kind"] not in ("teach", "letter"))
            for qtext, n in seen.items():
                if n > 1:
                    fails.append(f"同关题面重复 [{s_}/{lv['id']}]「{qtext}」出现 {n} 次")

    if unknown:
        warns.append("未登记图标（请在 ICON_CN 补一行）：" + ", ".join(f"{k}×{v}" for k, v in sorted(unknown.items())))
    return fails, warns


if __name__ == "__main__":
    fails, warns = audit()
    for w in warns:
        print(f"[WARN] {w}")
    for f in fails:
        print(f"[FAIL] {f}")
    print("-" * 64)
    print(f"结果: {len(fails)} 项语义不一致, {len(warns)} 条提醒")
    sys.exit(1 if fails else 0)
