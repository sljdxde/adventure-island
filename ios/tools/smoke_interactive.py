#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · 交互冒烟测试（需要「点一下」才暴露的缺陷）

为什么单独有这么一支：
`preview_sweep.py` 只渲染、不点击，所以「点了没反应」这类缺陷它看不见。
v0.11 的「双线合并」把 5 个函数定义整段删掉（调用它的 onclick 还留着），
它们全部只在**手指真的按下去**时才炸 ReferenceError，渲染扫描一路绿灯：

  wTracePos / wStrokeDone / wReplay  → 写字步骤：描不上、演示按钮无反应
                                       （全站 98 个写字步骤：识字 96 + 拼音 2）
  sudPlace / sudBounce               → 图案数独：点图标填不进格子
  ckHour / ckMin                     → 认钟表「拨一拨」：＋时/－时/整点/半点 全死
  moneyRemove                        → 买东西：多付了退不回来

本脚本用 headless Chrome 真派发事件 / 真点按钮，在每一类交互上走完整条通关路径：

  write  逐关：轻点不算写 → 重播演示不报错 → 逐笔描红 → done=true → 过关反馈出现
  clock  拨钟：＋时/－时 往返各一次 → 拖长针定分钟 → 拖短针定小时
         → 「拨好啦 ✓」→ solved=true（v1.0.1 起同时覆盖指针拖拽）
  money  付钱：按面额凑出标价 → 多付一枚 → 点 chip 退掉 → 「确认付钱 ✓」→ solved=true
  sudoku 数独：逐格点空格 → 点调色板图标 → 全部填满 → solved=true

用法：
    python3 ios/tools/smoke_interactive.py                 # 全量（约 2-4 分钟）
    python3 ios/tools/smoke_interactive.py --groups write  # 只测写字
    python3 ios/tools/smoke_interactive.py --limit 5       # 每组只测前 5 个（快查）
    python3 ios/tools/smoke_interactive.py --jobs 1        # 串行跑（排查用）
退出码：有任一项失败为 1。

依赖：本机 Chrome（macOS 默认路径）+ Python 标准库（脚本自己起本地 http 服务）。
对照闸门：`check_registry.py`（清单）/ `validate.py`（结构）/ `audit_preview.py`（语义）
/ `preview_sweep.py`（渲染盒模型）。本脚本补的是「交互」这一档。
"""
import argparse
import concurrent.futures as futures
import http.server
import json
import math
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # ios/
REPO = os.path.dirname(ROOT)                                            # 仓库根
PREVIEW = os.path.join(ROOT, "preview", "index.html")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]

# 页面内公共底座：错误收集 + 等待 + 结果回传（--dump-dom 取 #__wtest）
BASE_JS = r"""
window.__errs=[];
window.addEventListener('error',e=>window.__errs.push(String(e.message)+' @'+(e.lineno||'')+'\n'+(e.error&&e.error.stack||'')));
window.__out={phase:'boot'};
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
function waitFor(fn,ms){ return new Promise((res,rej)=>{ const t0=Date.now();
  (function poll(){ if(fn()) return res(); if(Date.now()-t0>(ms||8000)) return rej(new Error('timeout'));
    setTimeout(poll,20); })(); }); }
function emit(){
  const d=document.createElement('div'); d.id='__wtest'; d.textContent=JSON.stringify(window.__out);
  document.body.appendChild(d);
}
"""

# 写字：逐笔描红
WRITE_JS = BASE_JS + r"""
function XY(svg,x,y){ const r=svg.getBoundingClientRect();
  return {x:r.left+x/100*r.width, y:r.top+y/100*r.height}; }
