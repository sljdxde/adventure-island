# -*- coding: utf-8 -*-
"""
探险岛 · 图标生成共享基础（绘本手绘风 / 写实风通用）

所有并行图标生成脚本都 `from icon_common import *`，保证：
- 统一的深棕描边 INK、统一的水彩平涂配色
- 统一的 svg() 包装、立式动物模板
- 统一的输出目录与 XML 自检

【绘本手绘风硬性规范 —— 每个图标必须遵守】
1. 所有卡通/物品/框架层图标：深棕描边 INK="#5B4636"（class="st" 约 2.3~2.6px，
   线帽/拐角 round），内部水彩平涂，禁止线性渐变，禁止深色外发光。
2. 造型圆润饱满、略夸张、头大身小；给"会有脸"的东西加圆眼（带白点高光）+ 粉腮红，
   表情友好。风格参考：低幼绘本、贴纸、手绘童书。
3. 64 方形画布（viewBox 0 0 64 64）；立式动物 72×96；横版装饰（bush 等）见特殊清单。
4. 主体占画布 80% 左右、居中、留边，小尺寸（24~48px）也必须一眼可辨。
5. 颜色用下方调色板，饱和柔和、不刺眼；同一对象最多 2~3 个主色 + 描边。
6. 高光是半透明白色椭圆（opacity .45~.9），不是渐变。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(ROOT, "design", "assets", "icons")

# ----------------------------------------------------------------------
# 调色板（绘本水彩平涂）
# ----------------------------------------------------------------------
INK       = "#5B4636"   # 统一深棕描边
RED       = "#E8654F"   # 苹果红
CORAL     = "#F07868"
ORANGE    = "#F2A65A"
AMBER     = "#F5C842"   # 暖黄/金黄
YELLOW    = "#FFD93D"
GREEN     = "#7FC07F"
LEAF      = "#6FB56E"
TEAL      = "#6FC4B8"
BLUE      = "#6FA8D8"
NAVY      = "#4A7FB0"
PURPLE    = "#9B88B8"
PINK      = "#F2A0B0"
BROWN     = "#C08A5A"
DARKBROWN = "#8A5A32"
CREAM     = "#F7F1E3"
PAPER     = "#F7F1E3"
WHITE     = "#FFFFFF"
BLUSH     = "#FF9B8A"

AVB = "0 0 72 96"   # 立式动物画布

# ----------------------------------------------------------------------
# 基础包装
# ----------------------------------------------------------------------
def svg(body, vb=64):
    dims = f"0 0 {vb} {vb}" if isinstance(vb, (int, float)) else vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{dims}">'
            f'{body}</svg>')

def style(stroke=2.4, thin=1.5):
    """返回手绘风 <style>。.st 主描边 / .th 细线（内部纹理）。"""
    return (f'<style>.st{{stroke:{INK};stroke-width:{stroke};stroke-linejoin:round;stroke-linecap:round}}'
            f'.th{{stroke:{INK};stroke-width:{thin};fill:none;stroke-linecap:round;stroke-linejoin:round}}</style>')

# 兼容旧命名
_astyle = lambda: style(2.3, 1.5)

def eyes(x=27, y=26, r=2.9, color="#3A2A20", gap=18):
    cx2 = x + gap
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<circle cx="{cx2}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<circle cx="{x+0.9}" cy="{y-1}" r="{r*0.34}" fill="#fff"/>'
            f'<circle cx="{cx2+0.9}" cy="{y-1}" r="{r*0.34}" fill="#fff"/>')

_eyes = eyes

def blush(y=32, x=20, color=BLUSH):
    return (f'<ellipse cx="{x}" cy="{y}" rx="3.4" ry="2.4" fill="{color}" opacity="0.65"/>'
            f'<ellipse cx="{64-x}" cy="{y}" rx="3.4" ry="2.4" fill="{color}" opacity="0.65"/>')

_blush = blush

def gloss(cx, cy, rx, ry=6, op=0.5):
    """半透明白色高光。"""
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#fff" opacity="{op}"/>'

def animal(body, belly, ears, face, tail="", extra="", head_r=21, feet=None, arms=True):
    """通用立式动物模板（72×96）。"""
    p = [style(2.3, 1.5)]
    if tail: p.append(tail)
    if feet is None:
        p.append(f'<ellipse class="st" cx="25" cy="88" rx="10" ry="5.5" fill="{body}"/>')
        p.append(f'<ellipse class="st" cx="47" cy="88" rx="10" ry="5.5" fill="{body}"/>')
    else:
        p.append(feet)
    p.append(f'<rect class="st" x="19" y="48" width="34" height="34" rx="17" fill="{body}"/>')
    p.append(f'<ellipse cx="36" cy="66" rx="12.5" ry="14" fill="{belly}"/>')
    if arms:
        p.append(f'<ellipse class="st" cx="13" cy="58" rx="7" ry="8.5" fill="{body}"/>')
        p.append(f'<ellipse class="st" cx="59" cy="58" rx="7" ry="8.5" fill="{body}"/>')
    p.append(ears)
    p.append(f'<circle class="st" cx="36" cy="28" r="{head_r}" fill="{body}"/>')
    p.append(extra)
    p.append(face)
    return svg("".join(p), vb=AVB)

_animal = animal

# ----------------------------------------------------------------------
# 输出 + 自检
# ----------------------------------------------------------------------
def emit(icons, group=""):
    """icons: {name: callable()->svg字符串}。写文件并用 XML 解析自检。"""
    import xml.etree.ElementTree as ET
    os.makedirs(OUT, exist_ok=True)
    ok, bad = [], []
    for name, fn in icons.items():
        content = fn()
        try:
            ET.fromstring(content)
        except Exception as e:
            bad.append((name, str(e)))
            continue
        with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
            f.write(content)
        ok.append(name)
    print(f"[{group or 'icons'}] 生成 {len(ok)} 个：", " ".join(sorted(ok)))
    if bad:
        print("  ✗ XML 失败：")
        for n, e in bad:
            print("   ", n, e)
    return ok, bad

# 一个完整范例（苹果），展示手绘物品标准写法
def icon_apple_demo():
    p = [style()]
    p.append(f'<path class="st" d="M32 20 Q15 16 14 33 Q13 49 28 53 Q32 54 36 53 Q51 49 50 33 Q49 16 32 20 Z" fill="{RED}"/>')
    p.append('<path d="M32 19 Q31 14 33 11" stroke="#8A5A32" stroke-width="3" fill="none" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M33 14 Q42 9 44 15 Q37 18 33 14 Z" fill="{GREEN}"/>')
    p.append(gloss(24, 30, 3, 6, 0.5))
    return svg("".join(p))
