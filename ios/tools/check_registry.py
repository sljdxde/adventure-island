#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · 注册表一致性闸门（v0.12.2 新增）

存在理由：`validate.py` 校验「数据形状」，`audit_preview.py` 校验「图文语义」，
`preview_sweep.py` 量「盒模型」—— 三者都不问一句：**渲染器认不认识数据里的这些名字？**
于是 v0.12.1 出现过 28 种动画「全部生效」的虚报，v0.12.2 又发现 8 种题型（57 步 / 57 关）
落进「未知步骤」死面板，三个闸门全绿。

本脚本只做一件事：把散落在各处的**同名清单**互相比对，不一致就非零退出。
  · step.kind  : 数据 ⊆ index.html renderStep 的 case ⊆ CHIP_NAMES
  · anim id    : index.html ANIM_IDS == validate.py ANIM_IDS ⊇ 数据里实际用到的 anim
  · 图标名     : 全部 Resources/*.json 引用的图标 ⊆ 资产清单（validate 此前漏掉 shop.json）
  · 收集册 id  : 组内 item id 唯一（撞 id 会让「点亮一张解锁多张」）

零依赖、不启动浏览器、< 1 秒。放进 check.sh 快档里每轮跑。

用法：python3 ios/tools/check_registry.py
退出码：0 = 一致；1 = 有漂移。
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ios/
REPO = os.path.dirname(ROOT)                                         # 仓库根
RES = os.path.join(ROOT, "AdventureIsland", "Resources")
PREVIEW = os.path.join(ROOT, "preview", "index.html")
VALIDATE = os.path.join(ROOT, "tools", "validate.py")
DESIGN = os.path.join(REPO, "design")

errors, passes = [], []


def ok(msg):
    passes.append(msg)


def err(msg):
    errors.append(msg)


def read_preview_code():
    """去掉注入的 DATA/MAPS 大块，只留手写渲染代码（避免在数据里误匹配）"""
    html = open(PREVIEW, encoding="utf-8").read()
    a = html.find("/* === DATA-BEGIN === */")
    b = html.find("/* === DATA-END === */")
    c = html.find("/* === MAPS-BEGIN === */")
    d = html.find("/* === MAPS-END === */")
    if min(a, b, c, d) < 0:
        sys.exit("index.html 里找不到 DATA/MAPS 段标记，无法安全比对")
    return html[:a] + html[b:d] + html[d:]


def block_after(code, marker, size=4000):
    i = code.find(marker)
    if i < 0:
        return ""
    return code[i:i + size]


def render_step_kinds(code):
    seg = block_after(code, "function renderStep(sub, st){")
    if not seg:
        sys.exit("index.html 里找不到 renderStep")
    # 只取到兜底 return 之前，避免把后续代码里的 case 算进来
    cut = seg.find("这一题还没做好")
    return set(re.findall(r'case "([a-z]+)":', seg[:cut] if cut > 0 else seg))


def chip_names(code):
    m = re.search(r"const CHIP_NAMES\s*=\s*\{(.*?)\};", code, re.S)
    if not m:
        sys.exit("index.html 里找不到 CHIP_NAMES")
    return set(re.findall(r'([a-z]+):"', m.group(1)))


def html_anim_ids(code):
    m = re.search(r"const ANIM_IDS\s*=\s*\[(.*?)\];", code, re.S)
    if not m:
        sys.exit("index.html 里找不到 ANIM_IDS")
    return re.findall(r'"([^"]+)"', m.group(1))


def validate_anim_ids():
    src = open(VALIDATE, encoding="utf-8").read()
    m = re.search(r"^ANIM_IDS\s*=\s*\{(.*?)\}", src, re.S | re.M)
    if not m:
        sys.exit("validate.py 里找不到 ANIM_IDS")
    return re.findall(r'"([^"]+)"', m.group(1))


def collect(node, key=None, out=None):
    """收集 JSON 里出现的图标名与 anim 名"""
    if out is None:
        out = {"icons": set(), "anims": set()}
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, str):
                if k in ("icon", "leftIcon", "rightIcon", "guessIcon", "promptIcon",
                         "targetIcon", "shadow"):
                    out["icons"].add(v)
                elif k == "anim":
                    out["anims"].add(v)
            elif k == "decoys" and isinstance(v, list):
                out["icons"].update(x for x in v if isinstance(x, str))
            elif k == "bins" and isinstance(v, list):
                for b in v:
                    if isinstance(b, dict) and isinstance(b.get("icon"), str):
                        out["icons"].add(b["icon"])
            collect(v, key=k, out=out)
    elif isinstance(node, list):
        for v in node:
            collect(v, out=out)
    return out