function fire(svg,type,x,y){
  const p=XY(svg,x,y);
  return svg.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,
    clientX:p.x,clientY:p.y,pointerId:1,pointerType:'touch',isPrimary:true,
    button:0,buttons:type==='pointerup'?0:1}));
}
function drag(svg,pts){
  fire(svg,'pointerdown',pts[0].x,pts[0].y);
  for(let k=1;k<pts.length;k++) fire(svg,'pointermove',pts[k].x,pts[k].y);
  fire(svg,'pointerup',pts[pts.length-1].x,pts[pts.length-1].y);
}
(async function(){
  try{
    await waitFor(()=>!!document.getElementById('wsvg'));
    const svg=document.getElementById('wsvg');
    const n=writeState.sampled.length;
    window.__out.n=n; window.__out.len0=Math.round(writeState.len[0]||0);
    window.__out.doneAtStart=writeState.done;
    /* 轻点一下不该把长笔画算写完 */
    fire(svg,'pointerdown',writeState.sampled[0][0].x,writeState.sampled[0][0].y);
    fire(svg,'pointerup',writeState.sampled[0][0].x,writeState.sampled[0][0].y);
    await sleep(40);
    window.__out.curAfterTap=writeState.cur;
    wReplay(); await sleep(30);                       /* 演示按钮不该抛错 */
    window.__out.doneAfterFirstReplay=writeState.done;
    /* 逐笔描：永远按「当前这一笔」取路径（点、短撇可能已被轻点推进） */
    const prog=[];
    for(let guard=0;guard<n+2&&!writeState.done;guard++){
      const i=writeState.cur; if(i>=n) break;
      drag(svg,writeState.sampled[i]);
      await sleep(70);
      prog.push(writeState.cur);
      if(i===0&&writeState.cur===1){
        const wasDone=writeState.done;
        wReplay(); await sleep(20);
        if(writeState.cur!==1||writeState.done!==wasDone) window.__out.replayClobbered=true;
      }
    }
    window.__out.prog=prog;
    window.__out.doneAfterAll=writeState.done;
    window.__out.inkOffsets=Array.from({length:n},(_,i)=>{
      const el=document.getElementById('wink'+i); return el?el.style.strokeDashoffset:'?';});
    window.__out.fb=((document.getElementById('wfb')||{}).textContent||'').trim();
    await sleep(2200);
    window.__out.stepfb=((document.getElementById('stepfb')||{}).textContent||'').trim();
    window.__out.errs=window.__errs; window.__out.phase='done';
  }catch(err){
    window.__out.phase='fail'; window.__out.err=String(err&&err.stack||err);
    window.__out.errs=window.__errs;
  }
  emit();
})();
"""

# 认钟表「拨一拨」（v1.0.1）：按钮往返 + 真派发指针拖拽，不许直接调函数
CLOCK_JS = BASE_JS + r"""
(async function(){
  try{
    await waitFor(()=>typeof clockSet!=='undefined'&&!!document.getElementById('ckhour'));
    const btns=()=>[...document.querySelectorAll('button')];
    const byText=t=>btns().find(b=>(b.textContent||'').includes(t));
    const th=clockSet.targetH, tm=clockSet.targetM;
    window.__out.target=[th,tm];
    window.__out.h0=clockSet.h; window.__out.m0=clockSet.m;

    /* ① 按钮这条老路径不许坏：＋时 一次、－时 一次，回到原处 */
    const plus=byText('＋ 时'), minus=byText('－ 时');
    if(!plus||!minus) throw new Error('找不到拨小时的按钮');
    plus.click(); await sleep(20); window.__out.hAfterPlus=clockSet.h;
    minus.click(); await sleep(20); window.__out.hAfterMinus=clockSet.h;

    /* ② 拖指针：外圈（半径 40）抓长针定分钟，里圈（半径 18）抓短针定小时 */
    const svg=document.querySelector('#ckface svg');
    if(!svg) throw new Error('找不到钟面 svg');
    const XY=(deg,rad)=>{ const r=svg.getBoundingClientRect(); const a=deg*Math.PI/180;
      return {x:r.left+(50+Math.sin(a)*rad)/100*r.width,
              y:r.top+(50-Math.cos(a)*rad)/100*r.height}; };
    const fire=(type,pt)=>svg.dispatchEvent(new PointerEvent(type,{bubbles:true,cancelable:true,
      clientX:pt.x, clientY:pt.y, pointerId:1, pointerType:'touch', isPrimary:true,
      button:0, buttons:type==='pointerup'?0:1}));
    const dragHand=(rad,from,to)=>{ fire('pointerdown',XY(from,rad));
      for(let k=1;k<=6;k++) fire('pointermove',XY(from+(to-from)*k/6,rad));
      fire('pointerup',XY(to,rad)); };

    dragHand(40,0,tm===0?0:180); await sleep(20);
    window.__out.mAfterDrag=clockSet.m;
    const hDeg=(th%12)*30;
    dragHand(18,0,hDeg); await sleep(20);
    window.__out.hAfterDrag=clockSet.h;

    /* 图形要真的转过去（不是只改了状态）：长针 y2、短针 x2 都要落在目标角度上 */
    const mh=document.querySelector('#ckhandm'), hh=document.querySelector('#ckhandh');
    window.__out.mx2=mh?parseFloat(mh.getAttribute('x2')):null;
    window.__out.my2=mh?parseFloat(mh.getAttribute('y2')):null;
    window.__out.hx2=hh?parseFloat(hh.getAttribute('x2')):null;
    window.__out.current=((document.getElementById('cknow')||{}).textContent||'').trim();

    const ok=byText('拨好啦');
    if(!ok) throw new Error('找不到「拨好啦」');
    ok.click(); await sleep(200);
    window.__out.solved=clockSet.solved;
    window.__out.stepfb=((document.getElementById('stepfb')||{}).textContent||'').trim();
    window.__out.errs=window.__errs; window.__out.phase='done';
  }catch(err){
    window.__out.phase='fail'; window.__out.err=String(err&&err.stack||err);
    window.__out.errs=window.__errs;
  }
  emit();
})();
"""

# 买东西：凑钱 → 多付一枚 → 点 chip 退掉 → 确认
MONEY_JS = BASE_JS + r"""
(async function(){
  try{
    await waitFor(()=>typeof moneyState!=='undefined'&&!!document.querySelector('.coinbtn'));
    const st=window._money.st, price=st.price, dens=st.denominations;
    const coins=()=>[...document.querySelectorAll('.coinbtn')];
    window.__out.price=price; window.__out.dens=dens.map(d=>d.value);
    /* 面额凑出标价（DP，和 moneyAuto 同一套思路，但走真点击） */
    const dp=new Array(price+1).fill(-1); dp[0]=0;
    for(let v=0;v<=price;v++){ if(dp[v]<0) continue;
      dens.forEach((d,i)=>{ const nv=v+d.value; if(nv<=price&&dp[nv]<0) dp[nv]=i; }); }
    const picks=[]; let v=price;
    while(v>0&&dp[v]>=0){ picks.push(dp[v]); v-=dens[dp[v]].value; }
    if(price>0&&!picks.length) throw new Error('面额凑不出标价');
    for(const k of picks){ const b=coins()[k]; if(!b) throw new Error('找不到面额按钮 '+k); b.click(); await sleep(10); }
    window.__out.selPaid=moneyState.sel.length;
    if(!picks.length) throw new Error('没有可点的钱币（price=0）');
    /* 多付一枚 */
    coins()[picks[picks.length-1]].click(); await sleep(10);
    window.__out.selOverpaid=moneyState.sel.length;
    /* 点已选 chip 退掉刚多付的那枚 */
    const chips=[...document.querySelectorAll('.mchip')];
    if(!chips.length) throw new Error('已选钱币没有 ✕ chip');
    chips[chips.length-1].click(); await sleep(10);
    window.__out.selAfterRemove=moneyState.sel.length;
    window.__out.totalAfterRemove=moneyState.sel.reduce((s,k)=>s+dens[k].value,0);
    const ok=[...document.querySelectorAll('button')].find(b=>(b.textContent||'').includes('确认付钱'));
    if(!ok) throw new Error('找不到「确认付钱」');
    ok.click(); await sleep(200);
    window.__out.solved=moneyState.solved;
    window.__out.errs=window.__errs; window.__out.phase='done';
  }catch(err){
    window.__out.phase='fail'; window.__out.err=String(err&&err.stack||err);
    window.__out.errs=window.__errs;
  }
  emit();
})();
"""

# 图案数独：逐格点空格 → 点调色板
SUDOKU_JS = BASE_JS + r"""
(async function(){
  try{
    await waitFor(()=>typeof sudokuState!=='undefined'&&!!document.querySelector('.sud-cell'));
    const Sd=sudokuState, n=Sd.size;
    window.__out.size=n; window.__out.filled=0;
    let emptyCell=null;
    for(let r=0;r<n;r++) for(let c=0;c<n;c++){
      if(Sd.given.includes(r*n+c)) continue;
      const cell=document.getElementById('sd'+r+'_'+c);
      if(!cell) throw new Error('找不到格子 '+r+','+c);
      cell.click(); await sleep(10);
      const picks=[...document.querySelectorAll('.sud-pick')];
      if(!picks.length) throw new Error('点空格没有弹出图标调色板');
      if(emptyCell===null) emptyCell={r,c,palette:picks.length};
      const v=Sd.solution[r][c];
      if(!picks[v]) throw new Error('调色板里没有第 '+v+' 个图标');
      picks[v].click(); await sleep(10);
      if(Sd.grid[r][c]!==v) throw new Error('图标没填进格子 '+r+','+c);
      window.__out.filled++;
    }
    window.__out.firstCell=emptyCell;
    window.__out.solved=Sd.solved;
    await sleep(200);
    window.__out.stepfb=((document.getElementById('stepfb')||{}).textContent||'').trim();
    window.__out.errs=window.__errs; window.__out.phase='done';
  }catch(err){
    window.__out.phase='fail'; window.__out.err=String(err&&err.stack||err);
    window.__out.errs=window.__errs;
  }
  emit();
})();
"""

PAYLOADS = {"write": WRITE_JS, "clock": CLOCK_JS, "money": MONEY_JS, "sudoku": SUDOKU_JS}


def find_chrome():
    for c in CHROME_CANDIDATES:
        if os.path.exists(c):
            return c
    return None


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(directory):
    handler = lambda *a, **k: QuietHandler(*a, directory=directory, **k)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


def load_content():
    with open(PREVIEW, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"const CONTENT = (\{.*?\});\n", html, re.S)
    if not m:
        sys.exit("preview 里找不到 CONTENT")
    return json.loads(m.group(1))


def collect(content, groups, subjects):
    """返回 item 列表；item = {kind, sub, li, si, lid, label}"""
    items = []
    for sub in subjects:
        doc = content.get(sub)
        if not doc or "levels" not in doc:
            continue
        for li, lv in enumerate(doc["levels"]):
            for si, st in enumerate(lv.get("steps") or []):
                k = st.get("kind")
                if k == "write" and "write" in groups:
                    items.append({"kind": "write", "sub": sub, "li": li, "si": si, "lid": lv["id"],
                                  "label": f"「{st.get('char','?')}」{len(st.get('strokes') or [])} 笔"})
                elif k == "clock" and st.get("mode") == "set" and "clock" in groups:
                    items.append({"kind": "clock", "sub": sub, "li": li, "si": si, "lid": lv["id"],
                                  "label": f"拨到 {st.get('hour')}:{st.get('minute')}"})
                elif k == "money" and "money" in groups:
                    items.append({"kind": "money", "sub": sub, "li": li, "si": si, "lid": lv["id"],
                                  "label": f"标价 {st.get('price')} 角"})
                elif k == "sudoku" and "sudoku" in groups:
                    items.append({"kind": "sudoku", "sub": sub, "li": li, "si": si, "lid": lv["id"],
                                  "label": f"数独 {st.get('size','?')}×{st.get('size','?')}"})
    return items


PROBE_SEQ = 0


def run_one(chrome, base, probe_dir, item, budget):
    global PROBE_SEQ
    PROBE_SEQ += 1
    name = f"__smoke_{os.getpid()}_{PROBE_SEQ}.html"
    probe = os.path.join(probe_dir, name)
    with open(PREVIEW, encoding="utf-8") as f:
        html = f.read()
    with open(probe, "w", encoding="utf-8") as f:
        f.write(html.replace("</body>", "<script>" + PAYLOADS[item["kind"]] + "</script></body>"))
    prof = tempfile.mkdtemp(prefix="dsh_smoke_prof_")
    url = f"{base}/{name}?route=level:{item['sub']}:{item['li']}:{item['si']}"
    try:
        dom = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-first-run",
                              "--window-size=1100,780", "--user-data-dir=" + prof,
                              "--dump-dom", "--virtual-time-budget=" + str(budget), url],
                             capture_output=True, timeout=180).stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return {"phase": "timeout"}
    finally:
        try:
            os.remove(probe)
        except OSError:
            pass
        shutil.rmtree(prof, ignore_errors=True)
    m = re.search(r'id="__wtest">(.*?)</div>', dom, re.S)
    if not m:
        return {"phase": "nodom"}
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    try:
        return json.loads(raw)
    except Exception as e:
        return {"phase": "parse:" + str(e)[:40]}


def judge_write(out):
    bad = []
    if out.get("phase") != "done":
        return ["未跑完：" + str(out.get("phase")) + " " + str(out.get("err", ""))[:160]]
    if not out.get("n"):
        bad.append("没解析到笔画")
    if out.get("doneAtStart"):
        bad.append("一进来就已完成")
    # 短笔画（点、短撇：路径 < 32 viewBox 单位）本来就是「点」写成，
    # 轻点落在笔画上算描对是合理手感；长笔画轻点一下却算写完才是缺陷。
    if out.get("curAfterTap"):
        if (out.get("len0") or 0) >= 32:
            bad.append("长笔画轻点一下就推进到第 %s 笔" % out["curAfterTap"])
        elif out["curAfterTap"] > 1:
            bad.append("轻点一下推进了 %s 笔" % out["curAfterTap"])
    if out.get("replayClobbered"):
        bad.append("重播演示把已描进度清了")
    prog = out.get("prog") or []
    expect = (out.get("n") or 0) - (1 if out.get("curAfterTap") else 0)
    if len(prog) != expect:
        bad.append("笔画推进次数 %d 与笔画数 %s 不匹配（prog=%s）" % (len(prog), out.get("n"), prog))
    if not out.get("doneAfterAll"):
        bad.append("全部描完仍 done=false")
    for off in out.get("inkOffsets") or []:
        if off not in ("0", "0px"):
            bad.append("笔迹未填满（dashoffset=%s）" % off)
            break
    return bad


def judge_clock(out):
    bad = []
    if out.get("phase") != "done":
        return ["未跑完：" + str(out.get("phase")) + " " + str(out.get("err", ""))[:160]]
    th, tm = (out.get("target") or [None, None])
    h0 = out.get("h0")
    # 老按钮路径：＋时 要变、－时 要回到原处
    if out.get("hAfterPlus") == h0:
        bad.append("点「＋ 时」小时没变（%s）" % h0)
    if out.get("hAfterMinus") != h0:
        bad.append("点「－ 时」没回到 %s（%s）" % (h0, out.get("hAfterMinus")))
    # 新拖拽路径：状态要到位
    if out.get("mAfterDrag") != tm:
        bad.append("拖长针没把分钟拨到 %s（%s）" % (tm, out.get("mAfterDrag")))
    if out.get("hAfterDrag") != th:
        bad.append("拖短针没把小时拨到 %s（%s）" % (th, out.get("hAfterDrag")))
    # 图形要真的转过去，不能只改状态
    mx2, my2, hx2 = out.get("mx2"), out.get("my2"), out.get("hx2")
    want_my2 = 50 - 34 if tm == 0 else 50 + 34
    if mx2 is None or abs(mx2 - 50) > 1.5:
        bad.append("长针图形没转到 %s 分（x2=%s）" % (tm, mx2))
    if my2 is None or abs(my2 - want_my2) > 1.5:
        bad.append("长针图形没转到 %s 分（y2=%s，期望 %s）" % (tm, my2, want_my2))
    want_hx2 = 50 + math.sin((th % 12) * 30 * math.pi / 180) * 22
    if hx2 is None or abs(hx2 - want_hx2) > 1.5:
        bad.append("短针图形没转到 %s 点（x2=%s，期望 %.1f）" % (th, hx2, want_hx2))
    cur = (out.get("current") or "").strip()
    if cur != "%d:%02d" % (th, tm):
        bad.append("「当前」没跟着变（%r）" % cur)
    if not out.get("solved"):
        bad.append("拖到目标时间后按「拨好啦」没过关（solved=false）")
    return bad


def judge_money(out):
    bad = []
    if out.get("phase") != "done":
        return ["未跑完：" + str(out.get("phase")) + " " + str(out.get("err", ""))[:160]]
    paid = out.get("selPaid") or 0
    if not out.get("selOverpaid") or out["selOverpaid"] != paid + 1:
        bad.append("多付一枚没加上（selOverpaid=%s）" % out.get("selOverpaid"))
    if out.get("selAfterRemove") != paid:
        bad.append("点 ✕ 退不掉钱币（selAfterRemove=%s，期望 %s）" % (out.get("selAfterRemove"), paid))
    if out.get("totalAfterRemove") != out.get("price"):
        bad.append("退款后金额不对：%s，标价 %s" % (out.get("totalAfterRemove"), out.get("price")))
    if not out.get("solved"):
        bad.append("付对钱后按「确认付钱」没过关（solved=false）")
    return bad


def judge_sudoku(out):
    bad = []
    if out.get("phase") != "done":
        return ["未跑完：" + str(out.get("phase")) + " " + str(out.get("err", ""))[:160]]
    first = out.get("firstCell") or {}
    if not first.get("palette"):
        bad.append("点空格没有弹出调色板")
    if not out.get("filled"):
        bad.append("一格都没填上（sudPlace 没起作用）")
    if not out.get("solved"):
        bad.append("按答案填满后 solved=false")
    return bad


JUDGES = {"write": judge_write, "clock": judge_clock, "money": judge_money, "sudoku": judge_sudoku}


def main():
    ap = argparse.ArgumentParser(description="交互冒烟：写字/拨钟/付钱/数独 四类需要点击的步骤逐条走完整条通关路径")
    ap.add_argument("--groups", nargs="*", default=["write", "clock", "money", "sudoku"],
                    choices=["write", "clock", "money", "sudoku"])
    ap.add_argument("--subjects", nargs="*", default=["cn", "pinyin", "math"])
    ap.add_argument("--limit", type=int, default=None, help="每个组只测前 N 项")
    ap.add_argument("--jobs", type=int, default=4, help="并发 Chrome 数（默认 4）")
    ap.add_argument("--budget", type=int, default=22000, help="单个页面虚拟时间预算(ms)")
    ap.add_argument("--show-ok", action="store_true", help="连通过的项也逐条打印")
    a = ap.parse_args()

    chrome = find_chrome()
    if not chrome:
        sys.exit("找不到 Chrome/Chromium；本脚本需要本机浏览器")
    content = load_content()
    items = collect(content, a.groups, a.subjects)
    if not items:
        sys.exit("没找到可测的交互步骤（检查 --groups / --subjects）")
    if a.limit:
        keep, seen = [], {}
        for it in items:
            seen[it["kind"]] = seen.get(it["kind"], 0) + 1
            if seen[it["kind"]] <= a.limit:
                keep.append(it)
        items = keep

    httpd, port = serve(REPO)
    base = f"http://127.0.0.1:{port}/ios/preview"
    probe_dir = os.path.join(ROOT, "preview")
    counts = {}
    for it in items:
        counts[it["kind"]] = counts.get(it["kind"], 0) + 1
    print("交互步骤 %d 个（%s），并发 %d"
          % (len(items), " / ".join(f"{k} {v}" for k, v in counts.items()), a.jobs))
    fails = []
    try:
        with futures.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
            futs = {ex.submit(run_one, chrome, base, probe_dir, it, a.budget): it for it in items}
            for k, fut in enumerate(futures.as_completed(futs), 1):
                out = fut.result()
                item = futs[fut]
                why = JUDGES[item["kind"]](out)
                if out.get("errs") and out.get("phase") == "done":
                    why.append("页面报错：" + str(out["errs"])[:240])
                tag = f"{item['kind']} {item['sub']}/{item['lid']}/step{item['si']} {item['label']}"
                if not why:
                    if a.show_ok:
                        print(f"  [{k}/{len(items)}] PASS {tag}")
                else:
                    fails.append((tag, why))
                    print(f"  [{k}/{len(items)}] FAIL {tag}")
                    for w in why:
                        print("        - " + w)
    finally:
        httpd.shutdown()

    print("=" * 64)
    print(f"扫描 {len(items)} 项交互：通过 {len(items)-len(fails)}，失败 {len(fails)}")
    for tag, why in fails[:40]:
        print(f"  {tag}\n     " + "；".join(why))
    print("=" * 64)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
