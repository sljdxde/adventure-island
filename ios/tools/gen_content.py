#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛关卡内容 + 收集册 JSON 唯一数据源（v0.9 内容大扩充）

v0.9 六路纵扩 + 新增地理学科（全部表驱动，双端共用）：
  · 识字村 15→30 关：14 旧字 + 16 新字，每关「认一认 → 玩一玩 → 写一写(write)」，田字格笔画
  · 拼音谷 12→16 关：四声 / 复韵母 / 前鼻韵母 / 拼读大挑战（字母描红复用 write）
  · 思维镇 15→34 关：大数加减、乘除(muldiv)、扑克(cards)、数独(sudoku)、钟表(clock)、人民币(money)、奇偶、图形
  · 英语王国 12→24 关：12 个主题词场（约 60 词）
  · 天文台 10→16 关：八大行星、月相、银河系、宇航员
  · 环球号 geo（新）12 关：中国章 6 + 世界章 6（mappuzzle）
  · 收集册 7→8 组，新徽章 5 枚
科学岛实验工单 12 不做，保持现状。

v0.10 天文馆大扩充（知识点取材天文童书，不凭空编）：
  · 天文台 19→100 关：10 星区 × 10 关（96 正式 + 3 复习 + 1 Boss）
    星区：白天黑夜 / 地球 / 飞向太空 / 岩质行星 / 巨行星 / 太阳恒星 / 月亮 / 星星世界 / 银河宇宙 / 宇宙探索
    参考书目：《揭秘太空》《第一次发现》《神奇校车·迷失在太阳系》《DK儿童太空百科》
    《国家地理少儿太空百科》《DK神秘宇宙》《给孩子讲宇宙》(李淼)《乔治的宇宙》《万物简史(少儿版)》
  · 新题型 balance（天平比一比：哪边更重）+ sort（拖一拖分类：拖进正确的筐）
    去掉 astro 的 memory 翻牌配对；保留 quiz/pattern/count/listen/letter，题型共 7 种
  · 图鉴星空卡 16→25 张（补齐行星卡与 display 的解锁对应）
