#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成五学科关卡内容 + 收集册 JSON（v0.5：全模块题型多样化）

v0.5 设计要点（千篇一律 → 每关不同）：
  · 每个学科的关卡按 index 轮换不同「题型组合」，相邻关卡体验不同
  · 识字村：认一认 + [找图片 | 看图找字 | 组词选卡 | 找字] 轮换
  · 拼音谷：学一学 + [找字母 | 看图找声母 | 拼读 | 音节选图] 轮换
  · 英语王国：学一学 + [找字母 | 找图 | 大小写配对 | 图标规律] 轮换
  · 天文台：学一学 + [找一找 | 特征配对 | 星空规律] 轮换
  · 思维镇：8 种题型（v0.4 已完成）
  · listen 新增 promptIcon：题目大卡显示图片（看图找字/找声母），仍纯视觉作答
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
    """掷骰子：掷出 n 点 → 数一数 → 选数字"""
    return {"id": did, "kind": "dice", "count": n, "countOptions": opts,
            "question": "掷骰子：掷出了几点？",
            "hint": "一个一个数红点点", "praise": f"对，是 {n} 点！"}

def memory_step(mid, q, pairs):
    """翻牌配对（扑克牌风）：pairs = [(key, iconA|None, textA|None, iconB|None, textB|None)]
    某一侧也可以直接给 dict（天文台用 {"body":"jupiter"} 画行星圆盘）"""
    cards = []
    for key, ai, at, bi, bt in pairs:
        c1 = {"key": key}
        c2 = {"key": key}
        for c, art, tx in ((c1, ai, at), (c2, bi, bt)):
            if isinstance(art, dict): c.update(art)
            elif art: c["icon"] = art
            if tx: c["text"] = tx
        cards += [c1, c2]
    return {"id": mid, "kind": "memory", "question": q, "cards": cards}

# ================= 语文 15 关（teach + 题型组合轮换） =================
# (字, 拼音, 象形源图标, 词卡, 找一找目标图标, 找一找干扰×2, 找一找答案位)
CN = [
    ("日","rì","sunface",[("sunrise","日出"),("cake","生日"),("calendar","日子")],("sunrise","moon","cake"),0),
    ("月","yuè","moon",[("moon","月亮"),("calendar","一月"),("cake","月饼")],("moon","sun","star"),2),
    ("水","shuǐ","wave",[("wave","海水"),("crystal","泉水"),("apple","水果")],("wave","sun","crystal"),0),
    ("山","shān","volcano",[("volcano","上山"),("tree","山林")],("volcano","rocket","home"),1),
    ("木","mù","tree",[("tree","树木"),("flower","花木")],("tree","flower","rock"),0),
    ("人","rén","girl",[("girl","大人"),("party","人们")],("girl","duck","sun"),2),
    ("口","kǒu","speaker",[("speaker","开口"),("girl","人口")],("speaker","clock","moon"),0),
    ("天","tiān","sunrays",[("sun","天空"),("sunrise","今天")],("sun","banana","rocket"),1),
    ("田","tián","calendar",[("sprout","田里"),("wave","水田")],("calendar","gift","star"),2),
    ("石","shí","rock",[("rock","石头"),("volcano","山石")],("rock","balloon","leaf"),0),
    ("火","huǒ","flame",[("flame","火焰"),("volcano","火山"),("starface","火花")],("flame","crystal","key"),0),
    ("花","huā","flower",[("flower","花朵"),("leaf","花草"),("sprout","花苗")],("flower","star","train"),1),
    ("草","cǎo","leaf",[("leaf","小草"),("sprout","草地")],("leaf","cake","duck"),1),
    ("鸟","niǎo","duck",[("duck","小鸟"),("tree","鸟巢")],("duck","apple","rocket"),0),
]
WORD_POOL = [(ic, tx, ch) for (ch, py, mf, words, lo, la) in CN for (ic, tx) in words]

def other_words(ch, k, start):
    """从全词池里挑不含目标字的干扰词（按 start 轮转，各关不同）"""
    cands = [w for w in WORD_POOL if w[2] != ch]
    out, i = [], start
    while len(out) < k and i < start + len(cands) * 2:
        w = cands[i % len(cands)]
        if all(w[1] != o[1] for o in out):
            out.append(w)
        i += 1
    return out

def cn_listen_pic(i, ch, lo, lans):
    """找图片：目标大卡「字」，选项是图片"""
    tgt, d1, d2 = lo
    opts = [{"icon": tgt, "text": ch}, {"icon": d1}, {"icon": d2}]
    if lans != 0:
        opts[0], opts[lans] = opts[lans], opts[0]
    return {"id": f"cn-{i}-l", "kind": "listen", "prompt": ch, "speakText": ch,
            "question": f"找一找：哪张图片是「{ch}」？",
            "options": opts, "answer": lans,
            "hint": f"想想刚才的图片：「{ch}」", "praise": f"眼睛真亮！{ch} 找对啦！"}

CN_ASK_MORPH = ["看一看：这张图变成的字是哪个？", "想一想：这幅画是哪个字？",
                "象形字猜一猜：图里藏着哪个字？", "这张图画的是哪个字？点一点"]

