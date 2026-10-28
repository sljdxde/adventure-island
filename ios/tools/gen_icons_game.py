# -*- coding: utf-8 -*-
"""
Shard D：货币 + 马里奥游戏元素图标（绘本手绘风，纯 SVG）
- coin / m-jiao1 / m-jiao5 / m-yuan1 / m-yuan5 / m-yuan10
- pipe-blue / pipe-brown / pipe-green / pipe-indigo / pipe-orange / pipe-purple / pipe-red
- brick / mario(72x96) / boss(96x96)

规范：深棕描边 INK（class="st"）、水彩平涂、半透明白高光 gloss()、
禁止线性渐变、禁止深色外发光。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_common import *

INDIGO = "#6E7CC6"          # 靛蓝（调色板无，自定义）
MY5    = "#9B7FA6"          # 5元 棕紫

# ----------------------------------------------------------------------
# 通用小元件
# ----------------------------------------------------------------------
def yuan_mark(x, y, color=INK, w=1.7):
    """在 (x,y) 居中画 ¥ 记号（手绘细线条）。"""
    return (f'<path d="M{x-4} {y-5} L{x} {y-0.5} L{x+4} {y-5} '
            f'M{x} {y-0.5} L{x} {y+6} '
            f'M{x-3.4} {y+2} L{x+3.4} {y+2} '
            f'M{x-3.4} {y+4.6} L{x+3.4} {y+4.6}" '
            f'stroke="{color}" stroke-width="{w}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')

# ----------------------------------------------------------------------
# 货币
# ----------------------------------------------------------------------
def icon_coin():
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="21" fill="{AMBER}"/>')
    p.append(f'<circle cx="32" cy="32" r="15" fill="none" stroke="{YELLOW}" stroke-width="3"/>')
    p.append('<path d="M32 25 L33.9 29.4 L38.7 29.8 L35.0 33.0 L36.1 37.7 L32 35.2 L27.9 37.7 L29.0 33.0 L25.3 29.8 L30.1 29.4 Z" fill="#D99A2B"/>')
    p.append(gloss(24, 22, 4, 7, 0.55))
    return svg("".join(p), vb=64)

def icon_m_jiao1():
    """1角：小钢色（银白）硬币。"""
    p = [style()]
    p.append('<circle class="st" cx="32" cy="32" r="18" fill="#DDE3E8"/>')
    p.append('<circle cx="32" cy="32" r="12.5" fill="none" stroke="#BFC8D0" stroke-width="2"/>')
    p.append(yuan_mark(32, 32, color="#6B7680"))
    p.append(gloss(26, 24, 3, 5, 0.7))
    return svg("".join(p), vb=64)

def icon_m_jiao5():
    """5角：金色硬币。"""
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="21" fill="{AMBER}"/>')
    p.append('<circle cx="32" cy="32" r="15" fill="none" stroke="#E8B23A" stroke-width="2.2"/>')
    p.append(yuan_mark(32, 32, color="#B8791F"))
    p.append(gloss(25, 23, 4, 6, 0.6))
    return svg("".join(p), vb=64)

def bill(base, digit, dsize=16):
    p = [style()]
    p.append(f'<rect class="st" x="8" y="22" width="48" height="20" rx="5" fill="{base}"/>')
    p.append(f'<circle class="st" cx="19" cy="32" r="6.5" fill="{CREAM}"/>')
    p.append(yuan_mark(19, 31.5, color=INK, w=1.4))
    p.append('<rect x="30" y="26.8" width="23" height="2.4" rx="1.2" fill="#fff" opacity="0.3"/>')
    p.append(f'<text x="45" y="36.6" font-family="Arial, sans-serif" font-weight="bold" '
             f'font-size="{dsize}" fill="#FFFFFF" text-anchor="middle">{digit}</text>')
    return svg("".join(p), vb=64)

def icon_m_yuan1():
    return bill(GREEN, "1", 16)

def icon_m_yuan5():
    return bill(MY5, "5", 16)

def icon_m_yuan10():
    return bill(BLUE, "10", 11)

# ----------------------------------------------------------------------
# 马里奥水管（统一形状，仅换色）
# ----------------------------------------------------------------------
def pipe(color):
    p = [style()]
    p.append(f'<rect class="st" x="15" y="22" width="34" height="37" rx="3.5" fill="{color}"/>')
    p.append(f'<rect class="st" x="9" y="7" width="46" height="16" rx="6.5" fill="{color}"/>')
    p.append(f'<ellipse cx="32" cy="14" rx="15" ry="3.6" fill="{INK}" opacity="0.18"/>')
    p.append(f'<rect x="9" y="20.5" width="46" height="3.2" fill="{INK}" opacity="0.15"/>')
    p.append('<rect x="19" y="27" width="6" height="26" rx="3" fill="#fff" opacity="0.35"/>')
    p.append('<rect x="14" y="10" width="9" height="5" rx="2.5" fill="#fff" opacity="0.45"/>')
    return svg("".join(p), vb=64)

def icon_pipe_blue():   return pipe(BLUE)
def icon_pipe_brown():  return pipe(BROWN)
def icon_pipe_green():  return pipe(GREEN)
def icon_pipe_indigo():  return pipe(INDIGO)
def icon_pipe_orange(): return pipe(ORANGE)
def icon_pipe_purple(): return pipe(PURPLE)
def icon_pipe_red():     return pipe(RED)

# ----------------------------------------------------------------------
# 砖块
# ----------------------------------------------------------------------
def icon_brick():
    p = [style()]
    p.append(f'<rect class="st" x="6" y="12" width="52" height="40" rx="6" fill="{RED}"/>')
    p.append('<path class="th" d="M7 25 L57 25 M7 38 L57 38 '
             'M22 12 L22 25 M42 12 L42 25 '
             'M14 25 L14 38 M32 25 L32 38 M50 25 L50 38 '
             'M22 38 L22 52 M42 38 L42 52"/>')
    p.append(gloss(16, 18, 3, 2.5, 0.5))
    return svg("".join(p), vb=64)

# ----------------------------------------------------------------------
# 马里奥（72 x 96）
# ----------------------------------------------------------------------
def icon_mario():
    p = [style(2.5, 1.5)]
    MRED, MBLUE, SKIN = "#E54B3C", "#4A86C5", "#FFD9B3"
    p.append(f'<ellipse class="st" cx="25" cy="91" rx="11" ry="5.5" fill="{DARKBROWN}"/>')
    p.append(f'<ellipse class="st" cx="47" cy="91" rx="11" ry="5.5" fill="{DARKBROWN}"/>')
    p.append(f'<rect class="st" x="21" y="70" width="9" height="18" rx="4.5" fill="{MBLUE}"/>')
    p.append(f'<rect class="st" x="42" y="70" width="9" height="18" rx="4.5" fill="{MBLUE}"/>')
    p.append(f'<ellipse class="st" cx="13" cy="57" rx="7.5" ry="6" fill="{MRED}"/>')
    p.append(f'<circle class="st" cx="9" cy="61" r="5.5" fill="{WHITE}"/>')
    p.append(f'<ellipse class="st" cx="59" cy="57" rx="7.5" ry="6" fill="{MRED}"/>')
    p.append(f'<circle class="st" cx="63" cy="61" r="5.5" fill="{WHITE}"/>')
    p.append(f'<path class="st" d="M22 50 Q22 45 30 44 L42 44 Q50 45 50 50 L51 66 Q51 71 46 71 L26 71 Q21 71 21 66 Z" fill="{MRED}"/>')
    p.append(f'<path class="st" d="M24 54 L48 54 L49 71 L23 71 Z" fill="{MBLUE}"/>')
    p.append(f'<rect class="st" x="26" y="45" width="5.5" height="11" rx="2.75" fill="{MBLUE}"/>')
    p.append(f'<rect class="st" x="40.5" y="45" width="5.5" height="11" rx="2.75" fill="{MBLUE}"/>')
    p.append(f'<circle cx="29" cy="57" r="2.6" fill="{YELLOW}"/>')
    p.append(f'<circle cx="43" cy="57" r="2.6" fill="{YELLOW}"/>')
    p.append(f'<circle class="st" cx="16.5" cy="27" r="4.2" fill="{SKIN}"/>')
    p.append(f'<circle class="st" cx="55.5" cy="27" r="4.2" fill="{SKIN}"/>')
    p.append(f'<circle class="st" cx="36" cy="26" r="20" fill="{SKIN}"/>')
    p.append(f'<path class="st" d="M14 21 Q15 6 36 6 Q57 6 58 21 L58 22.5 Q58 24.5 55 24.5 L17 24.5 Q14 24.5 14 22.5 Z" fill="{MRED}"/>')
    p.append(f'<path class="st" d="M50 18.5 Q66 17.5 66 22 Q66 25.5 49 25 L49 20 Z" fill="{MRED}"/>')
    p.append(f'<circle class="st" cx="34" cy="14.5" r="6.2" fill="{WHITE}"/>')
    p.append('<path d="M34 10.8 L34.9 12.8 L37 13 L35.4 14.4 L35.8 16.5 L34 15.4 L32.2 16.5 L32.6 14.4 L31 13 L33.1 12.8 Z" fill="#E8A33D"/>')
    p.append('<ellipse cx="28" cy="27.5" rx="4" ry="5.4" fill="#fff"/>')
    p.append('<ellipse cx="44" cy="27.5" rx="4" ry="5.4" fill="#fff"/>')
    p.append('<circle cx="29" cy="28.5" r="2.2" fill="#3A2E22"/>')
    p.append('<circle cx="45" cy="28.5" r="2.2" fill="#3A2E22"/>')
    p.append('<circle cx="29.8" cy="27.6" r=".8" fill="#fff"/>')
    p.append('<circle cx="45.8" cy="27.6" r=".8" fill="#fff"/>')
    p.append('<ellipse cx="36" cy="33.5" rx="5" ry="4" fill="#F5C69A"/>')
    p.append('<path d="M26 37.5 Q31 34.5 36 37.5 Q41 34.5 46 37.5 Q46 41.5 41 41.5 L31 41.5 Q26 41.5 26 37.5 Z" fill="#5A3A22"/>')
    p.append('<ellipse cx="21" cy="18" rx="6" ry="3.2" fill="#fff" opacity=".3" transform="rotate(-18 21 18)"/>')
    return svg("".join(p), vb="0 0 72 96")

# ----------------------------------------------------------------------
# Boss（96 x 96）：绿壳尖刺龟
# ----------------------------------------------------------------------
def icon_boss():
    p = [style(2.6, 1.6)]
    SHELL, HEAD, BELLY = "#5FA85A", "#8FCB7E", "#F7EFCE"
    p.append(f'<path class="st" d="M80 74 Q92 72 90 62 Q86 60 82 64 Q84 70 78 71 Z" fill="{SHELL}"/>')
    p.append(f'<ellipse class="st" cx="32" cy="89" rx="12" ry="6.5" fill="{ORANGE}"/>')
    p.append(f'<ellipse class="st" cx="64" cy="89" rx="12" ry="6.5" fill="{ORANGE}"/>')
    p.append(f'<ellipse class="st" cx="48" cy="60" rx="39" ry="31" fill="{SHELL}"/>')
    for d in ("M14 52 L8 40 L22 46 Z", "M82 52 L88 40 L74 46 Z",
              "M20 36 L17 23 L30 31 Z", "M76 36 L79 23 L66 31 Z"):
        p.append(f'<path class="st" d="{d}" fill="{AMBER}"/>')
    p.append('<path d="M22 58 Q48 44 74 58" stroke="#8FD07E" stroke-width="2.4" fill="none" opacity=".8"/>')
    p.append('<path d="M26 70 Q48 58 70 70" stroke="#8FD07E" stroke-width="2.4" fill="none" opacity=".7"/>')
    p.append(f'<ellipse cx="48" cy="66" rx="21" ry="22" fill="{BELLY}"/>')
    p.append(f'<ellipse class="st" cx="24" cy="66" rx="8" ry="10" fill="{HEAD}"/>')
    p.append(f'<ellipse class="st" cx="72" cy="66" rx="8" ry="10" fill="{HEAD}"/>')
    p.append(f'<path class="st" d="M30 20 L24 5 L38 15 Z" fill="{CREAM}"/>')
    p.append(f'<path class="st" d="M66 20 L72 5 L58 15 Z" fill="{CREAM}"/>')
    p.append(f'<circle class="st" cx="48" cy="29" r="22" fill="{HEAD}"/>')
    p.append('<path d="M31 22 L43 27" stroke="#4A3A28" stroke-width="4.2" stroke-linecap="round"/>')
    p.append('<path d="M65 22 L53 27" stroke="#4A3A28" stroke-width="4.2" stroke-linecap="round"/>')
    p.append('<ellipse cx="38" cy="31" rx="5" ry="5.6" fill="#fff"/>')
    p.append('<ellipse cx="58" cy="31" rx="5" ry="5.6" fill="#fff"/>')
    p.append('<circle cx="39" cy="32" r="2.5" fill="#2E2418"/>')
    p.append('<circle cx="57" cy="32" r="2.5" fill="#2E2418"/>')
    p.append('<ellipse cx="48" cy="41" rx="13" ry="9" fill="#E9F2C8"/>')
    p.append('<circle cx="43" cy="39.5" r="1.8" fill="#4A3A28"/>')
    p.append('<circle cx="53" cy="39.5" r="1.8" fill="#4A3A28"/>')
    p.append('<path d="M41 45 Q48 41 55 45" stroke="#4A3A28" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    p.append('<path d="M43 44.6 L45 49 L47 44.6 Z" fill="#fff"/>')
    p.append('<path d="M49 44.6 L51 49 L53 44.6 Z" fill="#fff"/>')
    p.append('<ellipse cx="34" cy="42" rx="10" ry="5" fill="#fff" opacity=".22" transform="rotate(-18 34 42)"/>')
    return svg("".join(p), vb="0 0 96 96")


ICONS = {
    "coin": icon_coin,
    "m-jiao1": icon_m_jiao1,
    "m-jiao5": icon_m_jiao5,
    "m-yuan1": icon_m_yuan1,
    "m-yuan5": icon_m_yuan5,
    "m-yuan10": icon_m_yuan10,
    "pipe-blue": icon_pipe_blue,
    "pipe-brown": icon_pipe_brown,
    "pipe-green": icon_pipe_green,
    "pipe-indigo": icon_pipe_indigo,
    "pipe-orange": icon_pipe_orange,
    "pipe-purple": icon_pipe_purple,
    "pipe-red": icon_pipe_red,
    "brick": icon_brick,
    "mario": icon_mario,
    "boss": icon_boss,
}

if __name__ == "__main__":
    emit(ICONS, "game")
