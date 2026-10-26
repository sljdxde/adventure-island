# -*- coding: utf-8 -*-
"""
探险岛 · 概念图标重绘（纯 SVG 手绘绘本风）
修复题库内容审计发现的"抽象概念用错图标"问题，补上一批题目真正需要、
但旧图标库里缺失的概念图标。全部遵守绘本手绘风：深棕描边 INK + 水彩平涂、
无线性渐变、圆润可爱、64 画布小尺寸可辨。

产出：design/assets/icons/<name>.svg
依赖 icon_common.py；可独立运行 python3 ios/tools/gen_icons_concept.py
另含写实的 aurora（极光）/sunset（日落）在 gen_icons.py 的 REAL_ICONS 中。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_common import *

# 绘本配色外的少量主题色（平涂）
SKY    = "#A8D8F0"   # 浅天
SILVER = "#D8DCE4"   # 勺子银灰
SILVERD= "#B9C0CC"   # 银灰暗面
RUST   = "#C0573B"   # 铁锈红
RUSTD  = "#9E442E"   # 铁锈暗
CORAL_RED = "#EF6F5C"
NIGHT  = "#3E5A8C"   # 夜空蓝

# ============================================================
# 自然地理（手绘）
# ============================================================

# ---- 迎客松 / 松树（黄山）----
def icon_pine():
    p = [style()]
    # 树干
    p.append(f'<path class="st" d="M29 56 Q30 40 31 30 L35 31 Q34 44 35 56 Z" fill="{BROWN}"/>')
    # 向右平伸的迎客长枝（横向，端部松针）
    p.append(f'<path d="M33 34 Q44 32 54 30" stroke="{BROWN}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M50 26 Q57 24 55 31 Q51 30 48 32 Z" fill="{LEAF}"/>')
    # 三层三角树冠（层叠松针）
    p.append(f'<path class="st" d="M33 7 L22 22 L27 20 L24 27 L33 23 L42 27 L39 20 L44 22 Z" fill="{LEAF}"/>')
    p.append(f'<path class="st" d="M34 21 L20 38 L27 35 L23 43 L34 38 L45 43 L41 35 L48 38 Z" fill="{GREEN}"/>')
    p.append(gloss(27, 21, 3, 3, 0.45))
    return svg("".join(p))

# ---- 大草原（内蒙古）----
def icon_grassland():
    p = [style()]
    # 远处浅蓝天
    p.append(f'<rect x="6" y="6" width="52" height="28" rx="12" fill="{SKY}" opacity="0.5"/>')
    # 一朵小云
    p.append(f'<g fill="#ffffff" opacity="0.9"><ellipse cx="19" cy="17" rx="8" ry="4.5"/><circle cx="13" cy="16" r="4"/><circle cx="25" cy="15" r="3.4"/></g>')
    # 小太阳
    p.append(f'<circle cx="47" cy="16" r="5" fill="{AMBER}"/>')
    # 起伏草地（两层，远近）
    p.append(f'<path d="M6 58 Q6 42 22 40 Q34 38 46 41 Q58 43 58 58 Z" fill="{LEAF}"/>')
    p.append(f'<path class="st" d="M6 58 Q6 47 24 46 Q38 45 58 48 L58 58 Z" fill="{GREEN}"/>')
    # 整齐的草尖（前景）
    for bx, s in [(12, 1), (18, 0.8), (27, 1), (36, 0.85), (45, 1), (52, 0.8)]:
        h = 8 * s
        p.append(f'<path d="M{bx} 55 Q{bx-2} {50-h*0.3} {bx-3} {50-h} M{bx} 55 Q{bx} {48-h*0.4} {bx} {47-h} M{bx} 55 Q{bx+2} {50-h*0.3} {bx+3} {50-h}" stroke="{DARKBROWN}" stroke-width="1.7" fill="none" stroke-linecap="round"/>')
    p.append(gloss(17, 50, 7, 2.5, 0.35))
    return svg("".join(p))

# ---- 桂林山水（峰林 + 水面倒影）----
def icon_shanshui():
    p = [style()]
    # 水面（下半浅蓝）
    p.append(f'<rect x="6" y="40" width="52" height="18" rx="6" fill="{SKY}" opacity="0.7"/>')
    # 三座喀斯特钟形峰
    def peak(cx, top, w, h, col):
        return (f'<path class="st" d="M{cx-w} 42 Q{cx-w+2} {top} {cx} {top-3} Q{cx+w-2} {top} {cx+w} 42 Z" fill="{col}"/>')
    p.append(peak(20, 18, 9, 24, LEAF))
    p.append(peak(34, 10, 11, 32, GREEN))
    p.append(peak(47, 22, 8, 20, LEAF))
    # 水波纹
    for wy in [45, 50, 55]:
        p.append(f'<path d="M10 {wy} Q20 {wy-2} 30 {wy} Q40 {wy+2} 54 {wy}" fill="none" stroke="{NAVY}" stroke-width="1.6" stroke-linecap="round" opacity="0.5"/>')
    p.append(gloss(25, 18, 3, 3, 0.5))
    return svg("".join(p))

# ---- 珊瑚（珊瑚礁 / 大堡礁）----
def icon_coral():
    p = [style()]
    # 海水底
    p.append(f'<circle cx="32" cy="34" r="26" fill="{SKY}" opacity="0.6"/>')
    # 珊瑚主干与分枝（橙红圆角枝）
    p.append(f'<path class="st" d="M32 52 L32 34" stroke="{CORAL_RED}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    branches = [
        (32, 36, 24, 26), (32, 34, 22, 20), (32, 40, 40, 28),
        (32, 34, 42, 22), (32, 44, 25, 40), (32, 44, 40, 42),
    ]
    for x1, y1, x2, y2 in branches:
        p.append(f'<path d="M{x1} {y1} Q{(x1+x2)/2} {y1-2} {x2} {y2}" stroke="{CORAL_RED}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle cx="32" cy="32" r="3.4" fill="{CORAL_RED}" stroke="{INK}" stroke-width="1.6"/>')
    # 珊瑚枝尖小圆
    for cx, cy in [(24,26),(22,20),(40,28),(42,22),(25,40),(40,42)]:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="2.6" fill="{AMBER}" stroke="{INK}" stroke-width="1.3"/>')
    # 气泡
    p.append(f'<circle cx="15" cy="20" r="2" fill="{WHITE}" opacity="0.85"/>')
    p.append(f'<circle cx="50" cy="18" r="2.6" fill="{WHITE}" opacity="0.85"/>')
    return svg("".join(p))

# ---- 海岛（台湾 / 格陵兰）----
def icon_island():
    p = [style()]
    # 海
    p.append(f'<circle cx="32" cy="34" r="27" fill="{SKY}" opacity="0.7"/>')
    for wy in [46, 52]:
        p.append(f'<path d="M11 {wy} Q22 {wy-2} 32 {wy} Q42 {wy+2} 53 {wy}" fill="none" stroke="{NAVY}" stroke-width="1.6" stroke-linecap="round" opacity="0.45"/>')
    # 沙滩
    p.append(f'<ellipse class="st" cx="32" cy="44" rx="17" ry="8" fill="{SAND if False else "#F2D28A"}"/>')
    # 一棵小棕榈
    p.append(f'<path d="M32 44 Q32 34 34 26 L37 27 Q34 37 35 44 Z" fill="{BROWN}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>')
    p.append(f'<path class="st" d="M35 27 Q24 18 16 23 Q27 20 35 28 Z" fill="{LEAF}"/>')
    p.append(f'<path class="st" d="M35 27 Q47 17 52 24 Q43 20 35 28 Z" fill="{GREEN}"/>')
    p.append(f'<path class="st" d="M35 26 Q31 14 41 16 Q35 18 36 26 Z" fill="{LEAF}"/>')
    p.append(gloss(27, 43, 5, 2.5, 0.55))
    return svg("".join(p))

# ---- 松针 / 针叶（保留空位占位，暂不单独输出）----

# ============================================================
# 生活 / 物品 / 航天（手绘）
# ============================================================

# ---- 勺子（北斗七星像勺子）----
def icon_spoon():
    p = [style()]
    # 斜放：右下勺头 + 左上柄
    p.append(f'<g transform="rotate(35 32 32)">')
    # 柄
    p.append(f'<rect class="st" x="29.5" y="12" width="5" height="26" rx="2.5" fill="{SILVER}"/>')
    # 勺头
    p.append(f'<ellipse class="st" cx="32" cy="43" rx="11" ry="12" fill="{SILVER}"/>')
    p.append(f'<ellipse cx="32" cy="44" rx="7" ry="8" fill="{SILVERD}" opacity="0.45"/>')
    p.append(gloss(28, 39, 2.6, 4, 0.7))
    p.append('</g>')
    return svg("".join(p))

# ---- 指南针（指北）----
def icon_compass():
    p = [style()]
    p.append(f'<circle class="st" cx="32" cy="32" r="24" fill="{BROWN}"/>')
    p.append(f'<circle class="st" cx="32" cy="32" r="19" fill="{CREAM}"/>')
    # 刻度（四向小点）
    for deg in [0, 90, 180, 270]:
        import math
        rad = math.radians(deg - 90)
        x = 32 + 15 * math.cos(rad); y = 32 + 15 * math.sin(rad)
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.4" fill="{DARKBROWN}"/>')
    # 指针：北半红、南半白
    p.append(f'<path class="st" d="M32 16 L37 32 L32 30 L27 32 Z" fill="{RED}"/>')
    p.append(f'<path class="st" d="M32 48 L37 32 L32 34 L27 32 Z" fill="{SILVER}"/>')
    p.append(f'<circle cx="32" cy="32" r="2.4" fill="{DARKBROWN}"/>')
    # 顶部 N
    p.append(f'<text x="32" y="24" text-anchor="middle" font-size="7" font-weight="900" fill="{DARKBROWN}" font-family="sans-serif">N</text>')
    return svg("".join(p))

# ---- 睡袋（空间站睡觉）----
def icon_sleepingbag():
    p = [style()]
    # 挂钩
    p.append(f'<path class="th" d="M32 6 q6 0 6 6 q0 4 -4 4"/>')
    # 睡袋主体（圆筒，上口略宽）
    p.append(f'<path class="st" d="M22 20 Q22 16 32 16 Q42 16 42 20 L45 52 Q45 57 32 57 Q19 57 19 52 Z" fill="{BLUE}"/>')
    # 拉链
    p.append(f'<path d="M32 22 L31 52" stroke="{CREAM}" stroke-width="2" stroke-dasharray="2.5 2.4"/>')
    # 袋口露出的宇航员小脸
    p.append(f'<ellipse class="st" cx="32" cy="19" rx="7" ry="6.5" fill="#FFE2C4"/>')
    p.append(f'<path class="st" d="M25 17 Q25 12 32 12 Q39 12 39 17 Q36 14 32 14 Q28 14 25 17 Z" fill="{WHITE}"/>')
    p.append('<circle cx="29.5" cy="19" r="1.2" fill="#3A2A20"/><circle cx="34.5" cy="19" r="1.2" fill="#3A2A20"/>')
    p.append('<path class="th" d="M30 22 Q32 23.5 34 22"/>')
    p.append(gloss(25, 32, 2.6, 8, 0.5))
    return svg("".join(p))

# ---- 吸管水袋（空间站喝水）----
def icon_waterpouch():
    p = [style()]
    # 吸管
    p.append(f'<path class="st" d="M40 18 Q40 10 46 9" fill="none" stroke="{SILVERD}" stroke-width="3" stroke-linecap="round"/>')
    # 软袋
    p.append(f'<path class="st" d="M20 22 Q20 18 25 18 L39 18 Q44 18 44 23 L43 48 Q43 54 32 54 Q21 54 21 48 Z" fill="{BLUE}"/>')
    # 袋内水（上半留白，下半深蓝）
    p.append(f'<path d="M23 32 Q32 28 41 32 L40 48 Q40 50 32 50 Q24 50 24 48 Z" fill="{NAVY}" opacity="0.55"/>')
    # 可爱水滴脸
    p.append('<circle cx="28" cy="39" r="1.3" fill="#3A2A20"/><circle cx="36" cy="39" r="1.3" fill="#3A2A20"/>')
    p.append('<path class="th" d="M28.5 43 Q32 45.5 35.5 43"/>')
    p.append(gloss(26, 26, 2.4, 6, 0.55))
    return svg("".join(p))

# ---- 风筝（卫星题的"风筝"干扰项）----
def icon_kite():
    p = [style()]
    # 菱形风筝
    p.append(f'<path class="st" d="M30 8 L46 26 L30 44 L14 26 Z" fill="{RED}"/>')
    p.append(f'<path d="M30 8 L30 44 M14 26 L46 26" stroke="{INK}" stroke-width="1.6" opacity="0.5"/>')
    p.append(f'<path d="M30 8 L46 26 L30 26 Z" fill="{CORAL}" opacity="0.7"/>')
    p.append(f'<path d="M30 8 L14 26 L30 26 Z" fill="{ORANGE}" opacity="0.6"/>')
    # 线
    p.append(f'<path d="M30 44 Q34 49 30 52 Q26 55 31 58" fill="none" stroke="{DARKBROWN}" stroke-width="1.5"/>')
    # 飘带蝴蝶结
    p.append(f'<path class="st" d="M31 58 L37 55 L37 61 Z" fill="{TEAL}"/>')
    p.append(f'<path class="st" d="M31 58 L25 55 L25 61 Z" fill="{PURPLE}"/>')
    p.append(gloss(24, 20, 2.6, 3, 0.55))
    return svg("".join(p))

# ---- 南瓜灯（万圣节）----
def icon_pumpkin():
    p = [style()]
    # 瓜身（南瓜瓣）
    p.append(f'<ellipse class="st" cx="32" cy="38" rx="23" ry="18" fill="{ORANGE}"/>')
    p.append(f'<path d="M22 24 Q18 38 22 53" fill="none" stroke="{DARKBROWN}" stroke-width="1.8" opacity="0.55"/>')
    p.append(f'<path d="M42 24 Q46 38 42 53" fill="none" stroke="{DARKBROWN}" stroke-width="1.8" opacity="0.55"/>')
    # 蒂
    p.append(f'<path class="st" d="M30 19 Q32 12 37 13 L36 20 Z" fill="{DARKBROWN}"/>')
    # 鬼脸（三角眼 + 锯齿嘴）
    p.append(f'<path d="M22 34 L27 34 L24.5 39 Z" fill="#3A2A20"/>')
    p.append(f'<path d="M37 34 L42 34 L39.5 39 Z" fill="#3A2A20"/>')
    p.append(f'<path d="M22 44 L26 42 L29 45 L32 42 L35 45 L38 42 L42 44 L39 48 L25 48 Z" fill="#3A2A20"/>')
    p.append(gloss(21, 30, 3, 4, 0.5))
    return svg("".join(p))

# ---- 圣诞老人（芬兰圣诞老人村）----
def icon_santa():
    p = [style()]
    # 帽子（红色三角 + 白边 + 白球）
    p.append(f'<path class="st" d="M20 22 Q32 4 44 22 L20 22 Z" fill="{RED}"/>')
    p.append(f'<path class="st" d="M18 20 Q32 25 46 20 L45 26 Q32 31 19 26 Z" fill="{WHITE}"/>')
    p.append(f'<circle class="st" cx="44" cy="21" r="4" fill="{WHITE}"/>')
    # 脸（肤色）
    p.append(f'<ellipse class="st" cx="32" cy="32" rx="13" ry="11" fill="#FFE2C4"/>')
    # 眼睛
    p.append('<circle cx="27.5" cy="31" r="1.4" fill="#3A2A20"/><circle cx="36.5" cy="31" r="1.4" fill="#3A2A20"/>')
    # 红鼻子
    p.append(f'<circle cx="32" cy="35" r="2.6" fill="{CORAL_RED}" stroke="{INK}" stroke-width="1.2"/>')
    # 白胡子（大）
    p.append(f'<path class="st" d="M19 36 Q20 52 32 53 Q44 52 45 36 Q40 44 32 44 Q24 44 19 36 Z" fill="{WHITE}"/>')
    p.append(gloss(27, 27, 2.5, 2, 0.5))
    return svg("".join(p))

# ---- 旋涡风暴（木星大红斑）----
def icon_storm():
    p = [style()]
    # 风暴椭圆底（橙红，像大红斑）
    p.append(f'<ellipse class="st" cx="32" cy="32" rx="25" ry="17" fill="{RUST}"/>')
    # 螺旋线（深棕）
    p.append(f'<path class="th" d="M32 32 m-2 0 a2 2 0 1 1 4 0 a5 5 0 1 1 -10 0 a8 8 0 1 1 16 0 a11 11 0 1 1 -22 0 a14 14 0 1 1 28 0" stroke-width="2.2"/>')
    # 高光
    p.append(f'<ellipse cx="24" cy="25" rx="6" ry="3" fill="#fff" opacity="0.28"/>')
    p.append(gloss(22, 26, 4, 2.5, 0.35))
    return svg("".join(p))

# ---- 星光闪烁（空气流动让星光一闪一闪）----
def icon_airtwinkle():
    p = [style()]
    # 横向气流：星星上下、左右各画几条"水平走向"的风线（两端尖的波浪），
    # 强调是空气在水平流动、让星光晃动，而不是翅膀。
    def wind(d, w=2.4, op=0.7):
        return f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>'
    # 顶部一条
    p.append(wind("M21 12 Q27 8 32 12 Q37 16 43 12"))
    # 星星上方左右
    p.append(wind("M4 22 Q11 18 18 22", op=0.6))
    p.append(wind("M46 22 Q53 18 60 22", op=0.6))
    # 星星下方左右
    p.append(wind("M4 42 Q11 46 18 42", op=0.6))
    p.append(wind("M46 42 Q53 46 60 42", op=0.6))
    # 底部一条
    p.append(wind("M21 52 Q27 56 32 52 Q37 48 43 52"))
    # 中央星星（在气流之上）
    p.append(f'<path class="st" d="M32 16 L36 27 L48 28 L39 35 L42 47 L32 40 L22 47 L25 35 L16 28 L28 27 Z" fill="{AMBER}"/>')
    # 闪烁小光点
    p.append(f'<path d="M12 30 l1.4 3 L16.5 34.4 L13.4 35.8 L12 39 l-1.4-3.2 L6.1 34.4 L9.2 33 Z" fill="{YELLOW}"/>')
    p.append(f'<path d="M52 30 l1.2 2.6 L56 34 l-2.8 1.4 L52 38 l-1.2-2.6 L48 34 l2.8-1.4 Z" fill="{YELLOW}"/>')
    p.append(gloss(29, 28, 2.5, 3, 0.6))
    return svg("".join(p))

# ---- 铁锈色土壤 / 岩石（火星为什么红）----
def icon_rustsoil():
    p = [style()]
    # 红色地表起伏
    p.append(f'<path class="st" d="M5 58 Q5 44 18 42 L26 36 L36 42 L48 40 Q59 42 59 58 Z" fill="{RUST}"/>')
    # 小岩石块
    p.append(f'<path class="st" d="M18 40 Q14 33 20 31 Q27 30 28 37 Q26 41 18 40 Z" fill="{RUSTD}"/>')
    p.append(f'<path class="st" d="M40 42 Q37 36 43 34 Q49 34 49 40 Q47 43 40 42 Z" fill="{RUSTD}"/>')
    # 铁锈颗粒
    for x, y in [(13, 50), (24, 50), (33, 52), (44, 49), (52, 53)]:
        p.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="{DARKBROWN}" opacity="0.7"/>')
    p.append(gloss(18, 36, 3, 2, 0.4))
    return svg("".join(p))

# ============================================================
# 注册
# ============================================================
ICONS = {
    # 自然地理
    "pine": icon_pine,
    "grassland": icon_grassland,
    "shanshui": icon_shanshui,
    "coral": icon_coral,
    "island": icon_island,
    # 生活 / 物品 / 航天
    "spoon": icon_spoon,
    "compass": icon_compass,
    "sleepingbag": icon_sleepingbag,
    "waterpouch": icon_waterpouch,
    "kite": icon_kite,
    "pumpkin": icon_pumpkin,
    "santa": icon_santa,
    # 天文概念
    "storm": icon_storm,
    "airtwinkle": icon_airtwinkle,
    "rustsoil": icon_rustsoil,
}

if __name__ == "__main__":
    ok, bad = emit(ICONS, "concept")
    print(f"=== 概念图标完成：{len(ok)} 个；XML 失败 = {len(bad)} ===")