def cn_listen_pic_to_char(i, ch, mfrom, v=0):
    """看图找字：目标大卡是象形图片，选项是字"""
    others = [c[0] for c in CN if c[0] != ch]
    d1 = others[(i * 2) % len(others)]
    d2 = others[(i * 2 + 1) % len(others)]
    pos = i % 3
    opts, ans = rot([{"text": ch}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"cn-{i}-l2", "kind": "listen", "promptIcon": mfrom, "speakText": ch,
            "question": CN_ASK_MORPH[(i + v) % len(CN_ASK_MORPH)],
            "options": opts, "answer": ans,
            "hint": f"想一想它像什么字", "praise": f"对！这张图就是「{ch}」"}

def cn_word_quiz(i, ch, words):
    """组词选卡：哪个词里有这个字（图文选项）"""
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

def cn_word_quiz2(i, ch, words):
    """组词选卡第二题：换正确词与干扰轮转（棋盘题目格扩产用）"""
    correct = words[1] if len(words) > 1 else words[0]
    dis = other_words(ch, 2, start=i * 5 + 2)
    pos = (i + 2) % 3
    opts, ans = rot([{"icon": correct[0], "text": correct[1]},
                     {"icon": dis[0][0], "text": dis[0][1]},
                     {"icon": dis[1][0], "text": dis[1][1]}], 0, pos)
    return {"id": f"cn-{i}-w2", "kind": "quiz",
            "question": f"再想一想：「{ch}」还能组成哪个词？",
            "options": opts, "answer": ans,
            "hint": f"找一找还有「{ch}」的词", "praise": f"又是组词高手：{correct[1]}！"}

def cn_listen_pic2(i, ch, lo, lans):
    """找图片第二题：换答案位与干扰顺序（棋盘题目格扩产用）"""
    tgt, d1, d2 = lo
    correct = {"icon": tgt, "text": ch}
    others = [{"icon": d1}, {"icon": d2}]
    nlans = (lans + 1) % 3
    opts = others[:nlans] + [correct] + others[nlans:]
    return {"id": f"cn-{i}-l3", "kind": "listen", "prompt": ch, "speakText": ch,
            "question": f"再找一找：哪张图片是「{ch}」？",
            "options": opts, "answer": nlans,
            "hint": f"「{ch}」长什么样", "praise": f"又找对啦！{ch}！"}

# v0.8 工单02/03/05：迷你棋盘组成——题目格引用 step id（teach/letter 保留为开场卡，不入盘）；
# 普通关 = 题 6 + 金币 1-2 + 事件 1-2（规格决策 2），总数 8-10、题目占比 ≥60%（6/10 压线合规）
EVENT_COMBOS = [["chest"], ["mushroom"], ["rest"], ["chest", "mushroom"], ["mushroom", "rest"], ["chest", "rest"]]
REVIEW_EVENTS = [["chest", "mushroom"], ["chest", "rest"]]   # 复习关事件格加倍（2 个）
# v0.10 试玩反馈「关卡同质化」：五学科每一关都是同一套 q-q-c-q-q-c 模板。
# 插格落点（GAP_PATTERNS）× 目标格数（SHAPE_CYCLE）双周期错开，相邻关不撞形状；
# 格数区间与题目占比仍由 validate.py 闸门兜底，这里只负责「长得不一样」。
GAP_PATTERNS = [[2, 4, 6], [1, 3, 5, 7], [3, 5, 7], [1, 4, 6], [2, 5, 7], [1, 2, 5]]
SHAPE_CYCLE = [8, 9, 10, 9, 8, 10]

def build_board(qids, extra, rotate_by):
    """棋盘组装：题目引用轮转起步 + 按关散列的插格落点（金币/事件格不再每关同一位置）"""
    qq = qids[rotate_by % len(qids):] + qids[:rotate_by % len(qids)]
    gaps = GAP_PATTERNS[rotate_by % len(GAP_PATTERNS)]
    spaces, used = [], 0
    for qn in range(len(qq)):
        spaces.append({"type": "question", "step": qq[qn]})
        if (qn + 1) in gaps and used < len(extra):
            spaces.append({"type": extra[used]})
            used += 1
    while used < len(extra):                     # 保险：多余事件放倒数第二位
        spaces.insert(len(spaces) - 1, {"type": extra[used]})
        used += 1
    return {"spaces": spaces}

def cn_board(i, qids):
    extra = target_extras(len(qids), i)
    return build_board(qids, extra, i)

# ================= 试玩反馈②：全学科棋盘化 + 题库扩产 =================
# 病根：非识字学科每关只有 2-4 道静态题且未棋盘化，重玩全是同一道题。
# 药方：每关补 2-4 道同题型不同参数的变体（≥5 道），全部普通关挂 8 格棋盘；
#       count 题加 countRange，客户端每次进题在区间内随机取数。

def target_extras(n_q, idx):
    """普通关补足到 8-10 格：目标格数按 SHAPE_CYCLE 长短交替（同科内不再清一色同一格数）。
    三道闸门由 validate.py 逐条判，这里先自己守住：题目占比 ≥60% · 总格数 8-10 · 金币 1-2 / 事件 1-2。
    金币至少 1（决策 2「题多的关宁可多一格也不许金币格清零」），装不下时先削事件格。"""
    combo = list(EVENT_COMBOS[idx % 6])
    while len(combo) > 1 and n_q + 1 + len(combo) > 10:
        combo.pop()
    room = min(int(n_q * 2 / 3) - len(combo), 10 - n_q - len(combo))
    n_coin = max(1, min(2, SHAPE_CYCLE[idx % 6] - n_q - len(combo), room))
    return ["coin"] * n_coin + combo

def boardify(levels, extras_fn):
    """普通关全部棋盘化：先扩产题目，再挂棋盘；已有棋盘的（识字村/复习/boss）不动"""
    for idx, lv in enumerate(levels):
        if "board" in lv:
            continue
        lv["steps"].extend(extras_fn(idx, lv))
        qids = [s["id"] for s in lv["steps"] if s["kind"] not in ("teach", "letter")]
        lv["board"] = build_board(qids, target_extras(len(qids), idx), idx)

def math_extra_steps(i, steps, scene):
    """思维镇变体：count2 + 按本关已有题型各出一道不同参数的变体，不足再从通用池补"""
    out = []
    if scene is not None:
        cs = next((s for s in steps if s["kind"] == "count"), None)
        n1 = cs["count"] if cs else 3
        n2 = max(3, n1 - 1)                      # validate 口径：count 静态数量下限 3
        out.append(dict(count_step(i, n2, sorted({max(1, n2 - 2), n2 - 1, n2}), scene, v=1),
                        id=f"math-{i}-c2"))
    for s in steps:
        if len(out) >= 3:
            break
        k = s["kind"]
        if k == "compare":
            l2, r2 = s["leftCount"], s["rightCount"]
            if l2 == r2:
                r2 += 1
            lb = [o["label"] for o in s["compareOptions"]]
            # 标签跟着内容走：左右图标互换时，「苹果多/香蕉多」这类实物标签必须一起换；
            # 「左边多/右边多」这类方位标签（两边同一种图标）留在原位，换了反而错
            if s["leftIcon"] != s["rightIcon"]:
                lb = [lb[1], lb[0]] + lb[2:]
            out.append(compare_step(i, s["rightIcon"], r2, s["leftIcon"], l2,
                                    lb, s["question"], sid="cmp2"))
        elif k == "order":
            base = s["nums"]
            up2 = [n + 2 for n in base]
            dn2 = [max(1, n - 2) for n in base]
            nums2 = up2 if max(up2) <= 10 and len(set(up2)) == 3 else (dn2 if len(set(dn2)) == 3
                                                                       else ([3, 7, 5] if s["dir"] == "up" else [8, 2, 5]))
            out.append(order_step(f"math-{i}-x{len(out)}-o", nums2, "down" if s["dir"] == "up" else "up"))
        elif k == "arith":
            a2, b2 = s["leftCount"] + 1, s["rightCount"]
            correct = a2 + b2 if s["op"] == "+" else a2 - b2
            opts = sorted({correct - 1, correct, correct + 1})
            joiner, tail = ("再加", "一共有几") if s["op"] == "+" else ("拿走", "还剩几")
            out.append(dict(arith_step(i, s["op"], a2, b2, opts, s["leftIcon"], s["unit"],
                                       f"{a2} {s['unit']}{joiner} {b2} {s['unit']}，{tail}{s['unit']}？"),
                            id=f"math-{i}-x{len(out)}-a"))
        elif k == "split":
            t2 = s["total"] + 1
            out.append(split_step(f"math-{i}-x{len(out)}-s", t2, s["part"], s["leftIcon"], s["unit"],
                                  f"{t2} {s['unit']}分两堆，左边 {s['part']} {s['unit']}，右边几{s['unit']}？"))
        elif k == "neighbor":
            a2 = s["nums"][0] + 1
            out.append(neighbor_step(f"math-{i}-x{len(out)}-n", a2, a2 + 2))
        elif k == "pattern":
            seq2 = list(reversed(s["seq"][:3]))
            # 第 4 项必须是周期里的下一个：[a,b,a] → b，[a,b,c] → a。
            # 旧写法 seq2+[seq2[0]] 会拼出 star/moon/star/star 这种没有规律的串，还把答案写死成 0
            nxt = seq2[1] if seq2[0] == seq2[2] else seq2[0]
            uniq = list(dict.fromkeys(seq2 + [nxt]))
            fill = "candy" if "candy" not in uniq else "star"
            opts = (uniq + [fill])[:3]
            out.append(pattern_step(f"math-{i}-x{len(out)}-p", seq2, opts, opts.index(nxt)))
        elif k == "dice":
            n2 = s["count"] - 1 if s["count"] > 2 else s["count"] + 1
            out.append(dice_step(f"math-{i}-x{len(out)}-d", n2, sorted({max(1, n2 - 1), n2, n2 + 1})))
        elif k == "quiz" and "最大" in s["question"]:
            out.append({"id": f"math-{i}-x{len(out)}-q", "kind": "quiz", "question": "哪个数字最小？",
                        "options": [{"text": t} for t in ["4", "8", "1"]], "answer": 2,
                        "hint": "越早数到的越小哦", "praise": "思维小达人！"})
        elif k == "quiz" and "最小" in s["question"]:
            out.append({"id": f"math-{i}-x{len(out)}-q", "kind": "quiz", "question": "哪个数字最大？",
                        "options": [{"text": t} for t in ["6", "2", "9"]], "answer": 2,
                        "hint": "从 1 数到 10，谁排在最后？", "praise": "9 最大，答对啦！"})
        elif k == "quiz":
            out.append(classify_step(f"math-{i}-x{len(out)}-c", "火眼金睛：哪个能吃？", ["duck", "cake", "train"], 1))
    # 通用补位：凑不满 3 道变体时，补的是「本关还没出现过的题型」，不是再数一遍道具
    # （旧写法一关里塞三道 count，思维镇 100 道题有 38 道在数数，这就是「同质化」的病根）
    have = {s["kind"] for s in steps} | {o["kind"] for o in out}
    j = 0
    while len(out) < 3:
        pick = next((k for k in MATH_FILL if k not in have), None)
        if pick is None:
            pick = MATH_FILL[(i + j) % len(MATH_FILL)]
        out.append(math_fill(pick, i, j, out))
        have.add(pick)
        j += 1
    return out

# 补位题型的出场顺序：每关先补它没有的题型，题型之间再换参数
MATH_FILL = ["pattern", "split", "neighbor", "order", "compare", "classify", "dice"]
MATH_PAT = [["star", "moon", "star"], ["candy", "apple", "candy"], ["sun", "moon", "sun"],
            ["flower", "leaf", "flower"], ["duck", "panda", "duck"], ["balloon", "gift", "balloon"]]
MATH_CLS = [("火眼金睛：哪个是水果？", ["apple", "train", "clock"]),
            ("哪个能当小伞？", ["mushroom", "rock", "key"]),
            ("哪个是动物？", ["penguin", "cake", "book"]),
            ("哪个自己会发光？", ["sun", "duck", "tree"]),
            ("哪个用来数时间？", ["clock", "flower", "balloon"]),
            ("哪个能坐人？", ["train", "cake", "leaf"])]

def math_fill(kind, i, j, sofar):
    """补位题：同一题型在不同关里换参数，别让孩子连着做三道一模一样的事"""
    n = 3 + (i + j) % 6                                   # 3..8
    sid = f"math-{i}-f{j}-{kind[:3]}"
    if kind == "pattern":
        seq = list(MATH_PAT[(i + j) % len(MATH_PAT)])
        nxt = seq[1] if seq[0] == seq[2] else seq[0]
        pool = list(dict.fromkeys(seq + [nxt]))
        fill = [x for x in ("candy", "star", "flower") if x not in pool][0]
        opts = (pool + [fill])[:3]
        return pattern_step(sid, seq, opts, opts.index(nxt),
                            Q_ALT["pattern"][(i + j) % len(Q_ALT["pattern"])])
    if kind == "split":
        t = min(10, n + 2)
        p = max(1, min(t - 1, n - 1))
        return split_step(sid, t, p, "candy", "颗",
                          f"{t} 颗糖分两盘，这边 {p} 颗，那边几颗？")
    if kind == "neighbor":
        a = 1 + (i + j) % 7
        return neighbor_step(sid, a, a + 2)
    if kind == "order":
        up = (i + j) % 2 == 0
        base = [n, max(1, n - 3), min(10, n + 2)]
        nums = list(dict.fromkeys(base))
        while len(nums) < 3:
            nums.append(len(nums) + 1)
        return order_step(sid, nums[:3], "up" if up else "down")
    if kind == "compare":
        l = n
        r = max(1, n - 2) if (i + j) % 3 else n           # 三分之一概率出「一样多」
        return compare_step(i, "star", l, "moon", r, ["左边多", "右边多", "一样多"],
                            Q_ALT["compare"][(i + j) % len(Q_ALT["compare"])], sid=f"{kind}{j}")
    if kind == "classify":
        q, items = MATH_CLS[(i + j) % len(MATH_CLS)]
        pos = (i + j) % 3
        opts, ans = rot([{"icon": items[0]}, {"icon": items[1]}, {"icon": items[2]}], 0, pos)
        return {"id": sid, "kind": "quiz", "question": q, "options": opts, "answer": ans,
                "hint": "想一想它们分别是什么", "praise": "分类小能手！"}
    n = 1 + (i + j) % 6
    return dice_step(sid, n, sorted({max(1, n - 1), n, min(6, n + 1)}))

def boardify_math(levels):
    MATH_SCENES = [SC_duck, SC_candy, SC_apple, SC_balloon, SC_star, SC_train,
                   SC_flower, SC_heart, SC_coin, None, None, None, None, None, None]
    boardify(levels, lambda idx, lv: math_extra_steps(idx, lv["steps"], MATH_SCENES[idx]))

# 变体题是拿同一道题改参数生成的，题面常常原样抄过来（「想一想：藏起来的数字是几？」
# 一关里出现两遍）。这里按题型换一句同义问法；audit_content.py 规则 8 判 FAIL，漏不掉。
Q_ALT = {
    "order-up":   ["从小到大，依次点一点", "谁最小？从它开始点", "按小到大排一排", "从最小的那个开始点"],
    "order-down": ["从大到小，依次点一点", "谁最大？先点它", "按大到小排一排", "从最大的那个开始点"],
    "neighbor":   ["想一想：藏起来的数字是几？", "两个数中间，躲着谁？", "数到一半断了，中间是几？",
                   "问号的位置本该是几？"],
    "pattern":    ["找规律：下一个是哪个？", "谁在轮流出现？点下一个", "读一读前面几个，接下来是谁？",
                   "排列里藏着小秘密，下一个是？"],
    "dice":       ["掷骰子：掷出了几点？", "骰子停下来是几点？", "数数骰子上的点点", "这一把掷出了几点？"],
    "compare":    ["哪一边更多？", "两边比一比，谁多？", "数一数，哪边挤一点？", "哪一边的队伍更长？"],
    "max":        ["哪个数字最大？", "这几个数里谁最大？", "谁排在最最后面？"],
    "min":        ["哪个数字最小？", "这几个数里谁最小？", "谁排在最最前面？"],
}

def qkey(st):
    k = st["kind"]
    if k == "order":
        return f"order-{st.get('dir', 'up')}"
    if k in ("neighbor", "pattern", "dice", "compare"):
        return k
    if k == "quiz":
        q = st.get("question", "")
        return "max" if "最大" in q else ("min" if "最小" in q else None)
    return None

def dedupe_questions(levels):
    """同关撞句就换说法（count 的问句带着道具名，交给场景池在生成时管，这里不动）"""
    for lv in levels:
        seen = set()
        for st in lv["steps"]:
            if st["kind"] in ("teach", "letter", "count"):
                continue
            q = st.get("question", "")
            if q not in seen:
                seen.add(q)
                continue
            for alt in Q_ALT.get(qkey(st) or "", []):
                if alt not in seen:
                    st["question"] = alt
                    seen.add(alt)
                    break

def sample_questions(level_steps, count, tag):
    """复习关旧题抽取（工单05）：轮转各关的问题序列交错混排（开盲盒），重编 id 防与原关冲突。
    复习关本身也含旧题，混排时同一句话可能被抽到两次（boss 关里「数一数有几颗行星」出现两遍），
    这里按题面去重：撞句就跳过，往后抽一道不一样的。"""
    pool, take = [], [0] * len(level_steps)
    used_q = set()
    while len(pool) < count:
        moved = False
        for li, sts in enumerate(level_steps):
            qs = [s for s in sts if s["kind"] not in ("teach", "letter")]
            while take[li] < len(qs) and len(pool) < count:
                st = dict(qs[take[li]])
                take[li] += 1
                qt = st.get("question", "")
                moved = True
                if qt and qt in used_q:
                    continue
                st["id"] = f"{tag}-{len(pool)}"
                used_q.add(qt)
                pool.append(st)
                break
        if not moved:
            break
    return pool

def add_review_levels(levels, sub, positions, priors=(5, 10)):
    """每学科插 2 个复习关（约第 5、10 关之后）：旧题混排棋盘 + 事件格加倍，
    标记 review=True（默认解锁不挡路）；现有 id 一律不动，只做位置插入（平移迁移）"""
    q_by_level = [[s for s in lv["steps"] if s["kind"] not in ("teach", "letter")] for lv in levels]
    for k in (0, 1):
        p = priors[k]
        # 天文台等单题学科前 5 关可能凑不满 6 题：采样范围自适应扩到够用（仍是"以前学过的"）
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
    """工单06：boss 关（每学科 1 个，追加末尾，boss=True）——8 道旧题连续作答，
    血条玩法在客户端状态机；解锁规则（正式关全通）在 nodeState/node_state"""
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
               cn_word_quiz2(i, ch, words),
               cn_listen_pic2(i, ch, lo, lans)]
    steps = [{"id": f"cn-{i}-t", "kind": "teach", "morphFrom": mfrom, "char": ch, "pinyin": py,
              "words": [{"icon": w, "text": t, "say": t} for w, t in words]}] + q_steps
    cn_levels.append({"id": f"cn-{i}", "title": f"第 {i+1} 关 {ch}", "subtitle": f"认识「{ch}」",
                      "steps": steps, "board": cn_board(i, [s["id"] for s in q_steps])})
