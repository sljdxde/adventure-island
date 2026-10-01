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

# ================= 语文 15 关（teach + 题型组合轮换） =================
# (字, 拼音, 象形源图标, 词卡, 找一找目标图标, 找一找干扰×2, 找一找答案位)
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

def cn_listen_pic_to_char(i, ch, mfrom):
    """看图找字：目标大卡是象形图片，选项是字"""
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

def build_board(qids, extra, rotate_by):
    """棋盘组装：题目引用轮转起步（相邻关卡体验不同），金币/事件格插在第 2/4/5/6 题之后"""
    qq = qids[rotate_by % len(qids):] + qids[:rotate_by % len(qids)]
    gaps = [2, 4, 5, 6][:len(extra)]
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
    extra = ["coin"] * (2 if i % 2 == 0 else 1) + EVENT_COMBOS[i % 6]
    return build_board(qids, extra, i)

# ================= 试玩反馈②：全学科棋盘化 + 题库扩产 =================
# 病根：非识字学科每关只有 2-4 道静态题且未棋盘化，重玩全是同一道题。
# 药方：每关补 2-4 道同题型不同参数的变体（≥5 道），全部普通关挂 8 格棋盘；
#       count 题加 countRange，客户端每次进题在区间内随机取数。

def target_extras(n_q, idx):
    """普通关补足到 8-10 格：事件 1-2（EVENT_COMBOS 轮换）+ 金币格 1-2（决策 2，至少 1——
    题多的关宁可多一格也不许金币格清零；格数区间与占比由 validate.py 闸门兜底）"""
    combo = EVENT_COMBOS[idx % 6]
    n_coin = max(1, min(2, 8 - n_q - len(combo)))
    return ["coin"] * n_coin + list(combo)

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
        out.append(dict(count_step(i, n2, sorted({max(1, n2 - 2), n2 - 1, n2}), scene),
                        id=f"math-{i}-c2"))
    for s in steps:
        if len(out) >= 3:
            break
        k = s["kind"]
        if k == "compare":
            l2, r2 = s["leftCount"], s["rightCount"]
            if l2 == r2:
                r2 += 1
            out.append(compare_step(i, s["rightIcon"], r2, s["leftIcon"], l2,
                                    [o["label"] for o in s["compareOptions"]], s["question"], sid="cmp2"))
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
            uniq = list(dict.fromkeys(seq2))
            fill = "candy" if uniq[-1] != "candy" else "star"
            out.append(pattern_step(f"math-{i}-x{len(out)}-p", seq2 + [seq2[0]], (uniq + [fill])[:3], 0))
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
    # 通用补位：凑不满 3 道变体时（题型单一的关）——有场景的关补第三道 count（n 递增），否则补 order
    cs = next((s for s in steps if s["kind"] == "count"), None)
    j = 0
    while len(out) < 3:
        if scene is not None:
            n3 = min(10, ((cs["count"] if cs else 3) + 1 + j))
            out.append(dict(count_step(i, n3, sorted({max(1, n3 - 1), n3, min(10, n3 + 1)}), scene),
                            id=f"math-{i}-c{3 + j}"))
            j += 1
        else:
            out.append(order_step(f"math-{i}-x9{j}-o", [2, 5, 3] if j % 2 == 0 else [7, 3, 5], "up"))
            j += 1
    return out

def boardify_math(levels):
    MATH_SCENES = [SC_duck, SC_candy, SC_apple, SC_balloon, SC_star, SC_train,
                   SC_flower, SC_heart, SC_coin, None, None, None, None, None, None]
    boardify(levels, lambda idx, lv: math_extra_steps(idx, lv["steps"], MATH_SCENES[idx]))

