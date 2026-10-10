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

# ================= 识字村 30 字（teach + 5 题 + write 写字关） =================
# (字, 拼音, 象形源图标 morphFrom, 词卡[(icon,text)], 找一找(target,d1,d2), 找一找答案位)
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
            "board": build_board([q["id"] for q in qs], ["coin", "coin"] + REVIEW_EVENTS[k], k),
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
add_review_levels(cn_levels, "cn", (5, 11))
add_boss_level(cn_levels, "cn")
W("cn_levels.json", {"subject": "cn", "title": "识字村", "guide": "panda", "levels": cn_levels})

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
            "question": "想一想：藏起来的数字是几？",
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

add_review_levels(math_levels, "math", (5, 11))
add_boss_level(math_levels, "math")
W("math_levels.json", {"subject": "math", "title": "思维镇", "guide": "fox", "levels": math_levels})

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

add_review_levels(pinyin_levels, "pinyin", (5, 11))
add_boss_level(pinyin_levels, "pinyin")
W("pinyin_levels.json", {"subject": "pinyin", "title": "拼音谷", "guide": "panda", "levels": pinyin_levels})

# ================= 英语 24 关 =================
EN_LETTERS = [
    ("Aa", "apple", "Apple 苹果"), ("Bb", "banana", "Banana 香蕉"),
    ("Cc", "cake", "Cake 蛋糕"), ("Dd", "duck", "Duck 小鸭"),
    ("Ss", "sun", "Sun 太阳"), ("Mm", "moon", "Moon 月亮"),
    ("Ff", "flower", "Flower 花"), ("Ll", "leaf", "Leaf 叶子"),
    ("Kk", "key", "Key 钥匙"), ("Hh", "heart", "Heart 爱心"),
    ("Rr", "rainbow", "Rainbow 彩虹"), ("Gg", "gift", "Gift 礼物"),
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
for li, idx in [(8, 10), (9, 11)]:
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
    ("en-14","Level 15 Numbers","数字",[("starface","One","一"),("star","Two","二"),("moon","Three","三"),("sun","Four","四")]),
    ("en-15","Level 16 Fruits","水果",[("apple","Apple","苹果"),("banana","Banana","香蕉"),("heart","Peach","桃"),("candy","Grape","葡萄")]),
    ("en-16","Level 17 Family","家庭",[("girl","Mom","妈妈"),("fox","Dad","爸爸"),("paw","Baby","宝宝"),("home","Home","家")]),
    ("en-17","Level 18 Body","身体",[("starface","Eye","眼睛"),("paw","Hand","手"),("crystal","Nose","鼻子"),("speaker","Mouth","嘴")]),
    ("en-18","Level 19 Stationery","文具",[("book","Book","书"),("gift","Bag","书包"),("key","Pen","笔"),("school","School","学校")]),
    ("en-19","Level 20 Food","食物",[("cake","Cake","蛋糕"),("candy","Candy","糖"),("bread","Bread","面包"),("milk","Milk","牛奶")]),
    ("en-20","Level 21 Clothes","衣物",[("hanger","Shirt","衬衫"),("shoe","Shoe","鞋"),("hat","Hat","帽子"),("bear","Coat","外套")]),
    ("en-21","Level 22 Transport","交通",[("train","Train","火车"),("rocket","Rocket","火箭"),("wave","Boat","船"),("balloon","Plane","飞机")]),
    ("en-22","Level 23 Actions","动作",[("girl","Run","跑"),("rabbit","Jump","跳"),("fish","Swim","游"),("bird","Fly","飞")]),
]
EN_REVIEW_WORDS = [("cat","Cat","猫"),("apple","Apple","苹果"),("train","Train","火车"),("girl","Run","跑")]

def en_topic_level(lid, title, subtitle, words):
    li = int(lid.split("-")[1])
    examples = [{"icon": ic, "text": f"{en} {cn}", "say": en} for ic, en, cn in words]
    steps = [{"id": f"{lid}-t", "kind": "letter", "letters": [words[0][1][0]], "display": words[0][1],
              "examples": examples, "question": f"Learn: {subtitle} 主题单词"}]
    # 听选图：第 1 个词（options 元素为 (text, icon)）
    ic0, en0, cn0 = words[0]
    others = [w for w in words if w[0] != ic0]
    d1, d2 = others[0], others[1]
    opts, ans = rot([(en0, ic0), (d1[1], d1[0]), (d2[1], d2[0])], 0, li % 3)
    steps.append({"id": f"{lid}-q1", "kind": "quiz",
                  "question": f"Which one is {en0}? {cn0} 是哪一个？",
                  "options": [{"icon": ic, "text": tx} for tx, ic in opts], "answer": ans,
                  "hint": en0, "praise": f"Yes! It's {en0}!"})
    # 翻牌复习
    pairs = [(w[1], w[0], None, None, w[1]) for w in words[:3]]
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

