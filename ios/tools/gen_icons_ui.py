# -*- coding: utf-8 -*-
"""
探险岛 · Shard C：形状 + 符号 + UI + 人物 共 28 个图标（绘本手绘风，纯 SVG）。

与 food/animal 图标同语言：深棕描边 INK、水彩平涂（禁 linearGradient）、
圆润饱满、半透明白色高光 gloss()。全部 64×64。
运行：python3 gen_icons_ui.py  →  emit() 内置 XML 自检，失败数必须为 0。
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_common import *

# ----------------------------------------------------------------------
# 形状（给孩子认形状：规整几何、柔和填色、深棕描边、轻高光）
# ----------------------------------------------------------------------
def icon_circle():
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="20" fill="{GREEN}"/>')
    p.append(gloss(25, 24, 5, 3.5, 0.5))
    return svg("".join(p))

def icon_square():
    p = [style()]
    p.append(f'<rect class="st" x="14" y="14" width="36" height="36" rx="9" fill="{BLUE}"/>')
    p.append(gloss(24, 23, 5, 3.5, 0.5))
    return svg("".join(p))

def icon_triangle():
    p = [style()]
    p.append(f'<polygon class="st" points="32,14 52,48 12,48" fill="{CORAL}"/>')
    p.append(gloss(26, 26, 4.5, 3, 0.5))
    return svg("".join(p))

def icon_pentagon():
    p = [style()]
    p.append(f'<polygon class="st" points="32,12 52,26 45,50 19,50 12,26" fill="{PURPLE}"/>')
    p.append(gloss(25, 24, 4.5, 3, 0.5))
    return svg("".join(p))

# ----------------------------------------------------------------------
# 符号 / UI
# ----------------------------------------------------------------------
def icon_equal():
    p = [style()]
    p.append(f'<rect class="st" x="12" y="22" width="40" height="8" rx="4" fill="{BLUE}"/>')
    p.append(f'<rect class="st" x="12" y="35" width="40" height="8" rx="4" fill="{BLUE}"/>')
    return svg("".join(p))

def icon_slider():
    p = [style()]
    # 上轨（蓝）
    p.append(f'<rect class="st" x="10" y="20" width="44" height="7" rx="3.5" fill="{CREAM}"/>')
    p.append(f'<rect x="11.5" y="21.5" width="22" height="4" rx="2" fill="{BLUE}"/>')
    p.append(f'<circle class="st" cx="34" cy="23.5" r="7" fill="{WHITE}"/>')
    # 下轨（珊瑚）
    p.append(f'<rect class="st" x="10" y="38" width="44" height="7" rx="3.5" fill="{CREAM}"/>')
    p.append(f'<rect x="11.5" y="39.5" width="30" height="4" rx="2" fill="{CORAL}"/>')
    p.append(f'<circle class="st" cx="42" cy="41.5" r="7" fill="{WHITE}"/>')
    return svg("".join(p))

def icon_back():
    p = [style()]
    p.append(f'<path d="M41 14 L23 32 L41 50" fill="none" stroke="{ORANGE}" '
              f'stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg("".join(p))

def icon_blocklock():
    p = [style()]
    p.append(f'<rect class="st" x="7" y="7" width="50" height="50" rx="11" fill="{CREAM}"/>')
    for cx, cy in [(14, 14), (50, 14), (14, 50), (50, 50)]:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="{BROWN}"/>')
    p.append(f'<path d="M25 33 L25 28 Q25 21.5 32 21.5 Q39 21.5 39 28 L39 33" '
             f'fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<rect class="st" x="23" y="32" width="18" height="14" rx="4" fill="{BROWN}"/>')
    p.append(f'<circle cx="32" cy="38" r="2.2" fill="{INK}"/>'
             f'<rect x="30.8" y="39" width="2.4" height="5.5" rx="1.2" fill="{INK}"/>')
    return svg("".join(p))

def icon_blockok():
    p = [style()]
    p.append(f'<rect class="st" x="7" y="7" width="50" height="50" rx="11" fill="{GREEN}"/>')
    for cx, cy in [(14, 14), (50, 14), (14, 50), (50, 50)]:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="2.4" fill="{WHITE}" opacity="0.85"/>')
    p.append(f'<path d="M21 33 L29 41 L44 24" stroke="{WHITE}" stroke-width="6" '
             f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(gloss(18, 15, 5, 3, 0.5))
    return svg("".join(p))

def icon_chart():
    p = [style()]
    p.append(f'<rect class="st" x="9" y="34" width="11" height="22" rx="3.5" fill="{BLUE}"/>')
    p.append(f'<rect class="st" x="26.5" y="22" width="11" height="34" rx="3.5" fill="{AMBER}"/>')
    p.append(f'<rect class="st" x="44" y="12" width="11" height="44" rx="3.5" fill="{CORAL}"/>')
    p.append(f'<rect class="st" x="6" y="56" width="52" height="5" rx="2.5" fill="{BROWN}"/>')
    return svg("".join(p))

def icon_clock():
    p = [style()]
    p.append(f'<circle class="st" cx="15" cy="13" r="6.5" fill="{BLUE}"/>')
    p.append(f'<circle class="st" cx="49" cy="13" r="6.5" fill="{BLUE}"/>')
    p.append(f'<path d="M17 53 L13 59 M47 53 L51 59" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="32" cy="34" r="22" fill="{WHITE}"/>')
    p.append(f'<path d="M32 34 L32 21" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<path d="M32 34 L41 38" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<circle cx="32" cy="34" r="3" fill="{CORAL}"/>')
    p.append(gloss(25, 26, 4, 3, 0.5))
    return svg("".join(p))

def icon_flag():
    p = [style()]
    p.append(f'<path d="M16 9 L16 56" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="16" cy="9" r="3.5" fill="{AMBER}"/>')
    p.append(f'<path class="st" d="M19 12 L49 12 Q54 12 54 16 L54 29 Q54 33 49 33 L19 33 Z" fill="{CORAL}"/>')
    p.append(f'<path d="M22 19 L48 19" stroke="{WHITE}" stroke-width="3" stroke-linecap="round" opacity="0.75"/>')
    p.append(f'<path d="M11 56 L21 56" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>')
    return svg("".join(p))

def icon_heart():
    p = [style()]
    p.append(f'<path class="st" d="M32 54 Q9 39 9 24 Q9 11 20 11 Q28 11 32 19 Q36 11 44 11 Q55 11 55 24 Q55 39 32 54 Z" fill="{RED}"/>')
    p.append(gloss(21, 21, 4, 6, 0.5))
    return svg("".join(p))

def icon_key():
    p = [style()]
    p.append(f'<circle class="st" cx="19" cy="32" r="11" fill="{AMBER}"/>')
    p.append(f'<circle cx="19" cy="32" r="5" fill="{WHITE}"/>')
    p.append(f'<rect class="st" x="28" y="28.5" width="27" height="7" rx="3.5" fill="{AMBER}"/>')
    p.append(f'<rect class="st" x="44.5" y="34" width="4.5" height="9" rx="2" fill="{AMBER}"/>')
    p.append(f'<rect class="st" x="51.5" y="34" width="4" height="7" rx="2" fill="{AMBER}"/>')
    return svg("".join(p))

def icon_lock():
    p = [style()]
    p.append(f'<path d="M22 31 L22 23 Q22 11 32 11 Q42 11 42 23 L42 31" '
             f'fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    p.append(f'<rect class="st" x="13" y="29" width="38" height="27" rx="9" fill="{AMBER}"/>')
    p.append(f'<circle cx="32" cy="40" r="4" fill="{DARKBROWN}"/>'
             f'<rect x="30.5" y="41" width="3" height="8" rx="1.5" fill="{DARKBROWN}"/>')
    p.append(gloss(20, 36, 3, 6, 0.5))
    return svg("".join(p))

def icon_medal():
    p = [style()]
    p.append(f'<path class="st" d="M20 5 L31 23 L25 27 L13 11 Z" fill="{CORAL}"/>')
    p.append(f'<path class="st" d="M44 5 L33 23 L39 27 L51 11 Z" fill="{RED}"/>')
    p.append(f'<circle class="st" cx="32" cy="40" r="15" fill="{AMBER}"/>')
    p.append(f'<circle cx="32" cy="40" r="10.5" fill="#FFE9A8"/>')
    p.append(f'<path d="M32 33 L34.3 38 L40 38.6 L35.7 42.3 L37 48 L32 45 L27 48 L28.3 42.3 L24 38.6 L29.7 38 Z" fill="{ORANGE}"/>')
    p.append(gloss(26, 34, 3, 2.5, 0.6))
    return svg("".join(p))

def icon_paw():
    p = [style()]
    p.append(f'<ellipse class="st" cx="17" cy="21" rx="6" ry="8" fill="{BROWN}" transform="rotate(-14 17 21)"/>')
    p.append(f'<ellipse class="st" cx="30" cy="15" rx="6" ry="8.5" fill="{BROWN}"/>')
    p.append(f'<ellipse class="st" cx="43" cy="17" rx="6" ry="8.5" fill="{BROWN}" transform="rotate(12 43 17)"/>')
    p.append(f'<ellipse class="st" cx="51" cy="27" rx="5.5" ry="7.5" fill="{BROWN}" transform="rotate(24 51 27)"/>')
    p.append(f'<path class="st" d="M32 30 Q15 30 14 43 Q13 54 25 54 L39 54 Q51 54 50 43 Q49 30 32 30 Z" fill="#E0A86E"/>')
    return svg("".join(p))

def icon_question():
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="22" fill="{BLUE}"/>')
    p.append(f'<path d="M26 26 Q26 20 32 20 Q38 20 38 25 Q38 29 32 32 L32 36" '
             f'fill="none" stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(f'<circle cx="32" cy="43" r="3" fill="{WHITE}"/>')
    return svg("".join(p))

def icon_shield():
    p = [style()]
    p.append(f'<path class="st" d="M32 5 L53 12 Q53 38 32 58 Q11 38 11 12 Z" fill="{TEAL}"/>')
    p.append(f'<path d="M22 31 L29 39 L43 24" stroke="{WHITE}" stroke-width="5.5" '
             f'fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(gloss(20, 16, 4, 3, 0.5))
    return svg("".join(p))

def icon_sparkle():
    p = [style()]
    p.append(f'<path class="st" d="M32 8 Q35 27 54 32 Q35 37 32 56 Q29 37 10 32 Q29 27 32 8 Z" fill="{AMBER}"/>')
    p.append(f'<circle cx="48" cy="16" r="3" fill="{AMBER}" opacity="0.9"/>'
             f'<circle cx="17" cy="47" r="2.5" fill="{AMBER}" opacity="0.8"/>')
    return svg("".join(p))

def icon_speaker():
    p = [style()]
    p.append(f'<path class="st" d="M11 26 L21 26 L35 14 L35 50 L21 38 L11 38 Z" fill="{BLUE}"/>')
    p.append(f'<path d="M43 24 Q49 32 43 40" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<path d="M50 18 Q58 32 50 46" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linecap="round" opacity="0.55"/>')
    return svg("".join(p))

def icon_star():
    p = [style()]
    p.append(f'<path class="st" d="M32 7 L39.5 23.5 L57.5 25.5 L44 38 L48 55.5 L32 46.5 L16 55.5 L20 38 L6.5 25.5 L24.4 23.5 Z" fill="{AMBER}"/>')
    p.append(gloss(26, 21, 3.5, 5, 0.5))
    return svg("".join(p))

def icon_starface():
    p = [style()]
    p.append(f'<path class="st" d="M32 6 L39.6 23 L58 25.2 L44.4 37.8 L48.4 55.5 L32 46.3 L15.6 55.5 L19.6 37.8 L6 25.2 L24.4 23 Z" fill="{AMBER}"/>')
    p.append(f'<ellipse cx="26.5" cy="31" rx="2.3" ry="3.2" fill="{INK}"/>'
             f'<ellipse cx="37.5" cy="31" rx="2.3" ry="3.2" fill="{INK}"/>')
    p.append(f'<circle cx="27.3" cy="29.9" r="0.9" fill="{WHITE}"/>'
             f'<circle cx="38.3" cy="29.9" r="0.9" fill="{WHITE}"/>')
    p.append(f'<path d="M28.5 38 Q32 41 35.5 38" stroke="{INK}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle cx="22" cy="35" r="2.6" fill="{BLUSH}" opacity="0.6"/>'
             f'<circle cx="42" cy="35" r="2.6" fill="{BLUSH}" opacity="0.6"/>')
    return svg("".join(p))

def icon_sunface():
    p = [style()]
    # 8 道短光芒（先画，被圆盖住根部）
    for i in range(8):
        a = i * math.pi / 4
        x1 = 32 + 19 * math.cos(a); y1 = 32 + 19 * math.sin(a)
        x2 = 32 + 25 * math.cos(a); y2 = 32 + 25 * math.sin(a)
        p.append(f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{ORANGE}" '
                  f'stroke-width="3.5" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="32" cy="32" r="16" fill="{YELLOW}"/>')
    p.append(f'<circle cx="26.5" cy="30" r="2.1" fill="{INK}"/>'
             f'<circle cx="37.5" cy="30" r="2.1" fill="{INK}"/>')
    p.append(f'<path d="M27 36 Q32 40 37 36" stroke="{INK}" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle cx="22.5" cy="35" r="2.4" fill="{BLUSH}" opacity="0.6"/>'
             f'<circle cx="41.5" cy="35" r="2.4" fill="{BLUSH}" opacity="0.6"/>')
    return svg("".join(p))

def icon_party():
    p = [style()]
    p.append(f'<path class="st" d="M14 52 L32 15 L50 52 Z" fill="{CORAL}"/>')
    p.append(f'<path d="M20 43 L44 43" stroke="{WHITE}" stroke-width="3" stroke-linecap="round" opacity="0.85"/>')
    p.append(f'<path d="M25 32 L39 32" stroke="{WHITE}" stroke-width="3" stroke-linecap="round" opacity="0.85"/>')
    p.append(f'<circle class="st" cx="32" cy="12" r="5" fill="{AMBER}"/>')
    p.append(f'<circle cx="51" cy="14" r="3" fill="{BLUE}"/>'
             f'<circle cx="56" cy="27" r="2.5" fill="{GREEN}"/>')
    p.append(f'<rect x="47" y="31" width="5" height="5" rx="1.5" fill="{PURPLE}" transform="rotate(20 49.5 33.5)"/>')
    return svg("".join(p))

def icon_girl():
    p = [style()]
    skin, hair = "#FFE3C2", "#8A5A32"
    p.append(f'<circle class="st" cx="11" cy="37" r="8" fill="{hair}"/>')
    p.append(f'<circle class="st" cx="53" cy="37" r="8" fill="{hair}"/>')
    p.append(f'<circle class="st" cx="32" cy="34" r="22" fill="{hair}"/>')
    p.append(f'<circle cx="32" cy="39" r="17.5" fill="{skin}"/>')
    p.append(f'<path d="M15.5 33 Q17 16 32 16 Q47 16 48.5 33 Q44 26 39 28 Q36 22 32 23 Q28 22 25 28 Q20 26 15.5 33 Z" fill="{hair}"/>')
    p.append(f'<circle cx="25.5" cy="40" r="2.6" fill="{INK}"/><circle cx="38.5" cy="40" r="2.6" fill="{INK}"/>')
    p.append(f'<circle cx="26.4" cy="39.1" r="0.9" fill="{WHITE}"/><circle cx="39.4" cy="39.1" r="0.9" fill="{WHITE}"/>')
    p.append(f'<circle cx="21" cy="45" r="3" fill="{BLUSH}" opacity="0.6"/>'
             f'<circle cx="43" cy="45" r="3" fill="{BLUSH}" opacity="0.6"/>')
    p.append(f'<path d="M28.5 46 Q32 49 35.5 46" stroke="{INK}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    return svg("".join(p))

def icon_hanzi():
    p = [style()]
    p.append(f'<rect class="st" x="11" y="8" width="42" height="48" rx="8" fill="{WHITE}"/>')
    p.append(f'<rect x="17" y="14" width="30" height="36" rx="3" fill="none" '
             f'stroke="{BLUSH}" stroke-width="1.8" opacity="0.7"/>')
    p.append(f'<text x="32" y="43" text-anchor="middle" font-size="27" font-weight="700" '
             f'fill="{RED}" font-family="Kaiti SC, KaiTi, STKaiti, serif">字</text>')
    return svg("".join(p))

def icon_calendar():
    p = [style()]
    p.append(f'<rect class="st" x="10" y="13" width="44" height="42" rx="8" fill="{WHITE}"/>')
    p.append(f'<path d="M10 21 Q10 13 18 13 L46 13 Q54 13 54 21 L54 25 L10 25 Z" fill="{RED}"/>')
    p.append(f'<rect class="st" x="18" y="7" width="4.5" height="11" rx="2.2" fill="{BROWN}"/>')
    p.append(f'<rect class="st" x="41.5" y="7" width="4.5" height="11" rx="2.2" fill="{BROWN}"/>')
    p.append(f'<circle cx="20" cy="33" r="2.4" fill="{BLUE}"/><circle cx="32" cy="33" r="2.4" fill="{BLUE}"/>'
             f'<circle cx="44" cy="33" r="2.4" fill="{BLUE}"/>')
    p.append(f'<circle cx="20" cy="44" r="2.4" fill="{BLUE}"/><circle cx="32" cy="44" r="2.4" fill="{BLUE}"/>')
    p.append(f'<circle cx="44" cy="44" r="4.5" fill="{CORAL}"/>')
    return svg("".join(p))


# ----------------------------------------------------------------------
# 情绪 / 动作 / 人物（英语词场：开心、兴奋、唱歌、老师、人脚印）
# ----------------------------------------------------------------------
def _spark(cx, cy, r, color):
    """四角小闪星（兴奋眼、点缀用）。"""
    q = r * 0.28
    return (f'<path d="M{cx} {cy-r} Q{cx+q} {cy-q} {cx+r} {cy} Q{cx+q} {cy+q} {cx} {cy+r} '
            f'Q{cx-q} {cy+q} {cx-r} {cy} Q{cx-q} {cy-q} {cx} {cy-r} Z" fill="{color}"/>')

def icon_happy():
    """开心：黄色圆脸，弯月笑眼 + 张大的笑嘴。"""
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="23" fill="{YELLOW}"/>')
    p.append(f'<path d="M21 27 Q25 22.5 29 27" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>')
    p.append(f'<path d="M35 27 Q39 22.5 43 27" fill="none" stroke="{INK}" stroke-width="2.8" stroke-linecap="round"/>')
    p.append(f'<circle cx="19.5" cy="34" r="3.2" fill="{BLUSH}" opacity="0.65"/>')
    p.append(f'<circle cx="44.5" cy="34" r="3.2" fill="{BLUSH}" opacity="0.65"/>')
    p.append(f'<path class="st" d="M22 35 Q32 50 42 35 Z" fill="#B8453A"/>')
    p.append(f'<path d="M27 43 Q32 47 37 43 Q32 44.5 27 43 Z" fill="#F08A8A"/>')
    p.append(gloss(23, 20, 4.5, 3, 0.5))
    return svg("".join(p))

def icon_excited():
    """兴奋：星星眼 + 张圆的 O 嘴 + 上扬眉。"""
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="23" fill="{YELLOW}"/>')
    p.append(f'<path d="M20.5 20 L28 22.5" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    p.append(f'<path d="M43.5 20 L36 22.5" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    p.append(_spark(25, 28, 4.6, "#E8654F"))
    p.append(_spark(39, 28, 4.6, "#E8654F"))
    p.append(f'<circle cx="19" cy="36" r="3" fill="{BLUSH}" opacity="0.65"/>')
    p.append(f'<circle cx="45" cy="36" r="3" fill="{BLUSH}" opacity="0.65"/>')
    p.append(f'<ellipse class="st" cx="32" cy="41" rx="4.6" ry="5.6" fill="{DARKBROWN}"/>')
    p.append(gloss(23, 20, 4.5, 3, 0.5))
    return svg("".join(p))

def icon_sing():
    """唱歌：八分音符 + 两道音波（区别于喇叭 speaker）。"""
    p = [style()]
    p.append(f'<ellipse class="st" cx="18" cy="44" rx="8" ry="6" fill="{PURPLE}" transform="rotate(-20 18 44)"/>')
    p.append(f'<path class="st" d="M24.5 41 L24.5 13 L29 13 L29 39 Z" fill="{PURPLE}"/>')
    p.append(f'<path class="st" d="M29 14 Q43 18 40 31 Q37 22 29 23 Z" fill="{PURPLE}"/>')
    p.append(f'<path d="M44 25 Q47 30 44 35" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linecap="round"/>')
    p.append(f'<path d="M49 21 Q53 30 49 39" fill="none" stroke="{BLUE}" stroke-width="2.6" stroke-linecap="round" opacity="0.55"/>')
    return svg("".join(p))

def icon_teacher():
    """老师：戴圆眼镜的笑脸头像 + 底下一本打开的书（区别于 girl）。"""
    p = [style()]
    skin, hair = "#FFE3C2", "#5E4A38"
    p.append(f'<path class="st" d="M32 47 L12 51 L12 58 Q22 54.5 32 56.5 Q42 54.5 52 58 L52 51 Z" fill="{BLUE}"/>')
    p.append(f'<path d="M32 47 L32 56.5" stroke="{INK}" stroke-width="1.5" stroke-linecap="round"/>')
    p.append(f'<path d="M16 55 Q24 52.5 30 54 M34 54 Q40 52.5 48 55" fill="none" stroke="{WHITE}" stroke-width="1.3" stroke-linecap="round" opacity="0.8"/>')
    p.append(f'<circle class="st" cx="32" cy="28" r="17" fill="{hair}"/>')
    p.append(f'<circle cx="32" cy="32" r="13.5" fill="{skin}"/>')
    p.append(f'<path d="M16 28 Q17 13 32 13 Q47 13 48 28 Q43 21 38 24 Q34 19 32 20 Q30 19 26 24 Q21 21 16 28 Z" fill="{hair}"/>')
    p.append(f'<circle class="st" cx="26.5" cy="33" r="4.7" fill="{WHITE}" fill-opacity="0.45"/>')
    p.append(f'<circle class="st" cx="37.5" cy="33" r="4.7" fill="{WHITE}" fill-opacity="0.45"/>')
    p.append(f'<path d="M31.2 33 L32.8 33" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    p.append(f'<circle cx="26.5" cy="33" r="1.7" fill="{INK}"/>')
    p.append(f'<circle cx="37.5" cy="33" r="1.7" fill="{INK}"/>')
    p.append(f'<path d="M28 39 Q32 42 36 39" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    p.append(f'<circle cx="20.5" cy="37" r="2.6" fill="{BLUSH}" opacity="0.6"/>')
    p.append(f'<circle cx="43.5" cy="37" r="2.6" fill="{BLUSH}" opacity="0.6"/>')
    return svg("".join(p))

def icon_foot():
    """人的脚印：5 个小脚趾 + 长脚掌（区别于动物爪印 paw）。"""
    p = [style()]
    skin = "#FFE3C2"
    p.append(f'<path class="st" d="M27 58 Q18 42 22 30 Q26 22 34 24 Q43 27 41 40 Q39 52 34 58 Q30 59.5 27 58 Z" fill="{skin}"/>')
    p.append(f'<circle class="st" cx="37" cy="21" r="4.2" fill="{skin}"/>')
    p.append(f'<circle class="st" cx="31" cy="18.5" r="3.5" fill="{skin}"/>')
    p.append(f'<circle class="st" cx="25" cy="19" r="3.1" fill="{skin}"/>')
    p.append(f'<circle class="st" cx="20" cy="21.5" r="2.7" fill="{skin}"/>')
    p.append(f'<circle class="st" cx="16" cy="25" r="2.3" fill="{skin}"/>')
    return svg("".join(p))


ICONS = {
    "circle": icon_circle,
    "square": icon_square,
    "triangle": icon_triangle,
    "pentagon": icon_pentagon,
    "equal": icon_equal,
    "slider": icon_slider,
    "back": icon_back,
    "blocklock": icon_blocklock,
    "blockok": icon_blockok,
    "chart": icon_chart,
    "clock": icon_clock,
    "flag": icon_flag,
    "heart": icon_heart,
    "key": icon_key,
    "lock": icon_lock,
    "medal": icon_medal,
    "paw": icon_paw,
    "question": icon_question,
    "shield": icon_shield,
    "sparkle": icon_sparkle,
    "speaker": icon_speaker,
    "star": icon_star,
    "starface": icon_starface,
    "sunface": icon_sunface,
    "party": icon_party,
    "girl": icon_girl,
    "hanzi": icon_hanzi,
    "calendar": icon_calendar,
    "happy": icon_happy,
    "excited": icon_excited,
    "sing": icon_sing,
    "teacher": icon_teacher,
    "foot": icon_foot,
}

if __name__ == "__main__":
    emit(ICONS, "ui")