# 第15关 复习挑战：翻牌配对 + 题型混合（同样上棋盘，无开场卡）
cn_levels.append({"id": "cn-14", "title": "第 15 关 复习挑战", "subtitle": "汉字小达人", "steps": [
    memory_step("cn-14-m", "翻翻牌：把字和它的图片配成对", [
        ("日", "sunface", None, None, "日"),
        ("月", "moon", None, None, "月"),
        ("火", "flame", None, None, "火"),
    ]),
    {"id": "cn-14-l1", "kind": "listen", "promptIcon": "flame", "speakText": "火",
     "question": "看一看：这张图变成的字是哪个？",
     "options": [{"text": t} for t in ["山","火","水"]], "answer": 1,
     "hint": "热热的、红红的", "praise": "真棒！"},
    cn_word_quiz(14, "花", [("flower","花朵"),("leaf","花瓣")]),
    {"id": "cn-14-q", "kind": "quiz", "question": "大挑战：哪个是「鸟」？",
     "options": [{"text": t} for t in ["鸟","乌","鸣"]], "answer": 0, "hint": "有一点点，就是小鸟", "praise": "复习家！全对啦！"},
    {"id": "cn-14-q2", "kind": "quiz", "question": "连一连：哪个是「山」？",
     "options": [{"text": t} for t in ["出","山","田"]], "answer": 1, "hint": "三个尖尖头", "praise": "山找对啦！"},
    {"id": "cn-14-q3", "kind": "quiz", "question": "猜一猜：哪个是「月」？",
     "options": [{"text": t} for t in ["月","用","明"]], "answer": 0, "hint": "弯弯的，像小船", "praise": "月亮出来啦！"},
], "board": cn_board(14, ["cn-14-m", "cn-14-l1", "cn-14-w", "cn-14-q", "cn-14-q2", "cn-14-q3"])})
add_review_levels(cn_levels, "cn", (5, 11))
add_boss_level(cn_levels, "cn")
dedupe_questions(cn_levels)
W("cn_levels.json", {"subject": "cn", "title": "识字村", "guide": "panda", "levels": cn_levels})

# ================= 数学 15 关（8 种题型，v0.4） =================
math_levels = []