"""
import json, os

RES = os.path.join(os.path.dirname(__file__), "..", "AdventureIsland", "Resources")
os.makedirs(RES, exist_ok=True)

def W(name, obj):
    with open(os.path.join(RES, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(name, "OK")

def rot(opts, ans, pos):
    """把正确项挪到 pos 位置"""
    correct = opts[ans]
    rest = [o for i, o in enumerate(opts) if i != ans]
    return rest[:pos] + [correct] + rest[pos:], pos

def dice_step(did, n, opts):
    return {"id": did, "kind": "dice", "count": n, "countOptions": opts,
            "question": "掷骰子：掷出了几点？",
            "hint": "一个一个数红点点", "praise": f"对，是 {n} 点！"}

def memory_step(mid, q, pairs):
    """翻牌配对（扑克牌风）：pairs = [(key, iconA|None, textA|None, iconB|None, textB|None)]"""
    cards = []
    for key, ai, at, bi, bt in pairs:
        c1 = {"key": key}
        c2 = {"key": key}
        if ai: c1["icon"] = ai
        if at: c1["text"] = at
        if bi: c2["icon"] = bi
        if bt: c2["text"] = bt
        cards += [c1, c2]
    return {"id": mid, "kind": "memory", "question": q, "cards": cards}

def quiz_step(qid, q, items, ans, hint, praise):
    """通用三选一 quiz：items = [(icon|None, text|None), ...]"""
    opts = []
    for ic, tx in items:
        o = {}
        if ic: o["icon"] = ic
        if tx: o["text"] = tx
        opts.append(o)
    return {"id": qid, "kind": "quiz", "question": q, "options": opts, "answer": ans,
            "hint": hint, "praise": praise}

def tapall_step(tid, q, options, hint, praise="全点对啦，小天文学家！"):
    """点点看：options=[(icon, text|None, correct)]，点中全部正确项即过"""
    return {"id": tid, "kind": "tapall", "question": q,
            "options": [{"icon": ic, **({"text": t} if t else {}), "correct": c} for ic, t, c in options],
            "hint": hint, "praise": praise}

def match_step(mid, q, pairs, praise="全部连对，真棒！"):
    """连一连：pairs=[(leftIcon, leftText, rightText)]，右列打乱由渲染层处理"""
    return {"id": mid, "kind": "match", "question": q,
            "pairs": [{"left": {"icon": li, "text": lt}, "right": {"text": rt}} for li, lt, rt in pairs],
            "praise": praise}

def lineup_step(lid, q, items, praise="排好啦，顺序全对！"):
    """排排队：items 按正确顺序=[(icon, text)]，打乱由渲染层处理"""
    return {"id": lid, "kind": "lineup", "question": q,
            "lineup": [{"id": f"li{i}", "icon": ic, "text": t} for i, (ic, t) in enumerate(items)],
            "praise": praise}

def sequence_step(sid, q, seq, praise="🚀 发射！", hint="按顺序一个一个点"):
    """倒计时点火：按 seq 顺序逐个点 token"""
    return {"id": sid, "kind": "sequence", "question": q, "seq": seq,
            "hint": hint, "praise": praise}

def spotlight_step(sid, q, target, decoys, praise="找到啦，眼睛真亮！"):
    """望远镜找星：拖动镜筒在夜空里找到 target"""
    return {"id": sid, "kind": "spotlight", "question": q,
            "targetIcon": target, "decoys": decoys, "praise": praise}

def balance_step(bid, q, left, right, ans, hint, praise="天平答对啦，小天文学家！"):
    li, lt = left
    ri, rt = right
    return {"id": bid, "kind": "balance", "question": q,
            "left": {"icon": li, "text": lt}, "right": {"icon": ri, "text": rt},
            "answerKey": ans, "hint": hint, "praise": praise}

def shadow_step(sid, q, shadow, options, ans, hint, praise="猜对啦！"):
    """剪影猜猜：只给黑色剪影，三选一"""
    return {"id": sid, "kind": "shadow", "question": q, "shadow": shadow,
            "options": [{"icon": ic, **({"text": t} if t else {})} for ic, t in options],
            "answer": ans, "hint": hint, "praise": praise}

# ================= 识字村 30 字（teach + 5 题 + write 写字关） =================
# (字, 拼音, 象形源图标 morphFrom, 词卡[(icon,text)], 找一找(target,d1,d2), 找一找答案位)
CN = [
    ("日","rì","sunface",[("sunrise","日出"),("cake","生日"),("calendar","日子")],("sunrise","moon","cake"),0),
    ("月","yuè","moon",[("moon","月亮"),("moon","月牙"),("cake","月饼")],("moon","sun","star"),2),
    ("水","shuǐ","wave",[("wave","海水"),("crystal","泉水"),("leaf","水珠")],("wave","sun","crystal"),0),
    ("山","shān","volcano",[("school","上山"),("leaf","山林")],("volcano","rocket","home"),1),
    ("木","mù","sprout",[("leaf","树木"),("flower","花木")],("sprout","flower","rock"),0),
    ("人","rén","girl",[("heart","大人"),("party","人们")],("girl","duck","sun"),2),
    ("口","kǒu","speaker",[("speaker","开口"),("heart","口水")],("speaker","clock","moon"),0),
    ("天","tiān","sunrays",[("sun","天空"),("sunrise","今天")],("sun","banana","rocket"),1),
    ("田","tián","calendar",[("sprout","田里"),("flower","水田")],("calendar","gift","star"),2),
    ("石","shí","rock",[("rock","石头"),("castle","石桥")],("rock","balloon","leaf"),0),
    ("火","huǒ","flame",[("flame","火焰"),("volcano","火山"),("starface","火花")],("flame","crystal","key"),0),
    ("花","huā","flower",[("flower","花朵"),("leaf","花瓣"),("heart","花园")],("flower","star","train"),1),
    ("草","cǎo","leaf",[("leaf","小草"),("sprout","草地")],("leaf","cake","duck"),1),
    ("鸟","niǎo","duck",[("duck","小鸟"),("leaf","鸟窝")],("duck","apple","rocket"),0),
    # —— 新增 16 字（一二三四五六七八九十大 小 上 下 星 手）——
    ("一","yī","equal",[("equal","一个"),("sunrise","一天")],("equal","sun","moon"),0),
    ("二","èr","equal",[("moon","二月"),("calendar","第二")],("equal","star","sun"),1),
    ("三","sān","equal",[("star","三个"),("school","三角")],("equal","moon","flower"),2),
    ("四","sì","calendar",[("calendar","四季"),("gift","四方")],("calendar","equal","sunrise"),0),
    ("五","wǔ","star",[("star","五个"),("party","五官")],("star","equal","moon"),1),
    ("六","liù","sparkle",[("sparkle","六个"),("gift","六一小礼物")],("sparkle","star","equal"),2),
    ("七","qī","dice",[("dice","七天"),("balloon","七彩色")],("dice","star","balloon"),0),
    ("八","bā","candy",[("candy","八个"),("flower","八哥花")],("candy","balloon","star"),1),
    ("九","jiǔ","balloon",[("balloon","九月"),("star","九颗星")],("balloon","candy","moon"),2),
    ("十","shí","star",[("star","十个"),("school","十分好")],("star","equal","gift"),0),
    ("大","dà","girl",[("girl","大人"),("elephant" if False else "bear","大象")],("girl","bear","paw"),1),
    ("小","xiǎo","paw",[("paw","小手"),("rabbit","小兔子")],("paw","bear","girl"),2),
    ("上","shàng","sunrise",[("sunrise","上学"),("school","上面")],("sunrise","wave","rocket"),0),
    ("下","xià","wave",[("wave","下雨"),("home","下面")],("wave","sunrise","moon"),1),
    ("星","xīng","starface",[("starface","星星"),("rocket","星空")],("starface","moon","comet"),2),
    ("手","shǒu","paw",[("paw","小手"),("heart","手心")],("paw","girl","wave"),0),
    # —— 部编一年级常用字再补 16 字（v0.11，50 关扩容；图标取自现有资产）——
    ("目","mù","calendar",[("girl","目光"),("book","目录")],("girl","duck","calendar"),0),
    ("耳","ěr","speaker",[("speaker","耳机"),("girl","耳朵")],("speaker","calendar","star"),0),
    ("足","zú","ball",[("ball","足球"),("paw","手足")],("ball","paw","train"),1),
    ("云","yún","milk",[("milk","白云"),("rainbow","彩云")],("milk","sun","moon"),2),
    ("雨","yǔ","wave",[("wave","下雨"),("wave","雨水")],("wave","milk","crystal"),0),
    ("风","fēng","windmill",[("windmill","风车"),("windmill","风车转")],("windmill","leaf","flag"),1),
    ("禾","hé","sprout",[("sprout","禾苗"),("sprout","禾田")],("sprout","flower","leaf"),0),
    ("虫","chóng","bee",[("bee","虫子"),("bee","虫虫")],("bee","duck","fish"),2),
    ("贝","bèi","coin",[("coin","宝贝"),("gift","宝贝蛋")],("coin","rock","gift"),0),
    ("见","jiàn","girl",[("girl","看见"),("book","再见")],("girl","book","star"),1),
    ("白","bái","egg",[("egg","雪白"),("milk","白牛奶")],("egg","milk","star"),2),
    ("牛","niú","cow",[("cow","小牛"),("milk","牛奶")],("cow","milk","bear"),1),
    ("羊","yáng","polarbear",[("polarbear","小羊"),("milk","羊毛")],("polarbear","milk","duck"),2),
    ("果","guǒ","apple",[("apple","果子"),("leaf","果树")],("apple","banana","leaf"),0),
    ("车","chē","car",[("car","汽车"),("train","火车")],("car","train","bus"),1),
    ("糖","táng","candy",[("candy","糖果"),("sugar","糖水")],("candy","cake","gift"),2),
    # —— v0.12 部编二年级识字表 +50 字（100 关扩容；图标取自现有资产）——
    ("塘","táng","wave",[("wave","池塘"),("wave","水塘")],("wave","milk","sprout"),0),
    ("迎","yíng","party",[("party","欢迎"),("flag","迎面")],("party","flag","book"),1),
    ("姨","yí","girl",[("girl","阿姨"),("heart","姨妈")],("girl","home","party"),0),
    ("变","biàn","sparkle",[("sparkle","变化"),("milk","白云变")],("sparkle","egg","milk"),2),
    ("极","jí","polarbear",[("polarbear","北极"),("magnet","南北极")],("polarbear","star","magnet"),1),
    ("傍","bàng","sunrise",[("sunrise","傍晚"),("moon","傍晚上灯")],("sunrise","moon","star"),1),
    ("海","hǎi","wave",[("wave","大海"),("fish","海边")],("wave","fish","milk"),2),
    ("洋","yáng","wave",[("wave","海洋"),("fish","大洋")],("wave","fish","sun"),0),
    ("植","zhí","sprout",[("sprout","植物"),("leaf","种植")],("sprout","flower","leaf"),1),
    ("旅","lǚ","rocket",[("rocket","旅行"),("train","旅途")],("rocket","train","bus"),2),
    ("识","shí","book",[("book","认识"),("girl","识字")],("book","girl","star"),0),
    ("园","yuán","flower",[("flower","花园"),("sprout","园子")],("flower","sprout","home"),1),
    ("队","duì","party",[("party","排队"),("flag","队伍")],("party","flag","train"),0),
    ("旗","qí","flag",[("flag","红旗"),("flag","升旗")],("flag","party","book"),1),
    ("号","hào","speaker",[("speaker","吹号"),("clock","号码")],("speaker","clock","flag"),2),
    ("杨","yáng","tree",[("tree","杨树"),("leaf","白杨")],("tree","maple","leaf"),0),
    ("桐","tóng","tree",[("tree","梧桐"),("leaf","桐叶")],("tree","leaf","maple"),1),
    ("枫","fēng","maple",[("maple","枫叶"),("tree","枫树")],("maple","tree","flower"),2),
    ("松","sōng","tree",[("tree","松树"),("sprout","松果")],("tree","sprout","maple"),0),
    ("柏","bǎi","tree",[("tree","柏树"),("tree","松柏")],("tree","maple","leaf"),1),
    ("桂","guì","flower",[("flower","桂花"),("tree","桂树")],("flower","tree","sparkle"),2),
    ("雀","què","bird",[("bird","麻雀"),("bird","孔雀")],("bird","duck","bee"),0),
    ("鹰","yīng","bird",[("bird","老鹰"),("bird","雄鹰")],("bird","star","flag"),1),
    ("季","jì","calendar",[("calendar","四季"),("flower","季节")],("calendar","flower","sun"),2),
    ("农","nóng","sprout",[("sprout","农民"),("sprout","农田")],("sprout","apple","home"),0),
    ("麦","mài","sprout",[("sprout","麦苗"),("bread","麦子")],("sprout","bread","leaf"),1),
    ("象","xiàng","elephant",[("elephant","大象"),("bear","印象")],("elephant","bear","duck"),2),
    ("楼","lóu","castle",[("castle","高楼"),("castle","楼房")],("castle","home","shop"),0),
    ("闻","wén","speaker",[("speaker","新闻"),("girl","闻名")],("speaker","book","star"),1),
    ("峰","fēng","everest",[("everest","山峰"),("everest","高峰")],("everest","tree","sun"),2),
    ("潭","tán","wave",[("wave","日月潭"),("wave","水潭")],("wave","moon","fish"),0),
    ("城","chéng","castle",[("castle","城市"),("greatwall","长城")],("castle","greatwall","shop"),1),
    ("市","shì","shop",[("shop","市场"),("shop","城市")],("shop","home","school"),2),
    ("井","jǐng","jar",[("jar","水井"),("jar","井水")],("jar","cup","rock"),0),
    ("观","guān","telescope",[("telescope","观星"),("telescope","观看")],("telescope","star","book"),1),
    ("喝","hē","cup",[("cup","喝水"),("milk","喝奶")],("cup","milk","jar"),2),
    ("灯","dēng","bulb",[("bulb","电灯"),("bulb","红灯")],("bulb","star","moon"),0),
    ("娃","wá","girl",[("girl","娃娃"),("frog","蛙娃")],("girl","frog","party"),1),
    ("蛙","wā","frog",[("frog","青蛙"),("frog","蛙声")],("frog","duck","bee"),2),
    ("猫","māo","cat",[("cat","小猫"),("cat","熊猫")],("cat","dog","duck"),0),
    ("狗","gǒu","dog",[("dog","小狗"),("dog","看家狗")],("dog","cat","bear"),1),
    ("猪","zhū","pig",[("pig","小猪"),("pig","肥猪")],("pig","cow","duck"),2),
    ("鸡","jī","bird",[("bird","母鸡"),("bird","小鸡")],("bird","duck","cat"),0),
    ("熊","xióng","bear",[("bear","小狗熊"),("polarbear","白熊")],("bear","polarbear","cat"),1),
    ("狮","shī","lion",[("lion","狮子"),("lion","雄狮")],("lion","tiger","bear"),2),
    ("猴","hóu","monkey",[("monkey","猴子"),("monkey","猴山")],("monkey","bear","dog"),0),
    ("晴","qíng","sun",[("sun","晴天"),("sun","雨过天晴")],("sun","moon","star"),1),
    ("晚","wǎn","moon",[("moon","晚上"),("moon","晚霞")],("moon","sun","star"),2),
    ("雪","xuě","snowflake",[("snowflake","下雪"),("snowflake","雪人")],("snowflake","ice","milk"),0),
    ("冰","bīng","ice",[("ice","结冰"),("ice","冰淇淋")],("ice","snowflake","crystal"),1),
]

WORD_POOL = [(ic, tx, ch) for (ch, py, mf, words, lo, la) in CN for (ic, tx) in words]

# 田字格 100 坐标标准笔顺（每笔一条 d + start）。viewBox 0 0 100 100。
def S(d):
    """由 path d 首段推导起点（M x y）"""
    import re
    m = re.match(r"M\s*([\d.]+)[ ,]+([\d.]+)", d)
    return {"d": d, "start": {"x": float(m.group(1)), "y": float(m.group(2))}}

STROKES = {
 "一": ["M22 50 L78 50"],
 "二": ["M28 38 L72 38", "M22 62 L78 62"],
 "三": ["M30 32 L70 32", "M26 50 L74 50", "M22 68 L78 68"],
 "十": ["M24 50 L76 50", "M50 24 L50 76"],
 "人": ["M50 26 Q40 52 30 74", "M50 40 Q60 58 72 74"],
 "大": ["M26 40 L74 40", "M50 24 Q44 50 34 76", "M50 46 Q60 62 72 76"],
 "小": ["M50 26 L50 66 Q48 72 42 70", "M40 44 Q32 52 30 60", "M60 44 Q68 52 70 60"],
 "上": ["M50 22 L50 38", "M34 38 L66 38", "M24 62 L76 62"],
 "下": ["M26 40 L74 40", "M50 26 L50 72", "M62 48 Q70 52 72 60"],
 "日": ["M34 26 L34 74", "M34 26 L66 26 L66 74", "M34 50 L66 50", "M34 74 L66 74"],
 "月": ["M40 26 Q38 50 34 74", "M44 26 L66 26 L66 70 Q66 76 60 76", "M44 46 L62 46", "M44 62 L62 62"],
 "水": ["M50 26 L50 70 Q50 76 44 74", "M44 36 Q38 44 32 48", "M42 50 Q38 60 34 68", "M58 40 Q64 54 70 66"],
 "山": ["M50 30 L50 72", "M32 38 L32 72 L68 72", "M68 38 L68 72"],
 "木": ["M28 38 L72 38", "M50 30 L50 74", "M50 46 Q42 58 34 70", "M50 46 Q58 58 66 70"],
 "口": ["M36 32 L36 70", "M36 32 L64 32 L64 70", "M36 70 L64 70"],
 "天": ["M30 32 L70 32", "M34 46 L66 46", "M50 46 Q42 60 34 74", "M50 52 Q58 64 66 74"],
 "田": ["M32 30 L32 72", "M32 30 L68 30 L68 72", "M32 51 L68 51", "M50 30 L50 72", "M32 72 L68 72"],
 "石": ["M30 30 L66 30", "M40 30 Q36 50 30 70", "M52 38 L52 70", "M52 38 L68 38 L68 62", "M52 62 L68 62"],
 "火": ["M42 32 Q40 38 38 42", "M58 28 Q50 46 40 66", "M50 40 Q44 54 38 68", "M54 46 Q60 58 66 70"],
 "花": ["M28 30 L72 30", "M38 30 L38 44", "M62 30 L62 44", "M50 44 Q42 58 34 72", "M50 44 L50 66 Q50 74 58 74"],
 "草": ["M28 26 L72 26", "M36 26 L36 42", "M64 26 L64 42", "M42 44 L42 74", "M42 52 L62 52", "M52 44 L52 74"],
 "鸟": ["M46 24 Q42 30 38 34", "M42 32 L64 32 L64 58 Q64 66 56 66", "M46 44 Q48 48 50 50", "M46 56 L58 56 L58 64 Q58 70 52 70", "M44 66 L62 66"],
 "四": ["M28 26 L28 74", "M28 26 L66 26 L66 70", "M38 40 Q36 52 34 64", "M52 40 L52 64 Q52 70 58 70"],
 "五": ["M28 32 L72 32", "M40 32 L40 46", "M40 46 L66 46 L66 66", "M34 66 L66 66"],
 "六": ["M50 24 Q48 30 46 34", "M32 42 L58 42 Q60 46 54 52", "M52 54 Q56 62 54 70"],
 "七": ["M28 40 L66 40", "M50 40 L50 66 Q50 74 58 74"],
 "八": ["M46 32 Q40 50 32 68", "M54 32 Q60 50 68 68"],
 "九": ["M42 28 Q40 46 34 66", "M54 28 L66 28 L66 56 Q66 70 54 70"],
 "星": ["M36 24 L36 40", "M36 24 L64 24 L64 40", "M36 32 L64 32", "M40 46 Q36 54 32 60", "M34 58 L66 58", "M38 66 L62 66", "M50 58 L50 74"],
 "手": ["M42 26 Q40 34 38 40", "M34 46 L66 46", "M38 58 L62 58", "M50 28 L50 72 Q50 78 44 76"],
 # —— v0.11 新增 16 字笔顺（简化教学版）——
 "目": ["M34 24 L34 74", "M34 24 L66 24 L66 74", "M34 42 L66 42", "M34 58 L66 58", "M34 74 L66 74"],
 "耳": ["M30 30 L30 66", "M30 30 L70 30 L70 40", "M30 48 L64 48", "M30 66 L70 66", "M70 46 L70 66"],
 "足": ["M36 26 L60 26 L60 46 L36 46", "M48 46 L48 58", "M32 62 L48 74", "M48 60 Q60 66 68 72"],
 "云": ["M24 34 Q40 24 58 32", "M28 48 L60 48", "M46 56 Q40 66 32 72", "M46 56 Q52 66 58 70"],
 "雨": ["M30 22 L70 22", "M50 22 L50 32", "M24 40 Q50 32 76 40", "M32 48 L32 58", "M50 48 L50 58", "M40 60 L36 72", "M60 60 L56 72"],
 "风": ["M44 20 Q28 42 30 60 Q31 70 40 74", "M44 20 Q62 34 62 52", "M42 40 Q50 46 58 44", "M40 48 Q48 58 56 56"],
 "禾": ["M50 20 L50 44", "M32 34 L68 34", "M50 44 Q42 60 32 70", "M50 44 Q58 60 70 68", "M34 70 Q48 66 62 70"],
 "虫": ["M40 32 L58 32 L58 54 L40 54", "M49 18 L49 32", "M30 44 L40 44", "M49 54 L44 70", "M49 54 Q58 62 64 66"],
 "贝": ["M36 24 L36 66", "M36 24 L62 24 L62 66", "M62 66 Q46 64 30 74", "M50 66 Q56 70 62 74"],
 "见": ["M34 24 L34 62", "M34 24 L62 24 L62 62", "M62 62 Q48 64 38 74", "M52 54 Q60 66 70 70"],
 "白": ["M32 26 L58 26", "M45 18 L45 26", "M32 40 L32 74", "M32 40 L66 40 L66 74", "M32 74 L66 74"],
 "牛": ["M32 34 L68 34", "M50 20 L50 72", "M50 48 Q40 62 28 70", "M50 48 Q58 62 72 68"],
 "羊": ["M30 28 L70 28", "M32 42 L68 42", "M50 16 L50 72", "M50 48 Q40 60 30 68", "M50 48 Q60 60 68 68"],
 "果": ["M26 30 L74 30", "M50 14 L50 60", "M50 44 Q38 58 26 66", "M50 44 Q62 58 74 66", "M34 74 L66 74"],
 "车": ["M30 28 L70 28", "M50 18 L50 56", "M26 44 L50 56", "M50 56 L36 74", "M36 74 L64 74"],
 "糖": ["M30 24 L30 72", "M44 30 L58 30", "M52 30 L52 46", "M62 58 L74 58", "M56 54 L62 74", "M40 58 L52 58"],
 # —— v0.12 二年级 50 字笔顺（教学简化版）——
 "塘": ["M28 70 L72 70", "M50 24 L50 70", "M34 24 L66 24", "M38 42 Q50 36 62 42", "M36 54 L64 54", "M36 62 L64 62"],
 "迎": ["M40 24 L40 60", "M40 36 L58 36", "M58 30 L58 44", "M30 74 Q44 62 62 68", "M62 68 L74 58"],
 "姨": ["M40 24 Q32 44 28 72", "M40 38 L54 46", "M28 46 Q40 54 52 58", "M58 26 L72 26", "M58 40 L72 40", "M65 26 L65 40", "M58 56 L72 72"],
 "变": ["M50 16 L50 30", "M32 34 L68 34", "M30 48 Q50 56 70 48", "M42 60 L32 74", "M58 60 L68 74"],
 "极": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M62 28 Q56 50 62 66", "M62 44 Q72 54 68 70"],
 "片": ["M34 18 L34 74", "M46 28 L46 74", "M46 28 L66 40", "M46 48 Q60 60 64 74"],
 "傍": ["M32 24 Q26 48 24 72", "M32 38 L44 46", "M56 24 L72 24", "M50 40 Q64 34 74 42", "M50 54 L72 54", "M54 66 L68 66"],
 "海": ["M30 28 Q26 36 30 42", "M42 26 Q38 34 42 40", "M56 28 L56 70", "M40 46 Q58 38 68 48", "M40 60 Q58 52 68 62"],
 "洋": ["M30 28 Q26 36 30 42", "M42 26 Q38 34 42 40", "M32 40 L70 40", "M36 54 L64 54", "M50 28 L50 72", "M50 54 Q42 64 34 70", "M50 54 Q58 64 66 70"],
 "植": ["M30 26 L30 72", "M30 42 L46 42", "M54 26 L54 66", "M54 26 L72 26 L72 66", "M54 46 L72 46", "M54 66 L72 66", "M60 74 L66 60"],
 "旅": ["M32 24 Q26 48 24 72", "M32 38 L44 46", "M56 22 L56 40", "M48 40 L72 40", "M48 40 Q44 62 36 72", "M56 52 L72 66", "M60 44 L70 58"],
 "识": ["M30 24 Q26 34 30 40", "M38 30 L48 30", "M44 24 L44 36", "M56 26 L56 60", "M56 26 L70 26 L70 60", "M56 60 L42 74", "M62 62 L72 74"],
 "园": ["M26 22 L74 22", "M74 22 L74 76", "M74 76 L26 76", "M26 76 L26 22", "M42 36 L42 58", "M42 36 Q54 30 60 38", "M60 44 L60 58", "M46 48 L62 48"],
 "群": ["M34 24 Q30 40 30 56", "M34 38 L50 38", "M30 56 L54 56", "M42 30 L42 56", "M62 24 L78 24", "M62 36 L78 36", "M70 24 L70 60", "M62 48 Q70 42 78 48", "M58 72 Q70 66 80 72"],
 "队": ["M34 22 L34 72", "M34 44 L46 54", "M46 30 Q56 50 66 70", "M56 34 Q60 44 68 48"],
 "旗": ["M34 22 L34 74", "M28 34 L40 34", "M46 26 L70 26 L70 56", "M46 56 L70 56", "M58 26 L58 56", "M46 42 L70 42"],
 "号": ["M36 26 L62 26 L62 48 L36 48", "M36 38 L62 38", "M62 56 Q62 70 46 74", "M62 56 L74 46"],
 "杨": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M60 24 L60 66", "M60 30 L74 38", "M60 44 L74 52", "M60 58 L72 66"],
 "桐": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M60 24 Q54 44 60 66", "M60 30 L74 40", "M60 44 L74 54", "M60 56 L72 64"],
 "枫": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M60 24 Q52 44 60 66", "M60 32 L74 42", "M60 46 L72 58", "M56 52 Q62 58 70 56"],
 "松": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M60 26 L60 70", "M52 40 L68 40", "M50 54 L70 54", "M60 40 L60 54"],
 "柏": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M60 24 L60 70", "M52 34 L68 34", "M52 48 L68 48", "M52 60 L68 60"],
 "桂": ["M30 26 L30 72", "M30 42 L48 42", "M48 26 Q44 50 36 66", "M58 22 L58 40", "M58 40 L74 40", "M74 22 Q78 32 74 40", "M58 52 L74 52", "M58 52 Q64 64 74 70", "M58 64 L72 72"],
 "雀": ["M36 24 L36 46", "M36 24 L58 24 L58 46", "M36 36 L58 36", "M26 54 L68 54", "M68 54 L48 40", "M26 54 L44 74", "M68 54 L56 74"],
 "鹰": ["M32 22 L64 22", "M48 10 L48 22", "M36 28 L60 28", "M40 34 L56 50", "M56 34 L40 50", "M30 56 L66 56", "M36 62 L44 74", "M60 62 L52 74"],
 "季": ["M50 20 L50 40", "M34 30 L66 30", "M50 40 Q42 50 34 56", "M50 40 Q58 50 66 56", "M36 60 L62 60", "M36 60 Q40 72 52 74", "M62 60 Q60 70 52 74"],
 "农": ["M42 22 Q36 40 30 52", "M30 40 L52 40", "M52 30 Q62 40 70 44", "M36 54 L66 54", "M42 62 L58 62", "M50 54 L50 74", "M36 72 L64 72"],
 "麦": ["M50 16 L50 38", "M32 26 L68 26", "M28 40 Q50 32 72 40", "M50 40 Q40 58 28 68", "M50 40 Q60 58 72 68", "M30 72 Q50 66 70 72"],
 "象": ["M50 20 Q30 28 28 48 Q26 66 38 72", "M50 20 Q68 26 70 46", "M70 46 L72 66", "M38 72 L66 72", "M44 40 Q48 44 44 48", "M28 52 Q20 56 18 62", "M72 52 Q80 56 82 62"],
 "楼": ["M30 24 L30 74", "M30 24 L44 24 L44 74", "M30 48 L44 48", "M30 74 L44 74", "M52 26 L72 26 L72 72", "M52 44 L72 44", "M60 56 L66 56", "M52 72 L72 72"],
 "闻": ["M30 22 L70 22 L70 76", "M30 22 L30 76", "M30 76 L70 76", "M34 32 L66 32", "M42 42 L58 42", "M42 56 L58 56", "M48 32 L48 66"],
 "峰": ["M26 60 L42 24 L54 46", "M42 24 L42 70", "M28 70 L58 70", "M66 28 L66 70", "M66 34 Q74 40 78 34", "M60 48 Q70 44 78 50", "M66 60 Q74 58 80 64"],
 "潭": ["M30 28 Q26 36 30 42", "M42 26 Q38 34 42 40", "M54 28 L54 70", "M40 44 L68 44", "M40 58 L68 58", "M42 70 L66 70", "M54 44 Q60 50 54 58"],
 "城": ["M28 24 L28 74", "M28 38 L44 38", "M28 60 L44 60", "M52 26 Q46 48 50 66", "M52 30 Q66 26 74 32", "M58 44 Q66 42 74 46", "M54 58 L70 58"],
 "市": ["M26 26 L74 26", "M50 14 L50 26", "M32 40 L68 40", "M50 40 L50 74", "M32 58 L50 74", "M50 58 L68 58"],
 "井": ["M28 32 L72 32", "M28 52 L72 52", "M40 20 Q36 48 30 74", "M62 20 Q66 48 70 74"],
 "观": ["M32 26 Q26 40 24 54", "M32 38 L46 46", "M50 30 L62 42", "M62 30 L50 42", "M36 54 L36 68", "M36 54 L64 54", "M64 42 L64 74", "M38 74 L62 74"],
 "喝": ["M34 24 L34 66", "M34 40 L48 40", "M34 66 L48 66", "M58 24 Q52 40 58 50", "M66 22 Q62 40 68 50", "M50 58 L72 58", "M52 70 L70 70", "M62 58 L62 70"],
 "灯": ["M42 24 Q34 44 28 66", "M42 36 L56 44", "M28 46 Q38 54 50 58", "M62 40 L62 70", "M50 58 L74 58"],
 "娃": ["M40 24 Q32 44 28 72", "M40 38 L54 46", "M28 46 Q40 54 52 58", "M60 22 L60 44", "M60 22 L76 22 L76 44", "M76 44 Q60 42 52 56", "M66 50 Q72 54 78 54"],
 "蛙": ["M40 32 L58 32 L58 54 L40 54", "M49 18 L49 32", "M30 44 L40 44", "M49 54 L44 70", "M49 54 Q58 62 64 66", "M60 22 L60 44", "M60 22 L76 22 L76 44", "M76 44 Q60 42 52 56"],
 "猫": ["M34 24 Q28 46 24 70", "M34 38 L46 46", "M24 46 Q32 54 42 58", "M60 22 L60 46", "M60 22 L76 22 L76 46", "M76 46 Q62 42 52 58", "M58 52 Q64 46 70 52", "M62 58 L62 70", "M54 70 L72 70"],
 "狗": ["M34 24 Q28 46 24 70", "M34 38 L46 46", "M24 46 Q32 54 42 58", "M60 24 L60 44", "M60 24 L74 24 Q80 34 74 44", "M74 44 Q60 42 54 58", "M56 66 L72 66"],
 "猪": ["M34 24 Q28 46 24 70", "M34 38 L46 46", "M24 46 Q32 54 42 58", "M58 22 L58 44", "M58 22 L76 22 L76 44", "M58 34 L76 34", "M76 44 Q62 42 54 56", "M52 68 L74 68"],
 "鸡": ["M32 26 Q28 40 24 50", "M32 38 L44 46", "M58 22 Q52 40 58 54", "M58 54 L44 54 Q56 60 66 54", "M66 54 L66 22", "M44 66 L72 66", "M66 40 L58 40"],
 "熊": ["M32 22 L54 22", "M42 22 L42 34", "M28 34 L58 34 L58 58", "M28 58 Q43 52 58 58", "M64 26 Q60 46 66 62", "M74 30 L74 72", "M60 72 L86 72", "M50 66 L54 78"],
 "狮": ["M34 24 Q28 46 24 70", "M34 38 L46 46", "M24 46 Q32 54 42 58", "M58 22 L58 46", "M58 22 L74 22", "M74 22 L74 46", "M58 34 L74 34", "M58 46 Q62 42 66 46", "M52 66 L76 66"],
 "猴": ["M34 24 Q28 46 24 70", "M34 38 L46 46", "M24 46 Q32 54 42 58", "M58 22 Q52 36 58 46", "M58 28 L74 28 L74 60", "M58 44 L74 44", "M64 52 Q60 62 52 70", "M74 52 Q70 64 62 72"],
 "晴": ["M34 22 L34 68", "M34 22 L58 22 L58 44", "M34 40 L58 40", "M34 68 L58 68", "M70 26 Q64 44 70 60", "M52 54 Q64 48 76 56", "M56 66 L76 66"],
 "晚": ["M34 22 L34 68", "M34 22 L58 22 L58 44", "M34 40 L58 40", "M34 68 L58 68", "M70 22 Q62 46 70 68", "M70 40 Q78 46 84 40", "M64 52 Q76 52 82 58"],
 "雪": ["M28 22 L72 22", "M50 22 L50 34", "M22 40 Q50 30 78 40", "M32 48 L32 58", "M48 48 L48 58", "M64 48 L64 58", "M30 62 L42 70", "M58 70 L70 62", "M38 72 L50 74"],
 "冰": ["M30 20 L34 46", "M26 34 L38 32", "M56 24 Q48 46 56 72", "M44 52 Q56 62 68 52", "M68 40 Q64 50 68 58"],
}

def other_words(ch, k, start):
    cands = [w for w in WORD_POOL if w[2] != ch]
    out, i = [], start
    while len(out) < k and i < start + len(cands) * 2:
        w = cands[i % len(cands)]
        if all(w[1] != o[1] for o in out):
            out.append(w)
        i += 1
    return out

def cn_listen_pic(i, ch, lo, lans):
    tgt, d1, d2 = lo
    opts = [{"icon": tgt, "text": ch}, {"icon": d1}, {"icon": d2}]
    if lans != 0:
        opts[0], opts[lans] = opts[lans], opts[0]
    return {"id": f"cn-{i}-l", "kind": "listen", "prompt": ch, "speakText": ch,
            "question": f"找一找：哪张图片是「{ch}」？",
            "options": opts, "answer": lans,
            "hint": f"想想刚才的图片：「{ch}」", "praise": f"眼睛真亮！{ch} 找对啦！"}

def cn_listen_pic_to_char(i, ch, mfrom):
    others = [c[0] for c in CN if c[0] != ch]
    d1 = others[(i * 2) % len(others)]
    d2 = others[(i * 2 + 1) % len(others)]
    pos = i % 3
    opts, ans = rot([{"text": ch}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"cn-{i}-l2", "kind": "listen", "promptIcon": mfrom, "speakText": ch,
            "question": "看一看：这张图变成的字是哪个？",
            "options": opts, "answer": ans,
            "hint": f"想一想它像什么字", "praise": f"对！这张图就是「{ch}」"}

def cn_word_quiz(i, ch, words):
    correct = words[0]
    dis = other_words(ch, 2, start=i * 3)
    pos = (i + 1) % 3
    opts, ans = rot([{"icon": correct[0], "text": correct[1]},
                     {"icon": dis[0][0], "text": dis[0][1]},
                     {"icon": dis[1][0], "text": dis[1][1]}], 0, pos)
    return {"id": f"cn-{i}-w", "kind": "quiz",
            "question": f"「{ch}」可以组成哪个词？",
            "options": opts, "answer": ans,
            "hint": f"找一找有「{ch}」的词", "praise": f"组词成功：{correct[1]}！"}

def cn_char_quiz(i, ch):
    d1 = "木" if ch != "木" else "水"
    d2 = "口" if ch != "口" else "日"
    pos = i % 3
    opts, ans = rot([{"text": ch}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"cn-{i}-q", "kind": "quiz",
            "question": f"练一练：哪个字是「{ch}」？",
            "options": opts, "answer": ans,
            "hint": "想一想刚才的字", "praise": "记住啦！"}

def cn_listen_pic2(i, ch, lo, lans):
    tgt, d1, d2 = lo
    correct = {"icon": tgt, "text": ch}
    others = [{"icon": d1}, {"icon": d2}]
    nlans = (lans + 1) % 3
    opts = others[:nlans] + [correct] + others[nlans:]
    return {"id": f"cn-{i}-l3", "kind": "listen", "prompt": ch, "speakText": ch,
            "question": f"再找一找：哪张图片是「{ch}」？",
            "options": opts, "answer": nlans,
            "hint": f"「{ch}」长什么样", "praise": f"又找对啦！{ch}！"}

def cn_write(i, ch, py):
    """写字关：田字格逐笔描红，写完才入汉字册"""
    return {"id": f"cn-{i}-wr", "kind": "write", "char": ch, "pinyin": py,
            "strokes": [S(d) for d in STROKES[ch]],
            "question": f"写一写：看一笔、描一笔，写「{ch}」",
            "praise": "写得真好，汉字卡到手！"}

# v0.8 迷你棋盘组成
EVENT_COMBOS = [["chest"], ["mushroom"], ["rest"], ["chest", "mushroom"], ["mushroom", "rest"], ["chest", "rest"]]
REVIEW_EVENTS = [["chest", "mushroom"], ["chest", "rest"]]

def build_board(qids, extra, rotate_by):
    qq = qids[rotate_by % len(qids):] + qids[:rotate_by % len(qids)]
    gaps = [2, 4, 5, 6][:len(extra)]
    spaces, used = [], 0
    for qn in range(len(qq)):
        spaces.append({"type": "question", "step": qq[qn]})
        if (qn + 1) in gaps and used < len(extra):
            spaces.append({"type": extra[used]})
            used += 1
    while used < len(extra):
        spaces.insert(len(spaces) - 1, {"type": extra[used]})
        used += 1
    return {"spaces": spaces}

def cn_board(i, qids):
    extra = ["coin"] * (2 if i % 2 == 0 else 1) + EVENT_COMBOS[i % 6]
    return build_board(qids, extra, i)

def sample_questions(level_steps, count, tag):
    pool, take = [], [0] * len(level_steps)
    while len(pool) < count:
        moved = False
        for li, sts in enumerate(level_steps):
            qs = [s for s in sts if s["kind"] not in ("teach", "letter")]
            if take[li] < len(qs) and len(pool) < count:
                st = dict(qs[take[li]])
                st["id"] = f"{tag}-{len(pool)}"
                take[li] += 1
                pool.append(st)
                moved = True
        if not moved:
            break
    return pool

def add_review_levels(levels, sub, positions, priors=(5, 10)):
    q_by_level = [[s for s in lv["steps"] if s["kind"] not in ("teach", "letter")] for lv in levels]
    for k in (0, 1):
        p = priors[k]
        while p < len(q_by_level) and sum(len(s) for s in q_by_level[:p]) < 6:
            p += 1
        qs = sample_questions(q_by_level[:p], 6, f"{sub}-r{k}")
        levels.insert(positions[k], {
            "id": f"{sub}-r{k}",
            "title": "复习关 一" if k == 0 else "复习关 二",
            "subtitle": "旧题开盲盒 · 混排复习",
            "steps": qs,
            "board": build_board([q["id"] for q in qs], ["coin", "coin"] + REVIEW_EVENTS[k % len(REVIEW_EVENTS)], k),
            "review": True,
        })

def add_boss_level(levels, sub):
    q_by_level = [[s for s in lv["steps"] if s["kind"] not in ("teach", "letter")] for lv in levels]
    qs = sample_questions(q_by_level, 8, f"{sub}-boss")
    levels.append({
        "id": f"{sub}-boss",
        "title": "Boss 大挑战",
        "subtitle": "大壳壳兽 · 三颗心大决战",
        "steps": qs,
        "board": {"spaces": [{"type": "question", "step": q["id"]} for q in qs]},
        "boss": True,
    })

def append_extras(levels, extras):
    """v0.10.1 其他学科题型丰富化：把新题型步骤追加到指定关卡末尾。
    棋盘关（识字村）同时把最后一块金币格改成引用新步骤的题目格，保证新题可达且棋盘规格合法。"""
    for lid, step in extras:
        lv = next((l for l in levels if l["id"] == lid), None)
        assert lv is not None, f"append_extras: 找不到关卡 {lid}"
        lv["steps"].append(step)
        bd = lv.get("board")
        if bd:
            coins = [sp for sp in bd["spaces"] if sp.get("type") == "coin"]
            assert coins, f"{lid} 棋盘无金币格可替换"
            coins[-1]["type"] = "question"
            coins[-1]["step"] = step["id"]

def apply_anims(levels, mapping):
    """v0.10.2 学科专属学一学动画：把 anim 写进指定关卡的首个 letter 步骤。
    动画 id 必须是该学科知识点专属（拼音/英语/环球各有自己的动画集，不与天文共用）。"""
    for lid, anim in mapping.items():
        lv = next((l for l in levels if l["id"] == lid), None)
        assert lv is not None, f"apply_anims: 找不到关卡 {lid}"
        st = lv["steps"][0]
        assert st["kind"] == "letter", f"apply_anims: {lid} 首步不是 letter"
        st["anim"] = anim

# —— v0.12.1 动画第二批：数学/英语/环球/拼音教学卡按知识点关键词补动画 ——
# 规则按序匹配（关卡标题 + display + question），都不中用该科 default；已配 anim 的一律不动。
# 新增 26 个 id（groups…soft），与 index.html 的 ANIM_IDS、validate.py 的 ANIM_IDS 三处同步。
LETTER_ANIM_RULES = {
    "math": [
        (("口诀",), "groups"),
        (("除法", "平均", "求商", "装盒", "分书", "分一分", "分组"), "share"),
        (("厘米", "米尺", "长度", "比长短", "估一估", "选单位", "认识米", "跳远", "身高"), "ruler"),
        (("角",), "angle"),
        (("克", "千克", "重量", "轻重"), "scale"),
        (("笔算", "连加连减", "万以内", "数位", "读写", "比大小", "近似数"), "column"),
        (("观察物体", "前面", "后面", "侧面"), "viewcube"),
        (("应用", "乘车", "买文具", "分苹果", "排队伍"), "story"),
    ],
    "english": [
        (("Learn letter",), "abc"),
        (("Lion", "Fish", "Bee", "Fox", "Farm", "Pets", "Wild Animals", "Sea Friends",
          "Animal Babies", "Dinosaur"), "paw"),
        (("Days", "Months", "Seasons", "Week"), "calendar"),
        (("Cake", "Breakfast", "Fruit", "Drink", "Time to Eat", "On the Table"), "yummy"),
        (("Run", "Verbs", "Go Go Go", "I can", "Play Time", "Body Power"), "jump"),
    ],
    "geo": [
        (("哈尔滨", "冰岛", "格陵兰", "南极", "北极", "极地", "极昼极夜", "北冰洋", "芬兰",
          "雪山", "冰川", "降雪"), "snow"),
        (("海南", "台湾", "夏威夷", "大堡礁", "珊瑚", "太平洋", "海沟", "马里亚纳"), "wave"),
        (("新疆", "撒哈拉", "沙漠"), "camel"),
        (("云南",), "bloom"),
        (("火山",), "volcano"),
        (("恐龙", "化石"), "dino"),
        (("春节", "中秋", "端午", "圣诞", "万圣", "感恩"), "festival"),
        (("长江", "黄河", "尼罗河", "贝加尔湖", "死海", "青海湖", "亚马孙"), "river"),
        (("陨石", "彗星"), "meteor"),
        (("桂林", "黄山"), "mountain"),
        (("七大洲", "四大洋", "地球仪", "时差", "环球", "认方向", "指南针", "世界",
          "亚洲", "非洲", "欧洲", "美洲", "环保", "人种", "语言"), "globe"),
    ],
    "pinyin": [
        (("多音字",), "flip"),
        (("儿化",), "curl"),
        (("轻声",), "soft"),
        (("变调", "三声", "整体认读复习"), "tone"),
        (("平舌", "翘舌", "前后鼻", "前鼻", "后鼻", "r 声母"), "merge"),
        (("拼读儿歌", "总复习"), "pydraw"),
    ],
}


def assign_letter_anims(levels, sub, default):
    """给还没有 anim 的 letter 步骤按知识点关键词补动画（v0.12.1）。
    只补空位，不动 apply_anims/工厂已配好的 anim；规则都不中时用该科 default，保证教学卡 100% 有动画。"""
    rules = LETTER_ANIM_RULES[sub]
    n = 0
    for lv in levels:
        for st in lv["steps"]:
            if st.get("kind") != "letter" or st.get("anim"):
                continue
            text = f'{lv["title"]} {st.get("display", "")} {st.get("question", "")}'
            st["anim"] = next((a for kws, a in rules if any(k in text for k in kws)), default)
            n += 1
    return n

def finish_levels(levels, sub, total):
    """关卡收尾（通用）：正则关 + 复习@各星区段末 + Boss（每星区恰好 10 关）。
    50 关：复习@19/39/48；100 关：复习@29/59/89。复习题从之前所有正则关轮询采样。"""
    n_reg = {50: 46, 100: 96}[total]
    poses = {50: [19, 39, 48], 100: [29, 59, 89]}[total]
    assert len(levels) == n_reg, f"{sub} {total} 关布局需 {n_reg} 正则关，实际 {len(levels)}"
    q_by_level = [[st for st in lv["steps"] if st["kind"] not in ("teach", "letter")] for lv in levels]
    reviews = []
    for k, pos in enumerate(poses):
        qs = sample_questions(q_by_level[:pos], 6, f"{sub}-r{k}")
        reviews.append({"id": f"{sub}-r{k}", "title": f"复习关 {'一二三'[k]}",
                        "subtitle": "旧题开盲盒 · 混排复习", "steps": qs,
                        "board": build_board([q["id"] for q in qs],
                                             ["coin", "coin"] + REVIEW_EVENTS[k % len(REVIEW_EVENTS)], k),
                        "review": True})
    out = []
    prev = 0
    for k, pos in enumerate(poses):
        out += levels[prev:pos] + [reviews[k]]
        prev = pos
    out += levels[prev:]
    out.append(None)
    levels[:] = out[:-1]
    add_boss_level(levels, sub)
    assert len(levels) == total, f"{sub} 收尾后 {len(levels)} != {total}"
    for i, lv in enumerate(levels):
        lv["zone"] = i // 10 + 1

def finish_50(levels, sub):
    finish_levels(levels, sub, 50)

def zones_meta(titles, icons):
    return [{"n": i + 1, "title": t, "subtitle": st, "icon": ic}
            for i, (t, ic, st) in enumerate(zip(titles, icons[0], icons[1]))]

cn_levels = []
for i, (ch, py, mfrom, words, lo, lans) in enumerate(CN):
    q_steps = [cn_listen_pic(i, ch, lo, lans),
               cn_listen_pic_to_char(i, ch, mfrom),
               cn_word_quiz(i, ch, words),
               cn_char_quiz(i, ch),
               cn_listen_pic2(i, ch, lo, lans),
               cn_write(i, ch, py)]
    steps = [{"id": f"cn-{i}-t", "kind": "teach", "morphFrom": mfrom, "char": ch, "pinyin": py,
              "words": [{"icon": w, "text": t, "say": t} for w, t in words]}] + q_steps
    cn_levels.append({"id": f"cn-{i}", "title": f"第 {i+1} 关 识字写字", "subtitle": f"认识并会写「{ch}」",
                      "steps": steps, "board": cn_board(i, [s["id"] for s in q_steps])})
finish_levels(cn_levels, "cn", 100)
append_extras(cn_levels, [
    ("cn-0", match_step("cn-x1", "连一连：字和它变成的东西",
                        [("sun","日","太阳"),("moon","月","月亮"),("volcano","山","大山")])),
    ("cn-10", shadow_step("cn-x2", "看影子猜猜：哪张是「火」的词卡？", "flame",
                          [("flame","火"),("volcano","山"),("crystal","冰晶")], 0, "火苗向上跳的样子")),
    ("cn-13", tapall_step("cn-x3", "点点看：把动物朋友都点亮",
                          [("duck",None,True),("panda",None,True),("rabbit",None,True),("bear",None,True),
                           ("sun",None,False),("apple",None,False)],
                          "小鸟、熊猫、兔子、小熊是动物朋友")),
    ("cn-14", sequence_step("cn-x4", "按顺序点：一 → 二 → 三", ["一","二","三"], praise="汉字火车开动啦！")),
])
W("cn_levels.json", {"subject": "cn", "title": "识字村", "guide": "panda",
                    "zones": zones_meta(["自然万象", "动物朋友", "数字启蒙", "身体与动作", "生活器物",
                                          "植物园地", "家庭称谓", "山川湖海", "城市建筑", "汉字大挑战"],
                                        (["sun", "duck", "dice", "girl", "hanger",
                                          "sprout", "home", "wave", "castle", "medal"],
                                         ["日月水火山石", "花鸟虫鱼猫狗", "一二三四…十", "目耳手足见", "车灯杯井旗",
                                          "木杨桐松柏桂植", "娃姨迎群变", "海湖潭江河", "城市场楼峰", "雪冰 · 总复习"])),
                    "levels": cn_levels})

# ================= 数学 34 关 =================
math_levels = []

def count_step(i, n, opts, scene):
    return {"id": f"math-{i}-c", "kind": "count",
            "question": f"{scene['q']}（点一点，数数看）",
            "duckIcon": scene["icon"], "count": n, "countOptions": opts,
            "backdrop": scene["backdrop"], "unit": scene["unit"]}

def compare_step(i, li, l, ri, r, labels, q="哪一边更多？"):
    key = "same" if l == r else ("left" if l > r else "right")
    return {"id": f"math-{i}-cmp", "kind": "compare", "question": q,
            "leftIcon": li, "leftCount": l, "rightIcon": ri, "rightCount": r,
            "compareOptions": [{"key": k, "label": lb} for k, lb in
                               zip(("left","right","same"), labels)],
            "answerKey": key,
            "hint": "一个对着一个，比一比",
            "praise": {True: "火眼金睛！一样多！", "left": f"{labels[0]}，答对啦！",
                       "right": f"{labels[1]}，答对啦！"}[key if l != r else True]}

def arith_step(i, op, a, b, opts, icon, unit, q):
    correct = a + b if op == "+" else a - b
    return {"id": f"math-{i}-a{op}{a}{b}", "kind": "arith", "op": op,
            "leftIcon": icon, "leftCount": a, "rightCount": b, "unit": unit,
            "question": q,
            "arithOptions": opts,
            "hint": "指着图一个一个数" if op == "+" else "划掉的不算哦",
            "praise": f"算对啦，等于 {correct}！"}

def pattern_step(pid, seq, options, ans, q="找规律：下一个是哪个？"):
    return {"id": pid, "kind": "pattern", "seq": seq, "question": q,
            "options": [{"icon": o} for o in options], "answer": ans,
            "hint": "先读一读前面几个，找一找谁在轮流出现",
            "praise": "规律找对啦，小侦探！"}

def split_step(sid, total, part, icon, unit, q):
    rest = total - part
    cand = sorted({max(rest - 1, 0), rest, rest + 1, rest + 2})
    options = cand[:3] if rest in cand[:3] else cand[-3:]
    return {"id": sid, "kind": "split", "total": total, "part": part,
            "leftIcon": icon, "unit": unit, "question": q,
            "arithOptions": options,
            "hint": f"一共 {total} {unit}，左边有 {part} {unit}",
            "praise": f"分对啦，{total} 可以分成 {part} 和 {rest}！"}

def order_step(oid, nums, direction, q=None):
    d = "从小到大" if direction == "up" else "从大到小"
    return {"id": oid, "kind": "order", "nums": nums, "dir": direction,
            "question": q or f"{d}，依次点一点",
            "hint": f"{d}：{'小' if direction=='up' else '大'}的排前面",
            "praise": "排队排好啦！"}

def neighbor_step(nid, a, b, opts=None):
    correct = a + 1
    options = opts or sorted({correct, correct - 1, correct + 1})
    return {"id": nid, "kind": "neighbor", "nums": [a, 0, a + 2],
            "question": f"想一想：{a} 和 {a + 2} 中间藏起来的数字是几？",
            "arithOptions": options, "answer": options.index(correct),
            "hint": f"{a} 的后面是几？{a + 2} 的前面是几？",
            "praise": f"是 {correct}！{a} 和 {a + 2} 的中间是 {correct}！"}

SC_duck   = {"icon":"duck",   "unit":"只", "backdrop":"pond",  "q":"池塘里有几只小鸭"}
SC_candy  = {"icon":"candy",  "unit":"颗", "backdrop":"grass", "q":"盘子里有几颗糖"}
SC_apple  = {"icon":"apple",  "unit":"个", "backdrop":"grass", "q":"果园里摘了几个苹果"}
SC_balloon= {"icon":"balloon","unit":"个", "backdrop":"sky",   "q":"天上有几个气球"}
SC_star   = {"icon":"star",   "unit":"颗", "backdrop":"night", "q":"夜空里有几颗星星"}
SC_train  = {"icon":"train",  "unit":"辆", "backdrop":"grass", "q":"轨道上有几辆小火车"}
SC_flower = {"icon":"flower", "unit":"朵", "backdrop":"grass", "q":"花园里开了几朵花"}
SC_heart  = {"icon":"heart",  "unit":"颗", "backdrop":"grass", "q":"礼盒里有几颗爱心糖"}
SC_coin   = {"icon":"coin",   "unit":"枚", "backdrop":"night", "q":"宝箱里有几枚金币"}

specs = [
    ("math-0","第 1 关 池塘数鸭","3 以内点数", lambda i: [count_step(i,3,[2,3,4],SC_duck),
        compare_step(i,"apple",3,"banana",1,["苹果多","香蕉多","一样多"],"哪边的水果更多？")]),
    ("math-1","第 2 关 糖果店","4 以内 · 排一排", lambda i: [count_step(i,4,[3,4,5],SC_candy),
        order_step(f"math-{i}-o1",[2,4,1],"up")]),
    ("math-2","第 3 关 果园丰收","5 以内 · 分一分", lambda i: [count_step(i,5,[4,5,6],SC_apple),
        split_step(f"math-{i}-s1",5,2,"apple","个","5 个苹果分两篮，左边 2 个，右边几个？")]),
    ("math-3","第 4 关 气球派对","一样多 · 填一填", lambda i: [
        compare_step(i,"balloon",4,"balloon",4,["左边多","右边多","一样多"],"两边气球哪边多？"),
        neighbor_step(f"math-{i}-n1",3,5)]),
    ("math-4","第 5 关 夜空数星","6 以内点数", lambda i: [count_step(i,6,[5,6,7],SC_star),
        compare_step(i,"star",6,"moon",4,["星星多","月亮多","一样多"],"星星和月亮哪边多？")]),
    ("math-5","第 6 关 小火车","7 以内 · 排一排 · 掷骰子", lambda i: [count_step(i,7,[6,7,8],SC_train),
        order_step(f"math-{i}-o2",[3,6,4],"up"),
        dice_step(f"math-{i}-d1",5,[4,5,6])]),
    ("math-6","第 7 关 花园蜜蜂","8 以内 · 分一分", lambda i: [count_step(i,8,[7,8,9],SC_flower),
        split_step(f"math-{i}-s2",8,3,"flower","朵","8 朵花分两个花瓶，左边 3 朵，右边几朵？")]),
    ("math-7","第 8 关 爱心礼盒","9 以内 · 排一排 · 掷骰子", lambda i: [count_step(i,9,[8,9,10],SC_heart),
        order_step(f"math-{i}-o3",[9,4,7],"down"),
        dice_step(f"math-{i}-d2",6,[5,6,7])]),
    ("math-8","第 9 关 宝藏金币","10 以内点数", lambda i: [count_step(i,10,[8,9,10],SC_coin),
        pattern_step(f"math-{i}-p1",["star","moon","star"],["moon","star","candy"],0)]),
    ("math-9","第 10 关 数字擂台","比大小 · 归类", lambda i: [
        quiz_step(f"math-{i}-q1","哪个数字最大？",[(None,"5"),(None,"9"),(None,"3")],1,"从 1 数到 10，谁排在最后？","9 最大，答对啦！"),
        quiz_step(f"math-{i}-q2","哪个数字最小？",[(None,"2"),(None,"7"),(None,"10")],0,"越早数到的越小哦","思维小达人！"),
        quiz_step(f"math-{i}-q3","火眼金睛：哪个是交通工具？",[("duck",None),("train",None),("cake",None)],1,"想一想它们分别是做什么的","分类小能手！")]),
    ("math-10","第 11 关 糖果加法","合起来", lambda i: [arith_step(i,"+",1,1,[1,2,3],"candy","颗","1 颗糖加 1 颗糖，一共有几颗？"),
        arith_step(i,"+",2,1,[2,3,4],"candy","颗","2 颗糖加 1 颗糖，一共有几颗？")]),
    ("math-11","第 12 关 苹果加法","加法 · 分一分", lambda i: [arith_step(i,"+",2,2,[3,4,5],"apple","个","2 个苹果加 2 个苹果，一共有几个？"),
        split_step(f"math-{i}-s3",6,2,"apple","个","6 个苹果分两篮，左边 2 个，右边几个？")]),
    ("math-12","第 13 关 气球飞走了","减法初识", lambda i: [arith_step(i,"-",3,1,[1,2,3],"balloon","个","3 个气球飞走 1 个，还剩几个？"),
        arith_step(i,"-",4,2,[1,2,3],"balloon","个","4 个气球飞走 2 个，还剩几个？")]),
    ("math-13","第 14 关 星星回家","减法 · 填一填", lambda i: [arith_step(i,"-",5,2,[2,3,4],"star","颗","5 颗星星回家 2 颗，还剩几颗？"),
        neighbor_step(f"math-{i}-n2",6,8)]),
    ("math-14","第 15 关 思维大挑战","加减 · 排队 · 找规律", lambda i: [arith_step(i,"+",4,4,[7,8,9],"star","颗","4 颗星星加 4 颗星星，一共几颗？"),
        arith_step(i,"-",9,3,[5,6,7],"duck","只","9 只小鸭游走 3 只，还剩几只？"),
        order_step(f"math-{i}-o4",[10,2,7],"down"),
        pattern_step(f"math-{i}-p2",["sun","moon","star","sun","moon"],["moon","sun","star"],2)]),
]
for idx, (lid, title, sub, build) in enumerate(specs):
    math_levels.append({"id": lid, "title": title, "subtitle": sub, "steps": build(idx)})

# ---------- v0.9 新增 19 关（math-15 .. math-33） ----------
def muldiv_step(mid, op, mode, icon, unit, groups=None, per=None, total=None,
                opts=None, q=None, hint=None, praise=None):
    if op == "×":
        ans = groups * per
    elif mode == "average":
        ans = total // groups
    else:
        ans = total // per
    opts = opts or [ans - 1, ans, ans + 1]
    d = {"id": mid, "kind": "muldiv", "op": op, "mode": mode, "icon": icon, "unit": unit,
         "question": q, "hint": hint or "摆一摆、数一数",
         "praise": praise or f"算对啦，等于 {ans}！",
         "options": opts, "answer": opts.index(ans)}
    if op == "×":
        d["groups"], d["per"] = groups, per
    elif mode == "average":
        d["total"], d["groups"] = total, groups
    else:
        d["total"], d["per"] = total, per
    return d

def cards_step(cid, mode, target, pick, cards, q):
    return {"id": cid, "kind": "cards", "mode": mode, "target": target, "pick": pick,
            "cards": cards, "question": q, "praise": "凑数成功，算术小赌神！"}

def sudoku_step(sid, symbols, givens, solution, q):
    return {"id": sid, "kind": "sudoku", "size": 4, "symbols": symbols,
            "givens": givens, "solution": solution, "question": q,
            "praise": "数独侦探，推理成功！"}

def clock_step(cid, mode, hour, minute, options=None, answer=None, q=None):
    d = {"id": cid, "kind": "clock", "mode": mode, "hour": hour, "minute": minute,
         "question": q or ("看钟面：现在是几点？" if mode == "read" else "拨一拨：把时针分针拨到指定时间"),
         "praise": "认时小达人！"}
    if mode == "read":
        d["options"] = options
        d["answer"] = answer
    return d

def money_step(mid, price, q):
    denoms = [
        {"value": 1, "label": "1角", "icon": "m-jiao1"},
        {"value": 5, "label": "5角", "icon": "m-jiao5"},
        {"value": 10, "label": "1元", "icon": "m-yuan1"},
        {"value": 50, "label": "5元", "icon": "m-yuan5"},
        {"value": 100, "label": "10元", "icon": "m-yuan10"},
    ]
    return {"id": mid, "kind": "money", "price": price, "denominations": denoms,
            "question": q, "praise": "付钱小能手，正好付清！"}

new_math = [
    # 15 凑十法（20 以内加法）
    ("math-15","第 16 关 凑十法","20 以内加法", lambda i: [
        arith_step(i,"+",9,4,[12,13,14],"candy","颗","9 颗糖加 4 颗，凑成十再加，一共几颗？"),
        arith_step(i,"+",8,5,[12,13,14],"apple","个","8 个苹果加 5 个，凑十法算一算，一共几个？")]),
    # 16 破十法（20 以内减法）
    ("math-16","第 17 关 破十法","20 以内减法", lambda i: [
        arith_step(i,"-",13,5,[7,8,9],"star","颗","13 颗星星去掉 5 颗，破十法算一算，还剩几颗？"),
        arith_step(i,"-",15,8,[6,7,8],"balloon","个","15 个气球飞走 8 个，破十法算一算，还剩几个？")]),
    # 17 连加减
    ("math-17","第 18 关 连加连减","三个数", lambda i: [
        arith_step(i,"+",7,5,[11,12,13],"duck","只","先来了 7 只鸭，又来了 5 只，一共几只？"),
        arith_step(i,"-",14,6,[7,8,9],"candy","颗","14 颗糖吃掉 6 颗，还剩几颗？"),
        quiz_step(f"math-{i}-q3","连加：3 + 4 + 2 = ?",[(None,"8"),(None,"9"),(None,"10")],1,"先算 3+4，再加 2","连加小能手！")]),
    # 18 50 以内
    ("math-18","第 19 关 五十以内","两位数加减", lambda i: [
        arith_step(i,"+",23,15,[37,38,39],"block","块","两堆积木，23 块和 15 块，一共几块？"),
        arith_step(i,"-",45,22,[22,23,24],"block","块","45 块积木拿走 22 块，还剩几块？")]),
    # 19 100 / 200 以内挑战
    ("math-19","第 20 关 百数大挑战","100/200 以内", lambda i: [
        arith_step(i,"+",36,27,[62,63,64],"coin","枚","36 枚金币加 27 枚，一共几枚？"),
        arith_step(i,"-",80,35,[44,45,46],"coin","枚","80 枚金币花掉 35 枚，还剩几枚？"),
        quiz_step(f"math-{i}-q3","挑战：100 - 40 = ?",[(None,"50"),(None,"60"),(None,"70")],1,"10 个十去掉 4 个十","百数达人！")]),
    # 20 乘法启蒙 · 几个几
    ("math-20","第 21 关 几个几","乘法启蒙", lambda i: [
        muldiv_step(f"math-{i}-m1","×","groups","train","辆",groups=3,per=2,
                    q="3 组小车，每组 2 辆，一共几辆？",hint="几个几：3 个 2，连加 2+2+2",
                    praise="乘法小能手：3×2=6！"),
        muldiv_step(f"math-{i}-m2","×","groups","apple","个",groups=2,per=4,
                    q="2 盘苹果，每盘 4 个，一共几个？",hint="2 个 4",
                    praise="2×4=8，真棒！")]),
    # 21 认识乘号
    ("math-21","第 22 关 认识乘号","×", lambda i: [
        muldiv_step(f"math-{i}-m1","×","groups","flower","朵",groups=4,per=2,
                    q="4 组花，每组 2 朵，乘法算一算，一共几朵？",hint="4 个 2",
                    praise="4×2=8！"),
        muldiv_step(f"math-{i}-m2","×","groups","candy","颗",groups=3,per=3,
                    q="3 堆糖，每堆 3 颗，乘法算一算，一共几颗？",hint="3 个 3",
                    praise="3×3=9！")]),
    # 22 2/3/4/5 口诀
    ("math-22","第 23 关 乘法口诀","2~5", lambda i: [
        muldiv_step(f"math-{i}-m1","×","groups","star","颗",groups=5,per=2,
                    q="5 行星星，每行 2 颗，二五一十，一共几颗？",hint="二五一十",
                    praise="二五一十，口诀真熟！"),
        muldiv_step(f"math-{i}-m2","×","groups","duck","只",groups=4,per=3,
                    q="4 群小鸭，每群 3 只，三四十二，一共几只？",hint="三四十二",
                    praise="三四十二，乘法小达人！")]),
    # 23 除法 · 平均分
    ("math-23","第 24 关 平均分","除法启蒙", lambda i: [
        muldiv_step(f"math-{i}-d1","÷","average","candy","颗",total=12,groups=3,
                    q="12 颗糖平均分给 3 个人，每人几颗？",hint="一样多分",
                    praise="12÷3=4，分公平啦！"),
        muldiv_step(f"math-{i}-d2","÷","average","apple","个",total=10,groups=2,
                    q="10 个苹果平均装 2 盘，每盘几个？",hint="一样多分",
                    praise="10÷2=5！")]),
    # 24 除法 · 包含除
    ("math-24","第 25 关 能分几组","包含除", lambda i: [
        muldiv_step(f"math-{i}-d1","÷","contain","apple","个",total=12,per=3,
                    q="12 个苹果，每盘放 3 个，能放几盘？",hint="3 个一圈",
                    praise="12÷3=4 盘！"),
        muldiv_step(f"math-{i}-d2","÷","contain","candy","颗",total=15,per=5,
                    q="15 颗糖，每人分 5 颗，能分给几个人？",hint="5 个一组",
                    praise="15÷5=3 人！")]),
    # 25 扑克 · 凑十大战
    ("math-25","第 26 关 凑十大战","扑克 make10", lambda i: [
        cards_step(f"math-{i}-c1","make10",10,2,[3,7,2,8,5,1],
                   "凑十大战：点 2 张牌，恰好凑成 10"),
        cards_step(f"math-{i}-c2","make10",10,2,[4,6,1,9,5,2],
                   "再凑十：再点 2 张牌凑成 10")]),
    # 26 扑克 · 三牌凑目标
    ("math-26","第 27 关 三牌凑目标","扑克 target", lambda i: [
        cards_step(f"math-{i}-c1","target",12,3,[3,5,4,1,2,6],
                   "点 3 张牌，用加减凑出 12"),
        cards_step(f"math-{i}-c2","target",15,3,[7,2,6,3,4,1],
                   "点 3 张牌，用加减凑出 15")]),
    # 27 数独入门（给定多）
    ("math-27","第 28 关 图案数独","4×4 入门", lambda i: [
        sudoku_step(f"math-{i}-s1",["duck","apple","star","moon"],
            [{"r":0,"c":0,"v":0},{"r":0,"c":2,"v":2},{"r":1,"c":1,"v":3},{"r":1,"c":3,"v":1},
             {"r":2,"c":0,"v":1},{"r":2,"c":2,"v":3},{"r":3,"c":1,"v":0},{"r":3,"c":3,"v":2}],
            [[0,1,2,3],[2,3,0,1],[1,2,3,0],[3,0,1,2]],
            "图案数独：每行、每列、每个 2×2 宫图标不重复")]),
    # 28 数独进阶（给定少）
    ("math-28","第 29 关 数独侦探","4×4 进阶", lambda i: [
        sudoku_step(f"math-{i}-s1",["duck","apple","star","moon"],
            [{"r":0,"c":1,"v":0},{"r":1,"c":0,"v":3},{"r":2,"c":2,"v":2},{"r":3,"c":0,"v":2},{"r":3,"c":3,"v":0}],
            [[1,0,3,2],[3,2,0,1],[0,1,2,3],[2,3,1,0]],
            "再来一盘：给定更少，推理填完整个数独")]),
    # 29 钟表 · 整点
    ("math-29","第 30 关 认识钟表","整点", lambda i: [
        clock_step(f"math-{i}-cl1","read",3,0,["3:00","4:00","2:00"],0,"看钟面：现在是几点？"),
        clock_step(f"math-{i}-cl2","read",8,0,["8:00","7:00","9:00"],0,"再看一个钟面，是几点？")]),
    # 30 钟表 · 半点 + 拨针
    ("math-30","第 31 关 半点和拨针","半点", lambda i: [
        clock_step(f"math-{i}-cl1","read",7,30,["7:30","6:30","8:30"],0,"分针指 6，是半点，几点半？"),
        clock_step(f"math-{i}-cl2","set",9,30,q="拨一拨：把时针分针拨到 9 点半")]),
    # 31 人民币
    ("math-31","第 32 关 小小商店","人民币", lambda i: [
        money_step(f"math-{i}-m1",60,"买东西：点钱币，恰好付清 6 元"),
        money_step(f"math-{i}-m2",35,"再买一件：点钱币，恰好付清 3 元 5 角")]),
    # 32 奇偶
    ("math-32","第 33 关 单数和双数","奇偶", lambda i: [
        quiz_step(f"math-{i}-q1","哪个是单数？",[(None,"4"),(None,"7"),(None,"8")],1,"两两成对分完、多一个的是单数","7 是单数！"),
        quiz_step(f"math-{i}-q2","哪个是双数？",[(None,"3"),(None,"6"),(None,"9")],1,"两两正好分完的是双数","6 是双数！"),
        quiz_step(f"math-{i}-q3","8 个苹果两两分，有没有剩余？",[(None,"没有剩余"),(None,"剩1个"),(None,"剩2个")],0,"8 是双数","双数分完没剩余！")]),
    # 33 平面图形
    ("math-33","第 34 关 图形拼拼乐","平面图形", lambda i: [
        quiz_step(f"math-{i}-q1","哪个物品是圆圆的？",[("balloon",None),("tree",None),("book",None)],0,"圆圆的会滚","圆形滚得远！"),
        quiz_step(f"math-{i}-q2","车轮为什么是圆的？",[(None,"滚起来平稳"),(None,"会卡住"),(None,"容易碎")],0,"圆圆的滚起来不颠","圆的最平稳！"),
        pattern_step(f"math-{i}-p1",["sun","moon","sun"],["moon","sun","star"],0,"图形规律：下一个是谁？")]),
]
for lid, title, sub, build in new_math:
    idx = int(lid.split("-")[1])
    math_levels.append({"id": lid, "title": title, "subtitle": sub, "steps": build(idx)})

# —— v0.11 人教版一年级数学知识点补 12 关（46 正则 → 50 关）——
math_levels += [
    {"id": "math-34", "title": "第 35 关 认识图形", "subtitle": "平面图形", "steps": [
        quiz_step("math-34-q1", "哪个是圆形？", [("circle", None), ("triangle", None), ("square", None)], 0, "圆圆的，没有角", "对，圆形没有角！"),
        quiz_step("math-34-q2", "三角形有几条边？", [(None, "3 条"), (None, "4 条"), (None, "5 条")], 0, "三条边围起来", "对，3 条边！"),
        pattern_step("math-34-p", ["circle", "square", "circle"], ["square", "triangle", "ball"], 0),
    ]},
    {"id": "math-35", "title": "第 36 关 立体图形", "subtitle": "球和方块", "steps": [
        quiz_step("math-35-q1", "哪个能咕噜噜滚动，像球？", [("ball", None), ("block", None), ("dice", None)], 0, "球滚滚圆，到处滚", "对，球会滚！"),
        quiz_step("math-35-q2", "骰子是什么形状？", [(None, "方方的正方体"), (None, "球"), (None, "圆柱")], 0, "六个面都一样", "答对啦，正方体！"),
    ]},
    {"id": "math-36", "title": "第 37 关 比一比", "subtitle": "长短高矮", "steps": [
        quiz_step("math-36-q1", "大象和小鸟，谁长得高？", [("elephant", "大象"), ("duck", "小鸟"), ("cake", "蛋糕")], 0, "大象个子最高", "对，大象高！"),
        quiz_step("math-36-q2", "比长短：火车和小汽车，哪个长？", [(None, "火车长"), (None, "汽车长"), (None, "一样长")], 0, "火车一节连一节", "对，火车长！"),
    ]},
    {"id": "math-37", "title": "第 38 分分类", "subtitle": "分类整理", "steps": [
        tapall_step("math-37-t1", "点点看：把交通工具都点亮",
                    [("car", None, True), ("bus", None, True), ("train", None, True),
                     ("apple", None, False), ("duck", None, False)],
                    "汽车、公交车、火车都能载人载货"),
        quiz_step("math-37-q1", "把杯子、盘子放一起，是在做什么？",
                  [(None, "分类整理"), (None, "捉迷藏"), (None, "画画")], 0,
                  "同一类的东西放一起", "对，这叫分类！"),
    ]},
    {"id": "math-38", "title": "第 39 位置·上下", "subtitle": "上和下", "steps": [
        quiz_step("math-38-q1", "小鸟飞在天上，还是树下？", [("moon", "天上"), ("tree", "树下"), ("cake", "锅里")], 0,
                  "抬头看，小鸟在天上", "对，小鸟在天上！"),
        quiz_step("math-38-q2", "书放在桌子的上面，桌子在书的——",
                  [(None, "下面"), (None, "上面"), (None, "旁边没有")], 0,
                  "上和下是一对好朋友", "答对啦，桌子在下面！"),
    ]},
    {"id": "math-39", "title": "第 40 位置·前后", "subtitle": "前和后", "steps": [
        quiz_step("math-39-q1", "排队啦：火箭跑在最前面，谁在它后面？",
                  [("rocket", "火箭"), ("car", "汽车"), ("train", "火车")], 0,
                  "朝前看，前面只有一个头", "答对啦，看图找位置！"),
    ]},
    {"id": "math-40", "title": "第 41 第几", "subtitle": "序数", "steps": [
        quiz_step("math-40-q1", "5 只小鸭排队，从前往后数，第 3 只是——",
                  [(None, "第 3 只"), (None, "第 5 只"), (None, "第 1 只")], 0,
                  "1、2、3，数到 3 就是第 3", "对，第 3 只！"),
        quiz_step("math-40-q2", "赛跑得了第 1 名，就是——",
                  [(None, "跑在最前面"), (None, "跑在最后"), (None, "没参加")], 0,
                  "第 1 名最厉害", "答对啦！"),
    ]},
    {"id": "math-41", "title": "第 42 找规律", "subtitle": "变化规律", "steps": [
        pattern_step("math-41-p1", ["star", "moon", "star", "moon", "star"], ["moon", "sun", "comet"], 0, "找规律：下一个是谁？"),
        pattern_step("math-41-p2", ["apple", "apple", "banana", "apple", "apple"], ["banana", "apple", "cake"], 0, "再找一次规律：下一个是谁？"),
    ]},
    {"id": "math-42", "title": "第 43 相邻数", "subtitle": "数的邻居", "steps": [
        neighbor_step("math-42-n1", 6, 7),
        neighbor_step("math-42-n2", 3, 4),
    ]},
    {"id": "math-43", "title": "第 44 看图列式", "subtitle": "加法应用", "steps": [
        arith_step(4301, "+", 3, 2, [4, 5, 6], "apple", "个", "3 个苹果加 2 个苹果，一共几个？"),
        arith_step(4302, "+", 4, 1, [4, 5, 6], "star", "颗", "4 颗星加 1 颗星，一共几颗？"),
    ]},
    {"id": "math-44", "title": "第 45 认识人民币", "subtitle": "元角分", "steps": [
        quiz_step("math-44-q1", "买铅笔要 1 元，哪个钱币正好？", [("m-yuan1", "1 元"), ("m-jiao1", "1 角"), ("m-yuan10", "10 元")], 0,
                  "1 元 = 10 角", "对，1 元正好！"),
        money_step("math-44-m", 8, "买 8 角的橡皮，刚好付清"),
    ]},
    {"id": "math-45", "title": "第 46 整点复习", "subtitle": "钟表", "steps": [
        clock_step("math-44-c1", "read", 8, 0, ["3:00", "8:00", "5:30"], 1,
                   "看钟面：时针指 8、分针指 12，是几点？"),
        clock_step("math-45-c2", "read", 3, 30, ["3:00", "3:30", "6:00"], 1,
                   "再看：分针指 6，是几点半？"),
    ]},
]

# —— v0.12 二年级数学 +50 关（人教二上：乘法口诀/长度/角/观察物体；二下：除法/克千克/万以内）——
def mul_step(i, groups, per, icon):
    return {"id": f"math-x{ i }-m", "kind": "muldiv", "op": "×", "mode": "groups",
            "groups": groups, "per": per, "icon": icon,
            "question": f"{groups} 个 {per} 是多少？",
            "options": sorted({groups * per - 2, groups * per - 1, groups * per, groups * per + 1, groups * per + 2})[:3] + [groups * per] if groups * per not in sorted({groups * per - 2, groups * per - 1, groups * per, groups * per + 1, groups * per + 2})[:3] else sorted({groups * per - 2, groups * per - 1, groups * per, groups * per + 1, groups * per + 2})[:3],
            "answer": 3, "hint": f"{groups}×{per}={groups*per}，口诀别忘掉", "praise": f"对，{groups*per}！"}

def mulq_step(qid, a, b, opts, ans):
    return {"id": qid, "kind": "quiz",
            "question": f"{a} × {b} = ?（想口诀）",
            "options": [{"text": str(v)} for v in opts], "answer": ans,
            "hint": f"{a}{b} 的口诀", "praise": f"对，{a*b}！"}

def div_step(qid, total, groups, icon, variant=0):
    per = total // groups
    # variant：同关两题的题面要能区分（0=平均分 / 1=按每份分），
    # 否则同关出现两句完全相同的题面，孩子会以为题目卡住了（v0.12 修）。
    if variant == 1:
        q = f"每 {groups} 个一份，{total} 个能分成几份？"
        hint = f"几个一份几个一份地数：{groups}、{groups*2}…"
    else:
        q = f"{total} 个{icon}平均分成 {groups} 组，每组几个？"
        hint = "平均分，每份一样多"
    return {"id": qid, "kind": "muldiv", "op": "÷", "mode": "average",
            "total": total, "groups": groups, "icon": icon,
            "question": q,
            "options": [per - 1, per, per + 1], "answer": 1,
            "hint": hint, "praise": f"对，每组 {per} 个！"}

MUL_TABLE = [
    ("math-46", "乘法口诀·2", "二二得四起步", [("ball","皮球成对"),("dice","2 的口诀")], 2, [1,2,3,4,5]),
    ("math-47", "乘法口诀·3", "三七二十一", [("train","3 节车厢")], 3, [1,3,5,6,7]),
    ("math-48", "乘法口诀·4", "四四十六", [("apple","4 个苹果")], 4, [2,4,6,8]),
    ("math-49", "乘法口诀·5", "三五十五", [("starface","5 角星")], 5, [1,3,5,7]),
    ("math-50", "乘法口诀·6", "六六三十六", [("dice","骰子六面")], 6, [2,4,6]),
    ("math-51", "乘法口诀·7", "七七四十九", [("calendar","一周七天")], 7, [3,5,7]),
    ("math-52", "乘法口诀·8", "八八六十四", [("block","8 块积木"),("flag","8 面旗")], 8, [2,4,8]),
    ("math-53", "乘法口诀·9", "九九八十一", [("flower","九宫格花瓣")], 9, [3,6,9]),
]
for gi, (mid, title, subtitle, icons, base, mults) in enumerate(MUL_TABLE):
    steps = [{"id": f"{mid}-t", "kind": "letter", "letters": [f"{base} 的乘法口诀"], "display": f"{base} 的口诀",
              "examples": [{"text": f"{base}×{m}={base*m}"} for m in mults[:2]],
              "question": f"背一背：{base} 的乘法口诀"}]
    for k, m in enumerate(mults):
        opts = sorted({base*m-3, base*m-1, base*m, base*m+3})[:3] if base*m % 2 == 0 else sorted({base*m+3, base*m+1, base*m})
        steps.append(mulq_step(f"{mid}-q{k}", base, m, opts, opts.index(base*m)))
    math_levels.append({"id": mid, "title": f"第 {47+gi} 关 {title}", "subtitle": subtitle, "steps": steps[:4]})

DIV_NEW = [
    ("math-54", "认识除法·平均分", [("apple","12 个苹果")], 12, 4),
    ("math-55", "除法·分一分", [("star","15 颗星")], 15, 3),
    ("math-56", "除法·分组", [("duck","10 只鸭")], 10, 5),
    ("math-57", "口诀求商", [("ball","12 个球")], 12, 6),
    ("math-58", "除法·装袋", [("candy","16 颗糖")], 16, 4),
]
for gi, (mid, title, icons, total, groups) in enumerate(DIV_NEW):
    math_levels.append({"id": mid, "title": f"第 {55+gi} 关 {title}", "subtitle": "平均分 · 口诀求商", "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["除法"], "display": "除法",
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：把 {total} 平均分成 {groups} 份"},
        div_step(f"{mid}-d1", total, groups, icons[0][0] if icons else "apple"),
        div_step(f"{mid}-d2", min(total, 12), groups, icons[0][0] if icons else "apple", variant=1),
    ]})

# 长度单位（厘米/米）
LENGTH = [
    ("math-59", "认识厘米", "厘米 cm", [("book","铅笔和课本")], "量短东西用厘米", "量铅笔长度用——", [(None,"厘米"),(None,"米"),(None,"千克")], 0),
    ("math-60", "认识米", "米 m", [("home","教室门高约 2 米")], "量长东西/身高用米", "教室的门高约 2——", [(None,"米"),(None,"厘米"),(None,"克")], 0),
    ("math-61", "厘米和米", "1 米 = 100 厘米", [("train","操场跑道")], "1 米 = 100 厘米", "1 米 = ? 厘米", [(None,"100"),(None,"10"),(None,"1000")], 0),
    ("math-62", "选单位", "填 cm 还是 m", [("girl","小明身高 128 厘米")], "结合生活选单位", "小猫尾巴长约 30——", [(None,"厘米"),(None,"米"),(None,"克")], 0),
    ("math-63", "估一估", "先估再量", [("book","课本长约 26 厘米")], "估一估课本文长度", "课本长约——", [(None,"26 厘米"),(None,"26 米"),(None,"26 克")], 0),
    ("math-64", "比长短", "拉直再比", [("hanger","衣架拉直比")], "比长短要拉直、一端对齐", "比两条绳子长短，要先——", [(None,"拉直对齐"),(None,"随便放"),(None,"数颜色")], 0),
]
for gi, (mid, title, subtitle, icons, fact, q, opts, ans) in enumerate(LENGTH):
    math_levels.append({"id": mid, "title": f"第 {60+gi} 关 {title}", "subtitle": subtitle, "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["长度"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        quiz_step(f"{mid}-q1", q, opts, ans, subtitle, "量一量小能手！"),
    ]})

# 角的初步认识
ANGLE = [
    ("math-65", "认识角", "一个顶点两条边", [("triangle","三角有角"),("square","方角")], "角有一个顶点和两条直边", "角有——", [(None,"一个顶点两条边"),(None,"两条弯边"),(None,"没有顶点")], 0),
    ("math-66", "直角", "方方正正直角", [("square","正方形四个直角"),("clock","钟面直角")], "正方形的四个角都是直角", "哪个图形有直角？", [("square","正方形"),("circle","圆"),("ball","球")], 0),
    ("math-67", "找角", "生活里的角", [("book","书角"),("home","门角")], "书本、门框都有角", "下面哪里有角？", [(None,"书的角上"),(None,"圆球上"),(None,"月亮上")], 0),
]
for gi, (mid, title, subtitle, icons, fact, q, opts, ans) in enumerate(ANGLE):
    math_levels.append({"id": mid, "title": f"第 {66+gi} 关 {title}", "subtitle": subtitle, "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["角"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        quiz_step(f"{mid}-q1", q, opts, ans, subtitle, "火眼金睛找到角！"),
    ]})

# 克与千克
WEIGHT = [
    ("math-68", "认识克", "克 g", [("coin","一枚硬币约 3 克")], "很轻的东西用克", "一枚硬币约重 3——", [(None,"克"),(None,"千克"),(None,"米")], 0),
    ("math-69", "认识千克", "千克 kg", [("cup","两杯水约 1 千克")], "较重的用千克", "1 千克 = ? 克", [(None,"1000"),(None,"100"),(None,"10")], 0),
    ("math-70", "选重量单位", "克还是千克", [("elephant","大象约 4 吨"),("apple","苹果约 200 克")], "大象用吨，苹果用克", "一个苹果约重——", [(None,"200 克"),(None,"200 千克"),(None,"2 克")], 0),
]
for gi, (mid, title, subtitle, icons, fact, q, opts, ans) in enumerate(WEIGHT):
    math_levels.append({"id": mid, "title": f"第 {69+gi} 关 {title}", "subtitle": subtitle, "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["克 千克"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        balance_step(f"{mid}-b1", "天平秤一秤：西瓜和苹果，哪边更重？", ("ball","大西瓜"), ("apple","苹果"), "left",
                     "大的瓜比苹果重好几倍"),
        quiz_step(f"{mid}-q1", q, opts, ans, subtitle, "重量小达人！"),
    ]})

# 笔算加减（100 以内）+ 万以内 + 应用
CALC = [
    ("math-71", "笔算加法", "相同数位对齐", 35, 24, "+"),
    ("math-72", "笔算加法·进位", "满十进一", 47, 28, "+"),
    ("math-73", "笔算减法", "相同数位对齐", 68, 25, "-"),
    ("math-74", "笔算减法·退位", "退一当十", 82, 47, "-"),
    ("math-75", "连加连减", "从左往右算", 30, 18, "+"),
]
for gi, (mid, title, tip, a, b, op) in enumerate(CALC):
    correct = a + b if op == "+" else a - b
    math_levels.append({"id": mid, "title": f"第 {72+gi} 关 {title}", "subtitle": "100 以内", "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["竖式"], "display": title,
         "examples": [{"text": f"{a} {op} {b} = {correct}"}],
         "question": f"学一学：{tip}"},
        arith_step(7100 + gi, op, a, b, sorted({correct - 2, correct - 1, correct, correct + 1, correct + 2})[:3] + [correct] if correct not in sorted({correct - 2, correct - 1, correct, correct + 1, correct + 2})[:3] else sorted({correct - 2, correct - 1, correct, correct + 1, correct + 2})[:3],
                   "star", "颗", f"{a} {op} {b} = ?"),
    ]})

WAN = [
    ("math-76", "万以内数·数位", "个十百千万", [("dice","数位表")], "从右往左：个十百千万", "「3」在 3456 的哪一位？", [(None,"千位"),(None,"十位"),(None,"个位")], 0),
    ("math-77", "万以内数·读写", "读数从高位起", [("chart","3020 读作")], "中间有 0 要读零", "3020 读作——", [(None,"三千零二十"),(None,"三千二十"),(None,"三十二十")], 0),
    ("math-78", "比大小", "先比数位", [("equal","1000 和 999")], "位数多的大", "1000 和 999 谁大？", [(None,"1000"),(None,"999"),(None,"一样大")], 0),
    ("math-79", "近似数", "接近的整数", [("school","全校约 2000 人")], "接近整千的数", "1987 接近——", [(None,"2000"),(None,"1000"),(None,"3000")], 0),
]
for gi, (mid, title, subtitle, icons, fact, q, opts, ans) in enumerate(WAN):
    math_levels.append({"id": mid, "title": f"第 {77+gi} 关 {title}", "subtitle": subtitle, "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["万以内"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        quiz_step(f"{mid}-q1", q, opts, ans, subtitle, "数的嗅灵敏！"),
    ]})

APP = [
    ("math-80", "应用·乘车", "够不够坐", [("bus","45 座大巴")], "二(1)班 38 人坐 45 座车", "45 座车坐 38 人，座位——", [(None,"够，还剩 7 个"),(None,"不够"),(None,"正好")], 0),
    ("math-81", "应用·买文具", "付钱算找零", [("m-yuan10","付 10 元")], "10 - 6 = 4", "10 元买 6 元的笔，找——", [(None,"4 元"),(None,"5 元"),(None,"6 元")], 0),
    ("math-82", "应用·分苹果", "每人几个", [("apple","12 个苹果分给 4 人")], "12 ÷ 4 = 3", "12 个苹果平均分给 4 人，每人——", [(None,"3 个"),(None,"4 个"),(None,"2 个")], 0),
    ("math-83", "应用·排队伍", "前后位置", [("train","15 人排队")], "小猴前面 5 人后面 9 人", "队伍一共几人？", [(None,"15 人"),(None,"14 人"),(None,"16 人")], 0),
    ("math-84", "应用·量身高", "厘米记录", [("girl","身高 132 厘米")], "去年 125，今年 132", "长高了——", [(None,"7 厘米"),(None,"17 厘米"),(None,"70 厘米")], 0),
]
for gi, (mid, title, subtitle, icons, fact, q, opts, ans) in enumerate(APP):
    math_levels.append({"id": mid, "title": f"第 {82+gi} 关 {title}", "subtitle": subtitle, "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["应用题"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        quiz_step(f"{mid}-q1", q, opts, ans, subtitle, "应用题小能手！"),
    ]})

# —— v0.12 补充：观察物体 / 口诀巩固 / 除法应用 / 米尺练习（凑足 96 正则）——
MATH_EXTRA = [
    ("math-85", "观察物体·前面", [("robot","小机器人的前面")], "从前看机器人，看到的是正脸", "从前面看，看到——", [(None,"正脸"),(None,"后脑勺"),(None,"侧面")], 0),
    ("math-86", "观察物体·后面", [("robot","机器人的后面")], "从后面看，看到的是后脑勺", "从后面看，看到——", [(None,"后脑勺"),(None,"正脸"),(None,"脚底")], 0),
    ("math-87", "观察物体·侧面", [("dino","小恐龙的侧面")], "从侧面看，只看到半边", "从侧面看，看到——", [(None,"半边身体"),(None,"正脸"),(None,"全身两面")], 0),
    ("math-88", "口诀巩固·连线", [("train","3×4=?")], "三七二十一", "3×4=——", [(None,"12"),(None,"7"),(None,"14")], 0),
    ("math-89", "口诀巩固·五五", [("starface","五五二十五")], "五五二十五", "5×5=——", [(None,"25"),(None,"10"),(None,"55")], 0),
    ("math-90", "除法应用·装盒", [("egg","18 个鸡蛋")], "18 个鸡蛋每盒装 6 个", "需要几个盒子？", [(None,"3 个"),(None,"6 个"),(None,"2 个")], 0),
    ("math-91", "除法应用·分书", [("book","24 本书")], "24 本书分给 6 个小组", "每组几本？", [(None,"4 本"),(None,"6 本"),(None,"3 本")], 0),
    ("math-92", "米尺应用·跳远", [("frog","小青蛙跳远")], "小青蛙跳了 95 厘米", "95 厘米 接近——", [(None,"1 米"),(None,"1 厘米"),(None,"10 米")], 0),
    ("math-93", "米尺应用·身高", [("girl","兄妹比身高")], "哥哥 130 厘米，妹妹 120 厘米", "哥哥比妹妹高——", [(None,"10 厘米"),(None,"100 厘米"),(None,"1 厘米")], 0),
    ("math-94", "角练习·数角", [("triangle","三角形"),("square","正方形")], "三角形 3 个角，正方形 4 个角", "正方形有几个角？", [(None,"4 个"),(None,"3 个"),(None,"5 个")], 0),
    ("math-95", "克千克·比轻重", [("cup","1 千克水"),("coin","3 克硬币")], "1 千克 = 1000 克", "1 千克和 3 克谁重？", [(None,"1 千克"),(None,"3 克"),(None,"一样重")], 0),
]
for gi, (mid, title, icons, fact, q, opts, ans) in enumerate(MATH_EXTRA):
    math_levels.append({"id": mid, "title": f"第 {86+gi} 关 {title}", "subtitle": "二年级数学", "steps": [
        {"id": f"{mid}-t", "kind": "letter", "letters": ["数学"], "display": title,
         "examples": [{"icon": ic, "text": t} for ic, t in icons],
         "question": f"学一学：{fact}"},
        quiz_step(f"{mid}-q1", q, opts, ans, fact, "数学小达人！"),
    ]})

append_extras(math_levels, [
    ("math-0", balance_step("math-x1", "天平秤一秤：大象和小鸟，哪边更重？",
                            ("elephant","大象"), ("duck","小鸟"), "left",
                            "大象是陆地上最重的动物")),
    ("math-5", sequence_step("math-x2", "按 1→2→3→4 顺序点，小火车出发！", ["1","2","3","4"],
                             praise="呜呜——小火车开动啦！")),
    ("math-32", tapall_step("math-x3", "点点看：把双数都点亮",
                            [(None,"2",True),(None,"4",True),(None,"6",True),
                             (None,"1",False),(None,"3",False),(None,"5",False)],
                            "能两个两个分完的是双数")),
    ("math-33", match_step("math-x4", "连一连：形状和它的特点",
                           [("circle","圆形","没有角，滚滚圆"),("triangle","三角形","有三条边"),("square","正方形","四条边一样长")])),
])
finish_levels(math_levels, "math", 100)
assign_letter_anims(math_levels, "math", "story")
W("math_levels.json", {"subject": "math", "title": "思维镇", "guide": "fox",
                      "zones": zones_meta(["数与数数", "加减法", "乘法口诀", "除法初步", "长度单位",
                                           "角的初步认识", "克与千克", "图形与钟表", "万以内数", "思维大挑战"],
                                          (["dice", "equal", "train", "block", "hanger",
                                            "triangle", "cup", "clock", "chart", "medal"],
                                           ["点数 · 比较 · 序数", "凑十 · 破十 · 笔算", "二二得四…九九八十一", "平均分 · 口诀求商", "厘米和米",
                                            "顶点 · 边 · 直角", "克 · 千克 · 比轻重", "数独 · 钟表 · 人民币", "数位 · 读写 · 比大小", "应用题 · 总复习"])),
                      "levels": math_levels})

# ================= 拼音 16 关 =================
PY = [
    ("b", [("girl","爸爸 bà"),("banana","白菜 bái")], "b", "a", ["ba","bo","bu"]),
    ("p", [("volcano","山坡 pō"),("rocket","跑步 pǎo")], "p", "o", ["po","pa","pi"]),
    ("m", [("girl","妈妈 mā"),("moon","米粒 mǐ")], "m", "a", ["ma","mo","mu"]),
    ("f", [("flame","发烧 fā"),("leaf","飞机 fēi")], "f", "a", ["fa","fo","fu"]),
    ("d", [("sun","大地 dì"),("duck","大刀 dāo")], "d", "e", ["de","da","du"]),
    ("t", [("train","太阳 tài"),("tree","跳高 tiào")], "t", "a", ["ta","te","tu"]),
    ("n", [("girl","拿苹果 ná"),("heart","你好 nǐ")], "n", "i", ["ni","na","nu"]),
    ("l", [("leaf","拉手 lā"),("gift","老虎 lǎo")], "l", "a", ["la","le","lu"]),
    ("g", [("tree","哥哥 gē"),("moon","故事 gù")], "g", "e", ["ge","ga","gu"]),
    ("k", [("heart","开心 kāi"),("book","看书 kàn")], "k", "e", ["ke","ka","ku"]),
]
ICON_POOL = ["duck","sun","moon","cake","star","train","candy","apple","heart","clock"]

def py_listen_letter(i, letter):
    others = ["d","p","m","f","t","n","l","g","k","b"]
    dis = [x for x in others if x != letter][:2]
    opts = dis + [letter]
    ans = opts.index(letter)
    return {"id": f"py-{i}-l", "kind": "listen", "prompt": letter, "speakText": letter,
            "question": f"找一找：哪个是「{letter}」？",
            "options": [{"text": t} for t in opts], "answer": ans,
            "hint": "想一想它的样子", "praise": f"「{letter}」找对啦！"}

def py_listen_pic_to_initial(i, letter, ex0):
    icon, text = ex0
    word = text.split(" ")[0]
    others = ["d","p","m","f","t","n","l","g","k","b"]
    dis = [x for x in others if x != letter]
    d1, d2 = dis[(i * 2) % len(dis)], dis[(i * 2 + 1) % len(dis)]
    pos = i % 3
    opts, ans = rot([{"text": letter}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"py-{i}-l2", "kind": "listen", "promptIcon": icon, "speakText": letter,
            "question": f"看一看：「{word}」的开头是哪个声母？",
            "options": opts, "answer": ans,
            "hint": f"{word} 的第一个音", "praise": f"对！{word} 开头是 {letter}"}

def py_blend(i, b0, b1, blends):
    return {"id": f"py-{i}-b", "kind": "blend", "parts": [b0, b1],
            "question": f"拼一拼：{b0} — {b1} = ?",
            "options": [{"text": t} for t in blends], "answer": 0,
            "hint": f"{b0} 碰上 {b1}", "praise": f"拼对了，{blends[0]}！"}

def py_pic_quiz(i, letter, ex0, b0, b1):
    icon, text = ex0
    word = text.split(" ")[0]
    dis = [x for x in ICON_POOL if x != icon]
    d1 = dis[(i * 3) % len(dis)]
    d2 = dis[(i * 3 + 2) % len(dis)]
    pos = (i + 1) % 3
    opts, ans = rot([{"icon": icon, "text": word}, {"icon": d1}, {"icon": d2}], 0, pos)
    return {"id": f"py-{i}-pq", "kind": "quiz",
            "question": f"拼一拼 {b0} — {b1}：哪张图是「{word}」？",
            "options": opts, "answer": ans,
            "hint": f"{b0} 碰 {b1}", "praise": f"拼读小能手：{word}！"}

pinyin_levels = []
for i, (letter, examples, b0, b1, blends) in enumerate(PY):
    steps = [{"id": f"py-{i}-t", "kind": "letter", "letters": [letter], "display": letter,
              "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} for ic, t in examples],
              "question": f"学一学声母 {letter}"}]
    combo = i % 4
    if combo == 0:
        steps += [py_listen_letter(i, letter), py_blend(i, b0, b1, blends)]
    elif combo == 1:
        steps += [py_listen_pic_to_initial(i, letter, examples[0]), py_blend(i, b0, b1, blends)]
    elif combo == 2:
        steps += [py_pic_quiz(i, letter, examples[0], b0, b1), py_listen_letter(i, letter)]
    else:
        steps += [py_blend(i, b0, b1, blends), py_pic_quiz(i, letter, examples[0], b0, b1)]
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 声母", "subtitle": f"认识「{letter}」", "steps": steps})

pinyin_levels.append({"id": "py-10", "title": "第 11 关 韵母", "subtitle": "a o e i u ü", "steps": [
    {"id": "py-10-t", "kind": "letter", "letters": ["a","o","e","i","u","ü"], "display": "a",
     "examples": [{"icon": "duck", "text": "啊 ā 张大嘴", "say": "ā"}, {"icon": "flame", "text": "哦 ó", "say": "ó"}],
     "question": "学一学韵母 a"},
    {"id": "py-10-l", "kind": "listen", "prompt": "a", "speakText": "a",
     "question": "找一找：哪个是韵母「a」？",
     "options": [{"text": t} for t in ["o","a","e"]], "answer": 1,
     "hint": "张大嘴巴 āāā", "praise": "韵母 a 找对啦！"},
]})
pinyin_levels.append({"id": "py-11", "title": "第 12 关 复习", "subtitle": "整体认读 · 拼读", "steps": [
    memory_step("py-11-m", "翻翻牌：声母和它的图片配成对", [
        ("b", "girl", None, None, "b"),
        ("d", "duck", None, None, "d"),
        ("l", "leaf", None, None, "l"),
    ]),
    {"id": "py-11-l1", "kind": "listen", "prompt": "zhi", "speakText": "zhi",
     "question": "找一找：哪个是「zhi」？",
     "options": [{"text": t} for t in ["chi","zhi","zi"]], "answer": 1,
     "hint": "蜘蛛 zhī zhī 叫", "praise": "整体认读 zhi！"},
    {"id": "py-11-b", "kind": "blend", "parts": ["b","a"],
     "question": "拼一拼：b — a = ?",
     "options": [{"text": t} for t in ["ba","bo","pa"]], "answer": 0,
     "hint": "爸爸的爸", "praise": "拼读小能手！"},
    {"id": "py-11-pq", "kind": "quiz",
     "question": "拼一拼 m — a：哪张图是「妈妈」？",
     "options": [{"icon": "girl", "text": "妈妈"}, {"icon": "moon"}, {"icon": "train"}], "answer": 0,
     "hint": "m 碰 a", "praise": "拼读小达人！"},
]})

# —— v0.11 拼音 50 关扩容：13 新声母 + 单韵母/复韵母/鼻韵母/整体认读/标调/三拼 ——
def py_letter_level(i, display, letters, examples, anim=None):
    st = {"id": f"py-{i}-t", "kind": "letter", "letters": letters, "display": display,
          "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} if ic else {"text": t} for ic, t in examples],
          "question": f"学一学：{display}"}
    if anim:
        st["anim"] = anim
    return st

# 13 个新声母（h→w），沿用既有题型轮换
NEW_INITIALS = [
    ("h", [("flame","火红 huǒ"),("river","小河 hé")], "h", "e", ["he","ha","hu"]),
    ("j", [("home","回家 jiā"),("duck","母鸡 jī")], "j", "i", ["ji","ju","ja"]),
    ("q", [("balloon","气球 qì"),("apple","七 qī")], "q", "i", ["qi","qu","qa"]),
    ("x", [("star","星星 xīng"),("banana","香蕉 xiāngjiāo")], "x", "i", ["xi","xu","xa"]),
    ("zh", [("pig","小猪 zhū"),("bee","蜘蛛 zhī")], "zh", "i", ["zhi","zhu","zha"]),
    ("ch", [("bee","虫虫 chóng"),("car","开车 chē")], "ch", "i", ["chi","chu","cha"]),
    ("sh", [("lion","狮子 shī"),("sun","上山 shàng")], "sh", "i", ["shi","shu","sha"]),
    ("r", [("sun","日出 rì"),("girl","人多 rè")], "r", "i", ["ri","ru","re"]),
    ("z", [("sunrise","早起 zǎo"),("rock","坐 zuò")], "z", "i", ["zi","zu","za"]),
    ("c", [("leaf","草地 cǎo"),("crystal","刺 cì")], "c", "i", ["ci","cu","ca"]),
    ("s", [("star","三十 sān"),("paw","四十 sì")], "s", "i", ["si","su","se"]),
    ("y", [("fish","小鱼 yú"),("duck","鸭子 yā")], "y", "i", ["yi","yu","ya"]),
    ("w", [("frog","青蛙 wā"),("home","屋子 wū")], "w", "u", ["wu","wa","wo"]),
]
for k, (letter, examples, b0, b1, blends) in enumerate(NEW_INITIALS):
    i = 16 + k
    steps = [py_letter_level(i, letter, [letter], examples, anim="pydraw")]
    combo = k % 3
    if combo == 0:
        steps += [py_listen_letter(i, letter), py_blend(i, b0, b1, blends)]
    elif combo == 1:
        steps += [py_listen_pic_to_initial(i, letter, examples[0]), py_pic_quiz(i, letter, examples[0], b0, b1)]
    else:
        steps += [py_blend(i, b0, b1, blends), py_listen_letter(i, letter)]
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 声母", "subtitle": f"认识「{letter}」", "steps": steps})

def py_level_full(i, title, subtitle, letter_disp, letters, examples, anim, practice):
    steps = [py_letter_level(i, letter_disp, letters, examples, anim=anim)] + practice
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 {title}", "subtitle": subtitle, "steps": steps})

# 单韵母 o e / i u / ü（3 关）
py_level_full(29, "单韵母 o e", "o e", "o e", ["o","e"],
              [(None,"哦 ó 拔萝卜"), (None,"鹅 é 鹅 é"),], "pydraw",
              [{"id": "py-29-l", "kind": "listen", "prompt": "o", "speakText": "o",
                "question": "找一找：哪个是韵母「o」？",
                "options": [{"text": t} for t in ["e","o","a"]], "answer": 1,
                "hint": "嘴巴圆圆 ó", "praise": "韵母 o 找对啦！"},
               quiz_step("py-29-q", "大公鸡怎么叫？",
                         [(None,"ō ō ō"),(None,"ā ā ā"),(None,"ū ū ū")], 0, "喔喔啼", "对，公鸡 ō ō 啼！")])
py_level_full(30, "单韵母 i u", "i u", "i u", ["i","u"],
              [("girl","衣服 yīfu"), ("home","屋子 wū")], "pydraw",
              [{"id": "py-30-b", "kind": "blend", "parts": ["d","i"],
                "question": "拼一拼：d — i = ?", "options": [{"text": t} for t in ["di","du","da"]], "answer": 0,
                "hint": "弟弟 dìdì", "praise": "拼对了，dì！"},
               {"id": "py-30-b2", "kind": "blend", "parts": ["w","u"],
                "question": "拼一拼：w — u = ?", "options": [{"text": t} for t in ["wu","wa","wo"]], "answer": 0,
                "hint": "屋子 wū", "praise": "拼对了，wū！"}])
py_level_full(31, "单韵母 ü", "ü", "ü", ["ü"],
              [("fish","小鱼 yú 吹泡泡")], "pydraw",
              [quiz_step("py-31-q", "小 ü 见到 j q x，帽子要——", [(None,"摘掉再握手"),(None,"一直戴着"),(None,"反过来戴")], 0, "j q x 从不跟 ü 戴帽相拼", "答对啦，小 ü 有礼貌！"),
               {"id": "py-31-l", "kind": "listen", "prompt": "ü", "speakText": "ü",
                "question": "找一找：哪个是韵母「ü」？",
                "options": [{"text": t} for t in ["u","ü","i"]], "answer": 1,
                "hint": "小鱼吐泡泡 ǖ ǘ ǚ ǜ", "praise": "韵母 ü 找对啦！"}])

# 复韵母 ai ei ui / ao ou iu / ie üe er（3 关）
py_level_full(32, "复韵母 ai ei ui", "ai ei ui", "ai ei ui", ["ai","ei","ui"],
              [("girl","阿姨 āyí"), ("speaker","飞 fēi"), ("crystal","水 uǐ")], "merge",
              [{"id": "py-32-b", "kind": "blend", "parts": ["l","ai"],
                "question": "拼一拼：l — ai = ?", "options": [{"text": t} for t in ["lai","lai?","li"]], "answer": 0,
                "hint": "来 lái", "praise": "拼对了，lái！"},
               quiz_step("py-32-q", "「ui」是哪两个字母手拉手？", [(None,"u + i"),(None,"a + i"),(None,"e + i")], 0, "u 和 i 挨在一起", "答对啦，u+i！")])
py_level_full(33, "复韵母 ao ou iu", "ao ou iu", "ao ou iu", ["ao","ou","iu"],
              [("ball","棉袄 ǎo"), ("sun","藕 ǒu")], "merge",
              [{"id": "py-33-b", "kind": "blend", "parts": ["h","ao"],
                "question": "拼一拼：h — ao = ?", "options": [{"text": t} for t in ["hao","hou","hao?"]], "answer": 0,
                "hint": "好 hǎo", "praise": "拼对了，hǎo！"},
               quiz_step("py-33-q", "小猫喵喵叫，韵母是——", [(None,"ao"),(None,"ou"),(None,"iu")], 0, "喵 miāo 里有 ao", "对，是 ao！")])
py_level_full(34, "复韵母 ie üe er", "ie üe er", "ie üe er", ["ie","üe","er"],
              [("leaf","树叶 yè"), ("moon","月 yuè")], "merge",
              [quiz_step("py-34-q", "「er」单独做韵母时，写成——", [(None,"儿 er（耳朵 er）"),(None,"e"),(None,"r")], 0, "er 是特殊韵母，自己当韵母", "答对啦，儿化音的 er！")])

# 前鼻韵母 an en in un ün（2 关）+ 后鼻韵母 ang eng ing ong（1 关）
py_level_full(35, "前鼻韵母 an en in", "an en in", "an en in", ["an","en","in"],
              [("speaker","天安门 ān"), ("tree","树根 gēn")], "merge",
              [{"id": "py-35-b", "kind": "blend", "parts": ["g","an"],
                "question": "拼一拼：g — an = ?", "options": [{"text": t} for t in ["gan","gan?","gen"]], "answer": 0,
                "hint": "干净 gānjìng", "praise": "拼对了，gān！"},
               quiz_step("py-35-q", "前鼻韵母的尾巴是——", [(None,"n"),(None,"ng"),(None,"g")], 0, "舌尖顶住前上牙：-n", "对，前鼻音收尾 n！")])
py_level_full(36, "前鼻韵母 un ün", "un ün", "un ün", ["un","ün"],
              [("crystal","温 wēn"), ("fish","云 yún")], "merge",
              [{"id": "py-36-b", "kind": "blend", "parts": ["d","un"],
                "question": "拼一拼：d — un = ?", "options": [{"text": t} for t in ["dun","dan","din"]], "answer": 0,
                "hint": "蹲下 dūn", "praise": "拼对了，dūn！"}])
py_level_full(37, "后鼻韵母 ang eng ing ong", "ang eng ing ong", "ang eng ing ong", ["ang","eng","ing","ong"],
              [("star","亮 liàng"), ("bulb","灯 dēng")], "merge",
              [quiz_step("py-37-q", "后鼻韵母的尾巴是——", [(None,"ng"),(None,"n"),(None,"m")], 0, "舌根抬起：-ng，声音响亮", "对，后鼻音 ng！"),
               {"id": "py-37-b", "kind": "blend", "parts": ["g","ong"],
                "question": "拼一拼：g — ong = ?", "options": [{"text": t} for t in ["gong","gan","geng"]], "answer": 0,
                "hint": "公鸡 gōngjī", "praise": "拼对了，gōng！"}])

# 整体认读音节（3 关，16 个一次认读）
py_level_full(38, "整体认读 zhi chi shi ri zi ci si", "zhi chi shi ri zi ci si",
              "zhi chi shi ri zi ci si", ["zhi","chi","shi","ri","zi","ci","si"],
              [("bee","蜘蛛 zhī"), ("sun","日子 rì")], "tone",
              [quiz_step("py-38-q", "整体认读音节要——", [(None,"整个记住，不拆开拼"),(None,"拆成声母和韵母"),(None,"倒着读")], 0, "一口读出，不能拼", "对，整体认读！")])
py_level_full(39, "整体认读 yi wu yu", "yi wu yu", "yi wu yu", ["yi","wu","yu"],
              [("duck","阿姨 yī"), ("home","屋子 wū"), ("fish","鱼 yú")], "tone",
              [quiz_step("py-39-q", "「yī」是几个音节？", [(None,"1 个，整体认读"),(None,"2 个"),(None,"3 个")], 0, "yi 是大 y 带小 i 组成", "答对啦，1 个整体！")])
py_level_full(40, "整体认读 ye yue yuan yin yun ying", "ye yue yuan yin yun ying",
              "ye yue yuan yin yun ying", ["ye","yue","yuan","yin","yun","ying"],
              [("moon","月 yuè"), ("star","夜 yè")], "tone",
              [quiz_step("py-40-q", "夜晚的「yè」，属于——", [(None,"整体认读音节"),(None,"声母"),(None,"三拼音节")], 0, "ye 是整体认读", "对，整体认读 yè！")])

# 标调 / 三拼音节 / 拼读巩固（4 关）
py_level_full(41, "标调小规则", "标调口诀", "ā á ǎ à", ["a"],
              [("girl","ā á ǎ à"), ("paw","à à à")], "tone",
              [quiz_step("py-41-q", "标调口诀：a 母出现不放过——", [(None,"有 a 给 a 戴"),(None,"随便戴"),(None,"都戴")], 0, "没 a 找 o e，i u 并排标在后", "答对啦！"),
               quiz_step("py-41-q2", "hǎo（好）的声调戴在——", [(None,"a 上"),(None,"o 上"),(None,"h 上")], 0, "有 a 给 a 戴", "对，戴在 a 上！")])
py_level_full(42, "三拼音节", "声母+介母+韵母", "gua", ["g","u","a"],
              [(None,"瓜 guā"), ("home","锅 guō")], "merge",
              [quiz_step("py-42-q", "guā（瓜）是几拼音节？", [(None,"三拼：g-u-a"),(None,"两拼：g-a"),(None,"不用拼")], 0, "声母+介母+韵母，三音相连", "答对啦，三拼！")])
py_level_full(43, "拼读巩固一", "声母+复韵母", "bai fei hui", ["b","f","h"],
              [("egg","白 bái"), ("speaker","飞 fēi")], "merge",
              [{"id": "py-43-b", "kind": "blend", "parts": ["f","ei"],
                "question": "拼一拼：f — ei = ?", "options": [{"text": t} for t in ["fei","fa","fi"]], "answer": 0,
                "hint": "飞机 fēijī", "praise": "拼对了，fēi！"},
               {"id": "py-43-b2", "kind": "blend", "parts": ["h","ui"],
                "question": "拼一拼：h — ui = ?", "options": [{"text": t} for t in ["hui","hai","hu"]], "answer": 0,
                "hint": "回 huí", "praise": "拼对了，huí！"}])
py_level_full(44, "拼读巩固二", "声母+鼻韵母", "shan men ling", ["sh","m","l"],
              [("everest","闪 shǎn"), ("bulb","铃 líng")], "merge",
              [{"id": "py-44-b", "kind": "blend", "parts": ["sh","an"],
                "question": "拼一拼：sh — an = ?", "options": [{"text": t} for t in ["shan","sha","sheng"]], "answer": 0,
                "hint": "闪 shǎn 一闪一闪", "praise": "拼对了，shǎn！"}])
py_level_full(45, "韵母大复习", "24 韵母一家亲", "a o e … ong", ["a","o","e","ong"],
              [("star","韵母大家族")], "merge",
              [quiz_step("py-45-q", "汉语拼音一共有几个单韵母？", [(None,"6 个：a o e i u ü"),(None,"3 个"),(None,"23 个")], 0, "六个兄弟排队站", "对，6 个单韵母！"),
               quiz_step("py-45-q2", "声母一共有几个？", [(None,"23 个"),(None,"6 个"),(None,"16 个")], 0, "b p m f … y w", "答对啦，23 个声母！")])

# —— v0.9 新增 4 关：四声 / 复韵母 / 前鼻韵母 / 拼读大挑战 ——
def letter_write(wid, char, strokes, q, praise):
    return {"id": wid, "kind": "write", "char": char, "pinyin": char,
            "strokes": [S(d) for d in strokes], "question": q, "praise": praise}

LETTER_STROKES = {
 "b": ["M50 24 L50 76", "M50 38 Q72 38 72 56 Q72 74 50 74"],
 "a": ["M44 44 Q36 44 36 58 Q36 72 50 72 Q64 72 64 58 Q64 44 50 44", "M64 44 L64 72"],
 "m": ["M34 34 L34 72", "M34 44 Q44 34 50 44 Q56 34 62 44 L62 72"],
 "o": ["M50 38 Q34 44 34 56 Q34 70 50 72 Q66 70 66 56 Q66 44 50 38"],
}

pinyin_levels.append({"id": "py-12", "title": "第 13 关 四声小帽子", "subtitle": "ā á ǎ à", "steps": [
    {"id": "py-12-t", "kind": "letter", "letters": ["ā","á","ǎ","à"], "display": "a",
     "examples": [{"icon": "girl", "text": "mā 妈妈", "say": "mā"},
                  {"icon": "sunrise", "text": "má 麻绳", "say": "má"}],
     "question": "学一学四声：一声平、二声扬、三声拐弯、四声降"},
    {"id": "py-12-l", "kind": "listen", "prompt": "á", "speakText": "á",
     "question": "找一找：哪个是第二声「á」？",
     "options": [{"text": "ā"}, {"text": "á"}, {"text": "à"}], "answer": 1,
     "hint": "二声往上扬", "praise": "第二声找对啦！"},
    quiz_step("py-12-q1","mā 妈妈的「妈」是第几声？",
              [(None,"第一声"),(None,"第二声"),(None,"第四声")],0,"妈妈的妈声音平平的","第一声，真棒！"),
]})
pinyin_levels.append({"id": "py-13", "title": "第 14 关 复韵母", "subtitle": "ai ei ui", "steps": [
    {"id": "py-13-t", "kind": "letter", "letters": ["ai","ei","ui"], "display": "ai",
     "examples": [{"icon": "girl", "text": "āyí 阿姨", "say": "āyí"},
                  {"icon": "gift", "text": "wéijīn 围巾", "say": "wéijīn"}],
     "question": "学一学复韵母 ai ei ui"},
    py_blend(13, "a", "i", ["ai","an","ao"]),
    {"id": "py-13-l", "kind": "listen", "prompt": "ai", "speakText": "ai",
     "question": "找一找：哪个是复韵母「ai」？",
     "options": [{"text": "ai"}, {"text": "ao"}, {"text": "an"}], "answer": 0,
     "hint": "a 和 i 拉手", "praise": "复韵母 ai 找对啦！"},
]})
pinyin_levels.append({"id": "py-14", "title": "第 15 关 前鼻韵母", "subtitle": "an en in", "steps": [
    {"id": "py-14-t", "kind": "letter", "letters": ["an","en","in"], "display": "an",
     "examples": [{"icon": "sunrise", "text": "ān 天安门", "say": "ān"},
                  {"icon": "girl", "text": "rén 人", "say": "rén"}],
     "question": "学一学前鼻韵母 an en in"},
    py_blend(14, "e", "n", ["en","eng","er"]),
    {"id": "py-14-l", "kind": "listen", "prompt": "in", "speakText": "in",
     "question": "找一找：哪个是前鼻韵母「in」？",
     "options": [{"text": "in"}, {"text": "ing"}, {"text": "iu"}], "answer": 0,
     "hint": "舌尖抵上牙床", "praise": "前鼻韵母 in 找对啦！"},
]})
pinyin_levels.append({"id": "py-15", "title": "第 16 关 拼读大挑战", "subtitle": "两拼 · 描红", "steps": [
    memory_step("py-15-m", "翻翻牌：声母和音节配成对", [
        ("b", "girl", None, None, "b"),
        ("m", "moon", None, None, "m"),
        ("d", "duck", None, None, "d"),
    ]),
    py_blend(15, "b", "a", ["ba","bo","pa"]),
    letter_write("py-15-wb", "b", LETTER_STROKES["b"], "描一描字母 b：先竖，再右半圆", "字母 b 写得漂亮！"),
    letter_write("py-15-wo", "o", LETTER_STROKES["o"], "描一描字母 o：从右上起笔画个圆", "字母 o 描圆啦！"),
]})

# —— v0.12 二年级拼音 +50 关：大写字母·音序查字 / 多音字 / 轻声 / 儿化 / 变调 / 平翘舌（部编二上二下）——
def py_abc_level(i, gid, title, letters, ex_pairs, practice):
    steps = []
    if letters:
        st = {"id": f"py-{gid}-t", "kind": "letter", "letters": letters, "display": " ".join(letters[:4]),
              "examples": [{"icon": ic, "text": t, "say": t} if ic else {"text": t} for ic, t in ex_pairs],
              "question": f"学一学：{title}", "anim": "pydraw"}
        steps.append(st)
    pinyin_levels.append({"id": f"py-{gid}", "title": f"第 {i+1} 关 {title}", "subtitle": title, "steps": steps + practice})

def py_polyphonic(i, gid, word, disp, examples, quiz_q, opts, ans, hint):
    pinyin_levels.append({"id": f"py-{gid}", "title": f"第 {i+1} 关 多音字·{word}", "subtitle": disp, "steps": [
        {"id": f"py-{gid}-t", "kind": "letter", "letters": [word], "display": disp,
         "examples": [{"icon": ic, "text": t, "say": t} if ic else {"text": t} for ic, t in examples],
         "question": f"学一学多音字：「{word}」"},
        quiz_step(f"py-{gid}-q1", quiz_q, opts, ans, hint, f"答对啦，{disp}！"),
        quiz_step(f"py-{gid}-q2", f"「{word}」的两个读音你都记住了吗？",
                  [(None, disp.split(" / ")[0]), (None, disp.split(" / ")[1]), (None, disp.split(" / ")[0] + disp.split(" / ")[1])], 0,
                  "一字两读，意思不同", "都记住啦！"),
    ]})

ABC_GROUPS = [
    ("py-a1", "大写字母 A B C D", ["A","B","C","D"], [("apple","A 像 Apple 山尖"),("block","B 像积木"),("cat","C 像弯月"),("dice","D 像半圆")]),
    ("py-a2", "大写字母 E F G H", ["E","F","G","H"], [("egg","E 蛋 Egg"),("flame","F 火 Fire"),("gift","G 礼 Gift"),("heart","H 心 Heart")]),
    ("py-a3", "大写字母 I J K L", ["I","J","K","L"], [("ice","I 冰 Ice"),("jar","J 罐 Jar"),("key","K 钥 Key"),("lion","L 狮 Lion")]),
    ("py-a4", "大写字母 M N O P", ["M","N","O","P"], [("moon","M 月 Moon"),("newmoon","N 月牙"),("circle","O 圆圈"),("panda","P 熊猫 Panda")]),
    ("py-a5", "大写字母 Q R S T", ["Q","R","S","T"], [("question","Q 问题"),("rocket","R 火箭 Rocket"),("sun","S 太阳 Sun"),("train","T 火车 Train")]),
    ("py-a6", "大写字母 U V W", ["U","V","W"], [("cup","U 像杯子"),("volcano","V 山谷"),("wave","W 浪 Wave")]),
    ("py-a7", "大写字母 X Y Z", ["X","Y","Z"], [("star","X 星星闪烁"),("flag","Y 像树杈"),("crystal","Z 闪 Crystal")]),
    ("py-a8", "大小写对照", ["A a","B b","C c"], [("apple","A a 苹果"),("ball","B b 球"),("cat","C c 猫")]),
]
for k, (gid, title, letters, exs) in enumerate(ABC_GROUPS):
    py_abc_level(50 + k, gid, title, letters, exs, [
        quiz_step(f"py-{gid}-q1", f"「{letters[0]}」的小写是哪个？",
                  [(None, letters[0].lower()), (None, letters[0].upper()), (None, letters[1].lower())], 0,
                  "大写小写长得像", "答对啦！"),
        quiz_step(f"py-{gid}-q2", "字母表里谁排在最前面？",
                  [(None, letters[0]), (None, letters[1]), (None, letters[2])], 0,
                  "按 A B C D 顺序", "对，排在最前！"),
    ])

# 音序查字法（4 关）
for k, (gid, title, q, opts, ans, hint) in enumerate([
    ("py-xd1", "音序查字：查「花」", "用音序查字法查「花」，先查大写字母——", [("flower","H"),("sun","S"),("moon","M")], 0, "花 huā，音序 H"),
    ("py-xd2", "音序查字：查「星」", "查「星 xīng」，先查——", [("star","X"),("moon","M"),("flag","F")], 0, "星 xīng，音序 X"),
    ("py-xd3", "音序查字典步骤", "音序查字法第一步是——", [(None,"找音序（第一个大写字母）"),(None,"直接翻书"),(None,"问别人")], 0, "先定音序，再查页码"),
    ("py-xd4", "音序查字：查「城」", "查「城 chéng」，先查——", [("castle","C"),("cat","K"),("book","B")], 0, "城 chéng，音序 C"),
]):
    py_abc_level(58 + k, gid, title, [], [], [
        quiz_step(f"py-{gid}-q", q, opts, ans, hint, "音序查字小能手！")])

# 多音字（8 个，部编二上）
POLY = [
    ("py-d1", "长", "cháng / zhǎng", [("train","长 cháng 长城"),("sprout","长 zhǎng 长大")],
     "「长城」的长读——", [(None,"cháng"),(None,"zhǎng"),(None,"cáng")], 0, "长城很长 cháng"),
    ("py-d2", "乐", "lè / yuè", [("party","快乐 lè"),("speaker","音乐 yuè")],
     "「音乐」的乐读——", [(None,"yuè"),(None,"lè"),(None,"yuē")], 0, "音乐 yuè"),
    ("py-d3", "行", "xíng / háng", [("rocket","行走 xíng"),("train","银行 háng")],
     "「银行」的行读——", [(None,"háng"),(None,"xíng"),(None,"hàng")], 0, "银行 háng"),
    ("py-d4", "只", "zhī / zhǐ", [("bird","一只 zhī"),(None,"只有 zhǐ")],
     "「一只鸟」的只读——", [(None,"zhī"),(None,"zhǐ"),(None,"zī")], 0, "一只 zhī"),
    ("py-d5", "好", "hǎo / hào", [("heart","好人 hǎo"),(None,"爱好 hào")],
     "「爱好」的好读——", [(None,"hào"),(None,"hǎo"),(None,"háo")], 0, "爱好 hào"),
    ("py-d6", "都", "dōu / dū", [("party","都是 dōu"),("castle","首都 dū")],
     "「首都」的都读——", [(None,"dū"),(None,"dōu"),(None,"dú")], 0, "首都 dū"),
    ("py-d7", "种", "zhǒng / zhòng", [("sprout","种子 zhǒng"),("sprout","种树 zhòng")],
     "「种树」的种读——", [(None,"zhòng"),(None,"zhǒng"),(None,"chóng")], 0, "种树 zhòng"),
    ("py-d8", "教", "jiāo / jiào", [("girl","教书 jiāo"),("book,"  if False else "book","教室 jiào")],
     "「教室」的教读——", [(None,"jiào"),(None,"jiāo"),(None,"jiē")], 0, "教室 jiàoshì"),
]
for k, (gid, word, disp, exs, q, opts, ans, hint) in enumerate(POLY):
    py_polyphonic(66 + k, gid, word, disp, exs, q, opts, ans, hint)

# 轻声（3）· 儿化（3）· 变调（4）· 平翘舌（4）· 前后鼻音（3）· 整体认读巩固（3）· 拼读儿歌（8）
LIGHT = [
    ("py-q1", "轻声·叠词", "妈妈 māma / 爸爸 bàba", "叠词第二个字读轻声", "妈妈 的 妈 读——", [(None,"mā"),(None,"ma 轻声"),(None,"mà")], 1),
    ("py-q2", "轻声·词尾", "东西 dōngxi / 地方 dìfang", "词尾的字常读轻声", "「地方」的方读——", [(None,"fāng"),(None,"fang 轻声"),(None,"fáng")], 1),
    ("py-q3", "轻声·助词", "走了 zǒu le / 好吗 hǎo ma", "吗、了、呢 读轻声", "「好吗」的吗读——", [(None,"má"),(None,"ma 轻声"),(None,"mǎ")], 1),
]
ERHUA = [
    ("py-e1", "儿化·花儿", "花儿 huār", "花儿连读，r 别分开", "「花儿」读——", [(None,"huā ér 分开"),(None,"huār 连读"),(None,"huǒ")], 1),
    ("py-e2", "儿化·鸟儿", "鸟儿 niǎor", "鸟儿 r 轻轻带上", "「鸟儿」读——", [(None,"niǎo èr"),(None,"niǎor 连读"),(None,"niǎo")], 1),
    ("py-e3", "儿化·一点儿", "一点儿 yìdiǎnr", "一点儿 带上小 r", "「一点儿」读——", [(None,"yìdiǎnr 连读"),(None,"yī diǎn"),(None,"yìdiǎn ér")], 0),
]
SANDHI = [
    ("py-b1", "「一」的变调", "一个 yí gè", "一 在四声前读 yí", "「一个」读——", [(None,"yí gè"),(None,"yī gè"),(None,"yì gè")], 0),
    ("py-b2", "「一」的变调", "一天 yì tiān", "一 在一声前读 yì", "「一天」读——", [(None,"yì tiān"),(None,"yī tiān"),(None,"yí tiān")], 0),
    ("py-b3", "「不」的变调", "不是 bú shì", "不 在四声前读 bú", "「不是」读——", [(None,"bú shì"),(None,"bù shì"),(None,"bū shì")], 0),
    ("py-b4", "三声变调", "你好 nǐ hǎo", "两个三声相连，前变二声", "「你好」实际读——", [(None,"ní hǎo"),(None,"nǐ hǎo"),(None,"nì hǎo")], 0),
]
FLATS = [
    ("py-f1", "平舌 z c s", "自 zì / 从 cóng / 四 sì", "舌尖放平：z c s", "「四」的声母是——", [(None,"s 平舌"),(None,"sh 翘舌"),(None,"c")], 0),
    ("py-f2", "翘舌 zh ch sh", "知 zhī / 吃 chī / 狮 shī", "舌尖翘起：zh ch sh", "「狮」的声母是——", [(None,"sh 翘舌"),(None,"s 平舌"),(None,"x")], 0),
    ("py-f3", "z c s vs zh ch sh", "早 zǎo vs 找 zhǎo", "平翘不同，意思不同", "「早」的声母是——", [(None,"z"),(None,"zh"),(None,"c")], 0),
    ("py-f4", "r 声母", "日 rì / 热 rè", "r 也是翘舌", "「日」的声母是——", [(None,"r"),(None,"l"),(None,"y")], 0),
]
NASALS = [
    ("py-n1", "前鼻 an en", "山 shān / 人 rén", "前鼻收尾 n", "「山」的韵母是——", [(None,"an 前鼻"),(None,"ang 后鼻"),(None,"ai")], 0),
    ("py-n2", "后鼻 ang eng", "亮 liàng / 灯 dēng", "后鼻收尾 ng，声音响", "「灯」的韵母是——", [(None,"eng 后鼻"),(None,"en 前鼻"),(None,"ei")], 0),
    ("py-n3", "前后鼻对比", "陈 chén vs 城 chéng", "n 舌尖、ng 舌根", "「城」的韵母是——", [(None,"eng 后鼻"),(None,"en 前鼻"),(None,"un")], 0),
]
WHOLE = [
    ("py-w1", "整体认读复习", "zhi chi shi ri", "一口读出不拆开", "下面哪个是整体认读？", [(None,"shi"),(None,"sh"),(None,"sha")], 0),
    ("py-w2", "整体认读复习", "yi wu yu", "y 和 w 开头也整体读", "下面哪个是整体认读？", [(None,"yu"),(None,"y+u 拼读"),(None,"iu")], 0),
    ("py-w3", "整体认读复习", "yuan yin yun ying", "16 个整体认读要记牢", "「音 yīn」是——", [(None,"整体认读"),(None,"声母"),(None,"三拼")], 0),
]
EXTRA2 = [
    ("py-e4", "儿化·画儿", "画儿 huàr", "画儿 也带小 r", "「画儿」读——", [(None,"huàr 连读"),(None,"huà ér"),(None,"huà")], 0),
    ("py-d9", "多音字·地", "土地 dì / 慢慢地 de", "词尾的「地」读轻声 de", "「慢慢地」的地读——", [(None,"de 轻声"),(None,"dì"),(None,"dí")], 0),
]
for group in [EXTRA2]:
    for k, (gid, title, disp, tip, q, opts, ans) in enumerate(group):
        pinyin_levels.append({"id": f"py-{gid}", "title": f"第 {title}", "subtitle": disp, "steps": [
            {"id": f"py-{gid}-t", "kind": "letter", "letters": [disp], "display": disp,
             "examples": [{"text": disp}], "question": f"学一学：{title}"},
            quiz_step(f"py-{gid}-q", q, opts, ans, tip, "拼音小达人！"),
        ]})

SONGS = [
    ("py-g1", "拼读儿歌·数字", "四是四，十是十", "sì shí 分清平翘舌", "「十」读——", [(None,"shí 翘舌"),(None,"sí 平舌"),(None,"sì")], 0),
    ("py-g2", "拼读儿歌·四季", "春季夏天秋冬", "四季 jì 韵母 i", "「春 chūn」的韵母是——", [(None,"un"),(None,"ong"),(None,"uan")], 0),
    ("py-g3", "拼读儿歌·动物", "小熊熊，爬树丛", "熊 xióng 是三拼音节? i ong", "「熊 xióng」是——", [(None,"两拼 xi-ong"),(None,"三拼 x-i-ong"),(None,"整体认读")], 1),
    ("py-g4", "拼读儿歌·自然", "白云飘，太阳照", "飘 piāo 三拼音节", "「飘 piāo」是——", [(None,"三拼 p-i-ao"),(None,"两拼 p-ao"),(None,"整体认读")], 0),
    ("py-g5", "拼读儿歌·校园", "背着书包上学校", "书 shū 包 bāo", "「书 shū」的声母是——", [(None,"sh"),(None,"s"),(None,"x")], 0),
    ("py-g6", "拼读儿歌·问答", "谁的耳朵长？驴的耳朵长", "驴 lǘ 帽点 ü", "「驴 lǘ」遇到 j q x 会——", [(None,"去点变 ju"),(None,"保留两点"),(None,"变 u")], 0),
    ("py-g7", "拼读儿歌·反思", "拼读要看声调号", "声调标在韵母头上", "声调标在哪里？", [(None,"韵母上"),(None,"声母上"),(None,"随便")], 0),
    ("py-g8", "拼读总复习", "拼音学好了，识字本领高", "音序查字典也要用拼音", "拼音帮我们——", [(None,"识字和查字典"),(None,"只做游戏"),(None,"画画")], 0),
]
for group in [LIGHT, ERHUA, SANDHI, FLATS, NASALS, WHOLE, SONGS]:
    for k, (gid, title, disp, tip, q, opts, ans) in enumerate(group):
        pinyin_levels.append({"id": f"py-{gid}", "title": f"第 {title}", "subtitle": disp, "steps": [
            {"id": f"py-{gid}-t", "kind": "letter", "letters": [disp], "display": disp,
             "examples": [{"text": disp}], "question": f"学一学：{title}"},
            quiz_step(f"py-{gid}-q", q, opts, ans, tip, "拼音小达人！"),
        ]})

finish_levels(pinyin_levels, "pinyin", 100)
apply_anims(pinyin_levels, {
    **{f"py-{i}": "pydraw" for i in range(11)},          # 声母/单韵母：铅笔描画字母
    "py-12": "tone",                                      # 四声小帽子：声调符号逐个戴帽
    "py-13": "merge",                                     # 复韵母：两音相拼
    "py-14": "merge",                                     # 前鼻韵母：韵母+n 相拼
})
assign_letter_anims(pinyin_levels, "pinyin", "pydraw")   # v0.12.1：多音字/儿化/轻声等补位
append_extras(pinyin_levels, [
    ("py-1", match_step("py-x1", "连一连：声母和词语",
                        [("cat","m","小猫 māo"),("egg","d","鸡蛋 dàn"),("fish","y","小鱼 yú")])),
    ("py-2", tapall_step("py-x2", "点点看：把声母都点亮",
                         [(None,"b",True),(None,"p",True),(None,"m",True),
                          (None,"a",False),(None,"o",False),(None,"e",False)],
                         "b p m 是声母，a o e 是韵母")),
    ("py-10", sequence_step("py-x3", "按顺序点：a → o → e", ["a","o","e"], praise="单韵母排好队！")),
])
W("pinyin_levels.json", {"subject": "pinyin", "title": "拼音谷", "guide": "panda",
                         "zones": zones_meta(["字母启蒙", "声母闯关", "韵母家族", "整体认读", "音序查字",
                                              "多音字", "轻声与儿化", "变调妙用", "平翘与前后鼻", "拼读大挑战"],
                                             (["book", "speaker", "star", "sparkle", "school",
                                               "equal", "hanger", "bulb", "question", "medal"],
                                              ["A-J 字母与发音", "23 个声母逐关", "单韵母 · 复韵母 · 鼻韵母", "16 个整体认读音节",
                                               "大写字母与查字典", "一字两读", "词尾轻读 · 连读小 r", "一和不的变调", "平翘舌 · 前后鼻", "儿歌拼读总复习"])),
                         "levels": pinyin_levels})

# ================= 英语 24 关 =================
EN_LETTERS = [
    ("Aa", "apple", "Apple 苹果"), ("Bb", "banana", "Banana 香蕉"),
    ("Cc", "cake", "Cake 蛋糕"), ("Dd", "duck", "Duck 小鸭"),
    ("Ss", "sun", "Sun 太阳"), ("Mm", "moon", "Moon 月亮"),
    ("Ff", "flower", "Flower 花"), ("Ll", "leaf", "Leaf 叶子"),
    ("Kk", "key", "Key 钥匙"), ("Hh", "heart", "Heart 爱心"),
    ("Rr", "rainbow", "Rainbow 彩虹"), ("Gg", "gift", "Gift 礼物"),
    # —— v0.11 剑桥少儿英语字母表补全（K-T 等 9 个）——
    ("Ee", "egg", "Egg 蛋"), ("Tt", "train", "Train 火车"),
    ("Pp", "panda", "Panda 熊猫"), ("Ii", "ice", "Ice 冰"),
    ("Oo", "circle", "O 圆圈"), ("Nn", "newmoon", "N 月牙"),
    ("Qq", "question", "Question 问题"), ("Ww", "wave", "Wave 浪花"),
    ("Jj", "jar", "Jar 罐子"),
]

def en_listen_letter(li, disp):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    opts = [others[li % 4], others[(li + 1) % 4], disp]
    ans = opts.index(disp)
    return {"id": f"en-{li}-l", "kind": "listen", "prompt": disp, "speakText": disp[0],
            "question": f"Find: which one is {disp} ?",
            "options": [{"text": t} for t in opts], "answer": ans,
            "hint": f"{disp[0]} for {disp}", "praise": f"Yes! {disp}!"}

def en_pic_quiz(li, disp, icon, word):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    d1, d2 = others[(li + 2) % 8], others[(li + 3) % 8]
    d1i = next(x for x in EN_LETTERS if x[0] == d1)[1]
    d2i = next(x for x in EN_LETTERS if x[0] == d2)[1]
    return {"id": f"en-{li}-q", "kind": "quiz",
            "question": f"Which picture starts with {disp}?",
            "options": [{"icon": d1i}, {"icon": icon}, {"icon": d2i}],
            "answer": 1, "hint": word, "praise": "Great job!"}

def en_case_quiz(li, disp):
    upper, lower = disp[0], disp[1]
    others = [d[0] for d, _, _ in EN_LETTERS if d[0] != upper]
    d1 = others[(li * 2) % len(others)]
    d2 = others[(li * 2 + 1) % len(others)]
    pos = (li + 1) % 3
    opts, ans = rot([{"text": upper}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"en-{li}-c", "kind": "quiz",
            "question": f"小写 {lower} 对应哪个大写字母？",
            "options": opts, "answer": ans,
            "hint": f"{disp} = {upper}{lower}", "praise": f"{upper}{lower} 配对成功！"}

def en_pattern(li, icon):
    others = [ic for _, ic, _ in EN_LETTERS if ic != icon]
    o1 = others[(li * 2) % len(others)]
    o2 = others[(li * 2 + 1) % len(others)]
    seq = [icon, o1, icon]
    opts, ans = rot([{"icon": o1}, {"icon": o2}, {"icon": icon}], 0, li % 3)
    return {"id": f"en-{li}-p", "kind": "pattern", "seq": seq,
            "question": "Pattern: 下一个是谁？",
            "options": opts, "answer": ans,
            "hint": "Who comes next?", "praise": "Pattern star!"}

english_levels = []
for li in range(8):
    disp, icon, word = EN_LETTERS[li]
    steps = [{"id": f"en-{li}-t", "kind": "letter", "letters": [disp[0]], "display": disp,
              "examples": [{"icon": icon, "text": word, "say": word.split(" ")[0]}],
              "question": f"Learn letter {disp}"}]
    combo = li % 4
    if combo == 0:
        steps += [en_listen_letter(li, disp), en_pic_quiz(li, disp, icon, word)]
    elif combo == 1:
        steps += [en_case_quiz(li, disp), en_listen_letter(li, disp)]
    elif combo == 2:
        steps += [en_listen_letter(li, disp), en_pattern(li, icon)]
    else:
        steps += [en_pic_quiz(li, disp, icon, word), en_case_quiz(li, disp)]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} Letters", "subtitle": disp, "steps": steps})
for li, idx in [(8, 10), (9, 11)] + [(24 + k, idx) for k, idx in enumerate(range(12, 21))]:
    disp, icon, word = EN_LETTERS[idx]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} Letters", "subtitle": disp, "steps": [
        {"id": f"en-{li}-t", "kind": "letter", "letters": [disp[0]], "display": disp,
         "examples": [{"icon": icon, "text": word, "say": word.split(" ")[0]}],
         "question": f"Learn letter {disp}"},
        en_case_quiz(li, disp),
        en_pic_quiz(li, disp, icon, word),
    ]})

def word_quiz(wid, q, items, ans, say_hint, praise):
    return {"id": wid, "kind": "quiz", "question": q,
            "options": [{"icon": ic, "text": tx} for tx, ic in items], "answer": ans,
            "hint": say_hint, "praise": praise}

english_levels.append({"id": "en-10", "title": "Level 11 Words", "subtitle": "图词配对", "steps": [
    word_quiz("en-10-q1", "Which one is the sun? 太阳是哪一个？", [("sun","sun"),("moon","moon"),("starface","star")], 0, "Sun 太阳", "Great! It's the sun!"),
    word_quiz("en-10-q2", "Which one is the duck? 小鸭是哪一个？", [("heart","heart"),("duck","duck"),("leaf","leaf")], 1, "Duck 小鸭", "Great! It's a duck!"),
    word_quiz("en-10-q3", "Which one is the apple? 苹果是哪一个？", [("banana","banana"),("cake","cake"),("apple","apple")], 2, "Apple 苹果", "Yes! Apple!"),
]})
english_levels.append({"id": "en-11", "title": "Level 12 Review", "subtitle": "单词复习", "steps": [
    memory_step("en-11-m", "翻翻牌：单词和图片配成对", [
        ("sun", "sun", None, None, "sun"),
        ("moon", "moon", None, None, "moon"),
        ("duck", "duck", None, None, "duck"),
    ]),
    word_quiz("en-11-q1", "Which one is the moon? 月亮是哪一个？", [("moon","moon"),("sun","sun"),("starface","star")], 0, "Moon 月亮", "Yes! Moon!"),
    word_quiz("en-11-q2", "Which one is the flower? 花是哪一个？", [("leaf","leaf"),("flower","flower"),("tree","tree")], 1, "Flower 花", "Yes! Flower!"),
    word_quiz("en-11-q3", "Which one is the cake? 蛋糕是哪一个？", [("gift","gift"),("key","key"),("cake","cake")], 2, "Cake 蛋糕", "Super star! 全部通关!"),
]})

# —— v0.9 新增 12 个主题词场（en-12 .. en-23）——
# (id, title, subtitle, [(icon, english, 中文)], 教学 examples)
EN_TOPICS = [
    ("en-12","Level 13 Animals","动物",[("cat","Cat","猫"),("duck","Duck","鸭"),("rabbit","Rabbit","兔"),("bear","Bear","熊")]),
    ("en-13","Level 14 Colors","颜色",[("apple","Red","红"),("banana","Yellow","黄"),("wave","Blue","蓝"),("leaf","Green","绿")]),
    ("en-14","Level 15 Numbers","数字",[(None,"One","一"),(None,"Two","二"),(None,"Three","三"),(None,"Four","四")]),
    ("en-15","Level 16 Fruits","水果",[("apple","Apple","苹果"),("banana","Banana","香蕉"),("candy","Sweet","甜"),("bread","Bread","面包")]),
    ("en-16","Level 17 Family","家庭",[("girl","Me","我"),("girl","Teacher","老师"),("fox","Fox","狐狸"),("home","Home","家")]),
    ("en-17","Level 18 Body","身体",[("paw","Foot","脚"),("paw","Baby Paw","小脚丫"),("speaker","Mouth","嘴"),("girl","Me","我")]),
    ("en-18","Level 19 Stationery","文具",[("book","Book","书"),("clip","Clip","夹子"),("school","School","学校"),("chart","Chart","图表")]),
    ("en-19","Level 20 Food","食物",[("cake","Cake","蛋糕"),("candy","Candy","糖"),("bread","Bread","面包"),("milk","Milk","牛奶")]),
    ("en-20","Level 21 Clothes","衣物",[("shoe","Shoe","鞋"),("hat","Hat","帽子"),("hanger","Hanger","衣架"),("gift","Gift","礼物")]),
    ("en-21","Level 22 Transport","交通",[("train","Train","火车"),("rocket","Rocket","火箭"),("wave","Wave","浪"),("bus","Bus","公交")]),
    ("en-22","Level 23 Actions","动作",[("girl","Run","跑"),("rabbit","Jump","跳"),("fish","Swim","游"),("apple","Eat","吃")]),
    # —— v0.11 剑桥 Starters 主题词场补 13 个（50 关扩容）——
    ("en-33","Level 34 Toys","玩具",[("ball","Ball","球"),("block","Block","积木"),("dice","Dice","骰子"),("gift","Gift","礼物")]),
    ("en-34","Level 35 Home","家",[("home","Home","家"),("bed","Bed","床"),("cup","Cup","杯子"),("key","Key","钥匙")]),
    ("en-35","Level 36 Weather","天气",[("sun","Sun","太阳"),("moon","Moon","月亮"),("rainbow","Rainbow","彩虹"),("windmill","Windmill","风车")]),
    ("en-36","Level 37 City","城市",[("car","Car","汽车"),("bus","Bus","公交"),("school","School","学校"),("shop","Shop","商店"),("castle","Castle","城堡")]),
    ("en-37","Level 38 Nature","自然",[("tree","Tree","树"),("flower","Flower","花"),("leaf","Leaf","叶子"),("sprout","Sprout","幼苗")]),
    ("en-38","Level 39 Zoo","动物园",[("lion","Lion","狮子"),("tiger","Tiger","老虎"),("monkey","Monkey","猴子"),("elephant","Elephant","大象")]),
    ("en-39","Level 40 Ocean","海洋",[("fish","Fish","鱼"),("wave","Wave","浪"),("penguin","Penguin","企鹅"),("ice","Ice","海冰")]),
    ("en-40","Level 41 Party","派对",[("party","Party","派对"),("gift","Gift","礼物"),("cake","Cake","蛋糕"),("candy","Candy","糖果")]),
    ("en-41","Level 42 Magic","奇妙",[("bulb","Bulb","灯泡"),("magnet","Magnet","磁铁"),("crystal","Crystal","水晶"),("starface","Star","星")]),
    ("en-42","Level 43 Tools","工具",[("key","Key","钥匙"),("magnet","Magnet","磁铁"),("slider","Slider","滑块"),("clip","Clip","夹子")]),
    ("en-43","Level 44 Garden","花园",[("bee","Bee","蜜蜂"),("flower","Flower","花"),("leaf","Leaf","叶"),("tree","Tree","树")]),
    ("en-44","Level 45 Winter","冬天",[("snowflake","Snowflake","雪花"),("ice","Ice","冰"),("polarbear","Polar Bear","北极熊"),("penguin","Penguin","企鹅")]),
    ("en-45","Level 46 Friends","朋友",[("fox","Fox","狐狸"),("frog","Frog","青蛙"),("bear","Bear","熊"),("dino","Dino","恐龙")]),
]
EN_REVIEW_WORDS = [("cat","Cat","猫"),("apple","Apple","苹果"),("train","Train","火车"),("girl","Run","跑")]

def en_topic_level(lid, title, subtitle, words):
    li = int(lid.split("-")[1])
    def _opt(ic, en):
        # ⚠️ 有图标时也必须带 text：关卡页按 examples[0].text 记单词卡，
        #    缺 text 会让 renderLevel 读 undefined.split 崩掉、整关弹回地图（v0.12 修）。
        o = {"text": en}
        if ic:
            o = {"icon": ic, "text": en}
        return o
    examples = [dict(_opt(ic, f"{en} {cn}"), say=en) for ic, en, cn in words]
    steps = [{"id": f"{lid}-t", "kind": "letter", "letters": [words[0][1][0]], "display": words[0][1],
              "examples": examples, "question": f"Learn: {subtitle} 主题单词"}]
    # 听选图：第 1 个词（options 元素为 (text, icon)）
    # ⚠️ 干扰项按索引取，不能按 icon 去重——None 图标的词（星期/月份/数字）会有多个相同 icon，
    #    按 icon 过滤会把它们全删光导致越界（v0.12 修）。
    ic0, en0, cn0 = words[0]
    others = list(words[1:])
    while len(others) < 2:
        others.append(FALLBACK_POOL[len(others) % len(FALLBACK_POOL)])
    d1, d2 = others[0], others[1]
    opts, ans = rot([(en0, ic0), (d1[1], d1[0]), (d2[1], d2[0])], 0, li % 3)
    steps.append({"id": f"{lid}-q1", "kind": "quiz",
                  "question": f"Which one is {en0}? {cn0} 是哪一个？",
                  "options": [_opt(ic, tx) for tx, ic in opts], "answer": ans,
                  "hint": en0, "praise": f"Yes! It's {en0}!"})
    # 翻牌复习：数字等无图标的词场，图片侧退化用主题代表图，
    # ⚠️ 不能直接给 None：memory 牌 icon/text 至少一项（v0.12 validate 会 FAIL）
    pairs = [(w[1], (w[0] or "dice"), None, None, w[1]) for w in words[:3]]
    steps.append(memory_step(f"{lid}-m", "翻翻牌：单词和图片配成对", pairs))
    return {"id": lid, "title": title, "subtitle": subtitle, "steps": steps}

for lid, title, subtitle, words in EN_TOPICS:
    english_levels.append(en_topic_level(lid, title, subtitle, words))

# en-23 复习
english_levels.append({"id": "en-23", "title": "Level 24 Word Review", "subtitle": "单词大复习", "steps": [
    memory_step("en-23-m", "翻翻牌：主题单词大配对", [
        ("cat","cat",None,None,"Cat"),("apple","apple",None,None,"Apple"),("train","train",None,None,"Train"),
    ]),
    word_quiz("en-23-q1","Which one is the cat? 猫是哪一个？",[("Bear","bear"),("Cat","cat"),("Rabbit","rabbit")],1,"Cat 猫","Yes! Cat!"),
    word_quiz("en-23-q2","Which one is the train? 火车是哪一个？",[("Rocket","rocket"),("Boat","wave"),("Train","train")],2,"Train 火车","Yes! Train!"),
]})

# —— v0.12 剑桥 Starters/Movers +50 关：星期/月份/动词/季节/职业/句型——
FALLBACK_POOL = [("ball","Ball"),("apple","Apple"),("cat","Cat"),("star","Star"),("cup","Cup")]
def en_topic_level(i, gid, title, cn, words):
    # icon 为 None 的词（星期/月份/数字词本身画不出来）：走纯文字选项，
    # 由渲染层按字数自适应字号——不硬配近似图标（孩子会学错）。
    def opt(ic, en):
        o = {"text": en}
        if ic:
            o = {"icon": ic, "text": en}
        return o
    steps = [{"id": f"{gid}-t", "kind": "letter", "letters": [w[1] for w in words[:1]], "display": title,
              "examples": [dict(opt(ic, f"{en} {c}"), say=en) for ic, en, c in words],
              "question": f"Learn: {title} {cn}"}]
    for k, w in enumerate(words[:3]):
        others = [x for x in words if x is not w][:2]
        pads = [x for x in FALLBACK_POOL if all(x[0] != o[0] for o in others) and x[0] != w[0]]
        opts = [opt(x[0], x[1]) for x in others] + [opt(p[0], p[1]) for p in pads[:2 - len(others)]] + [opt(w[0], w[1])]
        steps.append({"id": f"{gid}-q{k}", "kind": "quiz",
                      "question": f"Which one is 「{w[2]}」?",
                      "options": opts, "answer": 2,
                      "hint": w[1], "praise": f"Yes! {w[1]}!"})
    english_levels.append({"id": gid, "title": f"Level {i+1} {title}", "subtitle": cn, "steps": steps})

NEW_TOPICS = [
    ("en-46", "Days 1", "星期一至三", [(None,"Monday","星期一"),(None,"Tuesday","星期二"),(None,"Wednesday","星期三")]),
    ("en-47", "Days 2", "星期四至五", [(None,"Thursday","星期四"),(None,"Friday","星期五"),(None,"Monday","星期一")]),
    ("en-48", "Days 3", "周末", [(None,"Saturday","星期六"),(None,"Sunday","星期日"),(None,"Monday","星期一")]),
    ("en-49", "Months 1", "一至四月", [(None,"March","三月"),(None,"April","四月"),(None,"May","五月")]),
    ("en-50", "Months 2", "六至九月", [(None,"June","六月"),(None,"July","七月"),(None,"September","九月")]),
    ("en-51", "Months 3", "十至十二月", [(None,"October","十月"),(None,"November","十一月"),(None,"December","十二月")]),
    ("en-52", "Seasons", "四季", [("flower","Spring","春天"),("sun","Summer","夏天"),("maple","Autumn","秋天"),("snowflake","Winter","冬天")]),
    ("en-53", "Verbs 1", "动作·吃跑睡", [("apple","Eat","吃"),("girl","Run","跑"),("bed","Sleep","睡觉")]),
    ("en-54", "Verbs 2", "动作·读画唱", [("book","Read","读"),("chart","Draw","画"),("speaker","Sing","唱")]),
    ("en-55", "Jobs", "职业", [("robot","Robot Maker","造机器人"),("girl","Teacher","老师"),("flask","Scientist","科学家")]),
    ("en-56", "Feelings", "心情", [("heart","Happy","开心"),("heart","Love","爱"),("party","Excited","兴奋")]),
    ("en-57", "Places", "场所", [("school","School","学校"),("shop","Shop","商店"),("castle","Castle","城堡")]),
    ("en-58", "Big and Small", "大小", [("elephant","Big","大"),("duck","Small","小"),("bear","Bear","熊")]),
    ("en-59", "Fast and Slow", "快慢", [("rocket","Fast","快"),("train","Train","火车"),("comet","Comet","彗星")]),
    ("en-60", "Breakfast", "早餐", [("bread","Bread","面包"),("milk","Milk","牛奶"),("egg","Egg","蛋")]),
    ("en-61", "Fruit Bowl", "水果盘", [("apple","Apple","苹果"),("banana","Banana","香蕉"),("candy","Sweet","甜食")]),
    ("en-62", "On the Farm", "农场", [("cow","Cow","奶牛"),("pig","Pig","猪"),("duck","Duck","鸭")]),
    ("en-63", "Pets", "宠物", [("cat","Cat","猫"),("dog","Dog","狗"),("rabbit","Rabbit","兔子")]),
    ("en-64", "Wild Animals", "野生动物", [("lion","Lion","狮子"),("fox","Fox","狐狸"),("polarbear","Polar Bear","北极熊")]),
    ("en-65", "Sea Friends", "海洋", [("fish","Fish","鱼"),("penguin","Penguin","企鹅"),("wave","Wave","海浪")]),
    ("en-66", "Sky", "天空", [("star","Star","星星"),("moon","Moon","月亮"),("sunface","Sun","太阳")]),
    ("en-67", "At Home", "在家里", [("home","House","房子"),("bed","Bed","床"),("clock","Clock","钟")]),
    ("en-68", "Play Time", "游戏", [("dice","Dice","骰子"),("block","Block","积木"),("ball","Ball","球")]),
    ("en-69", "Body Power", "身体本领", [("paw","Foot","脚"),("paw","Baby Paw","小脚丫"),("girl","Me","我")]),
    ("en-70", "Colours Again", "颜色", [("rainbow","Rainbow","彩虹"),("apple","Red","红"),("leaf","Green","绿")]),
    ("en-71", "Numbers 5-8", "数字五到八", [(None,"Five","五"),(None,"Six","六"),(None,"Seven","七"),(None,"Eight","八")]),
    ("en-72", "Greetings", "打招呼", [("girl","Hello","你好"),("party","Bye","再见"),("heart","Thank you","谢谢")]),
    ("en-73", "On the Table", "桌上", [("cup","Cup","杯子"),("book","Book","书"),("jar","Jar","罐")]),
]
for k, t in enumerate(NEW_TOPICS):
    en_topic_level(46 + k, *t)

# 词场复习 2 关 + 句型 2 关 + 总复习 1 关
english_levels.append({"id": "en-74", "title": "Level 75 Week Review", "subtitle": "星期复习", "steps": [
    {"id": "en-74-t", "kind": "letter", "letters": ["Monday"], "display": "Week",
     "examples": [{"text": "Monday 星期一"}, {"text": "Sunday 星期日"}], "question": "复习：一周七天"},
    quiz_step("en-74-q1", "The first day of school is——", [(None,"Monday"),(None,"Saturday"),(None,"Sunday")], 0, "上学第一天", "Yes! Monday!"),
    quiz_step("en-74-q2", "Which day is on the weekend?", [(None,"Saturday"),(None,"Monday"),(None,"Thursday")], 0, "周末两天", "Yes! Weekend!"),
]})
english_levels.append({"id": "en-75", "title": "Level 76 Seasons Review", "subtitle": "四季复习", "steps": [
    {"id": "en-75-t", "kind": "letter", "letters": ["Spring"], "display": "Seasons",
     "examples": [{"icon": "flower", "text": "Spring 春"}, {"icon": "snowflake", "text": "Winter 冬"}], "question": "复习：四季"},
    quiz_step("en-75-q1", "Snow falls in——", [("snowflake","Winter"),("sun","Summer"),("flower","Spring")], 0, "冬天下雪", "Yes! Winter!"),
    quiz_step("en-75-q2", "Flowers bloom in——", [("flower","Spring"),("snowflake","Winter"),("maple","Autumn")], 0, "春天开花", "Yes! Spring!"),
]})
english_levels.append({"id": "en-76", "title": "Level 77 I can...", "subtitle": "句型·我会", "steps": [
    {"id": "en-76-t", "kind": "letter", "letters": ["I can"], "display": "I can…",
     "examples": [{"icon": "girl", "text": "I can run 我会跑"}, {"icon": "fish", "text": "I can swim 我会游"}], "question": "句型：I can… 我会……"},
    quiz_step("en-76-q1", "「我会游泳」是——", [(None,"I can swim"),(None,"I can run"),(None,"I can sing")], 0, "swim 游泳", "Yes! I can swim!"),
    quiz_step("en-76-q2", "「我会读书」是——", [(None,"I can read"),(None,"I can jump"),(None,"I can fly")], 0, "read 读书", "Yes! I can read!"),
]})
english_levels.append({"id": "en-77", "title": "Level 78 I like...", "subtitle": "句型·我喜欢", "steps": [
    {"id": "en-77-t", "kind": "letter", "letters": ["I like"], "display": "I like…",
     "examples": [{"icon": "apple", "text": "I like apples 我喜欢苹果"}, {"icon": "cat", "text": "I like cats 我喜欢猫"}], "question": "句型：I like… 我喜欢……"},
    quiz_step("en-77-q1", "「我喜欢小猫」是——", [(None,"I like cats"),(None,"I like dogs"),(None,"I like cake")], 0, "cats 小猫复数", "Yes! I like cats!"),
]})

# —— v0.12 补充 18 个主题词场（凑足 96 正则）——
MORE_TOPICS = [
    ("en-78", "School Things", "学习用品", [("book","Book","书"),("chart","Chart","图表"),("clip","Clip","夹子"),("school","School","学校")]),
    ("en-79", "In the Park", "公园", [("tree","Tree","树"),("flower","Flower","花"),("bush","Bush","灌木"),("duck","Duck","鸭")]),
    ("en-80", "On the Beach", "海滩", [("wave","Wave","海浪"),("palm","Palm","椰树"),("desert","Sand","沙"),("penguin","Penguin","企鹅")]),
    ("en-81", "Music Time", "音乐时间", [("speaker","Speaker","喇叭"),("speaker","Sing","唱歌"),("party","Party","派对")]),
    ("en-82", "Wear This", "穿搭", [("hanger","Hanger","衣架"),("shoe","Shoe","鞋"),("hat","Hat","帽子")]),
    ("en-83", "Go Go Go", "出行", [("car","Car","汽车"),("bus","Bus","公交"),("rocket","Rocket","火箭")]),
    ("en-84", "My Family", "我的家", [("girl","Me","我"),("girl","Teacher","老师"),("fox","Fox","狐狸")]),
    ("en-85", "Toy Box", "玩具箱", [("balloon","Balloon","气球"),("shield","Shield","盾牌"),("gift","Gift","礼物")]),
    ("en-86", "Night Sky", "夜空", [("comet","Comet","彗星"),("rainbow","Rainbow","彩虹"),("blackhole","Black Hole","黑洞")]),
    ("en-87", "Dinosaur 1", "恐龙·霸王龙", [("dino","T-Rex","霸王龙"),("dino","Roar","吼"),("dino","Long Neck","长脖子")]),
    ("en-88", "Dinosaur 2", "恐龙·长脖子", [("dino","Long Neck","长脖子"),("leaf","Eats Leaves","吃叶子"),("dino","T-Rex","霸王龙")]),
    ("en-89", "Fruit Mix", "水果混合", [("apple","Apple","苹果"),("banana","Banana","香蕉"),("candy","Sweet","甜")]),
    ("en-90", "Drink Up", "喝的", [("milk","Milk","牛奶"),("cup","Cup","杯子"),("jar","Jar","罐子")]),
    ("en-91", "Animal Babies", "动物宝宝", [("paw","Baby Paw","小脚丫"),("duck","Duckling","小鸭"),("bear","Cub","小熊")]),
    ("en-92", "Hot and Cold", "热和冷", [("sun","Hot","热"),("snowflake","Cold","冷"),("ice","Ice","冰")]),
    ("en-93", "Little Helpers", "小帮手", [("robot","Robot","机器人"),("flask","Science","科学"),("magnet","Magnet","磁铁")]),
    ("en-94", "Fun Fair", "游乐场", [("party","Fun","欢乐"),("dice","Game","游戏"),("balloon","Balloon","气球")]),
    ("en-95", "Time to Eat", "吃饭啦", [("bread","Bread","面包"),("candy","Candy","糖果"),("cake","Cake","蛋糕")]),
]
for k, t in enumerate(MORE_TOPICS):
    en_topic_level(78 + k, *t)

finish_levels(english_levels, "english", 100)
apply_anims(english_levels, {
    "en-12": "walk",        # Animals：小猫散步
    "en-13": "rainbow",     # Colors：彩虹逐条扫入
    "en-14": "countpop",    # Numbers：星星逐个蹦出数数
    "en-15": "fall",        # Fruits：苹果落地
    "en-17": "heartbeat",   # Body：心跳扑通
    "en-21": "train",       # Transport：小火车喷烟
})
assign_letter_anims(english_levels, "english", "wordpop")   # v0.12.1：字母卡/词场卡补位
append_extras(english_levels, [
    ("en-0", sequence_step("en-x1", "Tap in order: A → B → C 按字母顺序点", ["A","B","C"],
                           praise="Great job! 字母小达人！")),
    ("en-12", tapall_step("en-x2", "Tap the animals! 把动物都点亮",
                          [("cat",None,True),("duck",None,True),("rabbit",None,True),
                           ("apple",None,False),("cake",None,False)],
                          "Cat、Duck、Rabbit 是动物")),
    ("en-15", shadow_step("en-x3", "看影子猜单词：What is it?", "apple",
                          [("apple","Apple"),("ball","Ball"),("book","Book")], 0, "圆圆的水果，A 开头")),
    ("en-19", match_step("en-x4", "Match: 单词和意思",
                         [("apple","Apple","苹果"),("banana","Banana","香蕉"),("cake","Cake","蛋糕")])),
])
W("english_levels.json", {"subject": "english", "title": "英语王国", "guide": "robot",
                         "zones": zones_meta(["字母启蒙", "动物与食物", "生活词汇", "星期月份", "多彩世界",
                                              "动作与职业", "主题词场", "四季与自然", "恐龙与朋友", "词汇大挑战"],
                                             (["book", "cat", "home", "star", "world-map",
                                               "girl", "block", "snowflake", "dino", "medal"],
                                              ["A-T 字母与发音", "Starters 动物食物", "家 · 城市 · 自然", "Days · Months · Seasons", "动物园 · 海洋 · 天气",
                                               "动作 · 职业 · 心情", "玩具 · 工具 · 花园", "四季 · 晚会 · 冬天", "恐龙 · 朋友 · 大小快慢", "句型 · 复习 · 大闯关"])),
                         "levels": english_levels})

# ================= 天文台 100 关（10 星区，知识点取材天文童书） =================
# 题型：letter 学一学 / quiz 练一练 / pattern 找规律 / count 数一数 / listen 找一找 /
#       balance 天平比一比（新） / sort 拖一拖分类（新）。不再使用 memory 翻牌配对。
# move 元组约定（由 astro_compose 装配成 step）：
#   ("letter",  en, display, chips, question)                chips=[(icon,text,say)]
#   ("quiz",    q, items, ans, hint, praise)                 items=[(icon|None, text|None)]
#   ("pattern", seq, opt_icons, ans, q)
#   ("balance", q, left, right, ansKey, hint)                left/right=(icon, text)
#   ("sort",    q, bins, items, praise)                      bins=[(id,label,icon)], items=[(id,icon,text,bin)]
#   ("count",   q, n, opts, icon, unit)
#   ("listen",  prompt, promptIcon, opt_icons, ans, speakText)

ASTRO_ZONES = [
    ("白天和黑夜", "太阳 · 月亮 · 星星"),
    ("地球我们的家", "蓝色星球 · 引力"),
    ("飞向太空", "火箭 · 宇航员"),
    ("巡游·岩质行星", "水金地火"),
    ("巡游·巨行星", "木土天海"),
    ("太阳我们的恒星", "光和热"),
    ("月亮变变变", "月相 · 登月"),
    ("星星的世界", "北斗 · 流星"),
    ("银河和宇宙", "光年 · 黑洞"),
    ("宇宙大探索", "望远镜 · 梦想"),
]

def astro_letter(lid, en, display, chips, question, anim=None):
    step = {"id": lid, "kind": "letter", "letters": [en], "display": display,
            "examples": [{"icon": ic, "text": t, "say": s} for ic, t, s in chips],
            "question": question}
    if anim:
        step["anim"] = anim
    return step

# 学一学动画（v0.10.1）：按关卡名映射动画 id，未映射的关回静态卡
ASTRO_ANIM_BY_LEVEL = {
    "太阳": "sunrise", "日出": "sunrise", "影子": "sunrise",
    "白天和黑夜": "daynight",
    "地球": "orbit", "引力": "orbit", "太阳系": "orbit",
    "水星": "orbit", "金星": "orbit", "火星": "orbit",
    "木星": "orbit", "土星": "orbit", "天王星": "orbit", "海王星": "orbit",
    "卫星": "satellite", "空间站": "satellite",
    "月亮": "moonphases", "月相": "moonphases",
    "火箭": "rocket", "登月": "rocket",
    "宇航员": "float", "宇航服": "float", "外星人": "float",
    "星星": "meteor", "陨石": "meteor", "光年": "meteor",
    "北斗七星": "bigdipper", "星座": "bigdipper",
    "黑洞": "blackhole",
    "银河系": "galaxy",
    "宇宙": "bigbang",
    "潮汐": "tide",
}

def sort_step(sid, q, bins, items, praise="分类完成，拖得又快又准！"):
    return {"id": sid, "kind": "sort", "question": q,
            "bins": [{"id": b, "label": lb, "icon": ic} for b, lb, ic in bins],
            "items": [{"id": i, "icon": ic, "text": t, "bin": b} for i, ic, t, b in items],
            "praise": praise}

def astro_count(cid, q, n, opts, icon, unit):
    return {"id": cid, "kind": "count", "question": q, "duckIcon": icon,
            "count": n, "countOptions": opts, "backdrop": "night", "unit": unit}

def astro_listen(lid, prompt, prompt_icon, opt_icons, ans, speak):
    opts = [{"icon": o} for o in opt_icons]
    if ans != 0:
        opts[0], opts[ans] = opts[ans], opts[0]
    return {"id": lid, "kind": "listen", "prompt": prompt, "promptIcon": prompt_icon,
            "speakText": speak, "question": f"找一找：哪张图片是「{prompt}」？",
            "options": opts, "answer": ans,
            "hint": f"想一想刚才学过的「{prompt}」", "praise": f"眼睛真亮，{prompt}找对啦！"}

# —— 96 个正式关（取材书目见文件头注释；每个条目 = (关卡名, [moves])）——
ASTRO_REGULAR = [
    # ── 星区 1 白天和黑夜（《揭秘太空》《第一次发现》启蒙）──
    ("太阳", [
        ("letter", "Sun", "太阳", [("sun","太阳 Sun","太阳"),("sunrise","日出 Sunrise","日出")], "学一学：太阳 Sun"),
        ("quiz", "白天挂在天上、发光发热的是谁？", [("sun","太阳"),("moon","月亮"),("star","星星")], 0,
         "太阳是大火球，白天照亮大地","对，太阳发光发热！"),
        ("pattern", ["sun","moon","sun"], ["moon","sun","star"], 0, "星空规律：下一个是谁？"),
    ]),
    ("月亮", [
        ("letter", "Moon", "月亮", [("moon","月亮 Moon","月亮"),("starface","星夜 Night","星夜")], "学一学：月亮 Moon"),
        ("quiz", "夜晚有时圆圆、有时弯弯的是谁？", [("crystal",None),("moon","月亮"),("sun",None)], 1,
         "月亮晚上挂夜空","对，是月亮！"),
        ("quiz", "月亮自己会发光吗？",
         [(None,"不会，它把太阳的光反射给我们"),(None,"会，它是个小灯泡"),(None,"会，它在燃烧")], 0,
         "月亮像一面小镜子","对，月亮反射太阳光！"),
        ("match", "连一连：谁在做什么？",
         [("sun","太阳","自己发光发热"),("moon","月亮","反射太阳的光"),("star","星星","一闪一闪眨眼睛")]),
    ]),
    ("星星", [
        ("letter", "Star", "星星", [("star","星星 Star","星星"),("sparkle","一闪一闪 Twinkle","一闪一闪")], "学一学：星星 Star"),
        ("quiz", "夜空里一闪一闪的是谁？", [("balloon",None),("star","星星"),("sun",None)], 1,
         "星星在夜空里眨眼睛","对，是星星！"),
        ("quiz", "星星为什么像在眨眼睛？",
         [(None,"星光穿过流动的空气，被抖得一闪一闪"),(None,"星星在调皮地眨眼"),(None,"星星没电了")], 0,
         "是空气在动哦","答对啦，是空气让星光闪烁！"),
    ]),
    ("白天和黑夜", [
        ("letter", "Day", "白天和黑夜", [("sun","白天 Day","白天"),("moon","黑夜 Night","黑夜")], "学一学：白天和黑夜 Day and Night"),
        ("quiz", "白天和黑夜轮流出现，是因为？",
         [(None,"地球在不停地转圈"),(None,"月亮挡住了太阳"),(None,"云太厚了")], 0,
         "地球转到面向太阳是白天","对，地球转一圈就是一天！"),
        ("sort", "拖一拖：把朋友送回对应的天空",
         [("day","白天",  "sun"),("night","黑夜","moon")],
         [("s1","sun","太阳","day"),("s2","sunrise","日出","day"),("s3","rainbow","彩虹","day"),
          ("n1","moon","月亮","night"),("n2","star","星星","night"),("n3","sparkle","流星","night")],
         "都送对啦，白天黑夜分得清！"),
    ]),
    ("日出", [
        ("letter", "Sunrise", "日出", [("sunrise","日出 Sunrise","日出"),("sun","太阳 Sun","太阳")], "学一学：日出 Sunrise"),
        ("quiz", "早上太阳从哪个方向升起？", [(None,"东方"),(None,"西方"),(None,"北方")], 0,
         "太阳公公从东边起床","对，从东边升起！"),
        ("quiz", "傍晚太阳落山之后，天空会？",
         [(None,"慢慢变暗，月亮星星出来"),(None,"马上更亮"),(None,"一直是大中午")], 0,
         "天黑了星星就出来","对，夜晚来啦！"),
    ]),
    ("数星星", [
        ("count", "夜空里有几颗星星在眨眼？", 6, [5,6,7], "star", "颗"),
        ("quiz", "白天怎么看不到星星？",
         [(None,"太阳光太亮，把星光盖住了"),(None,"星星白天睡觉"),(None,"星星被收进盒子")], 0,
         "星星一直在天上哦","对，星星白天也在！"),
    ]),
    ("找太阳", [
        ("listen", "太阳", "sun", ["sun","moon","star"], 0, "太阳"),
        ("quiz", "太阳升起后，天空会？",
         [(None,"越来越亮"),(None,"越来越黑"),(None,"下起雪来")], 0,
         "天亮啦，太阳出来了","对，越升越高越亮！"),
    ]),
    ("秤一秤·太阳和月亮", [
        ("balance", "天平秤一秤：太阳和月亮，哪边更重？",
         ("sun","太阳"), ("moon","月亮"), "left",
         "太阳是巨大的恒星，月亮只是绕地球转的小卫星"),
        ("quiz", "弯弯的月亮像什么？",
         [(None,"像一只小船"),(None,"像大方块"),(None,"像尖帽子")], 0,
         "弯弯月儿像小船","对，像小船！"),
    ]),
    ("影子", [
        ("letter", "Shadow", "影子", [("sun","太阳光 Light","太阳光"),("girl","小影子 Shadow","影子")], "学一学：影子 Shadow"),
        ("quiz", "影子是怎么来的？",
         [(None,"身体挡住了太阳光，光过不去就留下影子"),(None,"地里长出来的"),(None,"画上去的")], 0,
         "挡住光的地方就是影子","答对啦！"),
        ("quiz", "什么时候影子最长？",
         [(None,"早上和傍晚，太阳斜斜的时候"),(None,"中午正头顶"),(None,"半夜")], 0,
         "太阳斜射影子长","对，早晚影子最长！"),
    ]),
    ("星区小挑战", [
        ("pattern", ["sun","star","sun"], ["star","moon","rocket"], 0, "星空规律：下一个是谁？"),
        ("quiz", "太阳从哪个方向落下？", [(None,"西方"),(None,"东方"),(None,"南方")], 0,
         "东升西落","对，西边落下！"),
        ("quiz", "谁白天黑夜都在天上，晚上才看得清？",
         [("star","星星"),("car","汽车"),("cake","蛋糕")], 0,
         "星星一直在天上","对，抬头就能找！"),
    ]),
    # ── 星区 2 地球我们的家（《DK儿童太空百科》《万物简史》少儿版）──
    ("地球", [
        ("letter", "Earth", "地球", [("earth","地球 Earth","地球"),("rocket","坐火箭去看 Fly","坐火箭")], "学一学：地球 Earth"),
        ("quiz", "我们住在哪颗星球上？", [("earth","地球"),("sun","太阳"),("moon","月亮")], 0,
         "蓝蓝的圆圆的是我们的家","对，地球是我们的家！"),
        ("quiz", "从太空看地球，主要是什么颜色？",
         [(None,"蓝色，大部分是大海"),(None,"红色，全是火"),(None,"绿色，全是树")], 0,
         "海洋比陆地多得多","对，地球是蓝色星球！"),
    ]),
    ("圆圆的地球", [
        ("quiz", "地球是什么形状？", [(None,"圆圆的球"),(None,"方方的盒子"),(None,"扁扁的盘子")], 0,
         "地球是个大圆球","对，圆圆的地球！"),
        ("quiz", "为什么我们跳起来总会落回地面？",
         [(None,"地球的引力像看不见的手拉着我们"),(None,"地面会吸铁"),(None,"天上有个钩子")], 0,
         "引力把万物拉在地面上","答对啦，这就是引力！"),
    ]),
    ("地球在转动", [
        ("quiz", "地球自己转一圈是多久？",
         [(None,"一天（24小时）"),(None,"一小时"),(None,"一年")], 0,
         "自转一圈就是一天","对，转一圈是一天！"),
        ("pattern", ["earth","moon","earth"], ["moon","star","sun"], 0, "星空规律：下一个是谁？"),
    ]),
    ("引力", [
        ("letter", "Gravity", "引力", [("earth","地球 Earth","地球"),("apple","落下的苹果 Apple","苹果")], "学一学：引力 Gravity"),
        ("quiz", "跳起来之后会怎么样？",
         [(None,"落回地面"),(None,"飘走不回来"),(None,"飞到月亮上")], 0,
         "引力把我们拉回来","对，落回地面！"),
        ("quiz", "月亮为什么不跑丢，一直陪着地球？",
         [(None,"地球的引力拉着它转圈"),(None,"月亮怕黑"),(None,"月亮没力气走")], 0,
         "引力像看不见的绳子","对，引力拉着月亮！"),
    ]),
    ("空气", [
        ("quiz", "月亮上有没有空气？",
         [(None,"没有，所以要背氧气瓶"),(None,"有，和地球一样"),(None,"全是水汽")], 0,
         "月亮上没有空气","答对啦，所以要带氧气！"),
        ("quiz", "为什么宇航服鼓鼓的、包得严严实实？",
         [(None,"里面装着空气，像一艘小飞船保护宇航员"),(None,"为了好看"),(None,"冬天冷多穿点")], 0,
         "宇航服是小小飞船","对，它保护宇航员！"),
    ]),
    ("秤一秤·地球和月球", [
        ("balance", "天平秤一秤：地球和月球，哪边更重？",
         ("earth","地球"), ("moon","月球"), "left",
         "49个月球加起来，才和地球差不多大"),
        ("quiz", "谁晚上陪在地球身边转圈圈？",
         [("moon","月球"),("comet","彗星"),("rocket","火箭")], 0,
         "月球是地球的卫星","对，是月球！"),
    ]),
    ("白天的月亮", [
        ("quiz", "白天能看到月亮吗？",
         [(None,"有时能，月亮常常白天也挂着"),(None,"永远看不到"),(None,"月亮怕晒不敢出来")], 0,
         "《DK儿童太空百科》：月亮白天也常在天上","答对啦，白天也能找月亮！"),
        ("quiz", "月亮离我们有多远？",
         [(None,"很远很远，火箭要飞好几天"),(None,"隔壁楼那么近"),(None,"一伸手就够到")], 0,
         "月亮是离我们最近的天体","对，虽然近也要飞好几天！"),
    ]),
    ("蓝色的家", [
        ("quiz", "地球上大部分地方是什么？",
         [(None,"海洋"),(None,"沙漠"),(None,"冰川")], 0,
         "七分海洋三分陆地","对，大部分是海洋！"),
        ("listen", "地球", "earth", ["earth","mars","moon"], 0, "地球"),
    ]),
    ("找地球", [
        ("listen", "地球", "earth", ["earth","sun","star"], 0, "地球"),
        ("quiz", "谁给地球送来光和热？",
         [("sun","太阳"),("cake","蛋糕"),("rock","石头")], 0,
         "太阳是地球的能量站","对，是太阳！"),
    ]),
    ("星区小挑战", [
        ("pattern", ["earth","star","earth"], ["star","moon","comet"], 0, "星空规律：下一个是谁？"),
        ("quiz", "从太空看地球是什么颜色？", [("earth","蓝色"),("mars","红色"),("sun","金色")], 0,
         "大海是蓝色的","对，蓝色星球！"),
        ("quiz", "把我们拉在地面上不飞走的是？",
         [(None,"引力"),(None,"磁铁"),(None,"胶水")], 0,
         "地球的引力","答对啦，引力无处不在！"),
    ]),
    # ── 星区 3 飞向太空（《揭秘太空》《国家地理少儿版》）──
    ("火箭", [
        ("letter", "Rocket", "火箭", [("rocket","火箭 Rocket","火箭"),("flame","点火 3,2,1","点火")], "学一学：火箭 Rocket"),
        ("quiz", "谁能把宇航员送上太空？", [("rocket","火箭"),("train","火车"),("car","汽车")], 0,
         "火箭轰隆一声冲上天","对，是火箭！"),
        ("quiz", "火箭点火时，尾巴喷出什么？",
         [(None,"火焰和强大的气流"),(None,"彩色泡泡"),(None,"花瓣")], 0,
         "喷着火冲上天","答对啦！"),
        ("sequence", "倒计时点火：按 3→2→1 顺序点，发射火箭！", ["3","2","1"]),
    ]),
    ("宇航员", [
        ("letter", "Astronaut", "宇航员", [("astronaut","宇航员 Astronaut","宇航员"),("station","空间站 Station","空间站")], "学一学：宇航员 Astronaut"),
        ("quiz", "开飞船上太空工作的人叫什么？",
         [(None,"宇航员"),(None,"司机"),(None,"厨师")], 0,
         "他们乘火箭上太空","对，宇航员！"),
        ("quiz", "在空间站里水珠会飘走，宇航员怎么喝水？",
         [(None,"用带吸管的水袋吸着喝"),(None,"用杯子慢慢倒"),(None,"张嘴等雨")], 0,
         "太空里的水会飘","对，吸管袋喝水！"),
    ]),
    ("宇航服", [
        ("letter", "Spacesuit", "宇航服", [("astronaut","穿宇航服的宇航员","宇航员"),("rocket","火箭 Rocket","火箭")], "学一学：宇航服 Spacesuit"),
        ("quiz", "太空里没有空气，宇航员靠什么呼吸？",
         [(None,"宇航服里带的氧气"),(None,"憋气"),(None,"大口吸真空")], 0,
         "氧气装在宇航服里","对，靠氧气！"),
        ("quiz", "宇航服还能帮宇航员挡住什么？",
         [(None,"忽冷忽热的温度和小陨石"),(None,"别人的目光"),(None,"数学题")], 0,
         "太空温差特别大","答对啦，宇航服很能干！"),
    ]),
    ("失重", [
        ("quiz", "空间站里宇航员怎么睡觉？",
         [(None,"钻进睡袋，挂在墙上"),(None,"躺大床上盖被子"),(None,"坐摇椅")], 0,
         "失重时躺着会飘走","对，睡袋挂墙上！"),
        ("quiz", "在空间站里笔掉了，它会？",
         [(None,"飘在空中"),(None,"马上掉到地上"),(None,"自己飞走藏起来")], 0,
         "失重了，东西会飘","对，飘在空中！"),
    ]),
    ("空间站", [
        ("letter", "Station", "空间站", [("station","空间站 Station","空间站"),("astronaut","宇航员的家","宇航员")], "学一学：空间站 Space Station"),
        ("quiz", "宇航员在太空住的大房子叫什么？",
         [("station","空间站"),("castle","城堡"),("shop","商店")], 0,
         "太空之家","对，空间站！"),
        ("quiz", "空间站绕着谁转圈圈？",
         [("earth","地球"),("moon","月亮"),("cake","蛋糕")], 0,
         "绕地球一圈只要个把小时","对，绕着地球转！"),
    ]),
    ("卫星", [
        ("letter", "Satellite", "卫星", [("satellite","人造卫星 Satellite","人造卫星"),("moon","月亮也是卫星","月亮")], "学一学：卫星 Satellite"),
        ("quiz", "绕着地球转的人造飞行器叫什么？",
         [("satellite","人造卫星"),("rocket","火箭"),("train","火车")], 0,
         "人造卫星绕地球转","对，人造卫星！"),
        ("quiz", "我们看的电视、用的导航，谁在天上帮忙传信号？",
         [(None,"人造卫星"),(None,"小鸟"),(None,"风筝")], 0,
         "卫星是太空信使","答对啦！"),
        ("shadow", "看影子猜猜：这是谁？", "satellite",
         [("satellite","人造卫星"),("moon","月亮"),("rocket","火箭")], 0,
         "它张着两片太阳翼，绕着地球转"),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：谁在天上飞？谁在地上跑？",
         [("sky","天上飞","rocket"),("ground","地上跑","car")],
         [("a1","rocket","火箭","sky"),("a2","satellite","人造卫星","sky"),("a3","bird","小鸟","sky"),
          ("b1","car","汽车","ground"),("b2","train","火车","ground"),("b3","bus","公交车","ground")],
         "分得真清楚！"),
        ("quiz", "宇航员上天之前要穿好什么？",
         [("astronaut","宇航服"),("goggles","泳镜"),("hat","帽子")], 0,
         "宇航服是保命的小飞船","对，穿好宇航服！"),
    ]),
    ("数火箭", [
        ("count", "发射场上，等着上天的小火箭有几枚？", 5, [4,5,6], "rocket", "枚"),
        ("quiz", "空间站里的宇航员在做什么？",
         [(None,"做实验，研究太空的秘密"),(None,"睡大觉"),(None,"踢足球")], 0,
         "空间站就是太空实验室","对，做实验！"),
    ]),
    ("找火箭", [
        ("listen", "火箭", "rocket", ["rocket","earth","star"], 0, "火箭"),
        ("quiz", "空间站里的宇航员一天能看到很多次日出，因为？",
         [(None,"空间站绕地球转得飞快"),(None,"太阳跳来跳去"),(None,"表坏了")], 0,
         "绕地球一圈约一个半小时","答对啦，一天能看十几次日出！"),
    ]),
    # ── 星区 4 巡游·岩质行星（《神奇校车·迷失在太阳系》）──
    ("太阳系", [
        ("letter", "Solar System", "太阳系", [("sun","太阳在中间","太阳"),("planet","八颗行星绕着转","行星")], "学一学：太阳系 Solar System"),
        ("quiz", "太阳系里有几大行星？", [(None,"八颗"),(None,"三颗"),(None,"一百颗")], 0,
         "水金地火+木土天海","对，八大行星！"),
        ("quiz", "行星们都绕着谁转？", [("sun","太阳"),("earth","地球"),("moon","月亮")], 0,
         "太阳是太阳系的老大","对，绕太阳转！"),
        ("match", "连一连：行星的英文名",
         [("mercury","水星","Mercury"),("venus","金星","Venus"),("mars","火星","Mars")]),
    ]),
    ("水星", [
        ("letter", "Mercury", "水星", [("mercury","水星 Mercury","水星"),("sun","离太阳最近","太阳")], "学一学：水星 Mercury"),
        ("quiz", "跑得最快、离太阳最近的行星是？", [("mercury","水星"),("neptune","海王星"),("saturn","土星")], 0,
         "水星是跑步冠军","对，是水星！"),
        ("quiz", "在水星上过一年（绕太阳一圈）只要 88 天，所以？",
         [(None,"比地球上的一个暑假还短"),(None,"比 100 年还长"),(None,"和地球一年一样长")], 0,
         "水星上一年=88天","对，水星的一年特别短！"),
        ("match", "连一连：行星之最",
         [("mercury","水星","离太阳最近"),("earth","地球","我们的家"),("neptune","海王星","离太阳最远")]),
    ]),
    ("金星", [
        ("letter", "Venus", "金星", [("venus","金星 Venus","金星"),("sunrise","清晨最亮的星","清晨")], "学一学：金星 Venus"),
        ("quiz", "清晨东方最亮的那颗星叫？", [("venus","金星"),("mars","火星"),("moon","月亮")], 0,
         "金星也叫启明星","对，金星最亮！"),
        ("quiz", "太阳系最热的行星是？",
         [(None,"金星，厚厚的云像棉被捂得热"),(None,"水星，因为离太阳最近"),(None,"地球")], 0,
         "别看水星更近，金星裹着厚云更热","答对啦，金星是大火炉！"),
    ]),
    ("火星", [
        ("letter", "Mars", "火星", [("mars","火星 Mars","火星"),("robot","火星车 Rover","火星车")], "学一学：火星 Mars"),
        ("quiz", "哪颗行星红红的？", [("mars","火星"),("venus","金星"),("earth","地球")], 0,
         "火星像生了锈","对，红红的火星！"),
        ("quiz", "火星为什么是红色的？",
         [(None,"土壤里有铁锈"),(None,"被火烤过"),(None,"涂了红色颜料")], 0,
         "像铁锈一样的土壤","对，是铁锈色！"),
    ]),
    ("岩质行星", [
        ("quiz", "哪些行星是硬硬的岩石星球（岩质行星）？",
         [(None,"水星、金星、地球、火星"),(None,"木星、土星"),(None,"月亮和太阳")], 0,
         "离太阳近的四颗是岩质行星","对，水金地火！"),
        ("quiz", "我们住的地球是岩质行星吗？",
         [(None,"是呀，脚下就是岩石"),(None,"不是，地球是气体"),(None,"地球是水做的")], 0,
         "脚踩大地，当然是","答对啦！"),
        ("tapall", "点点看：把岩质行星都点亮",
         [("mercury",None,True),("venus",None,True),("mars",None,True),("earth",None,True),
          ("jupiter",None,False),("saturn",None,False)],
         "水金地火是硬硬的岩石星球"),
    ]),
    ("小行星带", [
        ("quiz", "火星和木星之间有一条什么地带？",
         [(None,"小行星带，许多小石头绕太阳转"),(None,"一条大河"),(None,"一堵大墙")], 0,
         "《神奇校车》就从这里穿过！","对，小行星带！"),
        ("quiz", "小行星是什么？",
         [(None,"绕太阳转圈的小石块"),(None,"小星星的宝宝"),(None,"会飞的小汽车")], 0,
         "大的像山，小的像石头","对，是太空小石块！"),
        ("tapall", "点点看：把绕着太阳转的都点亮",
         [("earth",None,True),("venus",None,True),("comet",None,True),
          ("moon",None,False),("satellite",None,False),("star",None,False)],
         "行星和彗星绕太阳，月亮和卫星绕地球"),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：把行星送回自己的队伍",
         [("rocky","岩质行星","mercury"),("gas","巨行星","jupiter")],
         [("a1","mercury","水星","rocky"),("a2","venus","金星","rocky"),("a3","mars","火星","rocky"),
          ("b1","jupiter","木星","gas"),("b2","saturn","土星","gas"),("b3","neptune","海王星","gas")],
         "行星分类小达人！"),
        ("quiz", "八大行星里个头最小的是？",
         [("mercury","水星"),("jupiter","木星"),("earth","地球")], 0,
         "水星小小的跑得快","对，水星最小！"),
    ]),
    ("秤一秤·水星和地球", [
        ("balance", "天平秤一秤：水星和地球，哪边更重？",
         ("mercury","水星"), ("earth","地球"), "right",
         "水星是八大行星里最小的，地球比它重得多"),
        ("quiz", "离太阳由近到远排，第三颗是谁？",
         [(None,"地球"),(None,"水星"),(None,"木星")], 0,
         "水金地…第三颗是我们","对，地球排第三！"),
    ]),
    ("排排队", [
        ("quiz", "八大行星排队，谁排第一（离太阳最近）？",
         [("mercury","水星"),("earth","地球"),("saturn","土星")], 0,
         "水星离太阳最近","对，水星第一！"),
        ("quiz", "行星排队的顺序是按什么排的？",
         [(None,"离太阳由近到远"),(None,"谁跑得慢"),(None,"颜色好看")], 0,
         "按离太阳远近排","答对啦！"),
        ("lineup", "排排队：按离太阳由近到远",
         [("mercury","水星"),("venus","金星"),("earth","地球"),("mars","火星")]),
    ]),
    ("星区小挑战", [
        ("pattern", ["mercury","venus","mercury"], ["venus","mars","sun"], 0, "星空规律：下一个是谁？"),
        ("quiz", "红色行星是哪颗？", [("mars","火星"),("venus","金星"),("neptune","海王星")], 0,
         "铁锈色的火星","对，火星！"),
        ("quiz", "小行星带夹在哪两颗行星中间？",
         [(None,"火星和木星"),(None,"地球和月亮"),(None,"水星和金星")], 0,
         "岩质行星和巨行星的分界线","对，火星和木星之间！"),
    ]),
    # ── 星区 5 巡游·巨行星（《神奇校车》《DK儿童太空百科》）──
    ("木星", [
        ("letter", "Jupiter", "木星", [("jupiter","木星 Jupiter","木星"),("starface","大红斑","大红斑")], "学一学：木星 Jupiter"),
        ("quiz", "八大行星里最大的是谁？", [("jupiter","木星"),("earth","地球"),("mars","火星")], 0,
         "木星是行星大老大","对，木星最大！"),
        ("quiz", "木星上的大红斑是什么？",
         [(None,"一场刮了几百年还没停的大风暴"),(None,"颜料点"),(None,"陨石砸的坑")], 0,
         "比地球还大的风暴","答对啦，大红斑是大风暴！"),
        ("shadow", "看影子猜猜：这是谁？", "jupiter",
         [("jupiter","木星"),("saturn","土星"),("earth","地球")], 0,
         "它是行星大老大，身上有大红斑"),
    ]),
    ("土星", [
        ("letter", "Saturn", "土星", [("saturn","土星 Saturn","土星"),("crystal","美丽的光环","光环")], "学一学：土星 Saturn"),
        ("quiz", "谁戴着像草帽一样的光环？", [("saturn","土星"),("mars","火星"),("venus","金星")], 0,
         "土星的光环最美","对，土星戴草帽！"),
        ("quiz", "土星的光环是什么做的？",
         [(None,"无数小冰块和石头"),(None,"彩虹糖"),(None,"云朵")], 0,
         "光环是冰块石头组成的","答对啦！"),
    ]),
    ("天王星", [
        ("letter", "Uranus", "天王星", [("uranus","天王星 Uranus","天王星"),("crystal","蓝绿色的星球","蓝绿色")], "学一学：天王星 Uranus"),
        ("quiz", "哪颗行星躺着自转、像打滚一样前进？",
         [("uranus","天王星"),("mercury","水星"),("venus","金星")], 0,
         "天王星是躺着的","对，天王星躺着转！"),
        ("quiz", "天王星是什么颜色？",
         [(None,"蓝绿色"),(None,"火红色"),(None,"黑色")], 0,
         "冰冰的蓝绿色","答对啦，蓝绿色！"),
    ]),
    ("海王星", [
        ("letter", "Neptune", "海王星", [("neptune","海王星 Neptune","海王星"),("wave","深蓝像大海","深蓝")], "学一学：海王星 Neptune"),
        ("quiz", "离太阳最远的行星是？", [("neptune","海王星"),("mercury","水星"),("earth","地球")], 0,
         "海王星在队伍最后","对，海王星最远！"),
        ("quiz", "海王星是什么颜色？",
         [(None,"深蓝色，像大海"),(None,"绿色"),(None,"五颜六色")], 0,
         "深蓝的海王星","对，深蓝色！"),
    ]),
    ("冥王星", [
        ("quiz", "冥王星现在还是八大行星之一吗？",
         [(None,"不是啦，它现在是矮行星"),(None,"是，它最大"),(None,"它变成恒星了")], 0,
         "个头太小被请出了行星队伍","对，冥王星是矮行星！"),
        ("quiz", "冥王星为什么被请出行星队伍？",
         [(None,"个头太小，和别的大行星不一样"),(None,"它太亮了"),(None,"它跑太快")], 0,
         "科学家重新分了类","答对啦！"),
    ]),
    ("秤一秤·木星和地球", [
        ("balance", "天平秤一秤：木星和地球，哪边更重？",
         ("jupiter","木星"), ("earth","地球"), "left",
         "木星是大块头，一千三百个地球才和它一样大"),
        ("quiz", "土星很轻很轻，如果有个足够大的水池，它会？",
         [(None,"像皮球一样浮在水面上"),(None,"咕咚沉底"),(None,"把水吸干")], 0,
         "土星密度比水还小","对，土星能浮起来！"),
    ]),
    ("巨行星", [
        ("quiz", "巨行星（木土天海）和岩质行星最大的不同是？",
         [(None,"巨行星主要由气体组成，像大气球"),(None,"巨行星是巧克力做的"),(None,"没有不同")], 0,
         "没有落脚的硬地面","对，巨行星是气体星球！"),
        ("quiz", "谁自转最快、一天不到10小时？",
         [("jupiter","木星"),("earth","地球"),("moon","月亮")], 0,
         "木星个头大转得快","答对啦，是木星！"),
    ]),
    ("八大行星点名", [
        ("count", "太阳系八大行星都来点名啦，一共有几颗？", 8, [7,8,9], "planet", "颗"),
        ("quiz", "八大行星里离太阳由近到远，地球排第几？",
         [(None,"第三颗"),(None,"第一颗"),(None,"最后一名")], 0,
         "水金地…我们排第三","对，第三颗！"),
        ("lineup", "排排队：按个头从大到小",
         [("jupiter","木星"),("saturn","土星"),("uranus","天王星"),("neptune","海王星")]),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：恒星和行星分一分",
         [("stars","恒星·自己发光","sun"),("planets","行星·绕恒星转","earth")],
         [("a1","sun","太阳","stars"),("a2","star","夜空里的星星","stars"),("a3","starface","北极星","stars"),
          ("b1","earth","地球","planets"),("b2","saturn","土星","planets"),("b3","mars","火星","planets")],
         "恒星行星分得清，真棒！"),
        ("quiz", "月亮绕着谁转？",
         [("earth","地球"),("sun","太阳"),("venus","金星")], 0,
         "月亮是地球的卫星","对，绕着地球转！"),
    ]),
    ("星区小挑战", [
        ("pattern", ["saturn","jupiter","saturn"], ["jupiter","uranus","earth"], 0, "星空规律：下一个是谁？"),
        ("quiz", "哪颗行星戴着光环？", [("saturn","土星"),("mars","火星"),("mercury","水星")], 0,
         "土星草帽光环","对，土星！"),
        ("quiz", "地球绕太阳转一圈是多久？",
         [(None,"一年"),(None,"一天"),(None,"一小时")], 0,
         "绕一圈就是一年","答对啦，一年！"),
    ]),
    # ── 星区 6 太阳我们的恒星（《DK儿童太空百科》《国家地理少儿版》）──
    ("恒星", [
        ("quiz", "太阳其实是一颗什么？",
         [(None,"恒星，自己发光发热"),(None,"行星"),(None,"大月亮")], 0,
         "太阳是离我们最近的恒星","对，太阳是恒星！"),
        ("quiz", "夜晚的星星和太阳是一家人吗？",
         [(None,"是，都是遥远的恒星"),(None,"不是，星星是灯"),(None,"星星是洞洞")], 0,
         "每颗星星都是个太阳","答对啦！"),
        ("tapall", "点点看：把恒星都点亮",
         [("sun",None,True),("star",None,True),("starface",None,True),
          ("earth",None,False),("moon",None,False),("comet",None,False)],
         "恒星自己会发光，太阳和夜空的星星都是"),
    ]),
    ("巨大的太阳", [
        ("quiz", "太阳的肚子里大约能装下多少个地球？",
         [(None,"100多万个"),(None,"10个"),(None,"100个")], 0,
         "太阳是个超级大胖子","对，100多万个地球！"),
        ("quiz", "太阳和地球谁大？",
         [(None,"太阳大多啦"),(None,"地球大"),(None,"一样大")], 0,
         "地球在太阳面前像小豆子","答对啦！"),
    ]),
    ("秤一秤·太阳和地球", [
        ("balance", "天平秤一秤：太阳和地球，哪边更重？",
         ("sun","太阳"), ("earth","地球"), "left",
         "太阳占整个太阳系绝大部分的重量"),
        ("quiz", "地球绕着太阳转，还是太阳绕着地球转？",
         [(None,"地球绕太阳转"),(None,"太阳绕地球转"),(None,"互相追着玩")], 0,
         "地球是太阳的行星","对，地球绕太阳！"),
    ]),
    ("阳光快递", [
        ("quiz", "太阳光跑到地球要多久？",
         [(None,"大约8分钟"),(None,"1秒钟"),(None,"一整年")], 0,
         "光速飞快也要跑一会儿","对，大约8分钟！"),
        ("quiz", "我们晒到的阳光是什么时候出发的？",
         [(None,"8分钟前从太阳出发"),(None,"刚刚出发"),(None,"昨天出发")], 0,
         "阳光是位小邮差","答对啦！"),
    ]),
    ("太阳的本领", [
        ("quiz", "小植物为什么朝着太阳长？",
         [(None,"晒太阳才能制造养分长大"),(None,"太阳会挠痒痒"),(None,"怕黑")], 0,
         "阳光是植物的饭菜","对，植物爱太阳！"),
        ("quiz", "太阳还能帮我们做什么？",
         [(None,"晒干衣服、太阳能发电"),(None,"煮动画片"),(None,"唱歌")], 0,
         "太阳能是大本领","答对啦！"),
    ]),
    ("极光", [
        ("letter", "Aurora", "极光", [("rainbow","极光像彩带","极光"),("star","夜空里舞动","星星")], "学一学：极光 Aurora"),
        ("quiz", "夜空里飘动的彩色光带叫什么？",
         [(None,"极光"),(None,"彩虹"),(None,"闪电")], 0,
         "太阳送来的粒子撞出彩带","对，是极光！"),
        ("quiz", "在哪里最容易看到极光？",
         [(None,"南北极附近"),(None,"沙漠中间"),(None,"游泳池里")], 0,
         "极地才有极光哦","答对啦！"),
    ]),
    ("保护眼睛", [
        ("quiz", "能不能用眼睛直接看太阳？",
         [(None,"不能，会伤到眼睛"),(None,"可以，随便看"),(None,"中午可以看")], 0,
         "太阳光太刺眼啦","对，不能直视太阳！"),
        ("quiz", "想看日食要请谁帮忙？",
         [(None,"专用观察镜（家长陪同）"),(None,"普通墨镜随便看"),(None,"闭上眼睛想象")], 0,
         "护眼第一","答对啦，护眼小卫士！"),
    ]),
    ("数星星", [
        ("count", "夜空里有几颗小星星在眨眼？", 7, [6,7,8], "star", "颗"),
        ("quiz", "太阳下山之后，星星会？",
         [(None,"一颗颗亮起来"),(None,"全部躲起来"),(None,"变成月亮")], 0,
         "夜幕是星星的舞台","对，星星亮起来！"),
    ]),
    ("找太阳", [
        ("listen", "太阳", "sun", ["sun","moon","star"], 0, "太阳"),
        ("quiz", "谁是太阳系的光和热之源？",
         [("sun","太阳"),("comet","彗星"),("satellite","卫星")], 0,
         "万物生长靠太阳","对，是太阳！"),
    ]),
    # ── 星区 7 月亮变变变（《DK神秘宇宙》《揭秘太空》）──
    ("月相", [
        ("letter", "New Moon", "月相", [("newmoon","新月 New Moon","新月"),("fullmoon","满月 Full Moon","满月")], "学一学：月亮有时弯弯、有时圆圆"),
        ("pattern", ["newmoon","fullmoon","newmoon"], ["fullmoon","newmoon","star"], 0,
         "月相规律：下一个是新月还是满月？"),
        ("quiz", "月亮为什么有时圆、有时弯？",
         [(None,"太阳照亮的部分在慢慢变"),(None,"月亮真的变大变小"),(None,"被云咬掉了")], 0,
         "月亮本身不发光","答对啦，月相在循环！"),
    ]),
    ("月相顺序", [
        ("quiz", "细细的月牙慢慢变圆，中间会先变成？",
         [(None,"半圆"),(None,"方方块"),(None,"三角形")], 0,
         "月牙→半月→满月","对，先变半圆！"),
        ("pattern", ["fullmoon","newmoon","fullmoon"], ["newmoon","fullmoon","comet"], 0,
         "月相规律：下一个是谁？"),
        ("lineup", "排排队：月相从小到圆",
         [("newmoon","新月"),("waxing","上弦月"),("fullmoon","满月")]),
    ]),
    ("环形山", [
        ("letter", "Crater", "环形山", [("moon","月亮上的大圆坑","环形山"),("rock","太空小石头","石头")], "学一学：环形山 Crater"),
        ("quiz", "月亮上圆圆的大坑是怎么来的？",
         [(None,"太空小石头撞出来的"),(None,"小朋友挖的"),(None,"雨点打出来的")], 0,
         "撞击坑也叫环形山","对，撞出来的坑！"),
        ("quiz", "月亮上没有风没有雨，所以脚印会？",
         [(None,"留很久很久"),(None,"马上被吹走"),(None,"被雨水冲掉")], 0,
         "没有风帮你擦脚印","答对啦！"),
    ]),
    ("安静的月亮", [
        ("quiz", "月亮上有没有刮风下雨？",
         [(None,"没有，因为没有空气"),(None,"天天下雨"),(None,"常刮台风")], 0,
         "没有空气就没有天气","对，月亮上没有天气！"),
        ("quiz", "在月亮上大声喊，能听到吗？",
         [(None,"听不到，没有空气传声音"),(None,"听得到，很响"),(None,"会传到地球")], 0,
         "声音要坐空气的车","答对啦，月亮上静悄悄！"),
    ]),
    ("潮汐", [
        ("letter", "Tide", "潮汐", [("wave","海水涨了又退","海浪"),("moon","月亮在牵着","月亮")], "学一学：潮汐 Tide"),
        ("quiz", "海水每天涨了又退，是谁在牵着？",
         [(None,"月亮的引力"),(None,"大鱼在游泳"),(None,"轮船推的")], 0,
         "月亮牵海水，一起做运动","对，是月亮的引力！"),
        ("quiz", "潮涨潮落一天有几次？",
         [(None,"大约两次涨、两次退"),(None,"一次都没有"),(None,"每小时一百次")], 0,
         "海水有自己的节拍","答对啦！"),
    ]),
    ("日食和月食", [
        ("quiz", "月亮挡住太阳，白天一下子变暗，这叫？",
         [(None,"日食"),(None,"月食"),(None,"停电了")], 0,
         "《DK神秘宇宙》里的天文奇观","对，是日食！"),
        ("quiz", "看日食的时候可以怎么做？",
         [(None,"戴专用观察镜，请家长陪着看"),(None,"瞪大眼睛直接看"),(None,"用望远镜直盯太阳")], 0,
         "护眼小卫士提醒你","答对啦，护眼第一！"),
    ]),
    ("登月", [
        ("letter", "Moon Landing", "登月", [("astronaut","宇航员登月","宇航员"),("flag","插上小旗","旗子")], "学一学：登月 Moon Landing"),
        ("quiz", "人类的脚印第一次踩在月亮上，是哪国宇航员？",
         [(None,"美国（阿姆斯特朗）"),(None,"中国"),(None,"法国")], 0,
         "1969年，全人类的一小步","对，美国宇航员先登月！"),
        ("quiz", "中国的探月车叫什么名字？",
         [(None,"玉兔号"),(None,"大白号"),(None,"熊猫号")], 0,
         "玉兔住在月亮上，名字正合适","答对啦，玉兔号！"),
        ("sequence", "登月火箭点火：按 3→2→1 顺序点，出发去月亮！", ["3","2","1"]),
    ]),
    ("找月亮", [
        ("listen", "月亮", "moon", ["moon","sun","earth"], 0, "月亮"),
        ("quiz", "中秋节的月亮是圆的还是弯的？",
         [(None,"圆圆的满月"),(None,"细细的月牙"),(None,"看不见")], 0,
         "八月十五月儿圆","对，圆圆的满月！"),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：月亮上到底有什么？",
         [("yes","月亮上有","moon"),("no","月亮上没有","wave")],
         [("a1","moon","环形山","yes"),("a2","astronaut","宇航员的脚印","yes"),("a3","robot","月球车","yes"),
          ("b1","wave","大海","no"),("b2","tree","大树","no"),("b3","duck","小鸟","no")],
         "没有空气和水，就没有大海和大树！"),
        ("quiz", "月亮绕地球转一圈大约要多久？",
         [(None,"一个月"),(None,"一天"),(None,"一小时")], 0,
         "这就是「月」的由来哦","答对啦，一个月！"),
    ]),
    ("星区小挑战", [
        ("quiz", "今晚是弯弯的月牙，过几天它会？",
         [(None,"慢慢变圆"),(None,"慢慢变方"),(None,"变成星星")], 0,
         "月相在慢慢变化","对，会越来越圆！"),
        ("pattern", ["newmoon","fullmoon","newmoon"], ["fullmoon","newmoon","earth"], 0,
         "月相规律：下一个是谁？"),
        ("quiz", "月亮自己会发光吗？",
         [(None,"不会，反射太阳光"),(None,"会，是灯泡"),(None,"会，在燃烧")], 0,
         "月亮是面小镜子","答对啦！"),
    ]),
    # ── 星区 8 星星的世界（《国家地理少儿版》《DK神秘宇宙》）──
    ("北斗七星", [
        ("letter", "Big Dipper", "北斗七星", [("bigdipper","北斗七星 Big Dipper","北斗七星"),("star","七颗亮星","星星")], "学一学：北斗七星 Big Dipper"),
        ("quiz", "天上那个大大的勺子是？",
         [("bigdipper","北斗七星"),("star","北极星"),("moon","月亮")], 0,
         "七颗亮星连成勺子","对，北斗七星！"),
        ("quiz", "北斗七星是由几颗星组成的？",
         [(None,"七颗"),(None,"三颗"),(None,"一百颗")], 0,
         "北斗=七颗星","答对啦，七颗！"),
        ("spotlight", "望远镜找一找：大勺子北斗七星在哪里？",
         "bigdipper", ["star","sparkle","starface","moon"]),
    ]),
    ("北极星", [
        ("quiz", "夜里迷路了，找哪颗星帮忙指路？",
         [("starface","北极星"),("meteor","流星"),("sun","太阳")], 0,
         "北极星永远在北方","对，找北极星！"),
        ("quiz", "北极星在天空的哪个方向？",
         [(None,"北方"),(None,"南方"),(None,"一直变来变去")], 0,
         "迷路时抬头找它","答对啦，在北方！"),
        ("spotlight", "望远镜找一找：北极星在哪里？",
         "starface", ["star","sparkle","comet","moon"]),
    ]),
    ("星座", [
        ("letter", "Constellation", "星座", [("bigdipper","星星连成图案","星座"),("star","讲故事的名字","星星")], "学一学：星座 Constellation"),
        ("quiz", "人们把星星连成图案，起名字讲故事，这就是？",
         [(None,"星座"),(None,"文字"),(None,"地图")], 0,
         "猎户座、大熊座都是星座","对，是星座！"),
        ("quiz", "冬夜里最亮的星座「猎户座」像什么？",
         [(None,"一位猎人"),(None,"一只小猫"),(None,"一辆汽车")], 0,
         "腰带三颗星最好认","答对啦，像猎人！"),
    ]),
    ("流星", [
        ("quiz", "「唰」地划过夜空的流星是什么？",
         [(None,"小石块冲进空气里烧出的亮光"),(None,"星星真的掉下来了"),(None,"飞机开灯")], 0,
         "划亮夜空的小访客","对，是石块在发光！"),
        ("quiz", "看到流星，大家可以？",
         [(None,"许个愿"),(None,"把它抓回家"),(None,"关灯睡觉不理它")], 0,
         "流星很快，愿望要快","答对啦，许个愿吧！"),
    ]),
    ("彗星", [
        ("quiz", "谁拖着长长的大尾巴扫过夜空？",
         [("comet","彗星"),("moon","月亮"),("earth","地球")], 0,
         "像一把大扫帚","对，是彗星！"),
        ("quiz", "著名的哈雷彗星绕太阳转一圈要多久？",
         [(None,"大约76年，一生能看到一次"),(None,"一天"),(None,"一万年")], 0,
         "人的一生大约能见到它一次","答对啦，约76年！"),
    ]),
    ("陨石", [
        ("letter", "Meteorite", "陨石", [("meteorite","陨石 Meteorite","陨石"),("rock","像一块小石头","石头")], "学一学：陨石 Meteorite"),
        ("quiz", "掉到地面上的太空石头叫什么？",
         [("meteorite","陨石"),("comet","彗星"),("satellite","卫星")], 0,
         "天上来的石头客人","对，是陨石！"),
        ("quiz", "陨石和流星是亲戚吗？",
         [(None,"是，流星没烧完掉下来就是陨石"),(None,"完全没关系"),(None,"陨石来自大海")], 0,
         "同一家族的不同结局","答对啦！"),
        ("match", "连一连：夜空访客的特征",
         [("comet","彗星","拖着长尾巴绕太阳转"),("sparkle","流星","划过夜空烧出光"),("meteorite","陨石","没烧完掉到地上")]),
    ]),
    ("数流星", [
        ("count", "流星雨来啦！数一数有几颗流星划过？", 6, [5,6,7], "sparkle", "颗"),
        ("quiz", "很多流星一起划过夜空叫什么？",
         [(None,"流星雨"),(None,"大雨"),(None,"流星糖")], 0,
         "一场太空的烟花","对，流星雨！"),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：谁在夜晚的天空？谁在白天的天空？",
         [("night","夜晚的天空","moon"),("day","白天的天空","sun")],
         [("a1","moon","月亮","night"),("a2","star","星星","night"),("a3","sparkle","流星","night"),
          ("b1","sun","太阳","day"),("b2","sunrise","日出","day"),("b3","rainbow","彩虹","day")],
         "白天黑夜的天空都认识啦！"),
        ("quiz", "星星的颜色都一样吗？",
         [(None,"不一样，有红有蓝有黄"),(None,"全都是白色"),(None,"星星没有颜色")], 0,
         "温度不同颜色不同","答对啦！"),
    ]),
    ("星区小挑战", [
        ("quiz", "星星白天还在天上吗？",
         [(None,"在，只是阳光太亮看不见"),(None,"不在，下班了"),(None,"被太阳吃掉了")], 0,
         "白天黑夜都在","对，一直都在！"),
        ("pattern", ["comet","star","comet"], ["star","moon","rocket"], 0, "星空规律：下一个是谁？"),
        ("quiz", "北斗七星像什么？",
         [(None,"一把大勺子"),(None,"一辆汽车"),(None,"一顶帽子")], 0,
         "勺子口对着北极星","答对啦，大勺子！"),
    ]),
    # ── 星区 9 银河和宇宙（《给孩子讲宇宙》（李淼）《时间简史》少儿版）──
    ("银河系", [
        ("letter", "Milky Way", "银河系", [("milkyway","银河系 Milky Way","银河系"),("sun","太阳是其中一颗","太阳")], "学一学：银河系 Milky Way"),
        ("quiz", "我们的太阳住在哪个星系？", [("milkyway","银河系"),("comet","彗星"),("rocket","火箭")], 0,
         "千千万万颗星星的大城市","对，银河系！"),
        ("quiz", "夏天夜空里那条淡淡的星星带是？",
         [(None,"银河"),(None,"云彩"),(None,"彩虹")], 0,
         "从地球看银河系的样子","答对啦，是银河！"),
    ]),
    ("数不清的星星", [
        ("quiz", "银河系里的星星有多少？",
         [(None,"上千亿颗，数也数不清"),(None,"几十颗"),(None,"100颗")], 0,
         "太阳只是普通的一员","对，多得数不清！"),
        ("quiz", "太阳在银河系里是？",
         [(None,"普普通通的一颗星"),(None,"最大的星"),(None,"唯一的星")], 0,
         "银河系里像太阳的星很多","答对啦！"),
    ]),
    ("光年", [
        ("letter", "Light-year", "光年", [("rocket","光跑得飞快","光"),("star","星星离得特别远","星星")], "学一学：光年 Light-year"),
        ("quiz", "光年是什么的单位？",
         [(None,"距离（光跑一年的路程）"),(None,"时间"),(None,"重量")], 0,
         "星星之间实在太远了","对，光年是距离！"),
        ("quiz", "为什么需要用「光年」来量星空？",
         [(None,"星星之间太远，用米量要写好多0"),(None,"光年听起来好听"),(None,"尺子太短了")], 0,
         "宇宙的尺子要够长","答对啦！"),
    ]),
    ("星云", [
        ("quiz", "新的星星从哪里诞生？",
         [(None,"星云，星星的摇篮"),(None,"大海里捞出来"),(None,"火山喷出来")], 0,
         "像一朵彩色的大雾","对，从星云诞生！"),
        ("quiz", "星云看上去像什么？",
         [(None,"彩色的大雾"),(None,"硬邦邦的石头"),(None,"一块黑板")], 0,
         "里面正在孕育新星星","答对啦！"),
    ]),
    ("黑洞", [
        ("letter", "Black Hole", "黑洞", [("blackhole","黑洞 Black Hole","黑洞"),("star","超级重的大天体","天体")], "学一学：黑洞 Black Hole"),
        ("quiz", "连光都逃不出来的洞是？", [("blackhole","黑洞"),("volcano","火山口"),("rock","山洞")], 0,
         "引力大得把光都拉住","对，是黑洞！"),
        ("quiz", "黑洞为什么看起来黑黑的？",
         [(None,"光被它拉住跑不出来"),(None,"它涂了黑漆"),(None,"它不开灯")], 0,
         "没有光出来，就一片黑","答对啦！"),
        ("shadow", "看影子猜猜：这是谁？", "blackhole",
         [("blackhole","黑洞"),("volcano","火山口"),("comet","彗星")], 0,
         "超级重，连光都逃不出来"),
    ]),
    ("宇宙大爆炸", [
        ("quiz", "宇宙是怎么开始的？",
         [(None,"从一个很小很小的点，爆炸膨胀开来"),(None,"从一块大石头"),(None,"本来就全都有")], 0,
         "《给孩子讲宇宙》的第一课","对，宇宙大爆炸！"),
        ("quiz", "大爆炸之后，宇宙在？",
         [(None,"一直膨胀，越来越大"),(None,"马上停住"),(None,"越来越小")], 0,
         "到今天还在长大","答对啦，一直在膨胀！"),
    ]),
    ("宇宙", [
        ("letter", "Universe", "宇宙", [("milkyway","千万个星系","星系"),("star","所有的空间和时间","星星")], "学一学：宇宙 Universe"),
        ("quiz", "宇宙是什么？",
         [(None,"所有星星、星系和空间的总和"),(None,"只有地球"),(None,"只有太阳系")], 0,
         "万物的家都叫宇宙","对，宇宙是一切！"),
        ("quiz", "银河系是宇宙里唯一的星系吗？",
         [(None,"不是，银河系只是其中之一"),(None,"是，就这一个"),(None,"星系是传说")], 0,
         "星系数也数不完","答对啦！"),
    ]),
    ("大还是小", [
        ("quiz", "宇宙在变大还是变小？",
         [(None,"在变大，星系们互相远离"),(None,"在变小"),(None,"不变")], 0,
         "《时间简史》少儿版也讲这个","对，宇宙在膨胀！"),
        ("quiz", "宇宙里的星星，和海边的沙子比？",
         [(None,"天上的星比沙子还多"),(None,"沙子多"),(None,"一样多")], 0,
         "想想都觉得了不起","答对啦，星比沙多！"),
    ]),
    ("拖一拖", [
        ("sort", "拖一拖：谁绕着谁转？",
         [("around-sun","绕太阳转","sun"),("around-earth","绕地球转","earth")],
         [("a1","earth","地球","around-sun"),("a2","mars","火星","around-sun"),("a3","saturn","土星","around-sun"),
          ("b1","moon","月亮","around-earth"),("b2","satellite","人造卫星","around-earth")],
         "行星绕恒星，卫星绕行星！"),
        ("quiz", "月亮和人造卫星都是谁的卫星？",
         [(None,"地球"),(None,"太阳"),(None,"月亮")], 0,
         "地球有月亮和好多人造卫星","答对啦，地球！"),
    ]),
    ("星区小挑战", [
        ("pattern", ["milkyway","star","milkyway"], ["star","moon","comet"], 0, "星空规律：下一个是谁？"),
        ("quiz", "光年量的是什么？", [(None,"距离"),(None,"时间"),(None,"重量")], 0,
         "光跑一年的路程","对，是距离！"),
        ("quiz", "连光都逃不出来的是？", [("blackhole","黑洞"),("comet","彗星"),("moon","月亮")], 0,
         "宇宙最神秘的大胃王","答对啦，黑洞！"),
    ]),
    # ── 星区 10 宇宙大探索（《乔治的宇宙》《万物简史》少儿版）──
    ("望远镜", [
        ("letter", "Telescope", "望远镜", [("telescope","望远镜 Telescope","望远镜"),("star","看得更远","星星")], "学一学：望远镜 Telescope"),
        ("quiz", "想看清远处的星星，用什么帮忙？", [("telescope","望远镜"),("cup","杯子"),("shoe","鞋子")], 0,
         "望远镜把远处的光收拢","对，用望远镜！"),
        ("quiz", "谁第一次用望远镜看到了月亮上的环形山？",
         [(None,"科学家伽利略"),(None,"邮递员"),(None,"小明")], 0,
         "四百多年前的第一次","答对啦，是伽利略！"),
    ]),
    ("天文台", [
        ("quiz", "天文台是做什么的地方？",
         [(None,"看星星、研究星空的房子"),(None,"卖望远镜的商店"),(None,"游乐场")], 0,
         "圆顶房子里藏着大宝贝","对，看星星的地方！"),
        ("quiz", "天文台的圆顶里通常藏着什么？",
         [(None,"巨大的望远镜"),(None,"大滑梯"),(None,"游泳池")], 0,
         "圆顶会打开看星星","答对啦，大望远镜！"),
        ("spotlight", "望远镜找一找：戴着光环的土星在哪里？",
         "saturn", ["jupiter","mars","moon","mercury"]),
    ]),
    ("探测器", [
        ("quiz", "替人类飞去遥远行星拍照的机器叫？",
         [(None,"太空探测器"),(None,"遥控汽车"),(None,"无人机航拍")], 0,
         "人类的太空眼睛","对，探测器！"),
        ("quiz", "旅行者号探测器带着一张地球的唱片，是为什么？",
         [(None,"向宇宙介绍我们的地球"),(None,"在太空听歌跳舞"),(None,"给外星人送快递")], 0,
         "《乔治的宇宙》也讲过它","答对啦，地球的名片！"),
        ("sequence", "探测器发射：按 3→2→1 顺序点，飞向深空！", ["3","2","1"]),
    ]),
    ("火星车", [
        ("letter", "Rover", "火星车", [("robot","火星车 Rover","火星车"),("mars","红色火星 Mars","火星")], "学一学：火星车 Mars Rover"),
        ("quiz", "火星车在火星上做什么？",
         [(None,"拍照、找水的痕迹、研究石头"),(None,"种菜钓鱼"),(None,"送外卖")], 0,
         "火星上的科学小侦探","对，在探索火星！"),
        ("quiz", "火星车是谁送上火星的？",
         [(None,"大火箭"),(None,"起重机"),(None,"热气球")], 0,
         "火箭再立新功","答对啦，火箭送上去！"),
        ("shadow", "看影子猜猜：这是谁？", "robot",
         [("robot","火星车"),("astronaut","宇航员"),("bear","棕小熊")], 0,
         "它有轮子，在火星上慢慢开"),
    ]),
    ("月球车", [
        ("quiz", "宇航员在月亮上开的车叫？",
         [(None,"月球车"),(None,"自行车"),(None,"公交车")], 0,
         "月亮上的专用座驾","对，月球车！"),
        ("quiz", "中国的月球车和探月车都叫什么？",
         [(None,"玉兔号"),(None,"闪电号"),(None,"喷火号")], 0,
         "月亮上的中国兔子","答对啦，玉兔号！"),
    ]),
    ("外星人", [
        ("letter", "UFO", "外星人", [("ufo","飞碟 UFO","飞碟"),("star","宇宙这么大","星星")], "学一学：外星人和 UFO"),
        ("quiz", "科学家用什么办法找外星生命？",
         [(None,"用望远镜和天线，倾听宇宙的声音"),(None,"在小区里贴寻人启事"),(None,"等外星人敲门")], 0,
         "《乔治的宇宙》里的寻星之旅","对，倾听宇宙！"),
        ("quiz", "到现在为止，发现外星人了吗？",
         [(None,"还没有，宇宙这么大也许有各种可能"),(None,"天天见面"),(None,"住在隔壁")], 0,
         "保持好奇，大胆想象","答对啦，还没发现！"),
    ]),
    ("火星家园", [
        ("quiz", "未来人类最想去哪颗行星安家？",
         [(None,"火星"),(None,"水星"),(None,"月亮（它不是行星哦）")], 0,
         "火星是最像地球的行星","对，目标是火星！"),
        ("quiz", "去火星要坐什么交通工具？",
         [(None,"大火箭"),(None,"公交车"),(None,"轮船")], 0,
         "火箭是唯一的天梯","答对啦，大火箭！"),
        ("sequence", "火星移民飞船点火：按 3→2→1 顺序点，出发！", ["3","2","1"]),
    ]),
    ("宇航员训练", [
        ("quiz", "想当宇航员，现在应该？",
         [(None,"好好吃饭锻炼身体，认真学习"),(None,"天天打游戏"),(None,"熬夜不睡觉")], 0,
         "身体和知识都要满分","对，从小练本领！"),
        ("quiz", "宇航员训练时要练习什么？",
         [(None,"转椅训练、穿宇航服、学科学"),(None,"只练跑步"),(None,"只练画画")], 0,
         "太空生活需要很多本领","答对啦！"),
    ]),
    ("星空梦想家", [
        ("quiz", "今晚就能做的观星活动是？",
         [(None,"抬头找北斗七星和月亮"),(None,"数飞机"),(None,"看路灯")], 0,
         "观星从家门口开始","对，抬头看星空！"),
        ("quiz", "记录看到的星星可以用？",
         [(None,"观星日记，画下来"),(None,"吃掉"),(None,"扔掉")], 0,
         "好记性不如烂笔头","答对啦，画下来！"),
        ("quiz", "看星星最好的地方是？",
         [(None,"灯光暗、视野开阔的地方"),(None,"商场顶楼"),(None,"KTV包厢")], 0,
         "灯光越少星星越亮","答对啦！"),
    ]),
]

def astro_compose(idx, name, moves):
    """把一个 move 列表装配成一关的 steps（id 规则 astro-{idx}-m{n}，letter 步固定 -t）"""
    steps = []
    for mi, mv in enumerate(moves):
        kind = mv[0]
        if kind == "letter":
            _, en, display, chips, question = mv
            steps.append(astro_letter(f"astro-{idx}-t", en, display, chips, question,
                                      anim=ASTRO_ANIM_BY_LEVEL.get(name)))
        elif kind == "quiz":
            _, q, items, ans, hint, praise = mv
            steps.append(quiz_step(f"astro-{idx}-m{mi}", q, items, ans, hint, praise))
        elif kind == "pattern":
            _, seq, opts, ans, q = mv
            steps.append(pattern_step(f"astro-{idx}-m{mi}", seq, opts, ans, q))
        elif kind == "balance":
            _, q, left, right, ans, hint = mv
            steps.append(balance_step(f"astro-{idx}-m{mi}", q, left, right, ans, hint))
        elif kind == "sort":
            _, q, bins, items, praise = mv
            steps.append(sort_step(f"astro-{idx}-m{mi}", q, bins, items, praise))
        elif kind == "count":
            _, q, n, opts, icon, unit = mv
            steps.append(astro_count(f"astro-{idx}-m{mi}", q, n, opts, icon, unit))
        elif kind == "listen":
            _, prompt, picon, opt_icons, ans, speak = mv
            steps.append(astro_listen(f"astro-{idx}-m{mi}", prompt, picon, opt_icons, ans, speak))
        elif kind == "tapall":
            _, q, options, hint = mv
            steps.append(tapall_step(f"astro-{idx}-m{mi}", q, options, hint))
        elif kind == "match":
            _, q, pairs = mv
            steps.append(match_step(f"astro-{idx}-m{mi}", q, pairs))
        elif kind == "lineup":
            _, q, items = mv
            steps.append(lineup_step(f"astro-{idx}-m{mi}", q, items))
        elif kind == "sequence":
            _, q, seq = mv
            steps.append(sequence_step(f"astro-{idx}-m{mi}", q, seq))
        elif kind == "spotlight":
            _, q, target, decoys = mv
            steps.append(spotlight_step(f"astro-{idx}-m{mi}", q, target, decoys))
        elif kind == "shadow":
            _, q, shadow, options, ans, hint = mv
            steps.append(shadow_step(f"astro-{idx}-m{mi}", q, shadow, options, ans, hint))
        else:
            raise SystemExit(f"未知 astro move: {kind}")
    return steps

assert len(ASTRO_REGULAR) == 96, f"天文正式关应 96 关，实际 {len(ASTRO_REGULAR)}"
astro_levels = []
for i, (name, moves) in enumerate(ASTRO_REGULAR):
    astro_levels.append({"id": f"astro-{i}", "title": f"第 {i+1} 关 {name}",
                         "subtitle": ASTRO_ZONES[min(i // 10, 9)][0], "steps": astro_compose(i, name, moves)})

# 复习关一/二/三 落在第 3/6/8 星区末（最终第 30/60/80 关），Boss 收官第 100 关
astro_reviews = []
q_by_level = [[s for s in lv["steps"] if s["kind"] not in ("teach", "letter")] for lv in astro_levels]
review_positions = [29, 59, 79]
review_tags = ["astro-r0", "astro-r1", "astro-r2"]
for k, pos in enumerate(review_positions):
    qs = sample_questions(q_by_level[:pos], 6, review_tags[k])
    astro_reviews.append({
        "id": review_tags[k],
        "title": f"复习关 {'一二三'[k]}",
        "subtitle": "旧题开盲盒 · 混排复习",
        "steps": qs,
        "board": build_board([q["id"] for q in qs], ["coin", "coin"] + REVIEW_EVENTS[k % len(REVIEW_EVENTS)], k),
        "review": True,
    })
astro_levels = (astro_levels[:29] + [astro_reviews[0]] + astro_levels[29:58] + [astro_reviews[1]]
                + astro_levels[58:77] + [astro_reviews[2]] + astro_levels[77:])
add_boss_level(astro_levels, "astro")
assert len(astro_levels) == 100, f"天文台应 100 关，实际 {len(astro_levels)}"

# 星区编号（保卫萝卜式分章：每星区恰好 10 关，UI 一次只展示一个星区）
for i, lv in enumerate(astro_levels):
    lv["zone"] = i // 10 + 1
assert [len([l for l in astro_levels if l["zone"] == z]) for z in range(1, 11)] == [10] * 10

W("astro_levels.json", {"subject": "astro", "title": "天文台", "guide": "robot",
                        "zones": [{"n": z + 1, "title": t, "subtitle": s}
                                  for z, (t, s) in enumerate(ASTRO_ZONES)],
                        "levels": astro_levels})

# ================= 环球号 geo（新学科）12 关 =================
geo_levels = []

def geo_letter(gid, display, examples, question):
    return {"id": f"{gid}-t", "kind": "letter", "letters": [display], "display": display,
            "examples": examples, "question": question}

def geo_quiz(qid, q, items, ans, hint, praise):
    return quiz_step(qid, q, items, ans, hint, praise)

def mappuzzle_step(mid, the_map, regions, q):
    return {"id": mid, "kind": "mappuzzle", "map": the_map, "regions": regions,
            "question": q, "praise": "拼好啦，地图在你手里！"}

# 中国章（6 关）
CHINA_BLOCKS = [
    {"id": "cn-north", "label": "东北", "color": "#8AB8E8", "points": [[60,8],[80,10],[78,22],[62,20]]},
    {"id": "cn-west", "label": "西部", "color": "#F4A259", "points": [[40,10],[60,8],[62,20],[44,24]]},
    {"id": "cn-central", "label": "中部", "color": "#7FC6A4", "points": [[44,24],[62,20],[66,34],[48,36]]},
    {"id": "cn-east", "label": "东部", "color": "#E07A5F", "points": [[62,20],[78,22],[80,38],[66,34]]},
    {"id": "cn-south", "label": "南方", "color": "#F2C14E", "points": [[48,36],[66,34],[70,48],[52,50]]},
    {"id": "cn-island", "label": "海岛", "color": "#9B8CE8", "points": [[52,50],[62,48],[60,56],[50,55]]},
]
geo_levels.append({"id": "geo-0", "title": "第 1 关 中国地图", "subtitle": "大雄鸡", "steps": [
    geo_letter("geo-0", "中国", [{"icon": "china-map", "text": "中国地图", "say": "中国"},
                                 {"icon": "panda", "text": "我们的家", "say": "中国"}],
               "学一学：中国地图像一只大雄鸡"),
    mappuzzle_step("geo-0-pz", "china", CHINA_BLOCKS, "拼一拼：把中国地图的六块拖回雄鸡轮廓"),
]})
geo_levels.append({"id": "geo-1", "title": "第 2 关 北京", "subtitle": "天安门", "steps": [
    geo_letter("geo-1", "北京", [{"icon": "tiananmen", "text": "天安门", "say": "天安门"},
                                 {"icon": "flag", "text": "国旗", "say": "国旗"}],
               "学一学：北京是中国的首都，天安门在北京"),
    geo_quiz("geo-1-q1","中国的首都是哪座城市？",
             [("beijing" if False else "tiananmen","北京"),("castle",None),("school",None)],0,"天安门在北京","北京是首都！"),
]})
geo_levels.append({"id": "geo-2", "title": "第 3 关 长江黄河", "subtitle": "母亲河", "steps": [
    geo_letter("geo-2", "江河", [{"icon": "river", "text": "长江黄河", "say": "长江"},
                                 {"icon": "wave", "text": "河水", "say": "河"}],
               "学一学：长江和黄河是中国的母亲河，从西向东流"),
    geo_quiz("geo-2-q1","长江和黄河是中国的什么河？",
             [("river",None),("moon",None),("comet",None)],0,"母亲河","母亲河记住啦！"),
]})
geo_levels.append({"id": "geo-3", "title": "第 4 关 万里长城", "subtitle": "长城", "steps": [
    geo_letter("geo-3", "长城", [{"icon": "greatwall", "text": "万里长城", "say": "长城"},
                                 {"icon": "castle", "text": "像长龙", "say": "长城"}],
               "学一学：万里长城像一条长龙，卧在山上"),
    geo_quiz("geo-3-q1","万里长城像一条卧在山上的什么？",
             [("dragon" if False else "greatwall",None),("rocket",None),("moon",None)],0,"长龙","长城真雄伟！"),
]})
geo_levels.append({"id": "geo-4", "title": "第 5 关 珠穆朗玛峰", "subtitle": "世界最高峰", "steps": [
    geo_letter("geo-4", "珠峰", [{"icon": "everest", "text": "珠穆朗玛峰", "say": "珠峰"},
                                 {"icon": "snow" if False else "ice", "text": "山顶积雪", "say": "雪"}],
               "学一学：珠穆朗玛峰是世界第一高峰，山顶盖着白雪"),
    geo_quiz("geo-4-q1","世界第一高峰是哪座山？",
             [("everest",None),("volcano",None),("castle",None)],0,"最高最高","珠峰真高！"),
]})
geo_levels.append({"id": "geo-5", "title": "第 6 关 熊猫故乡", "subtitle": "大熊猫", "steps": [
    geo_letter("geo-5", "熊猫", [{"icon": "panda", "text": "大熊猫", "say": "熊猫"},
                                 {"icon": "leaf", "text": "爱吃竹子", "say": "竹子"}],
               "学一学：大熊猫是中国的国宝，最爱吃竹子"),
    geo_quiz("geo-5-q1","中国的国宝、爱吃竹子的动物是谁？",
             [("bear",None),("panda",None),("rabbit",None)],1,"黑白毛、圆滚滚","大熊猫真可爱！"),
]})

# 世界章（6 关）
WORLD_BLOCKS = [
    {"id": "northamerica", "label": "北美洲", "color": "#F4A259", "points": [[10,14],[30,12],[34,30],[24,40],[12,34]]},
    {"id": "southamerica", "label": "南美洲", "color": "#E07A5F", "points": [[24,42],[34,40],[34,56],[26,58],[22,48]]},
    {"id": "europe", "label": "欧洲", "color": "#9B8CE8", "points": [[44,16],[54,14],[56,26],[46,28]]},
    {"id": "africa", "label": "非洲", "color": "#F2C14E", "points": [[46,28],[58,28],[60,50],[50,56],[44,44]]},
    {"id": "asia", "label": "亚洲", "color": "#8AB8E8", "points": [[56,12],[84,14],[86,38],[66,40],[56,28]]},
    {"id": "oceania", "label": "大洋洲", "color": "#7FC6A4", "points": [[76,46],[90,44],[92,54],[80,56]]},
    {"id": "antarctica", "label": "南极洲", "color": "#B8D4E8", "points": [[30,56],[70,56],[72,60],[30,60]]},
]
geo_levels.append({"id": "geo-6", "title": "第 7 关 七大洲拼图", "subtitle": "世界地图", "steps": [
    geo_letter("geo-6", "世界", [{"icon": "world-map", "text": "世界地图", "say": "世界"},
                                 {"icon": "earth", "text": "地球", "say": "地球"}],
               "学一学：地球上有七大洲，我们住在亚洲"),
    mappuzzle_step("geo-6-pz", "world", WORLD_BLOCKS, "拼一拼：把七大洲块拖回世界地图轮廓"),
]})
geo_levels.append({"id": "geo-7", "title": "第 8 关 亚洲", "subtitle": "我们的家", "steps": [
    geo_letter("geo-7", "亚洲", [{"icon": "earth", "text": "亚洲 Asia", "say": "亚洲"},
                                 {"icon": "home", "text": "我们的家", "say": "家"}],
               "学一学：我们住在亚洲，它是最大的大洲"),
    geo_quiz("geo-7-q1", "我们中国在哪个大洲？",
             [("asia" if False else "earth",None),("moon",None),("comet",None)],0,"最大的大洲","亚洲是我们的家！"),
]})
geo_levels.append({"id": "geo-8", "title": "第 9 关 非洲", "subtitle": "狮子大象", "steps": [
    geo_letter("geo-8", "非洲", [{"icon": "lion", "text": "狮子 Lion", "say": "狮子"},
                                 {"icon": "elephant", "text": "大象 Elephant", "say": "大象"}],
               "学一学：非洲草原上住着狮子和大象"),
    geo_quiz("geo-8-q1","非洲草原上「万兽之王」是谁？",
             [("elephant",None),("lion",None),("panda",None)],1,"吼——的大王","狮子是万兽之王！"),
]})
geo_levels.append({"id": "geo-9", "title": "第 10 关 欧洲", "subtitle": "城堡风车", "steps": [
    geo_letter("geo-9", "欧洲", [{"icon": "castle", "text": "城堡 Castle", "say": "城堡"},
                                 {"icon": "windmill", "text": "风车 Windmill", "say": "风车"}],
               "学一学：欧洲有许多古老的城堡和转动的风车"),
    geo_quiz("geo-9-q1","欧洲田野上慢慢转动的是什么？",
             [("windmill",None),("rocket",None),("comet",None)],0,"转呀转","风车转起来啦！"),
]})
geo_levels.append({"id": "geo-10", "title": "第 11 关 美洲", "subtitle": "自由女神", "steps": [
    geo_letter("geo-10", "美洲", [{"icon": "libertystatue", "text": "自由女神", "say": "自由女神"},
                                 {"icon": "ferris", "text": "摩天轮", "say": "摩天轮"}],
               "学一学：美洲有举着火炬的自由女神像"),
    geo_quiz("geo-10-q1","举着火炬、站在美国纽约港的是谁？",
             [("libertystatue",None),("panda",None),("moon",None)],0,"火炬女神","自由女神记住啦！"),
]})
geo_levels.append({"id": "geo-11", "title": "第 12 关 大洋洲与极地", "subtitle": "袋鼠企鹅", "steps": [
    geo_letter("geo-11", "大洋洲极地", [{"icon": "kangaroo", "text": "袋鼠 Kangaroo", "say": "袋鼠"},
                                      {"icon": "penguin", "text": "企鹅 Penguin", "say": "企鹅"},
                                      {"icon": "polarbear", "text": "北极熊", "say": "北极熊"}],
               "学一学：大洋洲有袋鼠，极地有企鹅和北极熊"),
    geo_quiz("geo-11-q1","肚子上有口袋、会跳的动物是谁？",
             [("rabbit",None),("kangaroo",None),("bear",None)],1,"大口袋","袋鼠跳得高！"),
    geo_quiz("geo-11-q2","冰天雪地里穿黑燕尾服的小鸟是谁？",
             [("duck",None),("penguin",None),("bird" if False else "cat",None)],1,"冰上绅士","企鹅真可爱！"),
]})

# —— v0.11 地理 50 关扩容（中国 12 · 世界国家 10 · 首都 6 · 自然纪录 6）——
def geo_new(gid, title, subtitle, disp, examples, question, quiz_q, quiz_opts, ans, hint):
    ex = [{"icon": ic, "text": t, "say": t} if ic else {"text": t} for ic, t in examples]
    return {"id": gid, "title": title, "subtitle": subtitle, "steps": [
        geo_letter(gid, disp, ex, question),
        geo_quiz(f"{gid}-q1", quiz_q, quiz_opts, ans, hint, f"{quiz_opts[ans][1] or quiz_opts[ans][0]}答对啦！"),
    ]}

GEO_NEW = [
    ("geo-12", "第 13 关 上海", "东方明珠", "上海", [("tower","东方明珠"),("flag","大上海")],
     "学一学：上海是中国最大的城市", "东方明珠塔在哪座城市？",
     [("tower","上海"),("tiananmen","北京"),("greatwall","长城")], 0, "黄浦江边，高高的塔"),
    ("geo-13", "第 14 关 哈尔滨", "冰城", "哈尔滨", [("snowflake","冰雪大世界"),("snowflake","冰雕")],
     "学一学：哈尔滨的冬天像冰做的童话世界", "冰雕最美的城市是？",
     [("snowflake","哈尔滨"),("palm","海南"),("desert","新疆")], 0, "东北的冰城"),
    ("geo-14", "第 15 关 海南", "椰林海滩", "海南", [("palm","椰子树"),("wave","大海")],
     "学一学：海南岛有椰子树和软软的沙滩", "椰子树最多的省份是？",
     [("palm","海南"),("snowflake","哈尔滨"),("everest","珠峰")], 0, "最南面的宝岛"),
    ("geo-15", "第 16 关 新疆", "戈壁瓜果", "新疆", [("desert","大沙漠"),("apple","哈密瓜")],
     "学一学：新疆有大沙漠，瓜果特别甜", "中国面积最大的省区是？",
     [("desert","新疆"),("china-map","北京"),("wave","上海")], 0, "西北好大好大"),
    ("geo-16", "第 17 关 云南", "彩云之南", "云南", [("rainbow","彩云"),("flower","鲜花")],
     "学一学：云南四季如春，鲜花盛开", "彩云之南指的是？",
     [("rainbow","云南"),("lion","非洲"),("windmill","荷兰")], 0, "鲜花四季开"),
    ("geo-17", "第 18 关 台湾", "宝岛", "台湾", [("tree","阿里山"),("wave","海峡")],
     "学一学：台湾是祖国的宝岛", "祖国的宝岛是？",
     [("tree","台湾"),("kangaroo","澳大利亚"),("penguin","南极")], 0, "海峡对面"),
    ("geo-18", "第 19 关 桂林山水", "山水如画", "桂林", [("sprout","漓江山水"),("wave","江水")],
     "学一学：桂林山水甲天下", "「桂林山水甲天下」说的是哪里最美？",
     [("sprout","桂林山水"),("desert","沙漠"),("castle","城堡")], 0, "山清水秀"),
    ("geo-19", "第 20 关 黄山", "奇松怪石", "黄山", [("sprout","黄山松"),("volcano","山峰")],
     "学一学：黄山有奇松、怪石和云海", "黄山最出名的是？",
     [("sprout","迎客松"),("penguin","企鹅"),("bigben","大本钟")], 0, "迎客松有名"),
    ("geo-20", "第 21 关 日本", "樱花和富士山", "日本", [("torii","鸟居"),("fuji","富士山")],
     "学一学：日本有樱花、富士山和鸟居", "富士山在哪国？",
     [("torii","日本"),("greatwall","中国"),("libertystatue","美国")], 0, "樱花之国"),
    ("geo-21", "第 22 关 泰国", "大象之国", "泰国", [("elephant","亚洲象"),("flag","泰国")],
     "学一学：泰国的亚洲象很有名", "大象之国是？",
     [("elephant","泰国"),("penguin","南极"),("kangaroo","澳大利亚")], 0, "亚洲南部"),
    ("geo-22", "第 23 关 埃及", "金字塔", "埃及", [("pyramid","金字塔"),("desert","沙漠")],
     "学一学：埃及有金字塔和尼罗河", "金字塔在哪国？",
     [("pyramid","埃及"),("bigben","英国"),("eiffel","法国")], 0, "尼罗河边的沙漠国"),
    ("geo-23", "第 24 关 法国", "埃菲尔铁塔", "法国", [("eiffel","埃菲尔铁塔"),("flag","巴黎")],
     "学一学：法国巴黎有埃菲尔铁塔", "埃菲尔铁塔在哪国？",
     [("eiffel","法国"),("pyramid","埃及"),("torii","日本")], 0, "浪漫之都巴黎"),
    ("geo-24", "第 25 关 英国", "大本钟", "英国", [("bigben","大本钟"),("flag","伦敦")],
     "学一学：英国伦敦有大本钟", "大本钟在哪国？",
     [("bigben","英国"),("eiffel","法国"),("pyramid","埃及")], 0, "伦敦的钟楼"),
    ("geo-25", "第 26 关 俄罗斯", "面积最大", "俄罗斯", [("castle","红场城堡"),("snowflake","冰雪")],
     "学一学：俄罗斯是世界上面积最大的国家", "世界上面积最大的国家是？",
     [("castle","俄罗斯"),("china-map","中国"),("kangaroo","澳大利亚")], 0, "横跨欧亚大陆"),
    ("geo-26", "第 27 关 印度", "泰姬陵", "印度", [("taj","泰姬陵"),("flag","印度")],
     "学一学：印度有雪白的泰姬陵", "泰姬陵在哪国？",
     [("taj","印度"),("bigben","英国"),("tower","上海")], 0, "南亚大国"),
    ("geo-27", "第 28 关 意大利", "比萨斜塔", "意大利", [("pisa","比萨斜塔"),("flag","罗马")],
     "学一学：意大利的比萨斜塔斜而不倒", "比萨斜塔在哪国？",
     [("pisa","意大利"),("eiffel","法国"),("bigben","英国")], 0, "斜而不倒真奇妙"),
    ("geo-28", "第 29 关 加拿大", "枫叶之国", "加拿大", [("maple","枫叶"),("flag","加拿大")],
     "学一学：加拿大的国旗上有一片枫叶", "枫叶之国是？",
     [("maple","加拿大"),("rainbow","云南"),("torii","日本")], 0, "北美的枫叶国"),
    ("geo-29", "第 30 关 巴西", "足球王国", "巴西", [("ball","足球"),("tree","雨林")],
     "学一学：巴西是足球王国，还有大雨林", "足球王国是？",
     [("ball","巴西"),("bigben","英国"),("torii","日本")], 0, "南美洲最大国"),
    ("geo-30", "第 31 关 首都·东京", "日本首都", "东京", [("torii","东京"),("tower","高塔")],
     "学一学：东京是日本的首都", "日本的首都是？",
     [("torii","东京"),("beijing" if False else "tiananmen","北京"),("eiffel","巴黎")], 0, "樱花下的都市"),
    ("geo-31", "第 32 关 首都·开罗", "埃及首都", "开罗", [("pyramid","金字塔"),("flag","开罗")],
     "学一学：开罗是埃及的首都", "埃及的首都是？",
     [("pyramid","开罗"),("bigben","伦敦"),("eiffel","巴黎")], 0, "金字塔下的城"),
    ("geo-32", "第 33 关 首都·巴黎", "法国首都", "巴黎", [("eiffel","埃菲尔铁塔"),("flag","巴黎")],
     "学一学：巴黎是法国的首都", "法国的首都是？",
     [("eiffel","巴黎"),("bigben","伦敦"),("torii","东京")], 0, "塞纳河畔"),
    ("geo-33", "第 34 关 首都·伦敦", "英国首都", "伦敦", [("bigben","大本钟"),("flag","伦敦")],
     "学一学：伦敦是英国的首都", "英国的首都是？",
     [("bigben","伦敦"),("pyramid","开罗"),("eiffel","巴黎")], 0, "泰晤士河边"),
    ("geo-34", "第 35 关 首都·莫斯科", "俄罗斯首都", "莫斯科", [("castle","红场"),("snowflake","冰雪")],
     "学一学：莫斯科是俄罗斯的首都", "俄罗斯的首都是？",
     [("castle","莫斯科"),("eiffel","巴黎"),("pisa","罗马")], 0, "红场在这里"),
    ("geo-35", "第 36 关 首都·华盛顿", "美国首都", "华盛顿", [("libertystatue","自由女神"),("flag","华盛顿")],
     "学一学：华盛顿是美国的首都", "美国的首都是？",
     [("libertystatue","华盛顿"),("torii","东京"),("bigben","伦敦")], 0, "白宫在这里"),
    ("geo-36", "第 37 关 太平洋", "最大的海洋", "太平洋", [("wave","大海"),("fish","鱼群")],
     "学一学：太平洋是世界上最大的海洋", "世界上最大的海洋是？",
     [("wave","太平洋"),("river","长江"),("desert","撒哈拉")], 0, "四大洋的老大"),
    ("geo-37", "第 38 关 北冰洋", "最小最冷的洋", "北冰洋", [("polarbear","北极熊"),("snowflake","浮冰")],
     "学一学：北冰洋最小最冷，北极熊住这里", "北极熊住在哪个洋边？",
     [("polarbear","北冰洋"),("wave","太平洋"),("elephant","非洲")], 0, "满海都是浮冰"),
    ("geo-38", "第 39 关 撒哈拉沙漠", "最大的沙漠", "撒哈拉", [("desert","沙丘"),("sun","烈日")],
     "学一学：撒哈拉是世界上最大的沙漠", "世界上最大的沙漠是？",
     [("desert","撒哈拉"),("wave","太平洋"),("sprout","森林")], 0, "非洲北部的沙海"),
    ("geo-39", "第 40 关 亚马孙雨林", "地球之肺", "亚马孙", [("tree","雨林"),("frog","树蛙")],
     "学一学：亚马孙雨林叫「地球之肺」", "「地球之肺」指的是？",
     [("tree","亚马孙雨林"),("desert","撒哈拉"),("wave","大海")], 0, "制造氧气的大森林"),
    ("geo-40", "第 41 大堡礁", "海底花园", "大堡礁", [("crystal","珊瑚"),("fish","鱼群")],
     "学一学：大堡礁是最大的珊瑚礁群", "最大的珊瑚礁群是？",
     [("crystal","大堡礁"),("greatwall","长城"),("pyramid","金字塔")], 0, "澳大利亚的海底花园"),
    ("geo-41", "第 42 尼罗河", "最长的河流", "尼罗河", [("river","尼罗河"),("pyramid","金字塔")],
     "学一学：尼罗河是世界上最长的河流", "世界上最长的河流是？",
     [("river","尼罗河"),("wave","太平洋"),("desert","撒哈拉")], 0, "埃及的母亲河"),
    ("geo-42", "第 43 火山", "会喷火的山", "火山", [("volcano","火山喷发"),("flame","岩浆")],
     "学一学：火山喷发时岩浆会流出来", "火山喷出的是？",
     [("volcano","岩浆"),("wave","海水"),("bulb","灯光")], 0, "地下冒出的红岩浆"),
    ("geo-43", "第 44 珊瑚海", "珊瑚的家", "珊瑚", [("crystal","珊瑚"),("fish","小鱼")],
     "学一学：珊瑚是小小的海洋动物建成的", "珊瑚是——",
     [(None,"小小的海洋动物"),(None,"海底的石头"),(None,"一种海草")], 0, "千万个小生命建成"),
    ("geo-44", "第 45 七大洲四大洋", "地球大家庭", "七大洲四大洋", [("world-map","世界地图"),("earth","地球")],
     "学一学：地球上有七大洲和四大洋", "地球上有几大洲几大洋？",
     [(None,"七大洲四大洋"),(None,"一大洲一大洋"),(None,"五大洲三大洋")], 0, "世界地图看一看"),
]

GEO_NEW.append(
    ("geo-45", "第 46 关 南极和北极", "地球的两端", "南极北极", [("penguin","南极企鹅"),("polarbear","北极熊")],
     "学一学：地球最南端和最北端都是冰雪世界", "企鹅住在哪一端？",
     [("penguin","南极"),("polarbear","北极"),("desert","撒哈拉")], 0, "企鹅在南极，北极熊在北极"))

for g in GEO_NEW:
    try:
        geo_levels.append(geo_new(*g))
    except TypeError:
        print("BAD GEO ENTRY:", g[0], "argc:", len(g))
        raise

# —— v0.12 地理二阶 +54 关（DK 儿童地理百科 / 国家地理少儿版）——
GEO2 = [
    # 中国各地（8）
    ("geo-46", "第 47 关 广州", "千年商都", "广州", [("shop","商贸之都"),("tower","小蛮腰")],
     "学一学：广州是中国南方的商贸大城", "「千年商都」是——", [("shop","广州"),("castle","莫斯科"),("torii","东京")], 0, "南方大港口"),
    ("geo-47", "第 48 关 杭州", "西湖龙井", "杭州", [("wave","西湖"),("sprout","龙井茶")],
     "学一学：杭州有西湖和龙井茶", "西湖在哪座城市？", [("wave","杭州"),("palm","海南"),("everest","西藏")], 0, "上有天堂下有苏杭"),
    ("geo-48", "第 49 关 成都", "天府之国", "成都", [("panda","大熊猫基地"),("sprout","天府沃野")],
     "学一学：成都是大熊猫的老家", "大熊猫基地在——", [("panda","成都"),("kangaroo","澳大利亚"),("lion","非洲")], 0, "四川成都"),
    ("geo-49", "第 50 关 甘肃", "敦煌莫高窟", "甘肃", [("desert","敦煌沙漠"),("flag","丝路")],
     "学一学：敦煌有莫高窟壁画", "莫高窟在哪一省？", [("desert","甘肃"),("wave","浙江"),("palm","海南")], 0, "丝绸之路重镇"),
    ("geo-50", "第 51 关 青海湖", "中国最大湖", "青海湖", [("wave","青海湖"),("sprout","油菜花")],
     "学一学：青海湖是中国最大的湖", "中国最大的湖是——", [("wave","青海湖"),("river","长江"),("wave","死海")], 0, "高原蓝宝石"),
    ("geo-51", "第 52 关 西藏", "世界屋脊", "西藏", [("everest","珠穆朗玛峰"),("flag","布达拉宫")],
     "学一学：西藏被称为世界屋脊", "「世界屋脊」是——", [("everest","西藏"),("wave","上海"),("castle","俄罗斯")], 0, "最高的高原"),
    ("geo-52", "第 53 关 内蒙古", "大草原", "内蒙古", [("sprout","大草原"),("flag","那达慕赛马")],
     "学一学：内蒙古有一望无际的草原", "内蒙古的代表风景是——", [("sprout","大草原"),("wave","大海"),("desert","沙漠")], 0, "风吹草低见牛羊"),
    ("geo-53", "第 54 关 香港", "东方之珠", "香港", [("tower","高楼"),("flag","紫荆花")],
     "学一学：香港被称为东方之珠", "「东方之珠」是——", [("tower","香港"),("palm","海南"),("torii","东京")], 0, "夜景最亮"),
    # 世界国家（14）
    ("geo-54", "第 55 关 荷兰", "风车王国", "荷兰", [("windmill","大风车"),("flower","郁金香")],
     "学一学：荷兰有风车和郁金香", "风车王国是——", [("windmill","荷兰"),("maple","加拿大"),("torii","日本")], 0, "低地之国"),
    ("geo-55", "第 56 关 瑞士", "雪山之国", "瑞士", [("everest","阿尔卑斯雪山"),("snowflake","滑雪")],
     "学一学：瑞士的阿尔卑斯雪山很有名", "雪山之国是——", [("everest","瑞士"),("desert","埃及"),("palm","海南")], 0, "滑雪胜地"),
    ("geo-56", "第 57 关 南非", "钻石之国", "南非", [("crystal","钻石"),("elephant","大象")],
     "学一学：南非出产钻石", "钻石之国是——", [("crystal","南非"),("pisa","意大利"),("torii","日本")], 0, "非洲最南端"),
    ("geo-57", "第 58 关 芬兰", "圣诞老人的家", "芬兰", [("snowflake","冰雪"),("party","圣诞老人村")],
     "学一学：传说圣诞老人住在芬兰", "圣诞老人村在——", [("party","芬兰"),("palm","海南"),("desert","埃及")], 0, "北欧千湖之国"),
    ("geo-58", "第 59 关 丹麦", "童话王国", "丹麦", [("book","安徒生童话"),("castle","美人鱼像")],
     "学一学：童话作家安徒生是丹麦人", "童话王国是——", [("book","丹麦"),("bigben","英国"),("eiffel","法国")], 0, "丑小鸭和小美人鱼"),
    ("geo-59", "第 60 关 印度扩展", "恒河与纱丽", "印度", [("taj","泰姬陵"),("wave","恒河")],
     "学一学：恒河是印度的圣河", "恒河流经——", [("taj","印度"),("bigben","英国"),("castle","俄罗斯")], 0, "南亚文明古国"),
    ("geo-60", "第 61 关 新西兰", "长白云之乡", "新西兰", [("sprout","绿地"),("wave","海湾")],
     "学一学：新西兰被称为长白云之乡", "长白云之乡是——", [("sprout","新西兰"),("kangaroo","澳大利亚"),("polarbear","北极")], 0, "大洋洲岛国"),
    ("geo-61", "第 62 关 挪威", "峡湾之国", "挪威", [("everest","峡湾陡壁"),("snowflake","极夜")],
     "学一学：挪威有美丽的峡湾", "峡湾之国是——", [("everest","挪威"),("windmill","荷兰"),("taj","印度")], 0, "北欧海盗国度"),
    ("geo-62", "第 63 关 希腊", "奥运发源地", "希腊", [("flag","奥林匹克"),("castle","神庙")],
     "学一学：奥林匹克运动会起源于希腊", "奥运会发源于——", [("flag","希腊"),("bigben","英国"),("pisa","意大利")], 0, "雅典卫城"),
    ("geo-63", "第 64 关 阿根廷", "探戈与足球", "阿根廷", [("ball","足球"),("party","探戈舞")],
     "学一学：阿根廷足球和探戈舞都很有名", "梅西的祖国是——", [("ball","阿根廷"),("torii","日本"),("pisa","意大利")], 0, "南美银之国"),
    ("geo-64", "第 65 关 肯尼亚", "动物大迁徙", "肯尼亚", [("lion","草原狮"),("elephant","象群")],
     "学一学：肯尼亚有动物大迁徙", "动物大迁徙在——", [("lion","肯尼亚"),("penguin","南极"),("kangaroo","澳大利亚")], 0, "非洲草原壮景"),
    ("geo-65", "第 66 关 智利", "最狭长的国家", "智利", [("everest","安第斯山"),("wave","太平洋")],
     "学一学：智利是世界上最狭长的国家", "最狭长的国家是——", [("everest","智利"),("ball","巴西"),("tower","上海")], 0, "安第斯山下"),
    ("geo-66", "第 67 关 冰岛", "冰与火之国", "冰岛", [("volcano","火山"),("snowflake","冰川")],
     "学一学：冰岛有冰川也有火山", "「冰与火之国」是——", [("volcano","冰岛"),("palm","海南"),("desert","埃及")], 0, "冰川火山共存"),
    ("geo-67", "第 68 关 秘鲁", "印加古道", "秘鲁", [("everest","安第斯古城"),("flag","马丘比丘")],
     "学一学：秘鲁有神秘的马丘比丘古城", "马丘比丘在——", [("everest","秘鲁"),("pyramid","埃及"),("taj","印度")], 0, "天空之城"),
    # 自然纪录（12）
    ("geo-68", "第 69 关 马里亚纳海沟", "最深的海", "马里亚纳海沟", [("wave","深深的海沟"),("fish","深海鱼")],
     "学一学：马里亚纳海沟是海洋最深的地方", "海洋最深处在——", [("wave","马里亚纳海沟"),("river","长江"),("desert","撒哈拉")], 0, "深过最高的山"),
    ("geo-69", "第 70 贝加尔湖", "最深的湖", "贝加尔湖", [("wave","清澈湖水"),("snowflake","蓝冰")],
     "学一学：贝加尔湖是最深的淡水湖", "最深的淡水湖是——", [("wave","贝加尔湖"),("river","尼罗河"),("wave","青海湖")], 0, "西伯利亚蓝眼睛"),
    ("geo-70", "第 71 死海", "最咸的湖", "死海", [("wave","死海漂浮"),("sun","烈日")],
     "学一学：死海太咸，人能浮在水面", "人能躺在水上看书的湖是——", [("wave","死海"),("river","尼罗河"),("wave","太平洋")], 0, "盐分超级高"),
    ("geo-71", "第 72 格陵兰岛", "最大的岛", "格陵兰", [("snowflake","冰雪大岛"),("polarbear","北极动物")],
     "学一学：格陵兰是世界最大的岛", "世界最大的岛是——", [("snowflake","格陵兰"),("wave","太平洋"),("tree","海南")], 0, "满岛冰川"),
    ("geo-72", "第 73 夏威夷", "火山群岛", "夏威夷", [("volcano","活火山"),("palm","草裙舞")],
     "学一学：夏威夷是火山喷出的群岛", "夏威夷群岛由什么组成？", [(None,"火山岛"),(None,"冰川岛"),(None,"珊瑚岛")], 0, "基拉韦厄活火山"),
    ("geo-73", "第 74 恐龙时代", "侏罗纪", "恐龙", [("dino","霸王龙"),("dino","梁龙")],
     "学一学：恐龙生活在几千万年前", "恐龙生活在——", [(None,"几千万年前"),(None,"去年"),(None,"明天")], 0, "史前巨兽"),
    ("geo-74", "第 75 恐龙灭绝", "大灭绝之谜", "恐龙灭绝", [("meteorite","陨石撞击"),("volcano","火山喷发")],
     "学一学：陨石撞击可能是恐龙灭绝的原因", "恐龙为什么灭绝？", [(None,"可能因陨石撞击"),(None,"被人类吃光"),(None,"去旅游了")], 0, "科学家仍在研究"),
    ("geo-75", "第 76 化石", "远古的脚印", "化石", [("rock","岩石里的化石"),("dino","恐龙化石")],
     "学一学：化石记录了远古生命", "化石藏在哪里？", [("rock","岩石里"),("wave","海水里"),("cake","蛋糕里")], 0, "地球的历史书"),
    ("geo-76", "第 77 陨石", "天外来客", "陨石", [("meteorite","陨石"),("comet","彗星")],
     "学一学：陨石是从太空掉落的石头", "陨石来自——", [(None,"太空"),(None,"地底"),(None,"大海")], 0, "太空访客"),
    ("geo-77", "第 78 彗星", "哈雷彗星", "哈雷彗星", [("comet","彗星"),("star","星空")],
     "学一学：哈雷彗星约 76 年回来一次", "哈雷彗星绕谁转？", [(None,"太阳"),(None,"月亮"),(None,"地球")], 0, "拖着尾巴的访客"),
    ("geo-78", "第 79 极昼极夜", "太阳不落山", "极昼极夜", [("polarbear","北极极昼"),("snowflake","极夜")],
     "学一学：极地夏天太阳不落，冬天不见太阳", "极昼是——", [(None,"太阳整日不落"),(None,"整天黑夜"),(None,"下雪")], 0, "南北极才有的奇景"),
    ("geo-79", "第 80 珊瑚礁", "海底热带雨林", "珊瑚礁", [("crystal","珊瑚"),("fish","鱼群")],
     "学一学：珊瑚礁养着四分之一的海洋生物", "珊瑚礁在——", [(None,"温暖浅海"),(None,"深海底"),(None,"沙漠里")], 0, "海洋生命摇篮"),
    # 节日文化（6）
    ("geo-80", "第 81 春节", "中国新年", "春节", [("party","贴春联放鞭炮"),("flag","红旗灯笼")],
     "学一学：春节是中国最重要的节日", "中国最重要的传统节日是——", [("party","春节"),("party","圣诞"),("cake","生日")], 0, "全家团圆过年"),
    ("geo-81", "第 82 中秋节", "月圆人团圆", "中秋节", [("moon","圆月"),("cake","月饼")],
     "学一学：中秋吃月饼、赏明月", "中秋节吃什么？", [("cake","月饼"),("candy","糖"),("bread","面包")], 0, "八月十五月儿圆"),
    ("geo-82", "第 83 端午节", "龙舟粽子", "端午节", [("wave","赛龙舟"),("leaf","粽叶")],
     "学一学：端午赛龙舟、吃粽子", "端午节纪念——", [(None,"屈原"),(None,"牛郎"),(None,"嫦娥")], 0, "五月初五"),
    ("geo-83", "第 84 圣诞节", "圣诞快乐", "圣诞节", [("snowflake","雪花"),("party","圣诞树")],
     "学一学：圣诞节是西方重要节日", "圣诞节在哪一天？", [(None,"12 月 25 日"),(None,"1 月 1 日"),(None,"8 月 15 日")], 0, "圣诞老人传说"),
    ("geo-84", "第 85 万圣节", "南瓜灯", "万圣节", [("party","南瓜灯"),("hat","化装舞会")],
     "学一学：万圣节孩子会讨糖果", "万圣节的标志是——", [("party","南瓜灯"),("moon","月亮"),("flag","国旗")], 0, "10 月 31 日"),
    ("geo-85", "第 86 感恩节", "火鸡大餐", "感恩节", [("cake","节日大餐"),("party","家人团聚")],
     "学一学：感恩节家人团聚吃火鸡", "感恩节流行于——", [(None,"美国和加拿大"),(None,"中国"),(None,"日本")], 0, "11 月第四个星期四"),
    # 地图技能与常识（10）
    ("geo-86", "第 87 认方向", "东南西北", "方向", [("flag","指南针"),("sun","早晨太阳在东")],
     "学一学：早晨太阳在东边", "太阳升起的方向是——", [(None,"东方"),(None,"西方"),(None,"北方")], 0, "面对太阳前东后西"),
    ("geo-87", "第 88 指南针", "中国四大发明", "指南针", [("flag","指南针"),("rock","司南")],
     "学一学：指南针是中国四大发明之一", "指南针的指针指向——", [(None,"南北"),(None,"东西"),(None,"上下")], 0, "四大发明还有造纸印刷火药"),
    ("geo-88", "第 89 七大洲", "七个大洲", "七大洲", [("world-map","世界地图"),("earth","地球")],
     "学一学：亚洲最大，大洋洲最小", "最大的洲是——", [(None,"亚洲"),(None,"欧洲"),(None,"南极洲")], 0, "我们就住在亚洲"),
    ("geo-89", "第 90 四大洋", "四个大洋", "四大洋", [("wave","太平洋"),("wave","大西洋")],
     "学一学：太平洋最大，北冰洋最小", "最小的洋是——", [(None,"北冰洋"),(None,"太平洋"),(None,"印度洋")], 0, "都在南极洲周围"),
    ("geo-90", "第 91 地球仪", "会转的地球", "地球仪", [("earth","地球仪"),("circle","圆圆的")],
     "学一学：地球仪是地球的模型", "地球仪上蓝色代表——", [(None,"海洋"),(None,"陆地"),(None,"云朵")], 0, "地球大部分是海"),
    ("geo-91", "第 92 国旗", "每个国家有国旗", "国旗", [("flag","五星红旗"),("flag","各国国旗")],
     "学一学：每个国家都有自己的国旗", "中国的国旗是——", [(None,"五星红旗"),(None,"枫叶旗"),(None,"米字旗")], 0, "升国旗要敬礼"),
    ("geo-92", "第 93 人种与语言", "说不同的话", "语言", [("speaker","各种语言"),("world-map","世界语言")],
     "学一学：世界上有几千种语言", "世界上说人数最多的母语是——", [(None,"汉语"),(None,"英语"),(None,"法语")], 0, "我们说普通话"),
    ("geo-93", "第 94 保护地球", "爱护环境", "环保", [("sprout","种树"),("earth","爱护地球")],
     "学一学：垃圾分类保护地球", "保护地球可以——", [(None,"垃圾分类、节约用水"),(None,"多扔垃圾"),(None,"浪费水")], 0, "地球是我们共同的家"),
    ("geo-94", "第 95 环球旅行家", "带地图出发", "环球旅行", [("world-map","世界地图"),("rocket","出发")],
     "学一学：看地图能找到想去的地方", "去陌生地方旅行要带上——", [(None,"地图"),(None,"玩具"),(None,"零食")], 0, "小小环球旅行家"),
    ("geo-95", "第 96 时差", "地球那边天黑了", "时差", [("earth","地球自转"),("moon","夜晚")],
     "学一学：地球自转，各地白天黑夜不同时", "我们白天时，地球另一边可能——", [(None,"正是黑夜"),(None,"也是白天"),(None,"没有时间")], 0, "地球转呀转，昼夜轮流来"),
]

for g in GEO2:
    geo_levels.append(geo_new(*g))

finish_levels(geo_levels, "geo", 100)
apply_anims(geo_levels, {
    "geo-2": "river",       # 长江黄河：江河奔流
    "geo-3": "wall",        # 万里长城：城墙绵延
    "geo-4": "mountain",    # 珠峰：雪峰云影
    "geo-5": "panda",       # 熊猫故乡：熊猫抱竹
    "geo-6": "drift",       # 七大洲：大陆漂移拼合
    "geo-9": "windmill",    # 欧洲：风车转动
})
assign_letter_anims(geo_levels, "geo", "pin")   # v0.12.1：国家城市/大洲/自然奇观补位
append_extras(geo_levels, [
    ("geo-1", shadow_step("geo-x1", "看影子猜猜：这是北京哪里？", "tiananmen",
                          [("tiananmen","天安门"),("castle","城堡"),("school","学校")], 0,
                          "北京是中国的首都，它就在天安门")),
    ("geo-3", match_step("geo-x2", "连一连：地标和国家",
                         [("greatwall","万里长城","中国"),("libertystatue","自由女神","美国"),("kangaroo","袋鼠","澳大利亚")])),
    ("geo-4", tapall_step("geo-x3", "点点看：把中国的地标和动物都点亮",
                          [("greatwall",None,True),("tiananmen",None,True),("panda",None,True),
                           ("libertystatue",None,False),("windmill",None,False),("penguin",None,False)],
                          "长城、天安门、大熊猫都在中国")),
    ("geo-9", spotlight_step("geo-x4", "望远镜找一找：欧洲的风车在哪里？",
                             "windmill", ["lion","elephant","penguin"])),
])
W("geo_levels.json", {"subject": "geo", "title": "环球号", "guide": "panda",
                     "zones": zones_meta(["中国风貌", "中国各地", "世界国家", "首都名城", "自然纪录",
                                          "恐龙与化石", "节日文化", "地图技能", "世界常识", "环球大挑战"],
                                         (["china-map", "greatwall", "world-map", "castle", "wave",
                                           "dino", "party", "flag", "earth", "medal"],
                                          ["地图 · 北京 · 长城珠峰", "上海杭州成都甘肃", "日泰埃法英俄", "六国首都巡礼",
                                           "海沟 · 湖泊 · 岛屿", "恐龙化石陨石彗星", "春节中秋圣诞", "方向 · 指南针 · 地球仪", "大洲大洋 · 语言环保", "总复习"])),
                     "levels": geo_levels})

# ================= 收集册 8 组 =================
def C(id, name, icon=None, text=None, pinyin=None, fact=None, tag=None, tagColor=None):
    d = {"id": id, "name": name}
    if icon: d["icon"] = icon
    if text: d["text"] = text
    if pinyin: d["pinyin"] = pinyin
    if fact: d["fact"] = fact
    if tag: d["tag"] = tag
    if tagColor: d["tagColor"] = tagColor
    return d

# 汉字卡 30（与 CN 字表一致）
HZ_ITEMS = []
for ch, py, *_ in CN:
    HZ_ITEMS.append(C(f"hz-{ch}", ch, text=ch, pinyin=py))

# 单词卡（字母 12 + 主题词表约 97）。v0.12.2：改为「先手写、再按主题补、最后统一去重」。
# 此前手写 12 张与 EN_TOPICS 撞车 + 主题词表内部同一个单词出现在多关，
# 一共产出 28 个重复 id（en-gift ×4）；收集册按 id 判点亮，重复 id = 点亮一张解锁多张。
_EN_CARD_SEED = [
    C("en-apple","Apple","apple"), C("en-banana","Banana","banana"), C("en-cake","Cake","cake"),
    C("en-duck","Duck","duck"), C("en-sun","Sun","sun"), C("en-moon","Moon","moon"),
    C("en-flower","Flower","flower"), C("en-leaf","Leaf","leaf"), C("en-key","Key","key"),
    C("en-heart","Heart","heart"), C("en-rainbow","Rainbow","rainbow"), C("en-gift","Gift","gift"),
]
EN_CARDS = list(_EN_CARD_SEED)
for lid, title, subtitle, words in EN_TOPICS:
    for ic, en, cn in words:
        EN_CARDS.append(C(f"en-{en.lower()}", f"{en} {cn}", ic))
EN_CARDS.append(C("en-run","Run 跑","girl")); EN_CARDS.append(C("en-jump","Jump 跳","rabbit"))
EN_CARDS.append(C("en-swim","Swim 游","wave")); EN_CARDS.append(C("en-fly","Fly 飞","duck"))
# 去重：同 id 只保留首次出现（手写卡优先，主题词表按关卡顺序）。同 id 必然同词，只影响数量不影响内容。
_seen_en = set()
EN_CARDS = [c for c in EN_CARDS if not (c["id"] in _seen_en or _seen_en.add(c["id"]))]

# 星空卡 25（v0.10：16 + 9 新；卡名首词 = letter 关 display，闯到即点亮）
ASTRO_CARDS = [
    C("as-sun","太阳 Sun","sun"), C("as-moon","月亮 Moon","moon"), C("as-star","星星 Star","star"),
    C("as-earth","地球 Earth","earth"), C("as-rocket","火箭 Rocket","rocket"), C("as-planet","行星 Planet","planet"),
    C("as-comet","彗星 Comet","comet"), C("as-meteor","流星 Meteor","sparkle"), C("as-rover","火星车 Rover","robot"),
    C("as-sky","星晶夜空","crystal"),
    C("as-mercury","水星 Mercury","mercury"), C("as-venus","金星 Venus","venus"),
    C("as-mars","火星 Mars","mars"), C("as-jupiter","木星 Jupiter","jupiter"),
    C("as-saturn","土星 Saturn","saturn"), C("as-milkyway","银河系 Milky Way","milkyway"),
    C("as-uranus","天王星 Uranus","uranus"), C("as-neptune","海王星 Neptune","neptune"),
    C("as-satellite","卫星 Satellite","satellite"), C("as-telescope","望远镜 Telescope","telescope"),
    C("as-blackhole","黑洞 Black Hole","blackhole"), C("as-bigdipper","北斗七星 Big Dipper","bigdipper"),
    C("as-meteorite","陨石 Meteorite","meteorite"), C("as-ufo","外星人 UFO","ufo"),
    C("as-universe","宇宙 Universe","milkyway"),
]

# 地理卡组（新建，约 16 张）
GEO_CARDS = [
    C("ge-china","中国地图","china-map",fact="中国地图像一只大雄鸡。"),
    C("ge-tiananmen","天安门","tiananmen",fact="天安门在北京，北京是中国的首都。"),
    C("ge-river","长江黄河","river",fact="长江和黄河是中国的母亲河。"),
    C("ge-greatwall","万里长城","greatwall",fact="长城像一条长龙卧在山上。"),
    C("ge-everest","珠穆朗玛峰","everest",fact="世界第一高峰，山顶盖着白雪。"),
    C("ge-panda","大熊猫","panda",fact="中国的国宝，最爱吃竹子。"),
    C("ge-world","世界地图","world-map",fact="地球上有七大洲四大洋。"),
    C("ge-asia","亚洲","earth",fact="我们住在亚洲，它是最大的大洲。"),
    C("ge-lion","狮子","lion",fact="非洲草原上的万兽之王。"),
    C("ge-elephant","大象","elephant",fact="非洲象有长长的鼻子和大耳朵。"),
    C("ge-windmill","风车","windmill",fact="欧洲田野上慢慢转动的大风车。"),
    C("ge-liberty","自由女神","libertystatue",fact="举着火炬，站在美国纽约港。"),
    C("ge-kangaroo","袋鼠","kangaroo",fact="肚子上有口袋，是大洋洲的动物。"),
    C("ge-penguin","企鹅","penguin",fact="住在南极，像穿黑燕尾服的小绅士。"),
    C("ge-polarbear","北极熊","polarbear",fact="住在北极，厚厚的白毛不怕冷。"),
]

collection = {"groups": [
    {"id": "science", "title": "科学图鉴", "icon": "flask", "lockedLabel": "？？？", "items": [
        C("sci-apple","苹果","apple",tag="浮",tagColor="blue",fact="苹果能浮起来，是因为果肉里藏着小气孔，像穿了救生衣！"),
        C("sci-rock","石头","rock",tag="沉",tagColor="coral",fact="石头比同体积的水重很多，所以一放就沉底啦。"),
        C("sci-wood","木头","wood",tag="浮",tagColor="blue",fact="木头里有很多小空隙，轻轻的，所以能浮在水面上。"),
        C("sci-key","钥匙","key",tag="沉",tagColor="coral",fact="金属钥匙个头小却很重，扑通一下就沉下去了。"),
        C("sci-sponge","海绵","sponge",tag="浮",tagColor="blue",fact="干海绵会浮，吸满水之后会慢慢往下沉，试试看！"),
        C("sci-balloon","气球","balloon",tag="浮",tagColor="blue",fact="气球里装的是空气，最轻最轻，漂在最上面。"),
        C("sci-ice","冰块","ice",tag="浮",tagColor="blue",fact="冰比水轻一点点，所以冰块会浮在饮料上。"),
        C("sci-magnet","磁铁","magnet",fact="磁铁能吸住铁做的东西，比如回形针和钥匙。"),
        C("sci-rainbow","彩虹","rainbow",fact="阳光穿过小水滴，会折出七种颜色。"),
        C("sci-volcano","火山","volcano",fact="岩浆压力太大时，就会从火山口喷出来。"),
        C("sci-sprout","种子","sprout",fact="种子喝饱水、晒到太阳，就会发芽长大。"),
        C("sci-heart","心跳","heart",fact="你的心脏一直在跳，跑完步会跳得更快哦。"),
    ]},
    {"id": "sticker", "title": "贴纸", "icon": "sparkle", "lockedLabel": "？？？", "items": [
        C("st-fuchen","浮沉小侦探","medal"), C("st-shizi","识字新星","book"), C("st-shuyazi","数数小鸭","duck"),
        C("st-party","闯关欢呼","party"), C("st-flower","春日限定","flower"), C("st-rocket","未来科学家","rocket"),
        C("st-bulb","金点子","bulb"), C("st-crystal","闪亮宝石","crystal"), C("st-star","大星星","starface"),
        C("st-sun","小太阳","sunface"), C("st-heart","爱心","heart"), C("st-gift","神秘礼物","gift"),
    ]},
    {"id": "hanzi", "title": "汉字卡", "icon": "hanzi", "lockedLabel": "？？？", "items": HZ_ITEMS},
    {"id": "pinyin", "title": "拼音卡", "icon": "speaker", "lockedLabel": "？？？", "items": [
        C("py-b","b 爸",text="b"), C("py-p","p 坡",text="p"), C("py-m","m 妈",text="m"), C("py-f","f 发",text="f"),
        C("py-d","d 大",text="d"), C("py-t","t 他",text="t"), C("py-n","n 拿",text="n"), C("py-l","l 拉",text="l"),
        C("py-g","g 哥",text="g"), C("py-k","k 开",text="k"),
        C("py-a","a 啊",text="a"), C("py-zhi","zhi 蜘",text="zhi"),
        C("py-tone1","一声 ā",text="ā"), C("py-tone2","二声 á",text="á"),
        C("py-tone3","三声 ǎ",text="ǎ"), C("py-tone4","四声 à",text="à"),
        C("py-ai","ai 阿姨",text="ai"), C("py-ei","ei 诶",text="ei"), C("py-ui","ui 围巾",text="ui"),
        C("py-an","an 天安门",text="an"), C("py-en","en 人",text="en"), C("py-in","in 音",text="in"),
    ]},
    {"id": "english", "title": "单词卡", "icon": "book", "lockedLabel": "？？？", "items": EN_CARDS},
    {"id": "astro", "title": "星空卡", "icon": "starface", "lockedLabel": "？？？", "items": ASTRO_CARDS},
    {"id": "geo", "title": "地理卡", "icon": "earth", "lockedLabel": "？？？", "items": GEO_CARDS},
    {"id": "badge", "title": "徽章", "icon": "medal", "lockedLabel": "？？？", "items": [
        C("bg-start","初来乍到","home"), C("bg-hanzi10","识字新星","book"), C("bg-math5","思维小达人","equal"),
        C("bg-lab1","实验狂人","flask"), C("bg-py1","拼音小能手","speaker"), C("bg-en1","ABC达人","book"),
        C("bg-astro1","摘星少年","rocket"), C("bg-listen7","磨耳朵七天","speaker"), C("bg-all","全勤之星","star"),
        C("bg-shield","护眼小卫士","shield"), C("bg-chart","进步王","chart"), C("bg-rocket","冲鸭！","rocket"), C("bg-king","全科通","medal"),
        C("bg-writer","小小书法家","hanzi",fact="写完 10 个汉字获得"),
        C("bg-mul","乘法小达人","equal",fact="学会乘法口诀获得"),
        C("bg-sudoku","数独侦探","block",fact="推理完成数独获得"),
        C("bg-geo","环球旅行家","earth",fact="通关环球号获得"),
        C("bg-words50","单词大富豪","book",fact="收集约 50 个单词获得"),
    ]},
]}
W("collection.json", collection)

# ================= 金币商店（不变） =================
def shop_item(id, name, icon, price, default=False):
    d = {"id": id, "name": name, "icon": icon, "price": price}
    if default: d["default"] = True
    return d

shop = {
    "characters": [
        shop_item("mario", "红帽小勇士", "mario", 0, True),
        shop_item("dino", "绿恐龙", "dino", 0, True),
        shop_item("cat", "橘小猫", "cat", 40),
        shop_item("rabbit", "小白兔", "rabbit", 60),
        shop_item("bear", "棕小熊", "bear", 80),
        shop_item("penguin", "小企鹅", "penguin", 120),
    ],
    "dice": [
        shop_item("std", "经典红点", "circle", 0, True),
        shop_item("fruit", "水果骰", "apple", 50),
        shop_item("star", "星星骰", "starface", 70),
        shop_item("paw", "脚印骰", "paw", 90),
        shop_item("heart", "爱心骰", "heart", 100),
    ],
}
W("shop.json", shop)
print("ALL DONE")
