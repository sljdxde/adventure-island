#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · 内联事件处理器闸门（onclick="xxx()" 里的函数必须真的存在）

为什么需要这一闸门：
v0.11「双线合并」删掉了 5 个函数定义，但调用它们的 `onclick=` 还留在 DOM 里。
这类缺陷**渲染时完全正常**（`preview_sweep.py` 0 报警），只有手指真按下去才抛
`ReferenceError`，表现是「按钮点了没反应」：

  wTracePos / wStrokeDone / wReplay  → 写字步骤描不上（98 个写字步骤全哑）
  sudPlace / sudBounce               → 数独点图标填不进格子
  ckHour / ckMin                     → 拨钟按钮全死
  moneyRemove                        → 买东西退不回钱币

`smoke_interactive.py` 能在运行时抓到这些（但它只覆盖四类交互），本闸门是静态补充：
把 index.html 里所有 `on*="name(...)"` 的 name 抽出来，逐个确认页内存在定义。
<1 秒跑完，适合每次改 index.html 后先跑一遍。

判定：名字必须在脚本里出现过定义（`function name`、`const/let/var name =`、
`window.name =`、`name = function`）。找不到即失败，退出码 1。

用法：
    python3 ios/tools/check_handlers.py            # 闸门模式
    python3 ios/tools/check_handlers.py --list     # 顺带列出所有被引用的处理器名
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # ios/
PREVIEW = os.path.join(ROOT, "preview", "index.html")

# onclick="foo(...)" / onchange='foo(...)' / oninput="foo(...)" …
HANDLER_RE = re.compile(r"""\b(on[a-z]+)\s*=\s*(["'])\s*([A-Za-z_$][\w$]*)\s*\(""")

# 定义形态：function foo / const foo= / let foo= / var foo= / window.foo= / foo = function|(
DEF_RES = [
    re.compile(r"\bfunction\s+([A-Za-z_$][\w$]*)"),
    re.compile(r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*="),
    re.compile(r"\bwindow\.([A-Za-z_$][\w$]*)\s*="),
    re.compile(r"(?:^|[;{}\s])([A-Za-z_$][\w$]*)\s*=\s*(?:function\b|\()", re.M),
]

# 语言内建 / 宿主 API：onclick="location.reload()" 之类不可能是本地函数
BUILTINS = {
    "location", "window", "document", "history", "navigator", "parent", "self", "top",
    "alert", "confirm", "prompt", "open", "close", "print", "focus", "blur", "stop",
    "setTimeout", "setInterval", "clearTimeout", "clearInterval", "requestAnimationFrame",
    "parseInt", "parseFloat", "isNaN", "Number", "String", "Boolean", "Array", "Object",
    "JSON", "Math", "Date", "Promise", "encodeURIComponent", "decodeURIComponent",
}


def main():
    ap = argparse.ArgumentParser(description="校验 inline on*= handler 里调用的函数都有定义")
    ap.add_argument("--list", action="store_true", help="列出全部被引用的处理器名")
    ap.add_argument("--file", default=PREVIEW, help="默认 ios/preview/index.html")
    a = ap.parse_args()

    with open(a.file, encoding="utf-8") as f:
        html = f.read()

    defined = set()
    for rx in DEF_RES:
        defined.update(rx.findall(html))

    refs = {}                                    # name -> [行号]
    for m in HANDLER_RE.finditer(html):
        name = m.group(3)
        line = html.count("\n", 0, m.start()) + 1
        refs.setdefault(name, []).append(line)

    missing = {n: ls for n, ls in refs.items() if n not in defined and n not in BUILTINS}

    if a.list:
        print("  引用的处理器：" + ", ".join(sorted(refs)))
    print(f"内联 handler：{len(refs)} 个不同函数名，页面内定义 {len(defined)} 个")
    if missing:
        print("[FAIL] 以下 handler 调用的函数在页面里没有定义（点了会 ReferenceError）：")
        for n, ls in sorted(missing.items()):
            print(f"   {n}  ← 行 {', '.join(map(str, ls))}")
        sys.exit(1)
    print("[PASS] 所有内联 handler 调用的函数都有定义")
    sys.exit(0)


if __name__ == "__main__":
    main()