def count_step(i, n, opts, scene, v=0):
    """countRange（试玩反馈②）：客户端每次进题在区间内随机取数+重组选项，重玩不再总是同一道。
    v = 本关里的第几道数数：轮着换道具场景和问法，同关三格数数不再长一个样、说一句话"""
    pool = [scene] + scene["alts"]
    sc = pool[v % len(pool)]
    return {"id": f"math-{i}-c", "kind": "count",
            "question": sc["qs"][(v // len(pool)) % len(sc["qs"])],
            "duckIcon": sc["icon"], "count": n, "countRange": [max(2, n - 2), n],
            "countOptions": opts,
            "backdrop": sc["backdrop"], "unit": sc["unit"]}

def compare_step(i, li, l, ri, r, labels, q="哪一边更多？", sid=None):
    key = "same" if l == r else ("left" if l > r else "right")
    return {"id": f"math-{i}-{sid or 'cmp'}", "kind": "compare", "question": q,
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


# 试玩反馈「几乎都是相同的题目重复出现」：一关棋盘上连着三格数数，道具、说法、
# 连问句里的括号都一模一样，孩子只觉得「这题我刚刚做过」。
# 药方：每套场景备三句问法，同关的第二、三道数数再换一套道具（连带换背景）。
def SC(icon, unit, backdrop, q0, q1, q2):
    return {"icon": icon, "unit": unit, "backdrop": backdrop, "q": q0, "qs": [q0, q1, q2], "alts": []}

SC_duck   = SC("duck",   "只", "pond",  "池塘里有几只小鸭？点一点", "水里游着几只鸭子？数一数", "鸭妈妈身后跟了几只？")
SC_candy  = SC("candy",  "颗", "grass", "盘子里有几颗糖？点一点", "桌上撒了几颗水果糖？数一数", "糖果罐前有几颗糖？")
SC_apple  = SC("apple",  "个", "grass", "果园里摘了几个苹果？点一点", "草地上放着几个苹果？数一数", "今天摘了几个大苹果？")
SC_balloon= SC("balloon","个", "sky",   "天上有几个气球？点一点", "飘着的气球有几个？数一数", "天花板下吊着几个气球？")
SC_star   = SC("star",   "颗", "night", "夜空里有几颗星星？点一点", "天黑了几颗小星星？数一数", "这片夜空亮着几颗星？")
SC_train  = SC("train",  "辆", "grass", "轨道上有几辆小火车？点一点", "停车场里停了几辆火车？数一数", "开来开去有几辆车？")
SC_flower = SC("flower", "朵", "grass", "花园里开了几朵花？点一点", "草丛里钻出几朵花？数一数", "今天开了几朵小花？")
SC_heart  = SC("heart",  "颗", "grass", "礼盒里有几颗爱心糖？点一点", "盒子里装了几颗爱心？数一数", "送人的爱心糖有几颗？")
SC_coin   = SC("coin",   "枚", "night", "宝箱里有几枚金币？点一点", "打开宝箱数数有几枚金币", "夜里宝箱亮着几枚金币？")
# 每套场景配两套「换道具」备选：同关第二、三道数数用它，画面不再是一模一样的三格
_ALL_SC = [SC_duck, SC_candy, SC_apple, SC_balloon, SC_star, SC_train, SC_flower, SC_heart, SC_coin]
for _k, _sc in enumerate(_ALL_SC):
    _sc["alts"] = [_ALL_SC[(_k + j) % len(_ALL_SC)] for j in (3, 6)]

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
boardify_math(math_levels)
add_review_levels(math_levels, "math", (5, 11))
add_boss_level(math_levels, "math")
dedupe_questions(math_levels)
W("math_levels.json", {"subject": "math", "title": "思维镇", "guide": "fox", "levels": math_levels})

# ================= 拼音 12 关（letter + 题型组合轮换） =================
PY = [
    # (声母, [(图标, 例词)], 拼读左, 拼读右, 拼读选项)
    # ⚠️ 例词的图必须真画得出那个东西：旧表按「图标英文名首字母 = 拼音声母」选图，
    #    于是出现香蕉配「白菜」、礼物配「老虎」、火车配「太阳」——孩子看图学音就学反了。
    #    改任何一行后跑 python3 ios/tools/audit_content.py，它会验图↔词↔声母三条链。
    ("b", [("rabbit", "白兔 bái"), ("ice", "冰块 bīng")], "b", "a", ["ba", "bo", "bu"]),
    ("p", [("apple", "苹果 píng"), ("jar", "瓶子 píng")], "p", "o", ["po", "pa", "pi"]),
    ("m", [("mushroom", "蘑菇 mó"), ("cat", "小猫 māo")], "m", "a", ["ma", "mo", "mu"]),
    ("f", [("home", "房子 fáng"), ("flame", "发烧 fā")], "f", "a", ["fa", "fo", "fu"]),
    ("d", [("earth", "大地 dì"), ("cake", "蛋糕 dàn")], "d", "e", ["de", "da", "du"]),
    ("t", [("sun", "太阳 tài"), ("candy", "糖果 táng")], "t", "a", ["ta", "te", "tu"]),
    ("n", [("duck", "小鸟 niǎo"), ("girl", "你好 nǐ")], "n", "i", ["ni", "na", "nu"]),
    ("l", [("leaf", "绿叶 lǜ"), ("speaker", "喇叭 lǎ")], "l", "a", ["la", "le", "lu"]),
    ("g", [("apple", "果子 guǒ"), ("bush", "灌木 guàn")], "g", "e", ["ge", "ga", "gu"]),
    ("k", [("book", "看书 kàn"), ("dino", "恐龙 kǒng")], "k", "e", ["ke", "ka", "ku"]),
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
    """看图找声母：大卡是图片，选项是声母"""
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

# 试玩反馈：「b — o = ?」这个破折号被孩子读成了减法。
# 题面改成「和/碰上/手拉手」的说法，卡片之间的连接符也在渲染层换成了 ⊕ + ⇒（见 blendHTML）。
def py_blend(i, b0, b1, blends):
    return {"id": f"py-{i}-b", "kind": "blend", "parts": [b0, b1],
            "question": f"拼一拼：{b0} 和 {b1} 手拉手，变成哪个音？",
            "options": [{"text": t} for t in blends], "answer": 0,
            "hint": f"{b0} 碰上 {b1}", "praise": f"拼对了，{blends[0]}！"}

def py_pic_quiz(i, letter, ex0, b0, b1):
    """音节选图：拼读音节，选对应的图"""
    icon, text = ex0
    word = text.split(" ")[0]
    dis = [x for x in ICON_POOL if x != icon]
    d1 = dis[(i * 3) % len(dis)]
    d2 = dis[(i * 3 + 2) % len(dis)]
    pos = (i + 1) % 3
    opts, ans = rot([{"icon": icon, "text": word}, {"icon": d1}, {"icon": d2}], 0, pos)
    return {"id": f"py-{i}-pq", "kind": "quiz",
            "question": f"拼一拼：{b0} 碰上 {b1}，哪张图是这个音？",
            "options": opts, "answer": ans,
            "hint": f"{b0} 碰 {b1}", "praise": f"拼读小能手：{word}！"}

pinyin_levels = []
for i, (letter, examples, b0, b1, blends) in enumerate(PY):
    steps = [{"id": f"py-{i}-t", "kind": "letter", "letters": [letter], "display": letter,
              "examples": [{"icon": ic, "text": t, "say": t.split(" ")[0]} for ic, t in examples],
              "question": f"学一学声母 {letter}"}]
    combo = i % 4
    if combo == 0:      # A：找字母 + 拼读
        steps += [py_listen_letter(i, letter), py_blend(i, b0, b1, blends)]
    elif combo == 1:    # B：看图找声母 + 拼读
        steps += [py_listen_pic_to_initial(i, letter, examples[0]), py_blend(i, b0, b1, blends)]
    elif combo == 2:    # C：音节选图 + 找字母
        steps += [py_pic_quiz(i, letter, examples[0], b0, b1), py_listen_letter(i, letter)]
    else:               # D：拼读 + 音节选图
        steps += [py_blend(i, b0, b1, blends), py_pic_quiz(i, letter, examples[0], b0, b1)]
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 声母 {letter}", "subtitle": f"认识「{letter}」", "steps": steps})
# 韵母关 + 复习关
pinyin_levels.append({"id": "py-10", "title": "第 11 关 韵母", "subtitle": "a o e i u ü", "steps": [
    {"id": "py-10-t", "kind": "letter", "letters": ["a","o","e","i","u","ü"], "display": "a",
     "examples": [{"icon": "duck", "text": "啊 ā 张大嘴", "say": "ā"}, {"icon": "speaker", "text": "哦 ó 圆口形", "say": "ó"}],
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
     "question": "拼一拼：b 和 a 合起来是？",
     "options": [{"text": t} for t in ["ba","bo","pa"]], "answer": 0,
     "hint": "爸爸的爸", "praise": "拼读小能手！"},
    {"id": "py-11-pq", "kind": "quiz",
     "question": "拼一拼：m 碰上 a，哪张图是「妈妈」？",
     "options": [{"icon": "girl", "text": "妈妈"}, {"icon": "moon"}, {"icon": "train"}], "answer": 0,
     "hint": "m 碰 a", "praise": "拼读小达人！"},
]})
# 试玩反馈②：拼音谷题库扩产（每关 ≥5 道不同变体）+ 全部普通关棋盘化
def py_listen_letter2(i, letter):
    others = ["d","p","m","f","t","n","l","g","k","b"]
    dis = [x for x in others if x != letter]
    opts = [letter, dis[(i * 2) % len(dis)], dis[(i * 2 + 1) % len(dis)]]
    return {"id": f"py-{i}-lb", "kind": "listen", "prompt": letter, "speakText": letter,
            "question": f"再找一找：哪个是「{letter}」？",
            "options": [{"text": t} for t in opts], "answer": 0,
            "hint": "想一想它的样子", "praise": f"「{letter}」又找对啦！"}

def py_blend2(i, b0, v, blends, tag):
    target = b0 + v
    opts = [target] + [x for x in blends if x != target][:2]
    return {"id": f"py-{i}-{tag}", "kind": "blend", "parts": [b0, v],
            "question": f"再来一拼：{b0} 和 {v} 合起来读什么？",
            "options": [{"text": t} for t in opts], "answer": 0,
            "hint": f"{b0} 碰上 {v}", "praise": f"拼对了，{target}！"}

def py_pic_quiz2(i, ex0, b0, b1):
    icon, text = ex0
    word = text.split(" ")[0]
    dis = [x for x in ICON_POOL if x != icon]
    d1, d2 = dis[(i * 3 + 1) % len(dis)], dis[(i * 3 + 4) % len(dis)]
    pos = i % 3
    opts, ans = rot([{"icon": icon, "text": word}, {"icon": d1}, {"icon": d2}], 0, pos)
    return {"id": f"py-{i}-pq2", "kind": "quiz",
            "question": f"看图拼一拼：{b0} 和 {b1} 合起来是哪张图？",
            "options": opts, "answer": ans,
            "hint": f"{b0} 碰 {b1}", "praise": f"拼读小能手：{word}！"}

def py_extras(i, lv):
    first = lv["steps"][0]
    if first["kind"] != "letter":          # 复习关（py-11）：补拼读与整体认读变体
        return [
            {"id": "py-11-lb", "kind": "blend", "parts": ["m", "a"],
             "question": "拼一拼：m 和 a 手拉手是？", "options": [{"text": t} for t in ["ma", "mo", "ba"]], "answer": 0,
             "hint": "m 碰 a", "praise": "拼对啦，ma！"},
            {"id": "py-11-l2", "kind": "listen", "prompt": "chi", "speakText": "chi",
             "question": "找一找：哪个是「chi」？", "options": [{"text": t} for t in ["zhi", "chi", "shi"]], "answer": 1,
             "hint": "吃东西的 chi", "praise": "整体认读 chi！"},
        ]
    letter = first["letters"][0]
    if i < 10:
        _, examples, b0, b1, blends = PY[i]
        return [py_listen_letter2(i, letter),
                py_blend2(i, b0, blends[1][1], blends, "b2"),
                py_pic_quiz2(i, examples[0], b0, b1)]
    # 韵母关（py-10）：单题关多补一道，凑满 5 题
    return [py_listen_letter2(i, letter),
            py_blend2(i, "m", "a", ["ma", "mo", "mi"], "b2"),
            py_blend2(i, "l", "a", ["la", "le", "lo"], "b3"),
            {"id": "py-10-l3", "kind": "listen", "prompt": "o", "speakText": "o",
             "question": "找一找：哪个是韵母「o」？",
             "options": [{"text": t} for t in ["e", "o", "a"]], "answer": 1,
             "hint": "圆圆嘴巴 óóó", "praise": "韵母 o 找对啦！"}]

boardify(pinyin_levels, py_extras)
add_review_levels(pinyin_levels, "pinyin", (5, 11))
add_boss_level(pinyin_levels, "pinyin")
dedupe_questions(pinyin_levels)
W("pinyin_levels.json", {"subject": "pinyin", "title": "拼音谷", "guide": "panda", "levels": pinyin_levels})

# ================= 英语 12 关（letter + 题型组合轮换） =================
EN_LETTERS = [
    ("Aa", "apple", "Apple 苹果"), ("Bb", "banana", "Banana 香蕉"),
    ("Cc", "cake", "Cake 蛋糕"), ("Dd", "duck", "Duck 小鸭"),
    ("Ss", "sun", "Sun 太阳"), ("Mm", "moon", "Moon 月亮"),
    ("Ff", "flower", "Flower 花"), ("Ll", "leaf", "Leaf 叶子"),
    ("Kk", "key", "Key 钥匙"), ("Hh", "heart", "Heart 爱心"),
    ("Rr", "rainbow", "Rainbow 彩虹"), ("Gg", "gift", "Gift 礼物"),
]

# 试玩反馈「几乎都是相同的题目重复出现」：英语王国 81 道题里只有 41 句不同问法，
# 「Which picture starts with X?」一句就问了 20 遍。这里两件事一起做：
# ① 每类题备几句同义问法，按关卡号轮转；② 补两种新玩法（数一数、拼单词），不再只有认字母。
EN_ASK_FIND = ["Find: which one is {d} ?", "听一听：哪个是 {d} ？", "Look again：找出 {d} 这两个字母",
               "哪一张卡片上写着 {d} ？"]
EN_ASK_PIC = ["Which picture starts with {u}?", "找一找：哪个图的开头是 {u} ？",
              "Which one begins with the sound {u}?", "这个字母开头的是哪张图？"]
EN_ASK_HOW = ["How many {w}? 数一数有几个？", "数数看：有几个 {w}？", "Count: 这里一共有几样东西？"]

def en_listen_letter(li, disp, v=0):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    opts = [others[li % 4], others[(li + 1) % 4], disp]
    ans = opts.index(disp)
    return {"id": f"en-{li}-l", "kind": "listen", "prompt": disp, "speakText": disp[0],
            "question": EN_ASK_FIND[(li + v) % len(EN_ASK_FIND)].format(d=disp),
            "options": [{"text": t} for t in opts], "answer": ans,
            "hint": f"{disp[0]} for {disp}", "praise": f"Yes! {disp}!"}

def en_pic_quiz(li, disp, icon, word, v=0):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    d1, d2 = others[(li + 2) % 8], others[(li + 3) % 8]
    d1i = next(x for x in EN_LETTERS if x[0] == d1)[1]
    d2i = next(x for x in EN_LETTERS if x[0] == d2)[1]
    return {"id": f"en-{li}-q", "kind": "quiz",
            "question": EN_ASK_PIC[(li + v) % len(EN_ASK_PIC)].format(u=disp[0]),
            "options": [{"icon": d1i}, {"icon": icon}, {"icon": d2i}],
            "answer": 1, "hint": word, "praise": "Great job!"}

EN_COUNT_SC = [("apple", "apples", "个", "grass"), ("duck", "ducks", "只", "pond"),
               ("star", "stars", "颗", "night"), ("balloon", "balloons", "个", "sky"),
               ("candy", "candies", "颗", "grass"), ("train", "trains", "辆", "grass")]

def en_count(li, idx, v=0):
    """数一数：用英语问数量，道具按关卡轮转（英语王国不再只有认字母）"""
    icon, plural, unit, bd = EN_COUNT_SC[(li + idx) % len(EN_COUNT_SC)]
    n = 3 + (li + idx) % 6
    return {"id": f"en-{li}-ct{idx}", "kind": "count",
            "question": EN_ASK_HOW[(li + v) % len(EN_ASK_HOW)].format(w=plural),
            "duckIcon": icon, "count": n, "countRange": [max(2, n - 2), n],
            "countOptions": [max(1, n - 1), n, min(10, n + 1)],
            "backdrop": bd, "unit": unit}

def en_blend(li, disp, icon, word, v=0):
    """拼单词：声母 + 韵脚合成整词，和拼音谷的拼读同一套动作（b + anana → banana）"""
    w = word.split(" ")[0].lower()
    head, tail = w[0], w[1:]
    others = [x for _, x, _ in EN_LETTERS if x != word]
    d1 = others[(li * 3) % len(others)].split(" ")[0].lower()
    d2 = others[(li * 3 + 5) % len(others)].split(" ")[0].lower()
    return {"id": f"en-{li}-bl{v}", "kind": "blend", "parts": [head, tail],
            "question": f"拼一拼：{head} 和 {tail} 手拉手，是哪个单词？",
            "options": [{"text": t} for t in [w, d1, d2]], "answer": 0,
            "hint": f"{disp} for {w}", "praise": f"拼对了，{w}！"}

def en_case_quiz(li, disp):
    """大小写配对：小写找大写"""
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
    # 六种组合轮转（原来只有四种，隔四关就把同样的两道题再演一遍）
    combo = li % 6
    if combo == 0:      # A：找字母 + 数一数
        steps += [en_listen_letter(li, disp), en_count(li, 0)]
    elif combo == 1:    # B：大小写配对 + 找图
        steps += [en_case_quiz(li, disp), en_pic_quiz(li, disp, icon, word)]
    elif combo == 2:    # C：拼单词 + 找字母
        steps += [en_blend(li, disp, icon, word), en_listen_letter(li, disp, v=1)]
    elif combo == 3:    # D：图标规律 + 找图
        steps += [en_pattern(li, icon), en_pic_quiz(li, disp, icon, word, v=1)]
    elif combo == 4:    # E：数一数 + 拼单词
        steps += [en_count(li, 1), en_blend(li, disp, icon, word)]
    else:               # F：大小写配对 + 图标规律
        steps += [en_case_quiz(li, disp), en_pattern(li, icon)]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} {disp}", "subtitle": disp, "steps": steps})
for li, idx in [(8, 10), (9, 11)]:
    disp, icon, word = EN_LETTERS[idx]
    english_levels.append({"id": f"en-{li}", "title": f"Level {li+1} {disp}", "subtitle": disp, "steps": [
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
# 试玩反馈②：英语王国题库扩产 + 全部普通关棋盘化
def en_listen_letter2(li, disp):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    opts = [disp, others[(li + 2) % 8], others[(li + 3) % 8]]
    return {"id": f"en-{li}-l2", "kind": "listen", "prompt": disp, "speakText": disp[0],
            "question": f"Find again: which one is {disp} ?",
            "options": [{"text": t} for t in opts], "answer": 0,
            "hint": f"{disp[0]} for {disp}", "praise": f"Yes! {disp}!"}

def en_case_quiz2(li, disp):
    upper, lower = disp[0], disp[1]
    others = [d[0] for d, _, _ in EN_LETTERS if d[0] != upper]
    d1, d2 = others[(li * 2 + 3) % len(others)], others[(li * 2 + 5) % len(others)]
    pos = li % 3
    opts, ans = rot([{"text": upper}, {"text": d1}, {"text": d2}], 0, pos)
    return {"id": f"en-{li}-c2", "kind": "quiz",
            "question": f"大写 {upper} 的小写是哪个？",
            "options": opts, "answer": ans,
            "hint": f"{disp} = {upper}{lower}", "praise": f"{upper}{lower} 又配对成功！"}

def en_pic_quiz2(li, disp, icon, word):
    others = [d for d, _, _ in EN_LETTERS if d != disp]
    d1, d2 = others[(li + 4) % 8], others[(li + 5) % 8]
    d1i = next(x for x in EN_LETTERS if x[0] == d1)[1]
    d2i = next(x for x in EN_LETTERS if x[0] == d2)[1]
    opts, ans = rot([{"icon": icon}, {"icon": d1i}, {"icon": d2i}], 0, li % 3)
    return {"id": f"en-{li}-q2", "kind": "quiz",
            "question": f"Which picture starts with {disp}?（再找一找）",
            "options": opts, "answer": ans, "hint": word, "praise": "Great job!"}

# 单词关的备用题：按关卡号取不同单词，别再和关卡里已有的两句撞车
EN_WORD_BANK = [
    ("star", "星星", [("star", "星星"), ("moon", "月亮"), ("sun", "太阳")], 0),
    ("rainbow", "彩虹", [("gift", "礼物"), ("rainbow", "彩虹"), ("heart", "爱心")], 1),
    ("banana", "香蕉", [("apple", "苹果"), ("banana", "香蕉"), ("cake", "蛋糕")], 1),
    ("gift", "礼物", [("gift", "礼物"), ("key", "钥匙"), ("duck", "小鸭")], 0),
]

def en_extras(i, lv):
    first = lv["steps"][0]
    if first["kind"] != "letter":          # en-10 / en-11 单词复习关
        out = []
        for j in (0, 1):
            ic_, cn_, items, ans = EN_WORD_BANK[(i * 2 + j) % len(EN_WORD_BANK)]
            # word_quiz 的 item 是 (文字, 图标)，知识库里存的是 (图标, 中文名)，别写反
            out.append(word_quiz(f"en-x{i}-{j}", f"Which one is the {ic_}? {cn_}是哪一个？",
                                 [(x[1], x[0]) for x in items], ans, f"{ic_.title()} {cn_}",
                                 f"Yes! {ic_.title()}!"))
        return out
    idx = 10 if i == 8 else (11 if i == 9 else i)
    disp, icon, word = EN_LETTERS[idx]
    # 三道变体里塞一道新玩法（数数/拼词），别全是认字母的翻版
    extra = [en_listen_letter2(i, disp), en_case_quiz2(i, disp), en_pic_quiz2(i, disp, icon, word)]
    extra[i % 3] = en_count(i, 2) if i % 2 == 0 else en_blend(i, disp, icon, word)
    return extra

boardify(english_levels, en_extras)
add_review_levels(english_levels, "english", (5, 11))
add_boss_level(english_levels, "english")
dedupe_questions(english_levels)
W("english_levels.json", {"subject": "english", "title": "英语王国", "guide": "robot", "levels": english_levels})

# ================= 天文台 15 关（v0.10 改版：太阳系课程，不是认图标） =================
# 病根：老版十关全在问「哪个是太阳」，那是识字，不是天文。
# 药方：照上海天文馆「家园」展项的路子重做——先认识这个家（1 颗恒星 + 8 颗行星 + 卫星 + 矮行星），
#       再拿真实数据比：距离、直径、质量、引力、自转、公转、温度、卫星数，
#       最后走到月相、恒星星座和中国航天。
# 行星不再是通用 planet.svg：圆盘按真实直径比例画，土星带环、木星有条纹和大红斑
#       （视觉在 index.html 的 BODIES / bodyHTML）；数据题用新题型 cmp——一行一个天体，点一行作答。
# 数据口径：NASA Planetary Fact Sheet。value 是可比对的真值，label 才是给孩子看的话；
#       温度条用热力学温度（K）画长度、标签仍写℃，否则负数画不出条。
P = {
    "mercury": {"cn": "水星", "en": "Mercury", "rank": 1, "dist": 58, "dia": 0.38, "mass": 0.06,
                "grav": 0.38, "day": 1408, "year": 88, "moons": 0, "temp": 167,
                "fact": "离太阳最近，88 天就跑完一圈，是太阳系的短跑冠军"},
    "venus":   {"cn": "金星", "en": "Venus", "rank": 2, "dist": 108, "dia": 0.95, "mass": 0.82,
                "grav": 0.91, "day": 5832, "year": 225, "moons": 0, "temp": 464,
                "fact": "厚云把热量捂住，464℃ 比离太阳更近的水星还热，而且它倒着转"},
    "earth":   {"cn": "地球", "en": "Earth", "rank": 3, "dist": 150, "dia": 1.0, "mass": 1.0,
                "grav": 1.0, "day": 24, "year": 365, "moons": 1, "temp": 15,
                "fact": "目前唯一找到生命的行星，表面七成以上是海洋"},
    "mars":    {"cn": "火星", "en": "Mars", "rank": 4, "dist": 228, "dia": 0.53, "mass": 0.11,
                "grav": 0.38, "day": 25, "year": 687, "moons": 2, "temp": -65,
                "fact": "有一座火山比珠穆朗玛峰还高两倍，是太阳系最高的山"},
    "jupiter": {"cn": "木星", "en": "Jupiter", "rank": 5, "dist": 779, "dia": 11.2, "mass": 318,
                "grav": 2.53, "day": 10, "year": 4333, "moons": 95, "temp": -110,
                "fact": "大红斑是一场刮了 300 多年的超级风暴，能塞下整个地球"},
    "saturn":  {"cn": "土星", "en": "Saturn", "rank": 6, "dist": 1434, "dia": 9.45, "mass": 95,
                "grav": 1.07, "day": 11, "year": 10759, "moons": 146, "temp": -140,
                "fact": "光环由无数冰块和石子组成；它轻得能浮在大水上"},
    "uranus":  {"cn": "天王星", "en": "Uranus", "rank": 7, "dist": 2871, "dia": 4.0, "mass": 14.5,
                "grav": 0.89, "day": 17, "year": 30687, "moons": 28, "temp": -195,
                "fact": "它是躺着打滚绕太阳的，身子歪了 98 度"},
    "neptune": {"cn": "海王星", "en": "Neptune", "rank": 8, "dist": 4515, "dia": 3.9, "mass": 17.1,
                "grav": 1.14, "day": 16, "year": 60190, "moons": 16, "temp": -200,
                "fact": "太阳系风最大的地方，一秒能吹两公里"},
    "sun":     {"cn": "太阳", "en": "Sun", "rank": 0, "dist": 0, "dia": 109, "mass": 333000,
                "grav": 28, "day": 609, "year": 0, "moons": 0, "temp": 5505,
                "fact": "太阳系 99.8% 的物质都集中在太阳身上"},
    "moon":    {"cn": "月球", "en": "Moon", "rank": 0, "dist": 0.4, "dia": 0.27, "mass": 0.012,
                "grav": 0.16, "day": 655, "year": 27, "moons": 0, "temp": -20,
                "fact": "月球自己不发光，你看到的是它反射的太阳光"},
    "pluto":   {"cn": "冥王星", "en": "Pluto", "rank": 9, "dist": 5906, "dia": 0.19, "mass": 0.002,
                "grav": 0.06, "day": 153, "year": 90560, "moons": 5, "temp": -225,
                "fact": "2006 年被降成矮行星，因为它没能清空自己轨道上的碎石"},
    "comet":   {"cn": "彗星", "en": "Comet", "rank": 0, "dist": 108, "dia": 0.001, "mass": 0.0001,
                "grav": 0.0, "day": 10, "year": 225, "moons": 0, "temp": -70,
                "fact": "冰做的脏雪球，靠近太阳时甩出长长的尾巴"},
}
for _k in P:
    P[_k]["k"] = P[_k]["temp"] + 273          # 画温度条用的热力学温度

def lab_dia(p):   return f"{p['dia']:g} 个地球"
def lab_mass(p):  return f"{p['mass']:g} 个地球"
def lab_grav(p):  return f"称出 {round(p['grav'] * 10)} 斤"
def lab_day(p):   return f"{p['day']} 小时"
def lab_dist(p):  return f"{p['dist']} 百万千米"
def lab_year(p):  return f"{p['year']} 天" if p["year"] < 730 else f"{round(p['year'] / 365.25)} 年"
def lab_temp(p):  return f"{p['temp']}℃"
def lab_moons(p): return f"{p['moons']} 颗"

def rows(keys, field, lab=None):
    """cmp 的一行行数据。温度改用 K 画条长，标签还是摄氏度。"""
    out = []
    for k in keys:
        p = P[k]
        r = {"body": k, "name": p["cn"], "value": p["k"] if field == "temp" else p[field]}
        if lab: r["label"] = lab(p)
        out.append(r)
    return out

def cmps(pid, q, rws, ans, ext, note="", viz="bar", hint="比一比每一条，看谁最长",
         praise="数据看对啦！", base=None):
    """cmp：数据比一比。ext 记下这题考极大还是极小，validate.py 会核对 answer 指向的行确实是
    那一个——数据题最怕题干问「谁最重」、答案标了「最轻」。"""
    st = {"id": pid, "kind": "cmp", "viz": viz, "question": q, "rows": rws,
          "answer": ans, "ext": ext, "hint": hint, "praise": praise}
    if note: st["note"] = note
    if base: st["base"] = base
    return st

def body_quiz(pid, q, opts, ans, hint, praise):
    """选项画天体圆盘：opts = [(bodyKey, 显示名), ...]"""
    return {"id": pid, "kind": "quiz", "question": q,
            "options": [{"body": b, "text": n} for b, n in opts], "answer": ans,
            "hint": hint, "praise": praise}

def body_listen(pid, q, target, opts, ans, hint, praise):
    """找一找的圆盘版：大卡和选项都是天体"""
    return {"id": pid, "kind": "listen", "promptBody": target, "speakText": P[target]["cn"],
            "question": q, "options": [{"body": b, "text": n} for b, n in opts],
            "answer": ans, "hint": hint, "praise": praise}

def rank_order(pid, q, keys, direction="up", field="rank",
               hint="想一想谁排在前面", praise="排好啦！"):
    """按真实数据排序，卡面是天体圆盘 + 名字"""
    return {"id": pid, "kind": "order", "dir": direction, "question": q,
            "items": [{"body": k, "name": P[k]["cn"], "v": P[k][field]} for k in keys],
            "hint": hint, "praise": praise}

def txt_quiz(pid, q, opts, ans, hint, praise):
    return {"id": pid, "kind": "quiz", "question": q,
            "options": [{"text": t} for t in opts], "answer": ans, "hint": hint, "praise": praise}

def astro_count(pid, q, icon, n, opts, unit, bd="night", praise="数对啦！"):
    return {"id": pid, "kind": "count", "question": q, "duckIcon": icon, "count": n,
            "countOptions": opts, "backdrop": bd, "unit": unit, "praise": praise}

def phase_order(pid, q, seq_items, hint, praise):
    """月相排序：items 用 phase 画圆缺，v 是月相进度（0 朔 → 0.25 上弦 → 0.5 望）"""
    return {"id": pid, "kind": "order", "dir": "up", "question": q,
            "items": seq_items, "hint": hint, "praise": praise}

def astro_open(i, body, cn, en, stats, question, size=118):
    """开场卡：body=None 时退回文字大卡（火箭、星星这类没有圆盘造型的）"""
    st = {"id": f"astro-{i}-t", "kind": "letter", "letters": [en], "display": cn,
          "examples": ([{"body": body, "text": f"{cn} {en}", "say": cn}] if body
                       else [{"icon": "rocket", "text": f"{cn} {en}", "say": cn}]),
          "stats": [{"label": a, "value": b} for a, b in stats], "fact": P[body]["fact"] if body else "",
          "question": question}
    if body: st["body"] = body; st["bodySize"] = size
    return st

# 每关：开场卡 + 5 道题（棋盘 8-10 格由 boardify 补金币/事件格）
ASTRO = [
    # 1 太阳系是一家
    (lambda i: [astro_open(i, "sun", "太阳", "Sun",
                           [("直径", "109 个地球"), ("表面", "5505℃"), ("占全家重量", "99.8%")],
                           "学一学：太阳，太阳系唯一会发光的恒星", 150),
                astro_count(f"astro-{i}-c1", "数一数：太阳系一共有几颗大行星？", "planet", 8, [6, 7, 8], "颗"),
                txt_quiz(f"astro-{i}-q1", "太阳会自己发光发热，它在太阳系里是什么身份？",
                         ["恒星", "行星", "卫星"], 0, "只有它自己会发光", "太阳是离我们最近的一颗恒星！"),
                cmps(f"astro-{i}-m1", "比一比：谁是行星里的巨无霸？",
                     rows(["jupiter", "saturn", "earth"], "dia", lab_dia), 0, "max", viz="disc", base=34,
                     note="11 个地球排成一排，才和木星一样宽", hint="看哪个圆盘最大", praise="木星最大！"),
                body_listen(f"astro-{i}-l1", "找一找：哪颗是我们住的地球？", "earth",
                            [("mars", "火星"), ("earth", "地球"), ("mercury", "水星")], 1,
                            "蓝蓝的、上面有海洋", "就是这颗蓝色弹珠！"),
                rank_order(f"astro-{i}-o1", "离太阳从近到远，把这三颗排一排",
                           ["mercury", "earth", "venus"], "up")]),

    # 2 离太阳由近到远
    (lambda i: [astro_open(i, "mercury", "水星", "Mercury",
                           [("离太阳", "58 百万千米"), ("直径", "0.38 个地球"), ("一年", "88 天")],
                           "学一学：水星，离太阳最近的行星"),
                cmps(f"astro-{i}-d1", "谁离太阳最近？",
                     rows(["mercury", "earth", "neptune"], "dist", lab_dist), 0, "min",
                     note="阳光跑到地球要 8 分钟，跑到海王星要 4 个小时",
                     hint="比一比哪一条最短", praise="水星最靠太阳！"),
                rank_order(f"astro-{i}-o1", "从离太阳近的排到远的", ["mars", "jupiter", "saturn"], "up"),
                {"id": f"astro-{i}-n1", "kind": "neighbor", "nums": [3, 0, 5],
                 "question": "行星排队：第 3 颗和第 5 颗之间，藏着第几颗？",
                 "arithOptions": [4, 2, 6], "answer": 0,
                 "hint": "3 的后面是 4，4 的后面是 5", "praise": "第 4 颗，就是火星！"},
                txt_quiz(f"astro-{i}-q1", "太阳路边第八个座位，坐的是哪颗行星？",
                         ["海王星", "天王星", "土星"], 0, "从水星开始一颗一颗数到八",
                         "海王星离太阳最远！"),
                body_listen(f"astro-{i}-l1", "找一找：离太阳第四近的那颗红色行星", "mars",
                            [("venus", "金星"), ("mars", "火星"), ("mercury", "水星")], 1,
                            "第 1 水、第 2 金、第 3 地、第 4 火", "火星，红色的那颗！")]),

    # 3 谁是巨无霸
    (lambda i: [astro_open(i, "jupiter", "木星", "Jupiter",
                           [("直径", "11.2 个地球"), ("能装下", "1300 个地球"), ("卫星", "95 颗")],
                           "学一学：木星，行星里的大哥", 150),
                cmps(f"astro-{i}-s1", "按真实大小比一比：谁的圆盘最大？",
                     rows(["jupiter", "uranus", "earth", "mercury"], "dia", lab_dia), 0, "max",
                     viz="disc", base=30, note="其他七颗行星加起来，都没有木星一个胖",
                     hint="看圆盘，不看名字", praise="木星最大！"),
                txt_quiz(f"astro-{i}-q1", "木星肚子里能装下多少个地球？",
                         ["11 个", "318 个", "1300 个"], 2, "11 是排成一排的个数，装进肚子里要多得多",
                         "1300 个地球才填满木星！"),
                rank_order(f"astro-{i}-o1", "从大到小排一排", ["saturn", "mars", "uranus"], "down", field="dia"),
                memory_step(f"astro-{i}-m1", "翻翻牌：行星和它的绰号配成对", [
                    ("jupiter", {"body": "jupiter"}, None, None, "巨无霸"),
                    ("saturn", {"body": "saturn"}, None, None, "光环王"),
                    ("earth", {"body": "earth"}, None, None, "蓝色弹珠"),
                ]),
                cmps(f"astro-{i}-s2", "卫星最多的行星是谁？",
                     rows(["saturn", "jupiter", "earth"], "moons", lab_moons), 0, "max",
                     note="土星身边围着 146 颗卫星，是全家孩子最多的",
                     hint="数一数哪一条最长", praise="土星是卫星之王！")]),

    # 4 比轻重
    (lambda i: [astro_open(i, "saturn", "土星", "Saturn",
                           [("质量", "95 个地球"), ("直径", "9.45 个地球"), ("一天", "11 小时")],
                           "学一学：土星，戴着光环的轻行星", 150),
                cmps(f"astro-{i}-w1", "比一比谁最重（1 表示一个地球那么重）",
                     rows(["jupiter", "saturn", "earth", "mercury"], "mass", lab_mass), 0, "max",
                     note="木星一个就顶 318 个地球，其他七颗加起来都不到它的一半",
                     hint="条最长的那个最重", praise="木星最重！"),
                txt_quiz(f"astro-{i}-q1", "把土星放进一个超大的浴缸里，它会怎么样？",
                         ["浮在水面上", "沉到缸底", "化成一片云"], 0, "土星平均密度比水还小",
                         "土星轻得能浮在水上！"),
                rank_order(f"astro-{i}-o1", "从轻的排到重的", ["neptune", "uranus", "mars"], "up", field="mass"),
                cmps(f"astro-{i}-w2", "谁比地球还轻？",
                     rows(["mars", "earth", "venus"], "mass", lab_mass), 0, "min",
                     note="火星只有地球的十分之一重", hint="找条最短的那一条", praise="火星最轻！"),
                {"id": f"astro-{i}-p1", "kind": "pattern",
                 "seq": [{"body": "earth"}, {"body": "jupiter"}, {"body": "earth"}],
                 "question": "小行星、大行星轮流排队，下一个是谁？",
                 "options": [{"body": "earth"}, {"body": "jupiter"}, {"body": "mars"}], "answer": 1,
                 "hint": "读一读：地球、木星、地球……", "praise": "轮到木星啦！"}]),

    # 5 称一称：引力
    (lambda i: [astro_open(i, "earth", "地球", "Earth",
                           [("引力", "1（标准）"), ("直径", "12756 千米"), ("卫星", "1 颗")],
                           "学一学：地球，引力的标准秤", 110),
                cmps(f"astro-{i}-g1", "在地球上称 10 斤，去哪个行星称出来最重？",
                     rows(["jupiter", "neptune", "mars"], "grav", lab_grav), 0, "max",
                     note="木星引力是地球的 2.5 倍：10 斤的东西到那儿称出 25 斤",
                     hint="哪一条最长，就称得最重", praise="木星上最沉！"),
                txt_quiz(f"astro-{i}-q1", "你在地球上重 20 斤，到木星上称会是多少斤？",
                         ["8 斤", "20 斤", "50 斤"], 2, "木星的引力是地球的 2.5 倍", "20 斤变 50 斤！"),
                cmps(f"astro-{i}-g2", "去哪颗星球称重最轻？",
                     rows(["moon", "mars", "earth"], "grav", lab_grav), 0, "min",
                     note="月球引力只有地球的六分之一，宇航员一蹦就老高",
                     hint="找称得最轻的那一条", praise="月球上轻得像羽毛！"),
                compare_step(i, "planet", 4, "planet", 4, ["左边多", "右边多", "一样多"],
                             "太阳系 8 颗行星：离太阳近的 4 颗和远的 4 颗，哪边多？"),
                body_listen(f"astro-{i}-l1", "找一找：哪颗卫星一直围着地球转？", "moon",
                            [("pluto", "冥王星"), ("moon", "月球"), ("venus", "金星")], 1,
                            "晚上天上那个会变圆变弯的", "月球是地球唯一的卫星！")]),

    # 6 一天有多长（自转）
    (lambda i: [astro_open(i, "venus", "金星", "Venus",
                           [("一天", "5832 小时"), ("自转", "倒着转"), ("一年", "225 天")],
                           "学一学：金星，一天比一年还长", 130),
                cmps(f"astro-{i}-r1", "比谁的一天最短（自转一圈要多久）",
                     rows(["jupiter", "earth", "venus"], "day", lab_day), 0, "min",
                     note="木星 10 小时就自己转完一圈，是太阳系的陀螺冠军",
                     hint="条越短，一天越短", praise="木星的一天最短！"),
                txt_quiz(f"astro-{i}-q1", "金星的一天比它的一年还长，为什么？",
                         ["它转得太慢了", "它离太阳太远", "它根本没有自转"], 0,
                         "金星自转一圈要 243 个地球日", "金星慢得一天比一年还长！"),
                rank_order(f"astro-{i}-o1", "按一天从短到长排一排",
                           ["saturn", "uranus", "mars"], "up", field="day"),
                cmps(f"astro-{i}-r2", "谁的一天最长？",
                     rows(["mercury", "earth", "jupiter"], "day", lab_day), 0, "max",
                     note="水星要 1408 小时才转一圈，等于地球上的 59 天",
                     hint="找最长的那一条", praise="水星的一天最漫长！"),
                {"id": f"astro-{i}-n1", "kind": "neighbor", "nums": [5, 0, 7],
                 "question": "木星是第 5 颗、天王星是第 7 颗，中间的土星排第几？",
                 "arithOptions": [6, 8, 4], "answer": 0,
                 "hint": "5、？、7，中间那个数", "praise": "土星排第 6！"}]),

    # 7 一年有多长（公转）
    (lambda i: [astro_open(i, "neptune", "海王星", "Neptune",
                           [("离太阳", "4515 百万千米"), ("一年", "165 地球年"), ("风速", "2 千米/秒")],
                           "学一学：海王星，最远的那一颗", 130),
                cmps(f"astro-{i}-y1", "谁过一岁生日要等最久？",
                     rows(["neptune", "earth", "mercury"], "year", lab_year), 0, "max",
                     note="海王星绕一圈要 165 个地球年——从清朝嘉庆年间转到今天",
                     hint="条越长，年越长", praise="海王星的一年最长！"),
                rank_order(f"astro-{i}-o1", "按一年从短到长排一排",
                           ["mars", "jupiter", "venus"], "up", field="year"),
                txt_quiz(f"astro-{i}-q1", "水星上过了 4 个生日，地球上大概过了几年？",
                         ["1 年", "4 年", "16 年"], 0, "水星一年只有 88 天，比地球短得多",
                         "水星 4 年 = 地球 1 年！"),
                cmps(f"astro-{i}-y2", "谁绕太阳跑得最快？",
                     rows(["mercury", "mars", "saturn"], "year", lab_year), 0, "min",
                     note="离太阳越近跑得越快，水星 88 天就绕完一圈",
                     hint="一年最短的就是跑得最快的", praise="水星是短跑冠军！"),
                astro_count(f"astro-{i}-c1", "数一数：有几颗行星的一年超过 10 个地球年？",
                            "planet", 4, [3, 4, 5], "颗",
                            praise="木星、土星、天王星、海王星，四颗都要等十年以上！")]),

    # 8 冷与热
    (lambda i: [astro_open(i, "mars", "火星", "Mars",
                           [("平均温度", "-65℃"), ("直径", "0.53 个地球"), ("一天", "25 小时")],
                           "学一学：火星，红色的沙尘世界", 110),
                cmps(f"astro-{i}-t1", "谁的表面最热？",
                     rows(["venus", "earth", "neptune"], "temp", lab_temp), 0, "max",
                     note="金星 464℃，铅扔进去都会化——它不是离太阳最近的，却是最热的",
                     hint="条最长的那一颗最热", praise="金星最热！"),
                txt_quiz(f"astro-{i}-q1", "离太阳最近的水星，为什么不是最热的？",
                         ["它没有厚云保温", "它转得太慢", "它太小了存不住热"], 0,
                         "金星那层厚云像锅盖，热量跑不掉", "没有厚云，热量全跑啦！"),
                cmps(f"astro-{i}-t2", "谁最冷？",
                     rows(["uranus", "mars", "mercury"], "temp", lab_temp), 0, "min",
                     note="天王星常年 -195℃，水在那儿比石头还硬", hint="条最短的那一颗最冷",
                     praise="天王星最冷！"),
                rank_order(f"astro-{i}-o1", "按温度从高到低排一排",
                           ["earth", "mars", "venus"], "down", field="temp"),
                body_listen(f"astro-{i}-l1", "找一找：温度刚好让水能喝的那颗行星", "earth",
                            [("venus", "金星"), ("earth", "地球"), ("neptune", "海王星")], 1,
                            "不冷不热，刚好有海洋", "只有地球不冷不热！")]),

    # 9 谁戴光环、谁躺着转
    (lambda i: [astro_open(i, "uranus", "天王星", "Uranus",
                           [("自转轴歪", "98 度"), ("直径", "4 个地球"), ("一年", "84 地球年")],
                           "学一学：天王星，躺着打滚的行星", 130),
                body_quiz(f"astro-{i}-q1", "哪颗行星戴着一顶大草帽似的光环？",
                          [("saturn", "土星"), ("jupiter", "木星"), ("mars", "火星")], 0,
                          "光环是冰块和石子组成的", "土星的光环最漂亮！"),
                txt_quiz(f"astro-{i}-q2", "哪颗行星是躺着打滚绕太阳的？",
                         ["天王星", "金星", "水星"], 0, "它的自转轴歪了 98 度", "天王星躺着转！"),
                memory_step(f"astro-{i}-m1", "翻翻牌：行星和它的样子配成对", [
                    ("mars", {"body": "mars"}, None, None, "锈红色的沙"),
                    ("neptune", {"body": "neptune"}, None, None, "深深的海军蓝"),
                    ("jupiter", {"body": "jupiter"}, None, None, "条纹大衣"),
                ]),
                body_quiz(f"astro-{i}-q3", "大红斑在谁的脸上？",
                          [("jupiter", "木星"), ("saturn", "土星"), ("venus", "金星")], 0,
                          "那是一个刮了 300 多年的大风暴", "木星的大红斑！"),
                cmps(f"astro-{i}-w1", "谁的卫星最多？",
                     rows(["saturn", "uranus", "mars"], "moons", lab_moons), 0, "max",
                     note="土星有 146 颗已确认的卫星", hint="比一比条的长短", praise="土星 146 颗！")]),

    # 10 矮行星、彗星和小行星
    (lambda i: [astro_open(i, "pluto", "冥王星", "Pluto",
                           [("直径", "0.19 个地球"), ("一年", "248 地球年"), ("身份", "矮行星")],
                           "学一学：冥王星，被请下牌的矮行星", 96),
                txt_quiz(f"astro-{i}-q1", "2006 年，冥王星为什么被请出了大行星的队伍？",
                         ["它没能清空自己轨道上的碎石", "它太小，望远镜看不见", "它跑出了太阳系"], 0,
                         "行星得能打扫干净自己的轨道", "冥王星成了矮行星！"),
                cmps(f"astro-{i}-s1", "比大小：谁最大？",
                     rows(["earth", "pluto", "moon"], "dia", lab_dia), 0, "max", viz="disc", base=70,
                     note="冥王星比月球还小一圈", hint="看圆盘大小", praise="地球最大！"),
                body_listen(f"astro-{i}-l1", "找一找：拖着长尾巴扫过夜空的是谁？", "comet",
                            [("comet", "彗星"), ("moon", "月球"), ("saturn", "土星")], 0,
                            "冰做的脏雪球，靠近太阳时甩出长尾巴", "彗星的尾巴永远背着太阳！"),
                txt_quiz(f"astro-{i}-q2", "流星是怎么来的？",
                         ["小石头掉进大气层烧起来了", "星星掉下来了", "云里开了灯"], 0,
                         "大气层把小石头烧成一道光", "那是小石头在发光！"),
                astro_count(f"astro-{i}-c1", "数一数：火星和木星之间的小行星带，画出了几颗小石头？",
                            "rock", 6, [5, 6, 7], "颗", bd="grass",
                            praise="真正的小行星多到数不清！")]),

    # 11 月亮为什么会变胖变瘦
    (lambda i: [astro_open(i, "moon", "月球", "Moon",
                           [("月相", "8 种模样"), ("离地球", "38 万千米"), ("引力", "地球的 1/6")],
                           "学一学：月球和它的阴晴圆缺"),
                phase_order(f"astro-{i}-o1", "月亮从新月长到满月，按顺序排一排",
                            [{"phase": 0.25, "name": "上弦月", "v": 0.25},
                             {"phase": 0.0, "name": "新月", "v": 0.0},
                             {"phase": 0.5, "name": "满月", "v": 0.5}],
                            "先剩一条边，再亮一半，最后整个圆", "月相排对啦！"),
                txt_quiz(f"astro-{i}-q1", "月亮自己会发光吗？",
                         ["不会，它反射太阳的光", "会，它是个小太阳", "只有满月时才发光"], 0,
                         "月亮像一面不太亮的镜子", "月亮是借太阳的光！"),
                {"id": f"astro-{i}-p1", "kind": "pattern",
                 "seq": [{"phase": 0.5}, {"phase": 0.0}, {"phase": 0.5}],
                 "question": "满月、新月轮流出现，下一个是哪一轮？",
                 "options": [{"phase": 0.5}, {"phase": 0.0}, {"phase": 0.25}], "answer": 1,
                 "hint": "圆、缺、圆、下一个是……", "praise": "该新月啦！"},
                txt_quiz(f"astro-{i}-q2", "从这次满月到下次满月，大约要隔多久？",
                         ["一个月", "一星期", "一整天"], 0, "月亮绕地球一圈要 27 天多",
                         "差不多一个月，圆一次！"),
                txt_quiz(f"astro-{i}-q3", "海边的涨潮和退潮，是谁在拉海水？",
                         ["月亮的引力", "海风", "太阳照的"], 0, "月亮一拉，海水就鼓起来",
                         "是月亮在拉海水！")]),

    # 12 恒星、星座与银河 + 中国航天
    (lambda i: [astro_open(i, None, "火箭", "Rocket",
                           [("第一颗卫星", "东方红 1 号"), ("飞天第一人", "杨利伟"), ("火星车", "祝融号")],
                           "学一学：火箭，离开地球的车"),
                txt_quiz(f"astro-{i}-q1", "天上的星星和太阳其实是一家人，靠什么分开？",
                         ["远近不同", "颜色不同", "会不会眨眼睛"], 0, "太阳是离我们最近的恒星",
                         "太阳就是一颗恒星！"),
                txt_quiz(f"astro-{i}-q2", "夜里最亮的那颗星就是北极星吗？",
                         ["不是，北极星只负责指正北", "是，它最亮", "它有时候才亮"], 0,
                         "找方向靠它，比亮度它排不进前十", "北极星是用来认方向的！"),
                {"id": f"astro-{i}-o1", "kind": "order", "dir": "up",
                 "question": "按先后排一排：哪件事先发生？",
                 "items": [{"icon": "rocket", "name": "东方红 1 号", "v": 1970},
                           {"icon": "rocket", "name": "神舟飞天", "v": 2003},
                           {"icon": "rocket", "name": "祝融上火星", "v": 2021}],
                 "hint": "先上天，再上人，最后去火星", "praise": "中国航天的三步排对了！"},
                txt_quiz(f"astro-{i}-q3", "中国的火星车叫什么名字？",
                         ["祝融号", "嫦娥号", "天问号"], 0, "祝融是神话里的火神", "祝融号在火星上散步！"),
                body_listen(f"astro-{i}-l1", "找一找：我们是从哪颗行星上发射火箭的？", "earth",
                            [("mars", "火星"), ("earth", "地球"), ("venus", "金星")], 1,
                            "我们住的那颗蓝色行星", "从地球上起飞！")]),
]

ASTRO_TITLES = [
    ("第 1 关 太阳系是一家", "1 颗恒星 + 8 颗行星"),
    ("第 2 关 行星的座位表", "离太阳由近到远"),
    ("第 3 关 谁是巨无霸", "行星比大小"),
    ("第 4 关 比一比轻重", "行星的质量"),
    ("第 5 关 称一称", "引力与体重"),
    ("第 6 关 一天有多长", "行星的自转"),
    ("第 7 关 一年有多长", "行星的公转"),
    ("第 8 关 冷与热", "表面温度"),
    ("第 9 关 谁戴光环", "行星的本事"),
    ("第 10 关 矮行星与彗星", "太阳系的其他住户"),
    ("第 11 关 月亮变胖变瘦", "月相与潮汐"),
    ("第 12 关 离开地球", "恒星、银河与中国航天"),
]

astro_levels = []
for i, build in enumerate(ASTRO):
    steps = build(i)
    assert steps[0]["kind"] == "letter", f"astro-{i} 开场卡必须在第一位"
    astro_levels.append({"id": f"astro-{i}", "title": ASTRO_TITLES[i][0],
                         "subtitle": ASTRO_TITLES[i][1], "steps": steps})
boardify(astro_levels, lambda idx, lv: [])
add_review_levels(astro_levels, "astro", (5, 10))
add_boss_level(astro_levels, "astro")
dedupe_questions(astro_levels)
W("astro_levels.json", {"subject": "astro", "title": "天文台", "guide": "robot", "levels": astro_levels})

# ================= 收集册 7 组 =================
def C(id, name, icon=None, text=None, pinyin=None, fact=None, tag=None, tagColor=None, body=None):
    d = {"id": id, "name": name}
    if body: d["body"] = body          # 天文台：图鉴里画按真实比例的天体圆盘，不用通用图标
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
        C("as-sun","太阳 Sun",body="sun",fact="太阳系 99.8% 的物质都集中在太阳身上。"),
        C("as-mercury","水星 Mercury",body="mercury",fact="离太阳最近，88 天就跑完一圈。"),
        C("as-venus","金星 Venus",body="venus",fact="厚云捂住热量，464℃ 是全家最热的。"),
        C("as-earth","地球 Earth",body="earth",fact="目前唯一找到生命的行星，表面七成是海洋。"),
        C("as-mars","火星 Mars",body="mars",fact="有太阳系最高的火山，比珠穆朗玛峰还高两倍。"),
        C("as-jupiter","木星 Jupiter",body="jupiter",fact="能装下 1300 个地球，大红斑刮了三百多年。"),
        C("as-saturn","土星 Saturn",body="saturn",fact="光环是冰块和石子；它轻得能浮在水上。"),
        C("as-uranus","天王星 Uranus",body="uranus",fact="躺着打滚绕太阳，自转轴歪了 98 度。"),
        C("as-neptune","海王星 Neptune",body="neptune",fact="风最大，一秒能吹两公里。"),
        C("as-moon","月球 Moon",body="moon",fact="自己不发光，你看到的是反射的太阳光。"),
        C("as-pluto","冥王星 Pluto",body="pluto",fact="2006 年被降成矮行星，因为它没清空轨道上的碎石。"),
        C("as-rocket","火箭 Rocket","rocket",fact="先上天、再上人、最后去火星——中国航天的三步。"),
    ]},
    {"id": "badge", "title": "徽章", "icon": "medal", "lockedLabel": "？？？", "items": [
        C("bg-start","初来乍到","home"), C("bg-hanzi10","识字新星","book"), C("bg-math5","思维小达人","equal"),
        C("bg-lab1","实验狂人","flask"), C("bg-py1","拼音小能手","speaker"), C("bg-en1","ABC达人","book"),
        C("bg-astro1","摘星少年","rocket"), C("bg-listen7","磨耳朵七天","speaker"), C("bg-all","全勤之星","star"),
        C("bg-shield","护眼小卫士","shield"), C("bg-chart","进步王","chart"), C("bg-rocket","冲鸭！","rocket"), C("bg-king","全科通","medal"),
    ]},
]}
W("collection.json", collection)

# ================= 金币商店（v0.8 工单08） =================
# 角色 6 款（mario/dino 默认拥有 + 4 款原创小伙伴），骰子皮肤 5 款，定价 40-120。
# 纯个性化，不含任何学习内容（解锁只看星星，ADR-0002 双轨制）。
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
    # 试玩反馈①：骰子皮肤下架，金币改换称号（图标全部复用现有资产，展示在地图铭牌旁）
    "titles": [
        shop_item("xiaoxian", "小小探险家", "flag", 0, True),
        shop_item("shizi", "识字小达人", "book", 40),
        shop_item("pinyin", "拼音小能手", "speaker", 50),
        shop_item("shuxue", "数字小天才", "equal", 60),
        shop_item("tansuo", "勇敢探险家", "rocket", 80),
        shop_item("mingxing", "岛屿大明星", "starface", 120),
    ],
}
W("shop.json", shop)
print("ALL DONE")
