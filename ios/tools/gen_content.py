#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成五学科关卡内容 + 收集册 JSON（v0.3：情境数学 / 视觉化找一找 / 天文镇 / 找规律）

v0.3 设计要点（飞机模式友好）：
  · 所有「听一听」改为「找一找」视觉匹配 —— 题目直接展示目标字/字母大卡，
    朗读永远可选（speakText 保留，但不做题的必要条件）
  · 思维镇每关一个情境（池塘/糖果店/果园/气球/夜空/火车/花园/宝箱…），
    点数/比多少/加减法全部换成情境道具，并新增「找规律」题型
  · 新增天文镇 astro（10 关）：太阳/月亮/星星/地球/火箭/行星/彗星/流星/火星车/复习
"""
import json, os

RES = os.path.join(os.path.dirname(__file__), "..", "AdventureIsland", "Resources")
os.makedirs(RES, exist_ok=True)

def W(name, obj):
    with open(os.path.join(RES, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    print(name, "OK")

# ================= 语文 15 关（teach + 找一找视觉匹配 + 练一练认字） =================
# (字, 拼音, 象形源图标, 词卡, 找一找目标图标, 找一找干扰图标×2, 答案位)
CN = [
    ("日","rì","sunface",[("sunrise","日出"),("cake","生日"),("calendar","日子")],("sunrise","moon","cake"),0),
    ("月","yuè","moon",[("moon","月亮"),("starface","星星"),("cake","月饼")],("moon","sun","star"),2),
    ("水","shuǐ","wave",[("wave","海浪"),("crystal","泉水"),("leaf","露珠")],("wave","sun","crystal"),0),
    ("山","shān","volcano",[("school","上山"),("leaf","山林")],("volcano","rocket","home"),1),
    ("木","mù","sprout",[("leaf","树叶"),("flower","花木")],("sprout","flower","rock"),0),
    ("人","rén","girl",[("heart","大人"),("party","人们")],("girl","duck","sun"),2),
    ("口","kǒu","speaker",[("speaker","开口"),("heart","口水")],("speaker","clock","moon"),0),
    ("天","tiān","sunrays",[("sun","天空"),("sunrise","今天")],("sun","banana","rocket"),1),
    ("田","tián","calendar",[("sprout","田里"),("flower","水田")],("calendar","gift","star"),2),
    ("石","shí","rock",[("rock","石头"),("castle","石桥")],("rock","balloon","leaf"),0),
    ("火","huǒ","flame",[("flame","火焰"),("volcano","火山"),("starface","火花")],("flame","crystal","key"),0),
    ("花","huā","flower",[("flower","花朵"),("leaf","花瓣"),("heart","花园")],("flower","star","train"),1),
    ("草","cǎo","leaf",[("leaf","小草"),("sprout","草地")],("leaf","cake","duck"),1),
    ("鸟","niǎo","duck",[("duck","小鸟"),("leaf","鸟窝")],("duck","apple","rocket"),0),
]
cn_levels = []
for i, (ch, py, mfrom, words, (tgt, d1, d2), lans) in enumerate(CN):
    opts = [{"icon": tgt, "text": ch}, {"icon": d1}, {"icon": d2}]
    if lans != 0:
        opts[0], opts[lans] = opts[lans], opts[0]
    steps = [
        {"id": f"cn-{i}-t", "kind": "teach", "morphFrom": mfrom, "char": ch, "pinyin": py,
         "words": [{"icon": w, "text": t, "say": t} for w, t in words]},
        {"id": f"cn-{i}-l", "kind": "listen", "prompt": ch, "speakText": ch,
         "question": f"找一找：哪张图片是「{ch}」？",
         "options": opts, "answer": lans,
         "hint": f"想想刚才的图片：「{ch}」", "praise": f"眼睛真亮！{ch} 找对啦！"},
        {"id": f"cn-{i}-q", "kind": "quiz", "question": f"练一练：哪个字是「{ch}」？",
         "options": [{"text": t} for t in [ch, "木" if ch != "木" else "水", "口" if ch != "口" else "日"]],
         "answer": 0, "hint": "想一想刚才的字", "praise": "记住啦！"},
    ]
    cn_levels.append({"id": f"cn-{i}", "title": f"第 {i+1} 关 象形字", "subtitle": f"认识「{ch}」", "steps": steps})
# 第15关 复习挑战
cn_levels.append({"id": "cn-14", "title": "第 15 关 复习挑战", "subtitle": "汉字小达人", "steps": [
    {"id": "cn-14-l1", "kind": "listen", "prompt": "火", "speakText": "火",
     "question": "找一找：哪张图片是「火」？",
     "options": [{"icon": "crystal"}, {"icon": "flame", "text": "火"}, {"icon": "key"}], "answer": 1,
     "hint": "热热的、红红的", "praise": "真棒！"},
    {"id": "cn-14-l2", "kind": "listen", "prompt": "花", "speakText": "花",
     "question": "找一找：哪张图片是「花」？",
     "options": [{"icon": "star"}, {"icon": "flower", "text": "花"}, {"icon": "duck"}], "answer": 1,
     "hint": "香香的、漂亮的", "praise": "眼睛真亮！"},
    {"id": "cn-14-q", "kind": "quiz", "question": "大挑战：哪个是「鸟」？",
     "options": [{"text": t} for t in ["鸟","乌","鸣"]], "answer": 0, "hint": "有一点点，就是小鸟", "praise": "复习家！全对啦！"},
]})
W("cn_levels.json", {"subject": "cn", "title": "识字村", "guide": "panda", "levels": cn_levels})

# ================= 数学 15 关（情境化 + 找规律） =================
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
    """分一分（数的组成）：total 分两堆，已知 part，求另一堆 = total - part"""
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
    """填一填（相邻数）：a, ?, a+2，问 a+1"""
    correct = a + 1
    options = opts or sorted({correct, correct - 1, correct + 1})
    return {"id": nid, "kind": "neighbor", "nums": [a, 0, a + 2],
            "question": "想一想：藏起来的数字是几？",
            "arithOptions": options, "answer": options.index(correct),
            "hint": f"{a} 的后面是几？{a + 2} 的前面是几？",
            "praise": f"是 {correct}！{a} 和 {a + 2} 的中间是 {correct}！"}

def classify_step(cid, q, items, ans):
    return {"id": cid, "kind": "quiz", "question": q,
            "options": [{"icon": ic} for ic in items], "answer": ans,
            "hint": "想一想它们分别是做什么的",
            "praise": "分类小能手！"}

# 情境表：icon/unit/backdrop/题目
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
    ("math-5","第 6 关 小火车","7 以内 · 排一排", lambda i: [count_step(i,7,[6,7,8],SC_train),
        order_step(f"math-{i}-o2",[3,6,4],"up")]),
    ("math-6","第 7 关 花园蜜蜂","8 以内 · 分一分", lambda i: [count_step(i,8,[7,8,9],SC_flower),
        split_step(f"math-{i}-s2",8,3,"flower","朵","8 朵花分两个花瓶，左边 3 朵，右边几朵？")]),
    ("math-7","第 8 关 爱心礼盒","9 以内 · 排一排", lambda i: [count_step(i,9,[8,9,10],SC_heart),
        order_step(f"math-{i}-o3",[9,4,7],"down")]),
    ("math-8","第 9 关 宝藏金币","10 以内点数", lambda i: [count_step(i,10,[8,9,10],SC_coin),
        pattern_step(f"math-{i}-p1",["star","moon","star"],["moon","star","candy"],0)]),
    ("math-9","第 10 关 数字擂台","比大小 · 归类", lambda i: [
        {"id": f"math-{i}-q1", "kind": "quiz", "question": "哪个数字最大？",
         "options": [{"text": t} for t in ["5","9","3"]], "answer": 1,
         "hint": "从 1 数到 10，谁排在最后？", "praise": "9 最大，答对啦！"},
        {"id": f"math-{i}-q2", "kind": "quiz", "question": "哪个数字最小？",
         "options": [{"text": t} for t in ["2","7","10"]], "answer": 0,
         "hint": "越早数到的越小哦", "praise": "思维小达人！"},
        classify_step(f"math-{i}-q3","火眼金睛：哪个是交通工具？",["duck","train","cake"],1)]),
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
W("math_levels.json", {"subject": "math", "title": "思维镇", "guide": "fox", "levels": math_levels})

# ================= 拼音 12 关（letter + 找一找 + blend） =================
PY = [
    ("b", [("girl","爸爸 bà"),("banana","白菜 bái")], "b", "a", ["ba","bo","bu"], 0),
    ("p", [("volcano","山坡 pō"),("rocket","跑步 pǎo")], "p", "o", ["po","pa","pi"], 0),
    ("m", [("girl","妈妈 mā"),("moon","米粒 mǐ")], "m", "a", ["ma","mo","mu"], 0),
    ("f", [("flame","发烧 fā"),("leaf","飞机 fēi")], "f", "a", ["fa","fo","fu"], 0),
    ("d", [("sun","大地 dì"),("duck","大刀 dāo")], "d", "e", ["de","da","du"], 0),
    ("t", [("train","太阳 tài"),("tree","跳高 tiào")], "t", "a", ["ta","te","tu"], 0),
    ("n", [("girl","拿苹果 ná"),("heart","你好 nǐ")], "n", "i", ["ni","na","nu"], 0),
    ("l", [("leaf","拉手 lā"),("gift","老虎 lǎo")], "l", "a", ["la","le","lu"], 0),
    ("g", [("tree","哥哥 gē"),("moon","故事 gù")], "g", "e", ["ge","ga","gu"], 0),
    ("k", [("heart","开心 kāi"),("book","看书 kàn")], "k", "e", ["ke","ka","ku"], 0),
]
pinyin_levels = []
for i, (letter, examples, b0, b1, blends, bans) in enumerate(PY):
    others = ["d","p","m","f","t","n","l","g","k","b"]
    distractors = [x for x in others if x != letter][:2]
    opts = distractors + [letter]
    ans = opts.index(letter)
    steps = [
        {"id": f"py-{i}-t", "kind": "letter", "letters": [letter], "display": letter,
         "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} for ic, t in examples],
         "question": f"学一学声母 {letter}"},
        {"id": f"py-{i}-l", "kind": "listen", "prompt": letter, "speakText": letter,
         "question": f"找一找：哪个是「{letter}」？",
         "options": [{"text": t} for t in opts], "answer": ans,
         "hint": f"「{examples[0][1].split(' ')[0]}」的开头", "praise": f"「{letter}」找对啦！"},
        {"id": f"py-{i}-b", "kind": "blend", "parts": [b0, b1],
         "question": f"拼一拼：{b0} — {b1} = ?",
         "options": [{"text": t} for t in blends], "answer": bans,
         "hint": f"{b0} 碰上 {b1}", "praise": f"拼对了，{blends[bans]}！"},
    ]
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 声母", "subtitle": f"认识「{letter}」", "steps": steps})
# 韵母关
pinyin_levels.append({"id": "py-10", "title": "第 11 关 韵母", "subtitle": "a o e i u ü", "steps": [
    {"id": "py-10-t", "kind": "letter", "letters": ["a","o","e","i","u","ü"], "display": "a",
     "examples": [{"icon": "duck", "text": "啊 ā 张大嘴", "say": "ā"}, {"icon": "flame", "text": "哦 ó", "say": "ó"}],
     "question": "学一学韵母 a"},
    {"id": "py-10-l", "kind": "listen", "prompt": "a", "speakText": "a",
     "question": "找一找：哪个是韵母「a」？",
     "options": [{"text": t} for t in ["o","a","e"]], "answer": 1,
     "hint": "张大嘴巴 āāā", "praise": "韵母 a 找对啦！"},
]})
# 复习+整体认读
pinyin_levels.append({"id": "py-11", "title": "第 12 关 复习", "subtitle": "整体认读", "steps": [
    {"id": "py-11-l1", "kind": "listen", "prompt": "zhi", "speakText": "zhi",
     "question": "找一找：哪个是「zhi」？",
     "options": [{"text": t} for t in ["chi","zhi","zi"]], "answer": 1,
     "hint": "蜘蛛 zhī zhī 叫", "praise": "整体认读 zhi！"},
    {"id": "py-11-b", "kind": "blend", "parts": ["b","a"],
     "question": "拼一拼：b — a = ?",
     "options": [{"text": t} for t in ["ba","bo","pa"]], "answer": 0,
     "hint": "爸爸的爸", "praise": "拼读小能手！"},
]})
W("pinyin_levels.json", {"subject": "pinyin", "title": "拼音谷", "guide": "panda", "levels": pinyin_levels})

# ================= 英语 12 关（全部视觉化：字母大卡 + 找一找 + 图词配对） =================
EN_LETTERS = [
    ("Aa", "apple", "Apple 苹果"), ("Bb", "banana", "Banana 香蕉"),
    ("Cc", "cake", "Cake 蛋糕"), ("Dd", "duck", "Duck 小鸭"),
    ("Ss", "sun", "Sun 太阳"), ("Mm", "moon", "Moon 月亮"),
    ("Ff", "flower", "Flower 花"), ("Ll", "leaf", "Leaf 叶子"),
    ("Kk", "key", "Key 钥匙"), ("Hh", "heart", "Heart 爱心"),
    ("Rr", "rainbow", "Rainbow 彩虹"), ("Gg", "gift", "Gift 礼物"),
]
english_levels = []
pair_specs = [0,1,2,3,4,5,6,7]
for li, idx in enumerate(pair_specs):
    disp, icon, word = EN_LETTERS[idx]
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    opts = [others[li % 4], others[(li+1) % 4], disp]
    ans = opts.index(disp)
    d1, d2 = others[(li+2) % 8], others[(li+3) % 8]
    d1i = next(x for x in EN_LETTERS if x[0] == d1)[1]
    d2i = next(x for x in EN_LETTERS if x[0] == d2)[1]
    steps = [
        {"id": f"en-{li}-t", "kind": "letter", "letters": [disp[0]], "display": disp,
         "examples": [{"icon": icon, "text": word, "say": word.split(" ")[0]}],
         "question": f"Learn letter {disp}"},
        {"id": f"en-{li}-l", "kind": "listen", "prompt": disp, "speakText": disp[0],
         "question": f"Find: which one is {disp} ?",
         "options": [{"text": t} for t in opts], "answer": ans,
         "hint": f"{word}", "praise": f"Yes! {disp}!"},
        {"id": f"en-{li}-q", "kind": "quiz", "question": f"Which picture starts with {disp}?",
         "options": [{"icon": d1i}, {"icon": icon}, {"icon": d2i}],
         "answer": 1, "hint": word, "praise": "Great job!"},
    ]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} Letters", "subtitle": disp, "steps": steps})
for li, idx in [(8, 10), (9, 11)]:
    disp, icon, word = EN_LETTERS[idx]
    steps = [
        {"id": f"en-{li}-t", "kind": "letter", "letters": [disp[0]], "display": disp,
         "examples": [{"icon": icon, "text": word, "say": word.split(" ")[0]}],
         "question": f"Learn letter {disp}"},
        {"id": f"en-{li}-q", "kind": "quiz", "question": f"Which one is {word.split(' ')[0]}?",
         "options": [{"icon": "book"}, {"icon": icon}, {"icon": "clock"}], "answer": 1,
         "hint": word, "praise": "Nice!"},
    ]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} Letters", "subtitle": disp, "steps": steps})
# 单词配对 L11 / 复习 L12（全部视觉：题目直接写出单词）
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
    word_quiz("en-11-q1", "Which one is the moon? 月亮是哪一个？", [("moon","moon"),("sun","sun"),("starface","star")], 0, "Moon 月亮", "Yes! Moon!"),
    word_quiz("en-11-q2", "Which one is the flower? 花是哪一个？", [("leaf","leaf"),("flower","flower"),("tree","tree")], 1, "Flower 花", "Yes! Flower!"),
    word_quiz("en-11-q3", "Which one is the cake? 蛋糕是哪一个？", [("gift","gift"),("key","key"),("cake","cake")], 2, "Cake 蛋糕", "Super star! 全部通关!"),
]})
W("english_levels.json", {"subject": "english", "title": "英语王国", "guide": "robot", "levels": english_levels})

# ================= 天文镇 10 关（letter 学一学 + 找一找 quiz） =================
ASTRO = [
    ("太阳","Sun","sun",[("sun","太阳 Sun"),("sunrise","日出 Sunrise")],"太阳会发光发热，白天照亮大地",[("moon",0),("star",2)]),
    ("月亮","Moon","moon",[("moon","月亮 Moon"),("starface","星夜 Night")],"月亮晚上出来，有时圆圆、有时弯弯",[("sun",1),("crystal",2)]),
    ("星星","Star","star",[("star","星星 Star"),("starface","小星星 Shine")],"星星在夜空里一闪一闪",[("moon",2),("balloon",0)]),
    ("地球","Earth","earth",[("earth","地球 Earth"),("rocket","飞呀 Fly")],"地球是我们的家，蓝蓝的、圆圆的",[("sun",2),("moon",1)]),
    ("火箭","Rocket","rocket",[("rocket","火箭 Rocket"),("flame","点火 Go")],"火箭轰隆一声，飞向太空",[("train",2),("balloon",0)]),
    ("行星","Planet","planet",[("planet","行星 Planet"),("crystal","光环 Ring")],"有的行星戴着漂亮的光环，像大草帽",[("earth",1),("star",2)]),
    ("彗星","Comet","comet",[("comet","彗星 Comet"),("sparkle","亮亮 Sparkle")],"彗星拖着长长的大尾巴，扫过夜空",[("rocket",2),("star",0)]),
    ("流星","Meteor","sparkle",[("sparkle","流星 Meteor"),("star","许愿 Wish")],"流星噌——地划过夜空，可以对它许个愿",[("star",1),("comet",2)]),
    ("火星车","Rover","robot",[("robot","火星车 Rover"),("volcano","火星 Mars")],"机器人火星车，在火星上慢慢探险",[("rocket",2),("earth",0)]),
]
astro_levels = []
ASTRO_FULL = [
    ("太阳","Sun","sun",[("sun","太阳 Sun"),("sunrise","日出 Sunrise")],"太阳会发光发热，白天照亮大地",("moon","star")),
    ("月亮","Moon","moon",[("moon","月亮 Moon"),("starface","星夜 Night")],"月亮晚上出来，有时圆圆、有时弯弯",("sun","crystal")),
    ("星星","Star","star",[("star","星星 Star"),("starface","小星星 Shine")],"星星在夜空里一闪一闪",("balloon","moon")),
    ("地球","Earth","earth",[("earth","地球 Earth"),("rocket","坐火箭 Fly")],"地球是我们的家，蓝蓝的、圆圆的",("sun","moon")),
    ("火箭","Rocket","rocket",[("rocket","火箭 Rocket"),("flame","点火 Go")],"火箭轰隆一声，飞向太空",("train","balloon")),
    ("行星","Planet","planet",[("planet","行星 Planet"),("crystal","光环 Ring")],"有的行星戴着光环，像大草帽",("earth","star")),
    ("彗星","Comet","comet",[("comet","彗星 Comet"),("sparkle","亮尾巴 Tail")],"彗星拖着长长的大尾巴，扫过夜空",("rocket","star")),
    ("流星","Meteor","sparkle",[("sparkle","流星 Meteor"),("star","许个愿 Wish")],"流星噌——地划过夜空，可以许个愿",("star","comet")),
    ("火星车","Rover","robot",[("robot","火星车 Rover"),("volcano","红色火星 Mars")],"机器人火星车，在火星上慢慢探险",("rocket","earth")),
]
for i, (name, en, icon, chips, fact, (d1, d2)) in enumerate(ASTRO_FULL):
    quiz_opts = [{"icon": d1}, {"icon": d2}]
    ans = (i * 2 + 1) % 3
    quiz_opts.insert(ans, {"icon": icon, "text": name})
    astro_levels.append({"id": f"astro-{i}", "title": f"第 {i+1} 关 {en}", "subtitle": name, "steps": [
        {"id": f"astro-{i}-t", "kind": "letter", "letters": [en], "display": name,
         "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} for ic, t in chips],
         "question": f"学一学：{name} {en}"},
        {"id": f"astro-{i}-q", "kind": "quiz", "question": f"找一找：哪个是{name}？",
         "options": quiz_opts, "answer": ans,
         "hint": fact, "praise": f"对啦！{fact}"},
    ]})
# 第10关 复习挑战
astro_levels.append({"id": "astro-9", "title": "第 10 关 星空大挑战", "subtitle": "复习", "steps": [
    {"id": "astro-9-q1", "kind": "quiz", "question": "我们的家是哪个星球？",
     "options": [{"icon": "sun"}, {"icon": "earth", "text": "地球"}, {"icon": "moon"}], "answer": 1,
     "hint": "蓝蓝的、圆圆的", "praise": "地球是我们的家！"},
    {"id": "astro-9-q2", "kind": "quiz", "question": "晚上挂在天上的是哪个？",
     "options": [{"icon": "moon", "text": "月亮"}, {"icon": "sun"}, {"icon": "rocket"}], "answer": 0,
     "hint": "有时圆圆、有时弯弯", "praise": "月亮答对啦！"},
    {"id": "astro-9-q3", "kind": "quiz", "question": "谁会轰隆隆飞向太空？",
     "options": [{"icon": "train"}, {"icon": "balloon"}, {"icon": "rocket", "text": "火箭"}], "answer": 2,
     "hint": "倒计时 3、2、1，发射！", "praise": "火箭发射！全部通关！"},
]})
W("astro_levels.json", {"subject": "astro", "title": "天文台", "guide": "robot", "levels": astro_levels})

# ================= 收集册 7 组（新增星空卡） =================
def C(id, name, icon=None, text=None, pinyin=None, fact=None, tag=None, tagColor=None):
    d = {"id": id, "name": name}
    if icon: d["icon"] = icon
    if text: d["text"] = text
    if pinyin: d["pinyin"] = pinyin
    if fact: d["fact"] = fact
    if tag: d["tag"] = tag
    if tagColor: d["tagColor"] = tagColor
    return d

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
    {"id": "hanzi", "title": "汉字卡", "icon": "hanzi", "lockedLabel": "？？？", "items": [
        C("hz-ri","日",text="日",pinyin="rì"), C("hz-yue","月",text="月",pinyin="yuè"), C("hz-shui","水",text="水",pinyin="shuǐ"),
        C("hz-shan","山",text="山",pinyin="shān"), C("hz-mu","木",text="木",pinyin="mù"), C("hz-ren","人",text="人",pinyin="rén"),
        C("hz-kou","口",text="口",pinyin="kǒu"), C("hz-tian","天",text="天",pinyin="tiān"), C("hz-tian2","田",text="田",pinyin="tián"),
        C("hz-shi","石",text="石",pinyin="shí"), C("hz-huo","火",text="火",pinyin="huǒ"), C("hz-hua","花",text="花",pinyin="huā"),
        C("hz-cao","草",text="草",pinyin="cǎo"), C("hz-niao","鸟",text="鸟",pinyin="niǎo"),
    ]},
    {"id": "pinyin", "title": "拼音卡", "icon": "speaker", "lockedLabel": "？？？", "items": [
        C("py-b","b 爸",text="b"), C("py-p","p 坡",text="p"), C("py-m","m 妈",text="m"), C("py-f","f 发",text="f"),
        C("py-d","d 大",text="d"), C("py-t","t 他",text="t"), C("py-n","n 拿",text="n"), C("py-l","l 拉",text="l"),
        C("py-g","g 哥",text="g"), C("py-k","k 开",text="k"),
        C("py-a","a 啊",text="a"), C("py-zhi","zhi 蜘",text="zhi"),
    ]},
    {"id": "english", "title": "单词卡", "icon": "book", "lockedLabel": "？？？", "items": [
        C("en-apple","Apple","apple"), C("en-banana","Banana","banana"), C("en-cake","Cake","cake"),
        C("en-duck","Duck","duck"), C("en-sun","Sun","sun"), C("en-moon","Moon","moon"),
        C("en-flower","Flower","flower"), C("en-leaf","Leaf","leaf"), C("en-key","Key","key"),
        C("en-heart","Heart","heart"), C("en-rainbow","Rainbow","rainbow"), C("en-gift","Gift","gift"),
    ]},
    {"id": "astro", "title": "星空卡", "icon": "starface", "lockedLabel": "？？？", "items": [
        C("as-sun","太阳 Sun","sun"), C("as-moon","月亮 Moon","moon"), C("as-star","星星 Star","star"),
        C("as-earth","地球 Earth","earth"), C("as-rocket","火箭 Rocket","rocket"), C("as-planet","行星 Planet","planet"),
        C("as-comet","彗星 Comet","comet"), C("as-meteor","流星 Meteor","sparkle"), C("as-rover","火星车 Rover","robot"),
        C("as-sky","星晶夜空","crystal"),
    ]},
    {"id": "badge", "title": "徽章", "icon": "medal", "lockedLabel": "？？？", "items": [
        C("bg-start","初来乍到","home"), C("bg-hanzi10","识字新星","book"), C("bg-math5","思维小达人","equal"),
        C("bg-lab1","实验狂人","flask"), C("bg-py1","拼音小能手","speaker"), C("bg-en1","ABC达人","book"),
        C("bg-astro1","摘星少年","rocket"), C("bg-listen7","磨耳朵七天","speaker"), C("bg-all","全勤之星","star"),
        C("bg-shield","护眼小卫士","shield"), C("bg-chart","进步王","chart"), C("bg-rocket","冲鸭！","rocket"), C("bg-king","全科通","medal"),
    ]},
]}
W("collection.json", collection)
print("ALL DONE")
