#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · HTML 模拟器「渲染质检」全量 sweep（v0.12 起为常驻闸门）

交接文档 v0.12 待办 1 说的浏览器全量审计，此前依赖两个临时脚本
（`__audit_tmp.js` / `__audit_auto.js`）+ 一个 /tmp 收集器，都没入库，随后就丢了。
本脚本把它固化成可复跑的命令行工具：用 headless Chrome 逐关逐题渲染，
在页面里量元素盒模型，收集三类缺陷：

  overflow      元素越出关卡可视区（四向 3px 容差）
  missingIcon   ❓ 兜底图案（图标名在资产清单里不存在）
  textHeavy     同一题 ≥2 个「≥14 字的纯文字选项」（文字堆叠，孩子读不动）
  bounce        关卡没渲染出来（弹回主页 / 白屏）——最严重的一类

用法：
    python3 ios/tools/preview_sweep.py                 # 全量（六科 600 关）
    python3 ios/tools/preview_sweep.py astro english   # 只扫指定学科
    python3 ios/tools/preview_sweep.py --steps 3       # 每关最多扫 3 步（快查）
退出码：发现 bounce 或 overflow 时为 1。

依赖：本机 Chrome（macOS 默认路径）+ 本地 http 服务（脚本自己起，随机端口）。
"""
import argparse
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import http.server
import socketserver

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # ios/
REPO = os.path.dirname(ROOT)                                            # 仓库根
PREVIEW = os.path.join(ROOT, "preview", "index.html")

ALL_SUBJECTS = ["cn", "math", "pinyin", "english", "astro", "geo"]

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# 页面内测量脚本：量 .lv-body / .sticker / .opt 等关键盒子是否越界
MEASURE_JS = r"""
(() => {
  const out = {overflow: [], textHeavy: [], missing: [], blank: false, screen: ''};
  const sc = document.querySelector('.screen');
  out.screen = sc ? sc.className : '';
  if (!sc || sc.className.indexOf('theme-home') >= 0) { out.blank = true; return out; }
  const host = document.querySelector('.lv-body') || document.getElementById('stage');
  if (!host) { out.blank = true; return out; }
  const hb = host.getBoundingClientRect();
  const TOL = 3;
  document.querySelectorAll('.lv-body *, .lv-body').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) return;
    const st = getComputedStyle(el);
    if (st.position === 'fixed' || st.visibility === 'hidden' || st.display === 'none') return;
    if (el.classList.contains('confetti')) return;
    const over = [];
    if (r.left  < hb.left  - TOL) over.push('left');
    if (r.right > hb.right + TOL) over.push('right');
    if (r.top   < hb.top   - TOL) over.push('top');
    if (r.bottom> hb.bottom+ TOL) over.push('bottom');
    if (over.length) {
      out.overflow.push({
        cls: (el.className || el.tagName).toString().slice(0, 60),
        over: over.join(','),
        box: [Math.round(r.left - hb.left), Math.round(r.top - hb.top),
              Math.round(r.width), Math.round(r.height)]
      });
    }
  });
  // ❓ 兜底：图标 onerror 会换成一个 span（含 ❓）
  document.querySelectorAll('.lv-body span, .lv-body div').forEach(el => {
    if (el.children.length === 0 && (el.textContent || '').indexOf('❓') >= 0) {
      out.missing.push((el.className || el.tagName).toString().slice(0, 40));
    }
  });
  // 长文字选项堆叠
  const opts = [...document.querySelectorAll('.opt .bigchar, .opt .slabel, .opt .bigtext')];
  const longTxt = opts.filter(o => (o.textContent || '').trim().length >= 14).length;
  if (longTxt >= 2) out.textHeavy.push({n: longTxt});
  return out;
})()
"""


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(directory):
    port = free_port()
    handler = lambda *a, **k: QuietHandler(*a, directory=directory, **k)
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, port


def load_levels():
    """从 preview 的 CONTENT 段读关卡清单（与真机同源）"""
    with open(PREVIEW, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"const CONTENT = (\{.*?\});\n", html, re.S)
    if not m:
        sys.exit("preview 里找不到 CONTENT")
    return json.loads(m.group(1))


def render(chrome, url, profile, budget=2600):
    """headless 渲染一页，dump DOM 后跑测量脚本并回传 JSON"""
    # Chrome 的 --dump-dom 不执行我们的返回值；用 --headless=new + --virtual-time-budget
    # 并把结果写进 DOM 的一个隐藏节点，再从 dump 里取。
    with open(PREVIEW, encoding="utf-8") as f:
        html = f.read()
    html = html.replace(
        "</body>",
        "<script>setTimeout(function(){var d=document.createElement('div');"
        "d.id='__sweep';d.textContent=JSON.stringify(" + MEASURE_JS + ");"
        "document.body.appendChild(d);},900);</script></body>")
    # probe 放在 preview 目录下，相对资源路径不变
    probe_in_preview = os.path.join(ROOT, "preview", "__sweep_probe.html")
    with open(probe_in_preview, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        dom = subprocess.run(
            [chrome, "--headless", "--disable-gpu", "--user-data-dir=" + profile,
             "--dump-dom", "--virtual-time-budget=" + str(budget), url],
            capture_output=True, timeout=90).stdout.decode("utf-8", "replace")
    finally:
        try:
            os.remove(probe_in_preview)
        except OSError:
            pass
    m = re.search(r'id="__sweep">(.*?)</div>', dom, re.S)
    if not m:
        return {"overflow": [], "textHeavy": [], "missing": [], "blank": True, "screen": "?nodom"}
    raw = (m.group(1)
           .replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    try:
        return json.loads(raw)
    except Exception as e:
        return {"overflow": [], "textHeavy": [], "missing": [], "blank": True,
                "screen": "?parse:" + str(e)[:40]}


def build_parser():
    p = argparse.ArgumentParser(
        description="用 headless Chrome 逐关逐题渲染，量元素盒模型，"
                    "收集 overflow / missingIcon / textHeavy / bounce 缺陷")
    p.add_argument("subjects", nargs="*", default=[],
                   help="只扫指定学科；缺省扫全部：" + " ".join(ALL_SUBJECTS))
    p.add_argument("--steps", type=int, default=None, metavar="N",
                   help="每关最多扫前 N 步（快查）；缺省扫全部步")
    return p


def parse_args(argv):
    """解析命令行；--steps 3 与 --steps=3 等价（argparse 天然支持两种写法）"""
    ns = build_parser().parse_args(argv)
    ns.subjects = ns.subjects or list(ALL_SUBJECTS)
    return ns


def main():
    opts = parse_args(sys.argv[1:])
    subjects = opts.subjects
    max_steps = opts.steps
    chrome = find_chrome()
    if not chrome:
        sys.exit("找不到 Chrome/Chromium；本 sweep 需要本机浏览器")
    content = load_levels()

    httpd, port = serve(REPO)
    base = f"http://127.0.0.1:{port}/ios/preview/__sweep_probe.html?route=level:"
    prof = tempfile.mkdtemp(prefix="dsh_sweep_prof_")

    overflows, blanks, heavy, missing = [], [], [], []
    total = 0
    try:
        for sub in subjects:
            doc = content.get(sub)
            if not doc:
                print(f"[SKIP] 未知学科 {sub}")
                continue
            for i, lv in enumerate(doc["levels"]):
                steps = lv.get("steps") or []
                if max_steps:
                    steps = steps[:max_steps]
                for si in range(len(steps)):
                    total += 1
                    r = render(chrome, f"{base}{sub}:{i}:{si}", prof)
                    tag = f"{sub}/{lv['id']}/{steps[si]['id']}"
                    if r.get("blank"):
                        blanks.append(f"{tag}（screen={r.get('screen')}）")
                        continue
                    for o in r.get("overflow", []):
                        overflows.append(f"{tag} {o['cls']} 越界[{o['over']}] box={o['box']}")
                    if r.get("textHeavy"):
                        heavy.append(f"{tag} 长文字选项 {r['textHeavy'][0]['n']} 个")
                    for mm in r.get("missing", []):
                        missing.append(f"{tag} 图标兜底 {mm}")
    finally:
        httpd.shutdown()
    print("=" * 64)
    for label, rows in (("弹回/白屏", blanks), ("越界", overflows),
                        ("长文字选项", heavy), ("图标缺失", missing)):
        print(f"{label}: {len(rows)}")
        for r in rows[:40]:
            print("   " + r)
    print("=" * 64)
    print(f"扫描 {total} 步；弹回 {len(blanks)}，越界 {len(overflows)}，"
          f"长文字 {len(heavy)}，缺图 {len(missing)}")
    sys.exit(1 if (blanks or overflows) else 0)


if __name__ == "__main__":
    main()
