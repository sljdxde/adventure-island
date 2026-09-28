#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
探险岛 · iOS 工程静态验证脚本
在没有 Mac/Xcode 的环境下，对工程做尽可能严格的静态检查：
  1. 内容 JSON 解析与业务规则校验（题目答案正确性等）
  2. 资产一致性：JSON/Swift 引用的图标名 ⊆ Assets.xcassets ⊆ 设计稿清单
  3. Emoji 兜底覆盖：每个资产必须有 Emoji 兜底
  4. iOS 16 兼容性扫描：禁止出现 iOS 17+ 专用 API
  5. Swift 源码基础健康检查（花括号平衡等）
  6. project.yml 关键配置检查
用法：python validate.py   （在 ios/ 目录下）
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ios/
DESIGN = os.path.dirname(ROOT)                                        # 项目根
APP = os.path.join(ROOT, "AdventureIsland")
RES = os.path.join(APP, "Resources")
CATALOG = os.path.join(APP, "Assets.xcassets")

errors, warnings, passes = [], [], []

def ok(msg): passes.append(msg)
def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)

# ---------- 1. 内容 JSON ----------
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

manifest = load_json(os.path.join(DESIGN, "design/assets/manifest.json"))
manifest_icons = {p.split("/")[1].replace(".svg", "") for p in manifest["icons"]} | \
                 {p.split("/")[1].replace(".svg", "") for p in manifest["bg"]}

cn = load_json(os.path.join(RES, "cn_levels.json"))
math = load_json(os.path.join(RES, "math_levels.json"))
exps = load_json(os.path.join(RES, "experiments.json"))
coll = load_json(os.path.join(RES, "collection.json"))

