#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · 品牌展示字子集生成（v0.10 视觉专项 档 A / A1 字体）

产出（全部落到 design/assets/fonts/，随离线包一起分发）：
  zcool-qingke-huangyou-subset.woff2   标题 / 学科名 / 答案数字用的站酷庆科黄油体
  fredoka-500-subset.woff2             数字与拉丁 · 中粗
  fredoka-600-subset.woff2             数字与拉丁 · 半粗
  fredoka-700-subset.woff2             数字与拉丁 · 粗体

为什么要子集化：黄油体全量 TTF 8.3MB（Google Fonts 全量 woff2 也有 ~2MB），
离线 zip 首屏不可接受；而 App 要能在飞行模式下用 file:// 打开就跑，所以字体必须
下载一次 → 抽子集 → vendoring 到仓库，绝不能用 Google Fonts CDN。

需要哪些字：只收「展示字作用域」的字形 ——
  1) 内容 JSON 的 title / subtitle / subject / name（自动从 Resources/*.json 抽）
  2) UI 固定文案（下面手写的 UI_LABELS）
缺字不会崩：CSS font stack 兜到 PingFang SC，只是那一格换系统字。

────────── 怎么重新生成 ──────────
    python3 ios/tools/gen_font_subset.py            # 在项目根或任意目录都行
可选：
    python3 ios/tools/gen_font_subset.py --fontsrc /path/to/ttf   # 指定源 TTF 目录
    python3 ios/tools/gen_font_subset.py --offline               # 缓存已存在时禁止联网

源 TTF 缓存查找顺序：--fontsrc → $AI_FONTSRC → ios/tools/.fontsrc/ → /tmp 缓存 → 联网下载。
默认缓存在 /tmp（8.3MB 的第三方全量 TTF 不该进 git，也不该进离线 zip）。

⚠️ 加了新 UI 文案就要加到 UI_LABELS：本脚本的 UI_LABELS 是「UI 固定文案」的唯一清单，
   新写的按钮/标题/toast 若不在这里，子集就缺字（表现为标题掉回苹方）。
   改完 iOS/SwiftUI 或 index.html 的 chrome 文案后，重跑本脚本即可（幂等，可反复执行）。
"""
import argparse
import json
import os
import re
import sys
import urllib.request

try:
    import fontTools.subset          # noqa: F401
    from fontTools.subset import main as subset_main
    from fontTools.ttLib import TTFont
except ImportError:
    sys.exit("需要 fontTools（pip install fonttools brotli）")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 项目根
RES = os.path.join(ROOT, "ios", "AdventureIsland", "Resources")
OUT_DIR = os.path.join(ROOT, "design", "assets", "fonts")
BUDGET_BYTES = 350 * 1024            # spec 硬约束：全部 woff2 合计 ≤ 350KB

# ----------------------------------------------------------------------------------
# 1. 源字体：Google Fonts 官方分发（OFL-1.1）
#    注意 UA：必须用一个「不声明支持 woff2」的朴素 UA，Google 才会回全量 .ttf；
#    完整 Chrome UA 会回 92 个 woff2 unicode-range 切片（切片没法用来再子集化）。
# ----------------------------------------------------------------------------------
CSS_URL = ("https://fonts.googleapis.com/css2?"
           "family=ZCOOL+QingKe+HuangYou&family=Fredoka:wght@500;600;700&display=swap")
UA = "Mozilla/5.0"
# 源文件名 → (css2 family, weight)
SOURCES = {
    "zcool-qingke-huangyou-400.ttf": ("ZCOOL QingKe HuangYou", "400"),
    "fredoka-500.ttf": ("Fredoka", "500"),
    "fredoka-600.ttf": ("Fredoka", "600"),
    "fredoka-700.ttf": ("Fredoka", "700"),
}

# ----------------------------------------------------------------------------------
# 2. UI 固定文案（展示字作用域）—— 抄自 ios/preview/index.html 的 chrome 字面量
#    与 design/07-board-monopoly.html 的新棋盘标签；只读、绝不改写那两个文件。
#    分组仅为可读性，脚本按字符去重。
# ----------------------------------------------------------------------------------
UI_LABELS = [
    # 应用名 / 首页 / HUD / 返回
    "探险岛 儿童学习大冒险 我在探险岛 点水管开始闯关吧 返回地图 首页 返回 关闭 退出 名字 "
    "连续 天 每日任务 今日任务全部完成 明天见 六个学科任玩三个就达标啦 幸运蘑菇 下次答错不掉心",
    # 棋盘格名（v0.10 大富翁式环形赛道：design/07 的 .nm 标签）
    "题目 金币 宝箱 蘑菇 休息 起点 终点 回城堡 城堡 掷骰子 前进 掷到几就走几格 答对题目 加 步 "
    "金币格 问号砖 开宝箱 到城堡啦 点 走 幸运蘑菇到手 已经有一朵幸运蘑菇啦 大壳壳兽 打败大壳壳兽啦 "
    "挑战 奖励 这次不掉心 被撞飞啦 星星和金币都还在 再挑战一次吧 再来一次 再玩一次",
    # 结算 / 仪式 / 关卡
    "本关完成 一次没错 完美通关 答错了 次也没关系 你已经学会啦 星星和金币都收好啦 你是学科小勇士 "
    "第 关 关卡进度 项已点亮 下一关 跳过 返回地图 本关结束后 让眼睛休息一下哦 格 个 字 张 词 次 分钟",
    # 六个学科名 + 学科副标
    "识字村 象形字 认读 思维镇 数感 加减法 科学岛 动手做实验 拼音谷 声母 拼读 英语王国 单词 天文台 太阳 月亮 星星",
    # 分区标题（收集册 / 商店 / 衣橱 / 家长中心）
    "收集册 商店 金币商店 小伙伴 称号 衣橱 已拥有 未获得 使用中 换上 去商店 已戴好 "
    "已经拥有啦 金币不够 还差 枚 买到 啦 换上啦 马上生效",
    # 题型小标签 CHIP_NAMES + 题面动词
    "认一认 学一学 找一找 练一练 数一数 比一比 拼一拼 算一算 找规律 分一分 排一排 填一填 翻翻牌 掷骰子 "
    "下一步 开始 继续 未知步骤 答对啦 答错了也没关系 再想一想哦 已数 再数一数 一个对着一个 比一比 碰韵母 再试一次 "
    "指着图一个一个数 划掉的不算哦 规律找对啦 读一读前面几个 找找谁在轮流出现 一共 分对啦 数一数两边合起来 "
    "排队排好啦 想一想顺序哦 填对啦 看看两边的数字 已配对 全部配对成功 点骰子 掷一掷 数一数红点有几个 再数一数红点点",
    # 科学实验（浮与沉）
    "科学实验室 浮与沉 实验 向导闪闪 工具箱 点选物品 再点水箱放进去 猜一猜 浮起来 沉下去 现象图鉴 还没有发现 "
    "已测试 已收进图鉴 收进图鉴 重新实验 虚拟实验室随便玩 真的做实验时 一定要请爸爸妈妈陪哦 动手做 看现象 测过 "
    "猜想已记录 把物品放进水箱验证吧 先完成猜一猜哦 先在左边工具箱里选一个物品哦 浮起来了 沉下去了 点我看小知识 "
    "猜对啦 加一颗智慧星 没关系 科学家就是靠不断试错发现规律的 图鉴 获得 贴纸 小侦探",
    # 引导卡 / 识字卡文案
    "想听读音可以点小喇叭哦 不出声也可以 是怎么变来的 图片变成了什么字 看一看 读一读 认识新朋友啦 看卡片 例词 本关字母 词卡 朗读",
    # 衣橱与收集册提示
    "在商店买到的小伙伴和称号 就会生效 出现在棋盘起点和结算仪式里 称号展示在地图左上角的名字旁边 "
    "去科学岛做实验 就能点亮更多现象图鉴 完成每日任务 闯关成功都能掉落贴纸 在识字村闯关 就能点亮更多汉字卡 "
    "在拼音谷闯关 就能点亮拼音卡 在英语王国闯关 就能点亮单词卡 去天文台闯关 认识更多星空朋友 "
    "徽章记录每一次了不起的坚持 每一枚徽章都是了不起的坚持 通关星星奖励 完美通关奖励 旧版 实验奖励 收集奖励 商店消费 "
    "已完成 个现象 已获得 张 已认读 已学会 个 已认识 星空朋友",
    # 家长中心 / 护眼与休息
    "家长中心 这里是大人的设置区 请完成验证 孩子答不出来的小算术 答案 进入 提示 会随题目刷新 设置已保存 "
    "家长验证通过 答案不对哦 再试试 已重置全部学习进度 孩子数据仅保存在本机 不上传云端 今日使用时长 今日完成 "
    "语文 数学 科学实验 还可玩 今日时长已用完 超时会自动进入 小眼睛休息 画面 休息结束再继续 演示 休息遮罩 "
    "当日结束 护眼与时长管理 单次使用时长 每日使用上限 休息间隔提醒 学习进度 累计金币 汉字 贴纸 拼音 单词 星空 "
    "难度与内容管理 难度模式 简单 自动适配 标准 跳过某个知识点 重置全部进度 金币收支明细 按来源 只读 累计获得 累计消费 当前余额 "
    "本产品承诺 家长可放心 无广告 无推送 无外链 无内购 无付费陷阱 无社交 无陌生人接触 数据只存在这台 上 "
    "进入家长区需通过家长门 超时自动提醒休息眼睛 今天的探险结束啦 小眼睛休息一下 明天再来玩 有新关卡等你哦 "
    "想继续 可调 看看窗外最远的地方 秒就回来 休息完毕 继续探险 咕咚咕咚 喝水休息一下 休息一下 幸运蘑菇挡了一下 这次不算错 "
    "今天的金币领过啦 明天再来 蹦蹦 出发喽 我在探险岛",
    # 拉丁与数字（UI 直接显示的字母词：GO/END/NEW/Lv/Boss/ABC + 进度分数）
    "GO END NEW Lv Boss ABC iOS iPad HTML",
    # 与当前 index.html chrome 字面量二次核对后补进来的零散字（别删，删了就缺字）
    "每天玩一小会儿 养成好习惯 哎呀 被撞飞啦 找规律 下一个是哪个 又 浮起来 沉下去 啦 "
    "跳过知识点功能将在二期提供 小恐龙 保留 纯装饰 传送已撤除 跳关 破坏学习节奏 进度只靠玩关卡推进",
]

# 展示字里会用到的中日标点 / 符号（黄油体全都有字形；U+00B7「·」黄油体没有，脚本会报缺字）
CJK_PUNCT = "，。、；：？！「」『』（）《》…—～·%×÷‘’“”"
LATIN_PUNCT = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`" \
              "abcdefghijklmnopqrstuvwxyz{|}~×÷·–—‘’“”•…"

# ----------------------------------------------------------------------------------
# 3. 从内容 JSON 抽「展示字作用域」的汉字
# ----------------------------------------------------------------------------------
def is_cjk(ch):
    o = ord(ch)
    return 0x3400 <= o <= 0x9fff or 0xf900 <= o <= 0xfaff


DISPLAY_KEYS = {"title", "subtitle", "name", "subject"}
SKIP_KEYS = {"steps", "board", "options", "cards", "pips"}   # 正文/题干不是展示字作用域


def collect_display_strings(node, out):
    """递归收集 title/subject/name/subtitle 字面量（跳过题干、选项等正文域）。"""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            if isinstance(v, str):
                if k in DISPLAY_KEYS:
                    out.append(v)
            else:
                collect_display_strings(v, out)
    elif isinstance(node, list):
        for x in node:
            collect_display_strings(x, out)


def json_scope_chars():
    """返回 (CJK 字符集合, 拉丁字符集合, 每文件统计)。"""
    cjk, latin = set(), set()
    stats = []
    for fn in sorted(os.listdir(RES)):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(RES, fn), encoding="utf-8") as f:
            doc = json.load(f)
        strings = []
        collect_display_strings(doc, strings)
        got = {c for s in strings for c in s if is_cjk(c)}
        got_latin = {c for s in strings for c in s if c.isascii() and c.isalpha()}
        cjk |= got
        latin |= got_latin
        stats.append((fn, len(strings), len(got)))
    return cjk, latin, stats


def labels_chars():
    text = "".join(UI_LABELS)
    cjk = {c for c in text if is_cjk(c)}
    latin = {c for c in text if (c.isascii() and (c.isalnum() or c in " ·"))}
    latin |= {c for c in text if c in "+/"}
    return cjk, latin


# ----------------------------------------------------------------------------------
# 4. 源 TTF：缓存查找 / 下载
# ----------------------------------------------------------------------------------
def _ssl_context():
    """macOS 上 python.org 的框架常缺根证书：有 certifi 就用，没有就退回默认。"""
    try:
        import ssl
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


def _fetch(url):
    ctx = _ssl_context()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        if ctx is None:
            return urllib.request.urlopen(req, timeout=120).read()
        return urllib.request.urlopen(req, timeout=120, context=ctx).read()
    except Exception:
        # 最后兜底：curl（多数机器有；本仓库其他构建步骤也走 curl）
        import subprocess
        r = subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", "180", url],
                           capture_output=True)
        if r.returncode != 0 or not r.stdout:
            raise RuntimeError(f"下载失败：{url}\n{r.stderr.decode('utf-8', 'replace')[:200]}")
        return r.stdout


def find_sources(prefer, offline):
    candidates = []
    if prefer:
        candidates.append(prefer)
    env = os.environ.get("AI_FONTSRC")
    if env:
        candidates.append(env)
    candidates += [os.path.join(ROOT, "ios", "tools", ".fontsrc"),
                   os.path.join("/tmp", "adventure-island-fontsrc")]
    for d in candidates:
        if d and all(os.path.isfile(os.path.join(d, f)) for f in SOURCES):
            return d
    if offline:
        sys.exit("源 TTF 缓存不存在，且指定了 --offline（先不带该参数跑一次）")
    cache = os.path.join("/tmp", "adventure-island-fontsrc")
    os.makedirs(cache, exist_ok=True)
    print(f"下载源 TTF（Google Fonts 全量）→ {cache}")
    css = _fetch(CSS_URL).decode("utf-8")
    urls = {}
    for block in re.findall(r"@font-face \{(.*?)\}", css, re.S):
        fam = re.search(r"font-family: '([^']+)'", block)
        w = re.search(r"font-weight: (\d+)", block)
        url = re.search(r"url\(([^)]+)\)", block)
        if fam and w and url:
            urls[(fam.group(1), w.group(1))] = url.group(1)
    for fname, (fam, w) in SOURCES.items():
        key = (fam, w)
        if key not in urls:
            sys.exit(f"CSS 里没找到 {key}；UA 需为朴素 UA（否则 Google 只给 woff2 切片）")
        dst = os.path.join(cache, fname)
        if not os.path.isfile(dst) or os.path.getsize(dst) == 0:
            with open(dst + ".tmp", "wb") as f:
                f.write(_fetch(urls[key]))
            os.replace(dst + ".tmp", dst)
        print(f"  {fname}: {os.path.getsize(dst):,} B")
    return cache


def verify_source(path):
    with TTFont(path, lazy=True) as f:
        cmap = f.getBestCmap()
        return f["maxp"].numGlyphs, set(cmap.keys())


# ----------------------------------------------------------------------------------
# 5. 子集化
# ----------------------------------------------------------------------------------
def uni_arg(chars):
    return ",".join("U+%04X" % ord(c) for c in sorted(chars))


def run_subset(src, dst, chars, extra=()):
    argv = [src,
            "--unicodes=" + uni_arg(set(chars) | set(extra)),
            "--flavor=woff2",
            "--layout-features=*",
            "--no-hinting",
            "--output-file=" + dst + ".tmp"]
    subset_main(argv)
    os.replace(dst + ".tmp", dst)          # 原子替换，重跑安全


def missing_glyphs(src_cmap_cps, requested):
    return "".join(sorted(c for c in requested if ord(c) not in src_cmap_cps))


def main():
    ap = argparse.ArgumentParser(description="生成探险岛品牌展示字子集（woff2）")
    ap.add_argument("--fontsrc", help="源 TTF 目录（默认自动查找，缺失则下载到 /tmp 缓存）")
    ap.add_argument("--offline", action="store_true", help="只用缓存，不联网")
    args = ap.parse_args()

    json_cjk, json_latin, stats = json_scope_chars()
    lab_cjk, lab_latin = labels_chars()
    print("内容 JSON 展示域（title/subtitle/subject/name）：")
    for fn, n_str, n_cjk in stats:
        print(f"  {fn:24s} {n_str:4d} 条展示文案 → {n_cjk:4d} 个不同汉字")
    print(f"  合计去重：{len(json_cjk)} 个汉字；UI_LABELS 另加 {len(lab_cjk - json_cjk)} 个 → {len(json_cjk | lab_cjk)} 个")

    zcool_chars = (json_cjk | lab_cjk | set(CJK_PUNCT) | json_latin | lab_latin
                   | set("0123456789") | set("+/"))
    fredoka_chars = {c for c in LATIN_PUNCT} | json_latin | lab_latin

    src_dir = find_sources(args.fontsrc, args.offline)
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = [
        ("zcool-qingke-huangyou-subset.woff2", "zcool-qingke-huangyou-400.ttf", zcool_chars, ()),
        ("fredoka-700-subset.woff2", "fredoka-700.ttf", fredoka_chars, ()),
        ("fredoka-600-subset.woff2", "fredoka-600.ttf", fredoka_chars, ()),
        ("fredoka-500-subset.woff2", "fredoka-500.ttf", fredoka_chars, ()),
    ]

    rows, total = [], 0
    for out_name, src_name, chars, extra in jobs:
        src = os.path.join(src_dir, src_name)
        _src_glyphs, cps = verify_source(src)
        miss = missing_glyphs(cps, chars)
        if miss:
            print(f"  ! {src_name} 源字体本身缺 {len(miss)} 个字形（子集不含，CSS 兜底）：{miss[:60]}")
        dst = os.path.join(OUT_DIR, out_name)
        run_subset(src, dst, chars - set(miss), extra)
        with TTFont(dst, lazy=True) as f:
            got = f["maxp"].numGlyphs
        size = os.path.getsize(dst)
        total += size
        rows.append((out_name, size, got, len(chars) - len(miss)))

    print("\n" + "-" * 78)
    print(f"{'文件':40s}{'字节':>12s}{'字形':>8s}{'请求码位':>10s}")
    for name, size, glyphs, requested in rows:
        print(f"{name:40s}{size:>12,d}{glyphs:>8,d}{requested:>10,d}")
    print("-" * 78)
    print(f"{'TOTAL':40s}{total:>12,d}")
    print(f"预算 {BUDGET_BYTES:,} B → 用了 {total * 100.0 / BUDGET_BYTES:.1f}%")
    print(f"输出目录：{OUT_DIR}")
    if total > BUDGET_BYTES:
        print("超预算！收窄 UI_LABELS 或删掉非展示域字符后重跑。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