add_review_levels(english_levels, "english", (5, 11))
add_boss_level(english_levels, "english")
W("english_levels.json", {"subject": "english", "title": "英语王国", "guide": "robot", "levels": english_levels})

# ================= 天文台 16 关 =================
ASTRO_FULL = [
    ("太阳","Sun","sun",[("sun","太阳 Sun"),("sunrise","日出 Sunrise")],"太阳会发光发热，白天照亮大地","moon","star","白天照亮大地、发光发热的是谁？"),
    ("月亮","Moon","moon",[("moon","月亮 Moon"),("starface","星夜 Night")],"月亮晚上出来，有时圆圆、有时弯弯","sun","crystal","晚上有时圆有时弯的是谁？"),
    ("星星","Star","star",[("star","星星 Star"),("starface","小星星 Shine")],"星星在夜空里一闪一闪","balloon","moon","夜空里一闪一闪的是谁？"),
    ("地球","Earth","earth",[("earth","地球 Earth"),("rocket","坐火箭 Fly")],"地球是我们的家，蓝蓝的、圆圆的","sun","moon","蓝蓝圆圆、我们的家是哪个星球？"),
    ("火箭","Rocket","rocket",[("rocket","火箭 Rocket"),("flame","点火 Go")],"火箭轰隆一声，飞向太空","train","balloon","轰隆一声飞向太空的是谁？"),
    ("行星","Planet","planet",[("planet","行星 Planet"),("crystal","光环 Ring")],"有的行星戴着光环，像大草帽","earth","star","戴着光环像大草帽的是谁？"),
    ("彗星","Comet","comet",[("comet","彗星 Comet"),("sparkle","亮尾巴 Tail")],"彗星拖着长长的大尾巴，扫过夜空","rocket","star","拖着长长尾巴扫过夜空的是谁？"),
    ("流星","Meteor","sparkle",[("sparkle","流星 Meteor"),("star","许个愿 Wish")],"流星噌——地划过夜空，可以许个愿","star","comet","噌地划过夜空、可以许愿的是谁？"),
    ("火星车","Rover","robot",[("robot","火星车 Rover"),("volcano","红色火星 Mars")],"机器人火星车，在火星上慢慢探险","rocket","earth","在火星上慢慢探险的机器人是谁？"),
]
ASTRO_PATTERNS = {
    2: (["moon","star","moon"], ["star","sun","comet"], 0),
    5: (["earth","star","earth"], ["rocket","star","earth"], 1),
    8: (["rocket","comet","rocket"], ["earth","comet","rocket"], 1),
}
astro_levels = []
for i, (name, en, icon, chips, fact, d1, d2, feat_q) in enumerate(ASTRO_FULL):
    steps = [{"id": f"astro-{i}-t", "kind": "letter", "letters": [en], "display": name,
              "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} for ic, t in chips],
              "question": f"学一学：{name} {en}"}]
    combo = i % 3
    if combo == 0:
        quiz_opts = [{"icon": d1}, {"icon": d2}]
        ans = (i + 1) % 3
        quiz_opts.insert(ans, {"icon": icon, "text": name})
        steps.append({"id": f"astro-{i}-q", "kind": "quiz",
                      "question": f"找一找：哪个是{name}？",
                      "options": quiz_opts, "answer": ans,
                      "hint": fact, "praise": f"对啦！{fact}"})
    elif combo == 1:
        quiz_opts = [{"icon": d1}, {"icon": d2}]
        ans = (i + 2) % 3
        quiz_opts.insert(ans, {"icon": icon, "text": name})
        steps.append({"id": f"astro-{i}-f", "kind": "quiz",
                      "question": feat_q,
                      "options": quiz_opts, "answer": ans,
                      "hint": fact, "praise": f"对啦！{fact}"})
    else:
        seq, opts, ans = ASTRO_PATTERNS.get(i, (["sun","moon","sun"], ["moon","sun","star"], 0))
        steps.append({"id": f"astro-{i}-p", "kind": "pattern", "seq": seq,
                      "question": "星空规律：下一个是谁？",
                      "options": [{"icon": o} for o in opts], "answer": ans,
                      "hint": "读一读前面几个，谁在轮流出现",
                      "praise": "规律找对啦，小天文学家！"})
    astro_levels.append({"id": f"astro-{i}", "title": f"第 {i+1} 关 {en}", "subtitle": name, "steps": steps})
