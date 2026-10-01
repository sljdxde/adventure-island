#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""内容一致性审计（v0.10 试玩反馈：compare 题左右板换了但标签没换，出现「香蕉画着苹果多」）。

这类错不是样式错而是**教学错**：5 岁的孩子靠图认字认拼音，图文对不上就是教反了。
本脚本把「图 ↔ 词 ↔ 答案」三条链都验一遍，跑一次几秒钟，改完内容必须跑。

用法：
    python3 ios/tools/audit_content.py        # 有 FAIL 时退出码 1
和 validate.py 的分工：validate 管**结构与配额**（格数、占比、字段齐全、id 唯一），
本脚本管**语义**（图标画的是不是那个词、答案是不是题面要的那个）。

要新增图标：在 ICON_CN 里补一行「图标 → 它能画出来的词」，漏了会被判 unknown-icon。
"""
import json, os, re, sys, unicodedata, collections

try:
    from pypinyin import lazy_pinyin, Style
except ImportError:
    sys.exit("需要 pypinyin：python3 -m pip install pypinyin")

RES = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "AdventureIsland", "Resources")
SUBS = ["cn", "math", "pinyin", "english", "astro"]

# 图标 → 这张图能画出来的词（宁可窄，不要宽：图是教学证据）
ICON_CN = {
    "apple":   {"苹果", "果子", "水果"},
    "banana":  {"香蕉", "蕉"},
    "book":    {"书", "课本", "看书", "读书", "故事书"},
    "cake":    {"蛋糕", "生日", "月饼", "点心"},
    "calendar":{"日历", "日子", "今天", "明天", "昨天", "周", "一月", "月份"},
    "castle":  {"城堡", "王宫", "城"},
    "cat":     {"猫", "小猫"},
    "comet":   {"彗星"},
    "crystal": {"水晶", "泉水", "光环", "钻石", "星晶"},
    "duck":    {"鸭", "小鸟", "鸟"},
    "earth":   {"地球", "大地"},
    "bear":    {"熊", "小熊"},
    "fire":    {"火", "火灾"},
    "flame":   {"火", "火焰", "点火", "发烧", "烫"},
    "flower":  {"花", "花朵", "花瓣", "花园", "花木"},
    "fox":     {"狐狸"},
    "gift":    {"礼物", "礼包"},
    "girl":    {"女孩", "妈", "人", "朋友", "你好", "拿苹果"},
    "heart":   {"心", "开心", "爱心", "心跳", "心意"},
    "home":    {"家", "房子", "大门", "回家"},
    "ice":     {"冰", "冰块"},
    "key":     {"钥匙", "锁"},
    "leaf":    {"叶", "树叶", "叶子", "草", "小草", "绿叶"},
    "magnet":  {"磁铁", "吸铁石"},
    "moon":    {"月亮", "月", "夜晚"},
    "mushroom":{"蘑菇", "伞"},
    "panda":   {"熊猫", "猫"},
    "party":   {"聚会", "庆祝", "派对", "人们"},
    "penguin": {"企鹅"},
    "planet":  {"行星", "星球", "火星"},
    "rabbit":  {"兔", "白兔", "兔子"},
    "rainbow": {"彩虹"},
    "robot":   {"机器人", "火星车"},
    "rock":    {"石头", "石"},
    "rocket":  {"火箭", "坐火箭", "飞"},
    "salt":    {"盐"},
    "sand":    {"沙", "沙漠", "海滩"},
    "school":  {"学校", "上学", "大学", "校"},
    "sparkle": {"星星", "闪光", "流星", "亮尾巴"},
    "speaker": {"喇叭", "声音", "开口", "口"},
    "sprout":  {"芽", "苗", "种子", "田里", "草"},
    "bulb":    {"灯", "电灯", "灯泡"},
    "star":    {"星星", "星"},
    "starface":{"星星", "星", "火花"},
    "sugar":   {"糖", "白糖"},
    "candy":   {"糖", "糖果"},
    "sun":     {"太阳", "日", "天", "天空", "阳光"},
    "sunface": {"太阳", "日", "晒"},
    "sunrays": {"阳光", "太阳光", "光芒"},
    "sunrise": {"日出", "早晨", "今天", "日", "太阳"},
    "train":   {"火车", "坐火车", "车"},
    "tree":    {"树", "树木", "森林", "山林", "花木", "木", "鸟巢"},
    "volcano": {"火山", "山", "山坡"},
    "wave":    {"水", "海浪", "波浪", "河"},
    "wood":    {"木", "木头", "木材"},
    "balloon": {"气球"},
    "bush":    {"灌木", "丛"},
    "dino":    {"恐龙"},
    "ferris":  {"摩天轮", "转轮"},
    "jar":     {"罐", "瓶子"},
    "sponge":  {"海绵"},
    "clock":   {"钟", "时钟", "时间"},
    "flag":    {"旗", "红旗"},
    "sand":    {"沙"},
}
# 识字村的「看图找字 / 听音找图」把汉字配成象形图，这一层是造字逻辑不是名词一致，
# 单独立表放行（否则「田 ↔ 日历格子」这类正确象形会被误判）
MORPH_ICON = {"日": {"sunface", "sun", "sunrise"}, "月": {"moon"}, "水": {"wave"}, "山": {"volcano"},
              "木": {"tree", "sprout"}, "人": {"girl"}, "口": {"speaker"}, "天": {"sunrays", "sun"},
              "田": {"calendar"}, "石": {"rock"}, "火": {"flame", "volcano"}, "花": {"flower"},
              "草": {"leaf", "sprout"}, "鸟": {"duck"}}

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
    return any(w and w in h for w in ICON_CN[icon])


def word_initial(text):
    """例词的目标声母：优先取词里标注的拉丁拼音（「山坡 pō」→ p），没有再取第一个汉字的声母"""
    m = LAT.search(text or "")
    if m:
        c = unicodedata.normalize("NFD", m.group(0))[0].lower()
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


def audit():
    fails, warns = [], []
    docs = {}
    for s in SUBS:
        with open(os.path.join(RES, f"{s}_levels.json"), encoding="utf-8") as f:
            docs[s] = json.load(f)
    exp = json.load(open(os.path.join(RES, "experiments.json"), encoding="utf-8"))
    coll = json.load(open(os.path.join(RES, "collection.json"), encoding="utf-8"))

    # —— 规则 1：图 ↔ 词 ——
    unknown = collections.Counter()
    for s in SUBS:
        for lv, st in steps_of(docs[s]):
            for key, o in pairs_of(st):
                if st["kind"] == "listen" and o.get("text") == st.get("prompt"):
                    if o["icon"] not in MORPH_ICON.get(st["prompt"], set()):
                        fails.append(f"象形配图错 [cn/{lv['id']}/{st['id']}]「{st['prompt']}」配了 {o['icon']}")
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
                ok = icon_matches(it["icon"], it["name"])
                if ok is None:
                    unknown[it["icon"]] += 1
                elif not ok:
                    fails.append(f"图文不符 [coll/{g['id']}/{it['id']}] icon={it['icon']} vs 「{it['name']}」")

    # —— 规则 2：拼音例词的声母必须等于本关声母 ——
    for lv, st in steps_of(docs["pinyin"]):
        target = (st.get("letters") or [None])[0]
        if st["kind"] == "letter" and target and target in "bpmfdtnlghk":
            for o in st.get("examples") or []:
                got = word_initial(o.get("text", ""))
                if got and got != target:
                    fails.append(f"声母不符 [pinyin/{lv['id']}/{st['id']}] 本关「{target}」，例词「{o['text']}」是 {got}")

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