def sample_questions(level_steps, count, tag):
    """复习关旧题抽取（工单05）：轮转各关的问题序列交错混排（开盲盒），重编 id 防与原关冲突"""
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
    cn_levels.append({"id": f"cn-{i}", "title": f"第 {i+1} 关 象形字", "subtitle": f"认识「{ch}」",
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
W("cn_levels.json", {"subject": "cn", "title": "识字村", "guide": "panda", "levels": cn_levels})

# ================= 数学 15 关（8 种题型，v0.4） =================
math_levels = []

def count_step(i, n, opts, scene):
    """countRange（试玩反馈②）：客户端每次进题在区间内随机取数+重组选项，重玩不再总是同一道"""
    return {"id": f"math-{i}-c", "kind": "count",
            "question": f"{scene['q']}（点一点，数数看）",
            "duckIcon": scene["icon"], "count": n, "countRange": [max(2, n - 2), n],
            "countOptions": opts,
            "backdrop": scene["backdrop"], "unit": scene["unit"]}

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
W("math_levels.json", {"subject": "math", "title": "思维镇", "guide": "fox", "levels": math_levels})

# ================= 拼音 12 关（letter + 题型组合轮换） =================
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

def py_blend(i, b0, b1, blends):
    return {"id": f"py-{i}-b", "kind": "blend", "parts": [b0, b1],
            "question": f"拼一拼：{b0} — {b1} = ?",
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
            "question": f"拼一拼 {b0} — {b1}：哪张图是「{word}」？",
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
    pinyin_levels.append({"id": f"py-{i}", "title": f"第 {i+1} 关 声母", "subtitle": f"认识「{letter}」", "steps": steps})
# 韵母关 + 复习关
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
            "question": f"拼一拼：{b0} — {v} = ?",
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
            "question": f"再拼一拼 {b0} — {b1}：哪张图是「{word}」？",
            "options": opts, "answer": ans,
            "hint": f"{b0} 碰 {b1}", "praise": f"拼读小能手：{word}！"}

def py_extras(i, lv):
    first = lv["steps"][0]
    if first["kind"] != "letter":          # 复习关（py-11）：补拼读与整体认读变体
        return [
            {"id": "py-11-lb", "kind": "blend", "parts": ["m", "a"],
             "question": "拼一拼：m — a = ?", "options": [{"text": t} for t in ["ma", "mo", "ba"]], "answer": 0,
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
    combo = li % 4
    if combo == 0:      # A：找字母 + 找图
        steps += [en_listen_letter(li, disp), en_pic_quiz(li, disp, icon, word)]
    elif combo == 1:    # B：大小写配对 + 找字母
        steps += [en_case_quiz(li, disp), en_listen_letter(li, disp)]
    elif combo == 2:    # C：找字母 + 图标规律
        steps += [en_listen_letter(li, disp), en_pattern(li, icon)]
    else:               # D：找图 + 大小写配对
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

def en_extras(i, lv):
    first = lv["steps"][0]
    if first["kind"] != "letter":          # en-10 / en-11 单词复习关
        return [word_quiz("en-x0", "Which one is the flower? 花是哪一个？",
                          [("tree","tree"),("flower","flower"),("leaf","leaf")], 1, "Flower 花", "Yes! Flower!"),
                word_quiz("en-x1", "Which one is the cake? 蛋糕是哪一个？",
                          [("gift","gift"),("key","key"),("cake","cake")], 2, "Cake 蛋糕", "Yes! Cake!")]
    idx = 10 if i == 8 else (11 if i == 9 else i)
    disp, icon, word = EN_LETTERS[idx]
    return [en_listen_letter2(i, disp), en_case_quiz2(i, disp), en_pic_quiz2(i, disp, icon, word)]

boardify(english_levels, en_extras)
add_review_levels(english_levels, "english", (5, 11))
add_boss_level(english_levels, "english")
W("english_levels.json", {"subject": "english", "title": "英语王国", "guide": "robot", "levels": english_levels})

# ================= 天文台 10 关（letter + 题型组合轮换） =================
ASTRO_FULL = [
    # (名, 英, 图标, 例词, 冷知识, 干扰1, 干扰2, 特征问题)
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
    if combo == 0:      # A：找一找（直接找图标）
        quiz_opts = [{"icon": d1}, {"icon": d2}]
        ans = (i + 1) % 3
        quiz_opts.insert(ans, {"icon": icon, "text": name})
        steps.append({"id": f"astro-{i}-q", "kind": "quiz",
                      "question": f"找一找：哪个是{name}？",
                      "options": quiz_opts, "answer": ans,
                      "hint": fact, "praise": f"对啦！{fact}"})
    elif combo == 1:    # B：特征配对（听特征找图）
        quiz_opts = [{"icon": d1}, {"icon": d2}]
        ans = (i + 2) % 3
        quiz_opts.insert(ans, {"icon": icon, "text": name})
        steps.append({"id": f"astro-{i}-f", "kind": "quiz",
                      "question": feat_q,
                      "options": quiz_opts, "answer": ans,
                      "hint": fact, "praise": f"对啦！{fact}"})
    else:               # C：星空规律
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
# 试玩反馈②：天文台题库扩产（单题关 → 5 题）+ 全部普通关棋盘化
def astro_quiz2(i, name, icon, d1, d2, q, tag, fact):
    opts = [{"icon": d2}, {"icon": d1}]
    ans = (i + 1) % 3
    opts.insert(ans, {"icon": icon, "text": name})
    return {"id": f"astro-{i}-{tag}", "kind": "quiz", "question": q,
            "options": opts, "answer": ans, "hint": fact, "praise": f"对啦！{fact}"}

def astro_extras(i, lv):
    first = lv["steps"][0]
    if first["kind"] != "letter":          # astro-9 星空大挑战
        return [{"id": "astro-9-q4", "kind": "quiz", "question": "谁晚上出来，有时圆有时弯？",
                 "options": [{"icon": "sun"}, {"icon": "moon", "text": "月亮"}, {"icon": "rocket"}], "answer": 1,
                 "hint": "弯弯的像小船", "praise": "月亮答对啦！"}]
    name, en, icon, chips, fact, d1, d2, feat_q = ASTRO_FULL[i]
    return [
        astro_quiz2(i, name, icon, d2, d1, f"再找一找：哪个是{name}？", "q2", fact),
        astro_quiz2(i, name, icon, d1, d2, feat_q, "f2", fact),
        {"id": f"astro-{i}-p2", "kind": "pattern",
         "seq": [icon, d1, icon], "question": "星空规律：下一个是谁？",
         "options": [{"icon": d1}, {"icon": icon}, {"icon": d2}], "answer": 1,
         "hint": "谁在轮流出现？", "praise": "规律找对啦！"},
        {"id": f"astro-{i}-q3", "kind": "quiz", "question": f"「{fact}」说的是谁？",
         "options": [{"icon": d1}, {"icon": icon, "text": name}, {"icon": d2}], "answer": 1,
         "hint": "想一想刚才学的话", "praise": f"对，就是{name}！"},
    ]

boardify(astro_levels, astro_extras)
add_review_levels(astro_levels, "astro", (5, 10))
add_boss_level(astro_levels, "astro")
W("astro_levels.json", {"subject": "astro", "title": "天文台", "guide": "robot", "levels": astro_levels})

# ================= 收集册 7 组 =================
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