astro_levels.append({"id": "astro-9", "title": "第 10 关 星空大挑战", "subtitle": "复习", "steps": [
    memory_step("astro-9-m", "翻翻牌：星空朋友和名字配成对", [
        ("sun", "sun", None, None, "太阳"),
        ("earth", "earth", None, None, "地球"),
        ("rocket", "rocket", None, None, "火箭"),
    ]),
    {"id": "astro-9-q1", "kind": "quiz", "question": "我们的家是哪个星球？",
     "options": [{"icon": "sun"}, {"icon": "earth", "text": "地球"}, {"icon": "moon"}], "answer": 1,
     "hint": "蓝蓝的、圆圆的", "praise": "地球是我们的家！"},
    {"id": "astro-9-q2", "kind": "quiz", "question": "谁拖着长长的尾巴扫过夜空？",
     "options": [{"icon": "moon"}, {"icon": "rocket"}, {"icon": "comet", "text": "彗星"}], "answer": 2,
     "hint": "像一把大扫帚", "praise": "彗星答对啦！"},
    {"id": "astro-9-q3", "kind": "pattern", "seq": ["sun","moon","sun"],
     "question": "星空规律：下一个是谁？",
     "options": [{"icon": "star"}, {"icon": "moon"}, {"icon": "rocket"}], "answer": 1,
     "hint": "谁和太阳在轮流出现？", "praise": "全部通关，小天文学家！"},
]})

# —— v0.9 新增 6 关：八大行星 / 排排队 / 月相 / 银河系 / 宇航员 ——
astro_levels.append({"id": "astro-10", "title": "第 11 关 岩质行星", "subtitle": "水金地火", "steps": [
    {"id": "astro-10-t", "kind": "letter", "letters": ["Mercury"], "display": "岩质四兄弟",
     "examples": [{"icon": "mercury", "text": "水星 Mercury", "say": "水星"},
                  {"icon": "venus", "text": "金星 Venus", "say": "金星"},
                  {"icon": "earth", "text": "地球 Earth", "say": "地球"},
                  {"icon": "mars", "text": "火星 Mars", "say": "火星"}],
     "question": "学一学：离太阳最近的四颗岩质行星"},
    quiz_step("astro-10-q1","哪个行星红红的，像火星？",
              [("venus",None),("mars",None),("mercury",None)],1,"火星是红色的","对，火星红红的！"),
    quiz_step("astro-10-q2","我们住在哪颗行星上？",
              [("earth","地球"),("moon",None),("sun",None)],0,"蓝蓝的家","地球是我们的家！"),
]})
astro_levels.append({"id": "astro-11", "title": "第 12 关 巨行星", "subtitle": "木土天海", "steps": [
    {"id": "astro-11-t", "kind": "letter", "letters": ["Jupiter"], "display": "巨行星四兄弟",
     "examples": [{"icon": "jupiter", "text": "木星 Jupiter", "say": "木星"},
                  {"icon": "saturn", "text": "土星 Saturn", "say": "土星"},
                  {"icon": "uranus", "text": "天王星 Uranus", "say": "天王星"},
                  {"icon": "neptune", "text": "海王星 Neptune", "say": "海王星"}],
     "question": "学一学：巨大的四颗行星，土星戴着光环"},
    quiz_step("astro-11-q1","哪颗行星戴着像草帽的光环？",
              [("jupiter",None),("saturn",None),("mars",None)],1,"像大草帽","土星有美丽的光环！"),
    quiz_step("astro-11-q2","八颗行星里个头最大的是谁？",
              [("jupiter",None),("earth",None),("moon",None)],0,"木星最大","木星是行星老大哥！"),
]})
astro_levels.append({"id": "astro-12", "title": "第 13 关 行星排排队", "subtitle": "远近与大小", "steps": [
    {"id": "astro-12-t", "kind": "letter", "letters": ["Order"], "display": "行星排队",
     "examples": [{"icon": "mercury", "text": "离太阳最近", "say": "水星"},
                  {"icon": "neptune", "text": "离太阳最远", "say": "海王星"}],
     "question": "学一学：八颗行星按离太阳远近排排站"},
    quiz_step("astro-12-q1","离太阳最近的行星是谁？",
              [("mercury",None),("earth",None),("saturn",None)],0,"排队第一名","水星排第一！"),
    quiz_step("astro-12-q2","谁个头最大、是行星老大哥？",
              [("moon",None),("jupiter",None),("mars",None)],1,"大胖子","木星最大！"),
]})
astro_levels.append({"id": "astro-13", "title": "第 14 关 月亮变变变", "subtitle": "月相循环", "steps": [
    {"id": "astro-13-t", "kind": "letter", "letters": ["Moon"], "display": "月相变化",
     "examples": [{"icon": "newmoon", "text": "新月 New Moon", "say": "新月"},
                  {"icon": "fullmoon", "text": "满月 Full Moon", "say": "满月"}],
     "question": "学一学：月亮有时弯弯、有时圆圆，月相在循环"},
    pattern_step("astro-13-p1",["newmoon","fullmoon","newmoon"],["fullmoon","newmoon","star"],0,
                 "月相规律：下一个是新月还是满月？"),
    quiz_step("astro-13-q1","月亮为什么有时圆、有时弯？",
              [(None,"月亮被太阳照亮的部分在变"),(None,"月亮真的变大变小"),(None,"被云挡住了")],0,"月亮本身不发光","月相变化，真神奇！"),
]})
astro_levels.append({"id": "astro-14", "title": "第 15 关 银河系", "subtitle": "我们的星之城", "steps": [
    {"id": "astro-14-t", "kind": "letter", "letters": ["Galaxy"], "display": "银河系",
     "examples": [{"icon": "milkyway", "text": "银河系 Milky Way", "say": "银河"},
                  {"icon": "sun", "text": "太阳是其中一颗星", "say": "太阳"}],
     "question": "学一学：银河系是千千万万颗星星组成的大城市"},
    quiz_step("astro-14-q1","我们的太阳在哪个星系里？",
              [("milkyway",None),("comet",None),("rocket",None)],0,"星星大城市","我们在银河系！"),
]})
astro_levels.append({"id": "astro-15", "title": "第 16 关 宇航员", "subtitle": "太空生活", "steps": [
    {"id": "astro-15-t", "kind": "letter", "letters": ["Astronaut"], "display": "宇航员",
     "examples": [{"icon": "astronaut", "text": "宇航员 Astronaut", "say": "宇航员"},
                  {"icon": "station", "text": "空间站 Station", "say": "空间站"},
                  {"icon": "blackhole", "text": "黑洞 Black Hole", "say": "黑洞"}],
     "question": "学一学：宇航员穿宇航服，在空间站里生活和做实验"},
    quiz_step("astro-15-q1","宇航员在太空中住的大房子叫什么？",
              [("station",None),("castle",None),("shop",None)],0,"太空之家","空间站答对啦！"),
    quiz_step("astro-15-q2","连光都逃不出来、超级重的洞叫什么？",
              [("comet",None),("blackhole",None),("volcano",None)],1,"神秘黑洞","黑洞真神秘！"),
]})

