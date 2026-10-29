# -*- coding: utf-8 -*-
"""
探险岛 · Shard A：自然植物 + 学科背景 + 装饰 图标重绘（纯 SVG 手绘绘本风）
产出：16 个普通图标（design/assets/icons/<name>.svg）+ 2 张背景山丘（design/assets/bg/）
依赖 icon_common.py；不改 gen_icons.py。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_common import *

SAND = "#F2D28A"   # 沙堆专用浅沙色（平涂）

# ======================================================================
# 普通图标（64 方形；bush 为 96×56 横版）
# ======================================================================

# ---- 灌木丛（横版 96×56）----
def icon_bush():
    p = [style(2.2, 1.4)]
    p.append(f'<circle cx="26" cy="40" r="15" fill="{LEAF}"/>')
    p.append(f'<circle cx="70" cy="41" r="14" fill="{LEAF}"/>')
    p.append(f'<circle class="st" cx="48" cy="35" r="19" fill="{GREEN}"/>')
    # 点缀小花
    p.append(f'<circle class="st" cx="30" cy="27" r="4" fill="{PINK}"/>')
    p.append(f'<circle cx="30" cy="27" r="1.8" fill="{YELLOW}"/>')
    p.append(f'<circle class="st" cx="67" cy="29" r="4" fill="{CORAL}"/>')
    p.append(f'<circle cx="67" cy="29" r="1.8" fill="{YELLOW}"/>')
    p.append(gloss(40, 26, 5, 3, 0.5))
    return svg("".join(p), vb="0 0 96 56")

# ---- 笑脸小花 ----
def icon_flower():
    p = [style()]
    p.append(f'<path d="M32 36 L32 55" stroke="{GREEN}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M32 47 Q22 45 20 37 Q30 38 32 45 Z" fill="{LEAF}"/>')
    petals = [(32, 15), (42.5, 22.6), (38.5, 34.9), (25.5, 34.9), (21.5, 22.6)]
    for (px, py) in petals:
        p.append(f'<circle class="st" cx="{px}" cy="{py}" r="8" fill="{PINK}"/>')
    p.append(f'<circle class="st" cx="32" cy="26" r="9" fill="{YELLOW}"/>')
    p.append('<circle cx="29" cy="25" r="1.3" fill="#3A2A20"/><circle cx="35" cy="25" r="1.3" fill="#3A2A20"/>')
    p.append('<path class="th" d="M29.5 29 Q32 31 34.5 29"/>')
    p.append(gloss(29, 21, 2, 2.5, 0.6))
    return svg("".join(p))

# ---- 一片绿叶 ----
def icon_leaf():
    p = [style()]
    p.append(f'<path class="st" d="M32 8 Q52 20 49 40 Q46 55 32 57 Q18 55 15 40 Q12 20 32 8 Z" fill="{LEAF}"/>')
    p.append('<path class="th" d="M32 15 L32 52"/>')
    p.append('<path class="th" d="M32 26 L23 23 M32 35 L41 32 M32 44 L24 41"/>')
    p.append(gloss(23, 20, 4, 2.5, 0.5))
    return svg("".join(p))

# ---- 枫叶 ----
def icon_maple():
    p = [style()]
    p.append(f'<path class="st" d="M32 7 L36 15 L45 11 L43 20 L53 22 L45 29 L49 37 L38 35 L36 46 L32 41 L28 46 L26 35 L15 37 L19 29 L11 22 L21 20 L19 11 L28 15 Z" fill="{ORANGE}"/>')
    p.append(f'<path d="M32 43 L32 56" stroke="{DARKBROWN}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    p.append(gloss(26, 18, 3, 4, 0.4))
    return svg("".join(p))

# ---- 红白点蘑菇 ----
def icon_mushroom():
    p = [style()]
    p.append(f'<rect class="st" x="25" y="35" width="14" height="18" rx="6" fill="{CREAM}"/>')
    p.append(f'<path class="st" d="M10 37 Q10 11 32 11 Q54 11 54 37 Q54 40 50 40 L14 40 Q10 40 10 37 Z" fill="{RED}"/>')
    p.append('<ellipse cx="32" cy="19" rx="5" ry="6" fill="#fff"/>')
    p.append('<ellipse cx="19" cy="30" rx="3.5" ry="4" fill="#fff"/>')
    p.append('<ellipse cx="45" cy="29" rx="3.5" ry="4" fill="#fff"/>')
    p.append('<circle cx="29" cy="43" r="1.3" fill="#3A2A20"/><circle cx="35" cy="43" r="1.3" fill="#3A2A20"/>')
    p.append('<path class="th" d="M29.5 46 Q32 48 34.5 46"/>')
    p.append(gloss(24, 20, 3, 5, 0.45))
    return svg("".join(p))

# ---- 棕榈树 ----
def icon_palm():
    p = [style()]
    p.append(f'<path class="st" d="M29 56 Q29 38 33 23 L37 24 Q34 39 35 56 Z" fill="{BROWN}"/>')
    p.append(f'<path class="st" d="M35 23 Q20 10 10 17 Q24 12 34 24 Z" fill="{LEAF}"/>')
    p.append(f'<path class="st" d="M35 23 Q50 9 56 18 Q45 12 35 24 Z" fill="{LEAF}"/>')
    p.append(f'<path class="st" d="M35 22 Q30 5 44 7 Q36 9 36 22 Z" fill="{GREEN}"/>')
    p.append(f'<circle class="st" cx="32" cy="26" r="2.6" fill="{DARKBROWN}"/>')
    p.append(f'<circle class="st" cx="38" cy="27" r="2.6" fill="{DARKBROWN}"/>')
    p.append(f'<path d="M8 57 Q32 51 56 57" stroke="{AMBER}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    return svg("".join(p))

# ---- 土中嫩芽 ----
def icon_sprout():
    p = [style()]
    p.append(f'<ellipse class="st" cx="32" cy="54" rx="16" ry="6" fill="{BROWN}"/>')
    p.append(f'<path d="M32 52 Q32 42 32 33" stroke="{GREEN}" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M32 35 Q15 33 13 18 Q28 18 32 32 Z" fill="{GREEN}"/>')
    p.append(f'<path class="st" d="M32 30 Q47 28 49 14 Q35 14 32 27 Z" fill="{LEAF}"/>')
    p.append(gloss(20, 22, 3, 2, 0.5))
    return svg("".join(p))

# ---- 圆头果树（带小果）----
def icon_tree():
    p = [style()]
    p.append(f'<rect class="st" x="28" y="38" width="8" height="18" rx="3" fill="{BROWN}"/>')
    p.append(f'<circle cx="21" cy="31" r="9.5" fill="{LEAF}"/>')
    p.append(f'<circle cx="43" cy="31" r="9.5" fill="{LEAF}"/>')
    p.append(f'<circle class="st" cx="32" cy="23" r="15" fill="{GREEN}"/>')
    p.append(f'<circle class="st" cx="26" cy="22" r="2.8" fill="{RED}"/>')
    p.append(f'<circle class="st" cx="39" cy="19" r="2.8" fill="{RED}"/>')
    p.append(f'<circle class="st" cx="36" cy="31" r="2.8" fill="{RED}"/>')
    p.append(gloss(25, 16, 3, 4, 0.5))
    return svg("".join(p))

# ---- 一截带年轮的木头 ----
def icon_wood():
    p = [style()]
    p.append(f'<rect class="st" x="10" y="22" width="38" height="22" rx="10" fill="{BROWN}"/>')
    p.append('<path class="th" d="M15 30 Q25 28 33 30"/><path class="th" d="M17 38 Q27 40 35 38"/>')
    p.append(f'<ellipse class="st" cx="46" cy="33" rx="8" ry="11" fill="{CREAM}"/>')
    p.append(f'<ellipse cx="46" cy="33" rx="4" ry="6" fill="none" stroke="{DARKBROWN}" stroke-width="1.6"/>')
    p.append(gloss(20, 26, 4, 2.5, 0.5))
    return svg("".join(p))

# ---- 可爱火苗 ----
def icon_fire():
    p = [style()]
    p.append(f'<path class="st" d="M32 5 Q46 19 46 34 Q46 50 32 56 Q18 50 18 34 Q18 23 24 15 Q24 25 30 27 Q28 13 32 5 Z" fill="{ORANGE}"/>')
    p.append(f'<path class="st" d="M32 26 Q39 32 39 40 Q39 49 32 52 Q25 49 25 40 Q25 32 32 26 Z" fill="{YELLOW}"/>')
    p.append('<circle cx="29.5" cy="39" r="1.2" fill="#3A2A20"/><circle cx="34.5" cy="39" r="1.2" fill="#3A2A20"/>')
    p.append('<path class="th" d="M29.5 42.5 Q32 44.5 34.5 42.5"/>')
    p.append(gloss(24, 22, 2.5, 4, 0.4))
    return svg("".join(p))

# ---- 沙堆 / 沙堡 ----
def icon_sand():
    p = [style()]
    p.append(f'<path class="st" d="M8 52 Q20 30 32 30 Q44 30 56 52 Z" fill="{SAND}"/>')
    p.append(f'<circle cx="24" cy="44" r="1.6" fill="{DARKBROWN}"/><circle cx="37" cy="47" r="1.6" fill="{DARKBROWN}"/><circle cx="30" cy="38" r="1.4" fill="{DARKBROWN}"/>')
    p.append(f'<path d="M32 30 L32 16" stroke="{DARKBROWN}" stroke-width="2.5" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M32 16 L41 19 L32 23 Z" fill="{RED}"/>')
    p.append(gloss(18, 44, 4, 2, 0.5))
    return svg("".join(p))

# ======================================================================
# 5 个学科小标识（拼图片 + 金色圆底 + 学科符号）
# ======================================================================
_PZ_L = 'M21 5 L32 22 L26 26 L15 9 Z'
_PZ_R = 'M43 5 L32 22 L38 26 L49 9 Z'

def icon_bg_geo():
    p = [style(2.2, 1.4)]
    p.append(f'<path class="st" d="{_PZ_L}" fill="{BLUE}"/>')
    p.append(f'<path class="st" d="{_PZ_R}" fill="{GREEN}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="14" fill="{AMBER}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="7.5" fill="{TEAL}"/>')
    p.append('<path class="th" d="M32 31.5 L32 46.5 M24.5 39 L39.5 39"/>')
    p.append(gloss(29, 35, 2, 3, 0.5))
    return svg("".join(p))

def icon_bg_mul():
    p = [style(2.2, 1.4)]
    p.append(f'<path class="st" d="{_PZ_L}" fill="{CORAL}"/>')
    p.append(f'<path class="st" d="{_PZ_R}" fill="{LEAF}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="14" fill="{AMBER}"/>')
    p.append('<path d="M26 33 L38 45 M38 33 L26 45" stroke="#8A5B20" stroke-width="3.6" stroke-linecap="round"/>')
    p.append(gloss(27, 33, 2.5, 2, 0.45))
    return svg("".join(p))

def icon_bg_sudoku():
    p = [style(2.2, 1.4)]
    p.append(f'<path class="st" d="{_PZ_L}" fill="{PURPLE}"/>')
    p.append(f'<path class="st" d="{_PZ_R}" fill="{BLUE}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="14" fill="{AMBER}"/>')
    p.append('<rect x="25" y="32" width="14" height="14" rx="1.5" fill="#fff" stroke="#8A5B20" stroke-width="1.8"/>')
    p.append('<path d="M32 32 L32 46 M25 39 L39 39" stroke="#8A5B20" stroke-width="1.4"/>')
    return svg("".join(p))

def icon_bg_words50():
    p = [style(2.2, 1.4)]
    p.append(f'<path class="st" d="{_PZ_L}" fill="{PINK}"/>')
    p.append(f'<path class="st" d="{_PZ_R}" fill="{CORAL}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="14" fill="{AMBER}"/>')
    p.append(f'<path class="st" d="M25 33 Q29 31 32 33 Q35 31 39 33 L39 45 Q35 43 32 45 Q29 43 25 45 Z" fill="{BLUE}"/>')
    p.append('<path class="th" d="M32 33 L32 45"/>')
    return svg("".join(p))

def icon_bg_writer():
    p = [style(2.2, 1.4)]
    p.append(f'<path class="st" d="{_PZ_L}" fill="{CORAL}"/>')
    p.append(f'<path class="st" d="{_PZ_R}" fill="{BLUE}"/>')
    p.append(f'<circle class="st" cx="32" cy="39" r="14" fill="{AMBER}"/>')
    p.append(f'<path class="st" d="M27 45 L36 32 L39 35 L30 48 Z" fill="{PINK}"/>')
    p.append(f'<path d="M36 32 L38.5 29.5 L41 32 L39 35 Z" fill="{INK}"/>')
    return svg("".join(p))


# ======================================================================
# 16 图标注册
# ======================================================================
ICONS = {
    "bush": icon_bush,
    "flower": icon_flower,
    "leaf": icon_leaf,
    "maple": icon_maple,
    "mushroom": icon_mushroom,
    "palm": icon_palm,
    "sprout": icon_sprout,
    "tree": icon_tree,
    "wood": icon_wood,
    "fire": icon_fire,
    "sand": icon_sand,
    "bg-geo": icon_bg_geo,
    "bg-mul": icon_bg_mul,
    "bg-sudoku": icon_bg_sudoku,
    "bg-words50": icon_bg_words50,
    "bg-writer": icon_bg_writer,
}

# ======================================================================
# 2 张背景山丘（保持原 viewBox；手绘深棕描边 + 柔和绿平涂，无渐变）
# ======================================================================
def _tree_dot(x, base, s):
    return (f'<rect x="{x-4*s:.1f}" y="{base-16*s:.1f}" width="{8*s:.1f}" height="{18*s:.1f}" rx="{3*s:.1f}" fill="{DARKBROWN}"/>'
            f'<circle cx="{x:.1f}" cy="{base-22*s:.1f}" r="{15*s:.1f}" fill="{GREEN}" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>')

def hills_back_svg():
    b = []
    b.append('<path d="M0 300 L0 205 Q200 155 400 195 Q600 232 800 192 Q1000 155 1200 200 L1200 300 Z" fill="#A9E08C"/>')
    b.append('<path d="M0 205 Q200 155 400 195 Q600 232 800 192 Q1000 155 1200 200" fill="none" stroke="#5B4636" stroke-width="5" stroke-linecap="round"/>')
    b.append(_tree_dot(250, 200, 0.9))
    b.append(_tree_dot(960, 196, 0.8))
    # 小云
    b.append('<g fill="#ffffff" opacity="0.85"><ellipse cx="150" cy="70" rx="30" ry="15"/><circle cx="125" cy="66" r="14"/><circle cx="178" cy="64" r="12"/></g>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300">'
            + "".join(b) + '</svg>')

def hills_front_svg():
    b = []
    b.append('<path d="M0 250 L0 150 Q180 108 360 143 Q560 180 740 138 Q940 102 1200 148 L1200 250 Z" fill="#6FBE5A"/>')
    b.append('<path d="M0 150 Q180 108 360 143 Q560 180 740 138 Q940 102 1200 148" fill="none" stroke="#5B4636" stroke-width="5" stroke-linecap="round"/>')
    # 坡上小灌木
    for cx, cy, r in [(180, 150, 16), (520, 156, 14), (880, 148, 16)]:
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#8AD06B" stroke="{INK}" stroke-width="3.5"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="250" viewBox="0 0 1200 250">'
            + "".join(b) + '</svg>')


def write_backgrounds():
    import xml.etree.ElementTree as ET
    bg_dir = os.path.join(ROOT, "design", "assets", "bg")
    jobs = [("hills-back.svg", hills_back_svg()), ("hills-front.svg", hills_front_svg())]
    bad = []
    for name, content in jobs:
        try:
            ET.fromstring(content)
        except Exception as e:
            bad.append((name, str(e)))
            continue
        with open(os.path.join(bg_dir, name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  背景写入 {name}")
    if bad:
        print("  ✗ 背景 XML 失败：", bad)
    return bad


if __name__ == "__main__":
    ok, bad = emit(ICONS, "nature")
    print("--- 背景山丘 ---")
    bg_bad = write_backgrounds()
    total_bad = len(bad) + len(bg_bad)
    print(f"=== 完成：图标 {len(ok)} 个 + 背景 2 张；XML 失败总数 = {total_bad} ===")