json_icons = set()
def collect_icons(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "icon" and isinstance(v, str): json_icons.add(v)
            if k == "morphFrom" and isinstance(v, str): json_icons.add(v)
            if k == "duckIcon" and isinstance(v, str): json_icons.add(v)
            if k in ("leftIcon", "rightIcon", "guessIcon") and isinstance(v, str): json_icons.add(v)
            collect_icons(v)
    elif isinstance(node, list):
        for v in node: collect_icons(v)

for doc in (cn, math, exps, coll): collect_icons(doc)

def check_subject(doc, name, expect_levels):
    levels = doc["levels"]
    if len(levels) != expect_levels:
        err(f"[{name}] 关卡数 {len(levels)} != {expect_levels}")
    else:
        ok(f"[{name}] {len(levels)} 关")
    ids = [l["id"] for l in levels]
    if len(set(ids)) != len(ids): err(f"[{name}] 关卡 id 重复")
    else: ok(f"[{name}] 关卡 id 唯一")
    for li, lv in enumerate(levels):
        if not lv["steps"]: err(f"[{name}] 第{li+1}关无步骤")
        for st in lv["steps"]:
            kind = st["kind"]
            sid = f"{name}/{st.get('id','?')}"
            if kind == "teach":
                for k in ("char", "pinyin", "morphFrom"):
                    if not st.get(k): err(f"{sid} teach 缺 {k}")
            elif kind == "quiz":
                opts = st.get("options") or []
                if len(opts) != 3: err(f"{sid} 选项数 {len(opts)} != 3")
                ans = st.get("answer")
                if not isinstance(ans, int) or not (0 <= ans < len(opts)):
                    err(f"{sid} answer 非法")
                for o in opts:
                    if not (o.get("icon") or o.get("text")): err(f"{sid} 选项为空")
            elif kind == "count":
                n = st.get("count"); opts = st.get("countOptions") or []
                if not (3 <= (n or 0) <= 10): err(f"{sid} 数量 {n} 超范围")
                if n not in opts: err(f"{sid} 选项不含正确数量 {n}")
            elif kind == "compare":
                keys = {o["key"] for o in st.get("compareOptions") or []}
                if keys != {"left", "right", "same"}: err(f"{sid} 比较选项不完整 {keys}")
                l, r = st.get("leftCount", 0), st.get("rightCount", 0)
                expect = "same" if l == r else ("left" if l > r else "right")
                if st.get("answerKey") != expect:
                    err(f"{sid} 答案 {st.get('answerKey')} 与数量不符（应为 {expect}）")
            else:
                err(f"{sid} 未知步骤类型 {kind}")

check_subject(cn, "cn_levels", 10)
check_subject(math, "math_levels", 10)

for exp in exps["experiments"]:
    if len(exp["items"]) < 3: err(f"[实验 {exp['id']}] 物品少于 3")
    if not any(i["id"] == exp["guessItem"] for i in exp["items"]):
        err(f"[实验 {exp['id']}] guessItem 不在物品列表")
    for it in exp["items"]:
        if not it.get("fact"): err(f"[实验] 物品 {it['id']} 缺 fact")
ok(f"[experiments] {len(exps['experiments'])} 个实验校验完成")

group_ids = [g["id"] for g in coll["groups"]]
if group_ids != ["science", "sticker", "hanzi", "badge"]: err(f"[collection] 分组顺序异常 {group_ids}")
for g in coll["groups"]:
    if len(g["items"]) < 10: warn(f"[collection/{g['id']}] 条目 {len(g['items'])} 偏少")
ok("[collection] 4 个分组校验完成")

# ---------- 2. 资产一致性 ----------
missing = json_icons - manifest_icons
if missing: err(f"JSON 引用了不存在的图标: {sorted(missing)}")
else: ok(f"JSON 引用的 {len(json_icons)} 个图标全部存在于设计资产清单")

cat_icons = {d[:-9] for d in os.listdir(CATALOG) if d.endswith(".imageset")}
if cat_icons != manifest_icons:
    only_cat = cat_icons - manifest_icons
    only_man = manifest_icons - cat_icons
    if only_cat: warn(f"资产目录多出（无害）: {sorted(only_cat)}")
    if only_man: err(f"资产目录缺失: {sorted(only_man)}")
else:
    ok(f"Assets.xcassets 与设计清单完全一致（{len(cat_icons)} 个）")

# ---------- 3. Emoji 兜底覆盖 ----------
common_path = os.path.join(APP, "Common.swift")
src = open(common_path, encoding="utf-8").read()
m = re.search(r"enum IconEmoji \{[^{]*static let map: \[String: String\] = \[(.*?)\]\n\}", src, re.S)
if not m:
    err("未找到 IconEmoji.map 定义")
else:
    fallback = set(re.findall(r'"([a-zA-Z-]+)"\s*:', m.group(1)))
    lack = manifest_icons - fallback
    if lack: err(f"以下图标缺少 Emoji 兜底: {sorted(lack)}")
    else: ok(f"Emoji 兜底覆盖全部 {len(manifest_icons)} 个图标")

# ---------- 4. iOS 16 兼容性扫描 ----------
FORBIDDEN = [
    (r"\.fontDesign\(", "iOS 16.1+ 字体 API（用 .system(design:) 替代）"),
    (r"ContentUnavailableView", "iOS 17+ API"),
    (r"@Observable", "iOS 17+ 宏（应用 ObservableObject）"),
    (r"import\s+SwiftData", "iOS 17+ 框架"),
    (r"scrollTargetBehavior", "iOS 17+ API"),
    (r"sensoryFeedback", "iOS 17+ API"),
    (r"\.onChange\(of:.*\)\s*\{\s*[^\s,]+,\s*", "iOS 17 双参数 onChange 写法"),
    (r"onTapGesture\s*\{\s*\w+ in", "onTapGesture 带位置参数是 iOS 17+（用 SpatialTapGesture）"),
    (r"TipKit|import\s+TipKit", "iOS 17+ 框架"),
]
swift_files = []
for dirpath, _, files in os.walk(APP):
    for f in files:
        if f.endswith(".swift"): swift_files.append(os.path.join(dirpath, f))
tests_dir = os.path.join(ROOT, "Tests/AdventureIslandTests")
for f in os.listdir(tests_dir):
    if f.endswith(".swift"): swift_files.append(os.path.join(tests_dir, f))

api_hits = []
for path in swift_files:
    text = open(path, encoding="utf-8").read()
    for i, line in enumerate(text.splitlines(), 1):
        for pat, why in FORBIDDEN:
            if re.search(pat, line):
                api_hits.append(f"{os.path.relpath(path, ROOT)}:{i}  {why}  →  {line.strip()[:80]}")
if api_hits:
    for h in api_hits: err("兼容性: " + h)
else:
    ok(f"iOS 16 兼容性扫描通过（{len(swift_files)} 个 Swift 文件）")

# ---------- 5. Swift 基础健康 ----------
for path in swift_files:
    text = open(path, encoding="utf-8").read()
    if text.count("{") != text.count("}"):
        err(f"花括号不平衡: {os.path.relpath(path, ROOT)} {{={text.count('{')} }}={text.count('}')}")
    if text.count("(") != text.count(")"):
        warn(f"圆括号数量不等（可能为字符串内符号，请人工确认）: {os.path.relpath(path, ROOT)}")
ok(f"花括号平衡检查完成（{len(swift_files)} 个文件）")

# ---------- 6. project.yml ----------
py = open(os.path.join(ROOT, "project.yml"), encoding="utf-8").read()
for key in ['deploymentTarget', 'iOS: "16.0"', 'TARGETED_DEVICE_FAMILY: "2"',
            'UIRequiresFullScreen: true', 'UIInterfaceOrientationLandscapeLeft',
            'bundle.unit-test', 'AdventureIslandTests']:
    if key not in py: err(f"project.yml 缺少关键配置: {key}")
else_ok = all(key in py for key in ['deploymentTarget', 'iOS: "16.0"', 'TARGETED_DEVICE_FAMILY: "2"',
                                    'UIRequiresFullScreen: true', 'UIInterfaceOrientationLandscapeLeft',
                                    'bundle.unit-test', 'AdventureIslandTests'])
if else_ok: ok("project.yml 关键配置齐全（iPad only / iOS16 / 横屏 / 测试目标）")

# ---------- 汇总 ----------
print("=" * 64)
print("探险岛 iOS 工程静态验证报告")
print("=" * 64)
for p in passes: print("  [PASS]", p)
for w in warnings: print("  [WARN]", w)
for e in errors: print("  [FAIL]", e)
print("-" * 64)
print(f"结果: {len(passes)} 通过, {len(warnings)} 警告, {len(errors)} 失败")
sys.exit(1 if errors else 0)