add_review_levels(astro_levels, "astro", (5, 10))
add_boss_level(astro_levels, "astro")
W("astro_levels.json", {"subject": "astro", "title": "天文台", "guide": "robot", "levels": astro_levels})

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

add_review_levels(geo_levels, "geo", (5, 11))
add_boss_level(geo_levels, "geo")
W("geo_levels.json", {"subject": "geo", "title": "环球号", "guide": "panda", "levels": geo_levels})

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

# 单词卡（字母 12 + 主题约 48）
EN_CARDS = [
    C("en-apple","Apple","apple"), C("en-banana","Banana","banana"), C("en-cake","Cake","cake"),
    C("en-duck","Duck","duck"), C("en-sun","Sun","sun"), C("en-moon","Moon","moon"),
    C("en-flower","Flower","flower"), C("en-leaf","Leaf","leaf"), C("en-key","Key","key"),
    C("en-heart","Heart","heart"), C("en-rainbow","Rainbow","rainbow"), C("en-gift","Gift","gift"),
]
for lid, title, subtitle, words in EN_TOPICS:
    for ic, en, cn in words:
        EN_CARDS.append(C(f"en-{en.lower()}", f"{en} {cn}", ic))
EN_CARDS.append(C("en-run","Run 跑","girl")); EN_CARDS.append(C("en-jump","Jump 跳","rabbit"))
EN_CARDS.append(C("en-swim","Swim 游","wave")); EN_CARDS.append(C("en-fly","Fly 飞","duck"))

# 星空卡 16（原 10 + 6 新）
ASTRO_CARDS = [
    C("as-sun","太阳 Sun","sun"), C("as-moon","月亮 Moon","moon"), C("as-star","星星 Star","star"),
    C("as-earth","地球 Earth","earth"), C("as-rocket","火箭 Rocket","rocket"), C("as-planet","行星 Planet","planet"),
    C("as-comet","彗星 Comet","comet"), C("as-meteor","流星 Meteor","sparkle"), C("as-rover","火星车 Rover","robot"),
    C("as-sky","星晶夜空","crystal"),
    C("as-mercury","水星 Mercury","mercury"), C("as-venus","金星 Venus","venus"),
    C("as-mars","火星 Mars","mars"), C("as-jupiter","木星 Jupiter","jupiter"),
    C("as-saturn","土星 Saturn","saturn"), C("as-milkyway","银河系 Milky Way","milkyway"),
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
        shop_item("std", "经典红点", "dot", 0, True),
        shop_item("fruit", "水果骰", "apple", 50),
        shop_item("star", "星星骰", "starface", 70),
        shop_item("paw", "脚印骰", "paw", 90),
        shop_item("heart", "爱心骰", "heart", 100),
    ],
}
W("shop.json", shop)
print("ALL DONE")
