# -*- coding: utf-8 -*-
"""
探险岛 · 生活物品类图标重绘（玩具文具 + 交通 + 建筑 + 家具）
绘本手绘风：深棕描边 INK、水彩平涂、圆润可爱、半透明白色高光。
全部 64x64，shop 为 96x96。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icon_common import *


# ---------------------------------------------------------------- 玩具文具
def icon_ball():
    """花皮球（彩色四瓣沙滩球）"""
    p = [style()]
    # 四色西瓜瓣
    p.append(f'<path d="M32 32 L18.6 18.6 A19 19 0 0 1 45.4 18.6 Z" fill="{RED}"/>')
    p.append(f'<path d="M32 32 L45.4 18.6 A19 19 0 0 1 45.4 45.4 Z" fill="{BLUE}"/>')
    p.append(f'<path d="M32 32 L45.4 45.4 A19 19 0 0 1 18.6 45.4 Z" fill="{YELLOW}"/>')
    p.append(f'<path d="M32 32 L18.6 45.4 A19 19 0 0 1 18.6 18.6 Z" fill="{GREEN}"/>')
    p.append(f'<circle class="st" cx="32" cy="32" r="19" fill="none"/>')
    p.append(gloss(24, 23, 3.2, 5, 0.6))
    return svg("".join(p))


def icon_balloon():
    """气球（带绳）"""
    p = [style()]
    p.append(f'<ellipse class="st" cx="32" cy="25" rx="15" ry="18" fill="{RED}"/>')
    p.append(f'<path class="st" d="M29 41 L35 41 L32 46 Z" fill="{RED}"/>')
    p.append(f'<path d="M32 46 Q27 52 33 58" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    p.append(gloss(25, 17, 4, 6, 0.55))
    return svg("".join(p))


def icon_block():
    """字母积木（A）"""
    p = [style()]
    p.append(f'<rect class="st" x="9" y="9" width="46" height="46" rx="11" fill="{AMBER}"/>')
    p.append(f'<circle cx="16" cy="16" r="2.4" fill="{CREAM}"/><circle cx="48" cy="16" r="2.4" fill="{CREAM}"/>')
    p.append(f'<circle cx="16" cy="48" r="2.4" fill="{CREAM}"/><circle cx="48" cy="48" r="2.4" fill="{CREAM}"/>')
    p.append(f'<text x="32" y="45" text-anchor="middle" font-size="32" font-weight="900" '
             f'fill="{WHITE}" stroke="{INK}" stroke-width="4" paint-order="stroke" '
             f'font-family="Arial, sans-serif">A</text>')
    return svg("".join(p))


def icon_book():
    """翻开的书"""
    p = [style()]
    p.append(f'<path class="st" d="M32 14 Q20 8 8 10 L8 48 Q22 46 32 52 Q42 46 56 48 L56 10 Q44 8 32 14 Z" fill="{BLUE}"/>')
    p.append(f'<path d="M32 16 Q22 11 12 13 L12 46 Q22 44 32 49 Q42 44 52 46 L52 13 Q42 11 32 16 Z" fill="{CREAM}"/>')
    p.append(f'<path d="M32 16 L32 49" stroke="{INK}" stroke-width="1.5" fill="none"/>')
    p.append(f'<path d="M17 22 L27 21 M17 29 L27 28 M37 21 L47 22 M37 28 L47 29" stroke="#C9B89A" stroke-width="1.8" stroke-linecap="round"/>')
    return svg("".join(p))


def icon_dice():
    """骰子（五点）"""
    p = [style()]
    p.append(f'<rect class="st" x="8" y="8" width="48" height="48" rx="12" fill="{WHITE}"/>')
    p.append(f'<circle cx="21" cy="21" r="5" fill="{RED}"/><circle cx="43" cy="21" r="5" fill="{RED}"/>')
    p.append(f'<circle cx="32" cy="32" r="5" fill="{RED}"/>')
    p.append(f'<circle cx="21" cy="43" r="5" fill="{RED}"/><circle cx="43" cy="43" r="5" fill="{RED}"/>')
    p.append(gloss(18, 16, 4, 2.5, 0.85))
    return svg("".join(p))


def icon_gift():
    """礼物盒（蝴蝶结）"""
    p = [style()]
    p.append(f'<rect class="st" x="11" y="28" width="42" height="26" rx="4" fill="{CORAL}"/>')
    p.append(f'<rect class="st" x="8" y="19" width="48" height="11" rx="4" fill="{RED}"/>')
    p.append(f'<rect x="29" y="19" width="6" height="35" fill="{YELLOW}"/>')
    p.append(f'<path class="st" d="M32 19 Q22 6 15 12 Q11 19 25 19 Z" fill="{YELLOW}"/>')
    p.append(f'<path class="st" d="M32 19 Q42 6 49 12 Q53 19 39 19 Z" fill="{AMBER}"/>')
    p.append(f'<circle cx="32" cy="18" r="3.5" fill="{AMBER}"/>')
    p.append(gloss(17, 34, 2.5, 7, 0.35))
    return svg("".join(p))


def icon_hat():
    """学士帽（平顶板 + 帽围 + 流苏）"""
    p = [style()]
    p.append(f'<path class="st" d="M23 25 L41 25 L41 36 Q32 40 23 36 Z" fill="{BLUE}"/>')
    p.append(f'<path class="st" d="M11 21 Q32 13 53 21 Q32 28 11 21 Z" fill="{NAVY}"/>')
    p.append(f'<path d="M45 22 Q52 25 50 33" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-linecap="round"/>')
    p.append(f'<circle cx="49.5" cy="34" r="2.6" fill="{AMBER}"/>')
    p.append(f'<circle cx="32" cy="21" r="2" fill="{AMBER}"/>')
    return svg("".join(p))


def icon_robot():
    """方头可爱机器人"""
    p = [style()]
    p.append(f'<path d="M32 14 L32 8" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="32" cy="6" r="3.5" fill="{RED}"/>')
    p.append(f'<circle class="st" cx="12" cy="33" r="3.5" fill="{PURPLE}"/>')
    p.append(f'<circle class="st" cx="52" cy="33" r="3.5" fill="{PURPLE}"/>')
    p.append(f'<rect class="st" x="12" y="14" width="40" height="38" rx="10" fill="{PURPLE}"/>')
    p.append(f'<rect x="19" y="22" width="26" height="15" rx="6" fill="#3E3564"/>')
    p.append(f'<circle cx="26" cy="29" r="3.2" fill="#8FF4FF"/><circle cx="38" cy="29" r="3.2" fill="#8FF4FF"/>')
    p.append(f'<circle cx="27" cy="28" r="1.1" fill="{WHITE}"/><circle cx="39" cy="28" r="1.1" fill="{WHITE}"/>')
    p.append(f'<path d="M27 34.5 Q32 37.5 37 34.5" stroke="{WHITE}" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
    p.append(gloss(22, 18, 4, 2, 0.4))
    return svg("".join(p))


def icon_shoe():
    """小童鞋"""
    p = [style()]
    p.append(f'<path class="st" d="M11 42 Q10 48 16 48 L48 48 Q54 48 53 42 L52 38 L13 38 Z" fill="{WHITE}"/>')
    p.append(f'<path class="st" d="M12 38 Q12 28 22 28 L34 28 Q44 28 50 36 L52 38 L12 38 Z" fill="{BLUE}"/>')
    p.append(f'<path d="M21 30 L25 35 M27 29.5 L30 35" stroke="{WHITE}" stroke-width="2" stroke-linecap="round"/>')
    p.append(gloss(20, 33, 2.5, 1.6, 0.5))
    return svg("".join(p))


def icon_magnet():
    """马蹄形磁铁（红/蓝两极）"""
    p = [style()]
    p.append(f'<path class="st" d="M18 10 L18 40 A14 14 0 0 0 46 40 L46 10 L36 10 L36 40 A4 4 0 0 0 28 40 L28 10 Z" fill="{RED}"/>')
    p.append(f'<path d="M36 10 L46 10 L46 40 A14 14 0 0 0 32 54 L32 44 A4 4 0 0 1 36 40 Z" fill="{BLUE}"/>')
    p.append(gloss(22, 16, 2.5, 5, 0.4))
    return svg("".join(p))


def icon_bulb():
    """发光灯泡"""
    p = [style()]
    p.append(f'<path d="M32 4 L32 9 M15 10 L19 14 M49 10 L45 14 M8 25 L13 25 M56 25 L51 25" stroke="{AMBER}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="32" cy="27" r="15" fill="{YELLOW}"/>')
    p.append(f'<path d="M28 29 Q32 23 36 29" stroke="#E5A916" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    p.append(f'<rect class="st" x="26" y="41" width="12" height="6" rx="2.5" fill="#9AA7B4"/>')
    p.append(f'<rect x="28" y="48" width="8" height="4" rx="2" fill="#7E8B98"/>')
    p.append(gloss(26, 20, 3.5, 5, 0.6))
    return svg("".join(p))


def icon_flask():
    """科学烧瓶（彩色液体+气泡）"""
    p = [style()]
    p.append(f'<path class="st" d="M27 10 L27 24 L14 48 Q11 56 19 56 L45 56 Q53 56 50 48 L37 24 L37 10 Z" fill="#EAF9FF" opacity="0.9"/>')
    p.append(f'<path d="M18 40 L46 40 L50 48 Q52 54 45 54 L19 54 Q12 54 14 48 Z" fill="{PURPLE}"/>')
    p.append(f'<circle cx="26" cy="47" r="2.6" fill="{WHITE}" opacity="0.7"/><circle cx="36" cy="45" r="1.9" fill="{WHITE}" opacity="0.6"/>')
    p.append(f'<rect class="st" x="24" y="4" width="16" height="6" rx="3" fill="{BROWN}"/>')
    p.append(f'<path d="M24 30 L20 42" stroke="{WHITE}" stroke-width="2.6" stroke-linecap="round" opacity="0.8"/>')
    return svg("".join(p))


def icon_goggles():
    """泳镜/护目镜"""
    p = [style()]
    p.append(f'<rect x="6" y="27" width="52" height="10" rx="5" fill="{PURPLE}"/>')
    p.append(f'<rect class="st" x="11" y="22" width="18" height="18" rx="7" fill="{TEAL}"/>')
    p.append(f'<rect class="st" x="35" y="22" width="18" height="18" rx="7" fill="{TEAL}"/>')
    p.append(f'<rect x="29" y="28" width="6" height="5" rx="2.5" fill="{PURPLE}"/>')
    p.append(gloss(16, 26, 3, 2, 0.6))
    p.append(gloss(40, 26, 3, 2, 0.6))
    return svg("".join(p))


def icon_clip():
    """剪贴板（板+纸+夹+对勾）"""
    p = [style()]
    p.append(f'<rect class="st" x="14" y="8" width="36" height="50" rx="6" fill="{BROWN}"/>')
    p.append(f'<rect x="19" y="14" width="26" height="38" rx="3" fill="{WHITE}"/>')
    p.append(f'<path d="M23 24 L41 24 M23 31 L41 31" stroke="#C9D2DA" stroke-width="2.4" stroke-linecap="round"/>')
    p.append(f'<path d="M24 40 L29 45 L39 35" stroke="{LEAF}" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(f'<rect class="st" x="25" y="4" width="14" height="9" rx="4" fill="#9AA7B4"/>')
    p.append(f'<circle cx="32" cy="8.5" r="2" fill="#5B6673"/>')
    return svg("".join(p))


def icon_hanger():
    """衣架"""
    p = [style()]
    p.append(f'<path d="M32 16 Q32 9 37 9 Q41 9 41 13 Q41 16 38 17" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linecap="round"/>')
    p.append(f'<path class="st" d="M32 17 L11 39 Q8 42 12 42 L52 42 Q56 42 53 39 Z" fill="{BROWN}"/>')
    p.append(f'<path d="M14 42 L50 42" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    return svg("".join(p))


# ---------------------------------------------------------------- 交通
def icon_bus():
    """校车"""
    p = [style()]
    p.append(f'<rect class="st" x="8" y="18" width="48" height="28" rx="6" fill="{YELLOW}"/>')
    p.append(f'<rect x="13" y="23" width="10" height="9" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="27" y="23" width="10" height="9" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="41" y="23" width="10" height="9" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="8" y="38" width="48" height="4" fill="{RED}"/>')
    p.append(f'<circle cx="20" cy="48" r="5.5" fill="#3A3A46"/><circle cx="44" cy="48" r="5.5" fill="#3A3A46"/>')
    p.append(f'<circle cx="20" cy="48" r="2" fill="{WHITE}"/><circle cx="44" cy="48" r="2" fill="{WHITE}"/>')
    return svg("".join(p))


def icon_car():
    """小汽车"""
    p = [style()]
    p.append(f'<path class="st" d="M17 35 L21 25 L43 25 L47 35 Z" fill="{CORAL}"/>')
    p.append(f'<path d="M24 27 L24 34 M40 27 L40 34" stroke="{INK}" stroke-width="1.6"/>')
    p.append(f'<rect class="st" x="9" y="35" width="46" height="11" rx="4" fill="{RED}"/>')
    p.append(f'<circle cx="20" cy="48" r="5.5" fill="#3A3A46"/><circle cx="44" cy="48" r="5.5" fill="#3A3A46"/>')
    p.append(f'<circle cx="20" cy="48" r="2" fill="{WHITE}"/><circle cx="44" cy="48" r="2" fill="{WHITE}"/>')
    return svg("".join(p))


def icon_train():
    """小火车"""
    p = [style()]
    p.append(f'<rect x="12" y="15" width="6" height="11" rx="2" fill="#7E8B98"/>')
    p.append(f'<circle cx="15" cy="11" r="3.5" fill="{WHITE}" opacity="0.9"/>')
    p.append(f'<rect class="st" x="8" y="26" width="30" height="18" rx="5" fill="{RED}"/>')
    p.append(f'<rect class="st" x="36" y="16" width="18" height="28" rx="4" fill="{CORAL}"/>')
    p.append(f'<rect x="40" y="21" width="8" height="7" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="8" y="40" width="44" height="5" rx="2.5" fill="#7E2A20"/>')
    p.append(f'<circle cx="16" cy="50" r="5.5" fill="#3A3A46"/><circle cx="31" cy="50" r="5.5" fill="#3A3A46"/><circle cx="45" cy="50" r="5.5" fill="#3A3A46"/>')
    p.append(f'<circle cx="16" cy="50" r="2" fill="{WHITE}"/><circle cx="31" cy="50" r="2" fill="{WHITE}"/><circle cx="45" cy="50" r="2" fill="{WHITE}"/>')
    return svg("".join(p))


# ---------------------------------------------------------------- 建筑
def icon_castle():
    """城堡"""
    p = [style()]
    p.append(f'<rect class="st" x="10" y="24" width="12" height="32" rx="2" fill="{PINK}"/>')
    p.append(f'<rect class="st" x="42" y="24" width="12" height="32" rx="2" fill="{PINK}"/>')
    p.append(f'<rect class="st" x="21" y="32" width="22" height="24" rx="3" fill="{CORAL}"/>')
    p.append(f'<rect x="12" y="18" width="4" height="8" fill="{PINK}"/><rect x="18" y="18" width="4" height="8" fill="{PINK}"/>')
    p.append(f'<rect x="42" y="18" width="4" height="8" fill="{PINK}"/><rect x="48" y="18" width="4" height="8" fill="{PINK}"/>')
    p.append(f'<path d="M16 18 L16 9 L24 12 L16 15 Z" fill="{RED}"/>')
    p.append(f'<path d="M48 18 L48 9 L56 12 L48 15 Z" fill="{RED}"/>')
    p.append(f'<path d="M28 56 L28 46 Q32 41 36 46 L36 56 Z" fill="{PURPLE}"/>')
    p.append(f'<circle cx="16" cy="32" r="2.4" fill="{WHITE}"/><circle cx="48" cy="32" r="2.4" fill="{WHITE}"/>')
    return svg("".join(p))


def icon_school():
    """学校楼"""
    p = [style()]
    p.append(f'<path class="st" d="M6 32 L32 12 L58 32 Z" fill="{RED}"/>')
    p.append(f'<rect class="st" x="12" y="32" width="40" height="24" rx="3" fill="{CREAM}"/>')
    p.append(f'<rect class="st" x="27" y="42" width="10" height="14" rx="4" fill="{DARKBROWN}"/>')
    p.append(f'<rect x="16" y="37" width="8" height="8" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="40" y="37" width="8" height="8" rx="2" fill="#BEE3F5"/>')
    p.append(f'<path d="M32 12 L32 4" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    p.append(f'<path d="M32 4 L42 7.5 L32 11 Z" fill="{ORANGE}"/>')
    p.append(f'<circle cx="32" cy="28" r="4" fill="{WHITE}"/><circle cx="32" cy="28" r="1.4" fill="{RED}"/>')
    return svg("".join(p))


def icon_home():
    """独栋小房子"""
    p = [style()]
    p.append(f'<path class="st" d="M8 30 L32 10 L56 30 Z" fill="{ORANGE}"/>')
    p.append(f'<rect class="st" x="14" y="28" width="36" height="26" rx="4" fill="{CREAM}"/>')
    p.append(f'<rect class="st" x="27" y="38" width="10" height="16" rx="4" fill="{DARKBROWN}"/>')
    p.append(f'<circle cx="34.5" cy="46" r="1.2" fill="{YELLOW}"/>')
    p.append(f'<rect x="18" y="34" width="7" height="7" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect x="39" y="34" width="7" height="7" rx="2" fill="#BEE3F5"/>')
    return svg("".join(p))


def icon_station():
    """车站（带站牌）"""
    p = [style()]
    p.append(f'<rect x="30.5" y="22" width="3" height="32" fill="#7E8B98"/>')
    p.append(f'<rect class="st" x="11" y="10" width="42" height="15" rx="5" fill="{TEAL}"/>')
    p.append(f'<rect x="20" y="14" width="18" height="7" rx="2.5" fill="{WHITE}"/>')
    p.append(f'<circle cx="25" cy="22.5" r="1.6" fill="#3A3A46"/><circle cx="33" cy="22.5" r="1.6" fill="#3A3A46"/>')
    p.append(f'<path d="M42 17 L48 17" stroke="{WHITE}" stroke-width="2.5" stroke-linecap="round"/>')
    p.append(f'<rect x="20" y="54" width="24" height="4" rx="2" fill="#9AA7B4"/>')
    return svg("".join(p))


def icon_windmill():
    """风车房"""
    p = [style()]
    p.append(f'<path class="st" d="M26 52 L28 26 L36 26 L38 52 Z" fill="{CREAM}"/>')
    p.append(f'<rect x="29" y="44" width="6" height="8" rx="1.5" fill="{DARKBROWN}"/>')
    p.append(f'<path d="M32 26 L32 9 M32 26 L46 16 M32 26 L18 16 M32 26 L44 36" stroke="{BROWN}" stroke-width="4" stroke-linecap="round"/>')
    p.append(f'<circle class="st" cx="32" cy="26" r="3.5" fill="{RED}"/>')
    return svg("".join(p))


# ---------------------------------------------------------------- 家具
def icon_bed():
    """小床"""
    p = [style()]
    p.append(f'<rect class="st" x="8" y="20" width="8" height="26" rx="3" fill="{BROWN}"/>')
    p.append(f'<rect class="st" x="8" y="34" width="48" height="12" rx="4" fill="{BLUE}"/>')
    p.append(f'<rect class="st" x="15" y="28" width="13" height="8" rx="3" fill="{WHITE}"/>')
    p.append(f'<rect x="50" y="27" width="6" height="19" rx="2" fill="{BROWN}"/>')
    p.append(f'<path d="M28 40 L50 40" stroke="{WHITE}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
    return svg("".join(p))


def icon_chair():
    """小木椅（靠背＋座面＋四条腿）"""
    p = [style()]
    W = BROWN
    # 靠背立柱（兼后腿，竖在座面之后）
    p.append(f'<rect class="st" x="15" y="10" width="6" height="23" rx="3" fill="{W}"/>')
    p.append(f'<rect class="st" x="43" y="10" width="6" height="23" rx="3" fill="{W}"/>')
    # 靠背顶梁
    p.append(f'<rect class="st" x="13" y="9" width="38" height="8" rx="4" fill="{W}"/>')
    # 座面
    p.append(f'<rect class="st" x="11" y="31" width="42" height="9" rx="3.5" fill="{W}"/>')
    # 两条前腿
    p.append(f'<rect class="st" x="14" y="40" width="6" height="15" rx="2.5" fill="{W}"/>')
    p.append(f'<rect class="st" x="44" y="40" width="6" height="15" rx="2.5" fill="{W}"/>')
    # 座面高光
    p.append(f'<rect x="15" y="33" width="20" height="2.4" rx="1.2" fill="{WHITE}" opacity="0.55"/>')
    return svg("".join(p))


# ---------------------------------------------------------------- 商店（96x96）
def icon_shop():
    """商店建筑（96x96，带雨棚招牌）"""
    p = [style()]
    # 建筑主体
    p.append(f'<rect class="st" x="18" y="46" width="60" height="42" rx="4" fill="{CREAM}"/>')
    # 门
    p.append(f'<rect class="st" x="42" y="62" width="14" height="26" rx="2" fill="{DARKBROWN}"/>')
    p.append(f'<circle cx="53" cy="76" r="1.6" fill="{YELLOW}"/>')
    # 橱窗
    p.append(f'<rect class="st" x="24" y="58" width="13" height="13" rx="2" fill="#BEE3F5"/>')
    p.append(f'<rect class="st" x="61" y="58" width="13" height="13" rx="2" fill="#BEE3F5"/>')
    # 雨棚
    p.append(f'<path d="M14 40 L82 40 L77 50 L19 50 Z" fill="{RED}"/>')
    p.append(f'<path d="M26 40 L22.5 50 L30 50 L32 40 Z M42 40 L40.5 50 L48 50 L50 40 Z M58 40 L56.5 50 L64 50 L66 40 Z" fill="{WHITE}"/>')
    p.append(f'<circle cx="19" cy="50" r="3" fill="{RED}"/><circle cx="31" cy="50" r="3" fill="{WHITE}"/>')
    p.append(f'<circle cx="43" cy="50" r="3" fill="{RED}"/><circle cx="55" cy="50" r="3" fill="{WHITE}"/>')
    p.append(f'<circle cx="67" cy="50" r="3" fill="{RED}"/><circle cx="79" cy="50" r="3" fill="{WHITE}"/>')
    # 招牌
    p.append(f'<rect class="st" x="30" y="26" width="36" height="12" rx="6" fill="{YELLOW}"/>')
    # 屋顶小旗
    p.append(f'<path d="M47 12 L47 26" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>')
    p.append(f'<path d="M47 12 L57 15 L47 18 Z" fill="{RED}"/>')
    return svg("".join(p), vb="0 0 96 96")


ICONS = {
    "ball": icon_ball, "balloon": icon_balloon, "block": icon_block, "book": icon_book,
    "dice": icon_dice, "gift": icon_gift, "hat": icon_hat, "robot": icon_robot,
    "shoe": icon_shoe, "magnet": icon_magnet, "bulb": icon_bulb, "flask": icon_flask,
    "goggles": icon_goggles, "clip": icon_clip, "hanger": icon_hanger,
    "bus": icon_bus, "car": icon_car, "train": icon_train,
    "castle": icon_castle, "school": icon_school, "home": icon_home,
    "station": icon_station, "windmill": icon_windmill, "bed": icon_bed, "chair": icon_chair,
    "shop": icon_shop,
}

if __name__ == "__main__":
    emit(ICONS, "life")