def main():
    code = read_preview_code()
    kinds = render_step_kinds(code)
    chips = chip_names(code)

    # ---------- 数据：全部 Resources/*.json（含此前被漏掉的 shop.json） ----------
    docs = {}
    for p in sorted(glob.glob(os.path.join(RES, "*.json"))):
        name = os.path.basename(p)[:-5]
        docs[name] = json.load(open(p, encoding="utf-8"))

    data_kinds, data = set(), {"icons": set(), "anims": set()}
    for name, doc in docs.items():
        acc = collect(doc)
        data["icons"] |= acc["icons"]
        data["anims"] |= acc["anims"]
    for name in docs:
        if not name.endswith("_levels"):
            continue
        for lv in docs[name]["levels"]:
            for st in lv.get("steps") or []:
                if isinstance(st.get("kind"), str):
                    data_kinds.add(st["kind"])

    # ---------- 1. step.kind ----------
    if not kinds:
        err("[kind] 没能从 renderStep 里解析出任何 case")
    missing = sorted(data_kinds - kinds)
    if missing:
        err(f"[kind] 数据里有 {len(missing)} 种题型渲染器没实现：{missing}")
    else:
        ok(f"[kind] 数据 {len(data_kinds)} 种题型渲染器全部实现")

    chip_missing = sorted(data_kinds - chips)
    if chip_missing:
        err(f"[kind] CHIP_NAMES 缺 {len(chip_missing)} 项（棋盘/步骤条会退化成默认名）：{chip_missing}")
    else:
        ok(f"[kind] CHIP_NAMES 覆盖全部 {len(data_kinds)} 种题型")

    # ---------- 2. anim id ----------
    html_anims = html_anim_ids(code)
    val_anims = validate_anim_ids()
    dup = sorted({x for x in html_anims if html_anims.count(x) > 1})
    if dup:
        err(f"[anim] index.html 的 ANIM_IDS 有重复项：{dup}")
    if set(html_anims) != set(val_anims):
        only_h = sorted(set(html_anims) - set(val_anims))
        only_v = sorted(set(val_anims) - set(html_anims))
        err(f"[anim] index.html 与 validate.py 的 ANIM_IDS 不一致：仅 html {only_h}，仅 validate {only_v}")
    else:
        ok(f"[anim] index.html 与 validate.py 的 ANIM_IDS 一致（{len(html_anims)} 个）")

    unused = sorted(data["anims"] - set(html_anims))
    if unused:
        err(f"[anim] 数据里用了 ANIM_IDS 之外的 anim（会静默回退静态卡）：{unused}")
    else:
        ok(f"[anim] 数据用到的 {len(data['anims'])} 个 anim 全部在 ANIM_IDS 内")

    # ---------- 3. 图标 ----------
    manifest_path = os.path.join(DESIGN, "assets", "manifest.json")
    if os.path.exists(manifest_path):
        man = json.load(open(manifest_path, encoding="utf-8"))
        manifest_icons = {os.path.basename(p).replace(".svg", "")
                          for p in man.get("icons", []) + man.get("bg", [])}
        unknown = sorted(data["icons"] - manifest_icons)
        if unknown:
            err(f"[icon] 数据引用了资产清单里没有的图标（两端都会渲染 ❓）：{unknown}")
        else:
            ok(f"[icon] 全部 {len(data['icons'])} 个图标引用都在资产清单内")
    else:
        err(f"[icon] 找不到资产清单 {manifest_path}")

    # ---------- 4. 收集册 id 唯一 ----------
    coll = docs.get("collection")
    if coll:
        dups = []
        for g in coll.get("groups", []):
            ids = [it.get("id") for it in g.get("items", []) if it.get("id")]
            seen, seen_again = set(), set()
            for i in ids:
                (seen_again if i in seen else seen).add(i)
            if seen_again:
                dups.append((g.get("id"), sorted(seen_again)))
        if dups:
            total = sum(len(d[1]) for d in dups)
            err(f"[collection] {len(dups)} 组内共 {total} 个重复 item id（点亮一张会解锁多张）：{dups[:6]}")
        else:
            ok("[collection] 各组 item id 唯一")

    # ---------- 输出 ----------
    for p in passes:
        print("  [PASS]", p)
    for e in errors:
        print("  [FAIL]", e)
    print("-" * 64)
    print(f"结果: {len(passes)} 通过, {len(errors)} 失败")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
