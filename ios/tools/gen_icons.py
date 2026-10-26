#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_icons.py — 探险岛图标生成器（双层设计语言）

框架层（外部/导航/通用/吉祥物/装饰）：绘本手绘风（深棕描边 + 水彩平涂 + 纸张）
内容层（天文/地理等学科题目内部）：写实图标（球体光照 + 真实纹理 + 大气光晕）

输出：design/assets/icons/{name}.svg（按文件名复用，重绘即全局生效）

用法：
  python3 ios/tools/gen_icons.py            # 生成全部
  python3 ios/tools/gen_icons.py --only earth mars
  python3 ios/tools/gen_icons.py --group real
"""
import os, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT  = os.path.join(ROOT, "design", "assets", "icons")

# ----------------------------------------------------------------------
# 通用工具
# ----------------------------------------------------------------------
def svg(body, vb=64):
    dims = f"0 0 {vb} {vb}" if isinstance(vb, (int, float)) else vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{dims}">'
            f'{body}</svg>')

# ----------------------------------------------------------------------
# 写实天体
# 关键：clipPath 把纹理限制在球内；径向渐变做单侧光照；大气光晕在球外
# 64 画布，球心 (32,32)，半径 R
# ----------------------------------------------------------------------
def _sphere_defs(name, base_stops, glow=None):
    """球体光照渐变：cx/cy 偏左上（光源），中心亮、右下暗。
    base_stops: 固有色明暗（受光面→背光面），用 radial 叠加。"""
    s = f'''<radialGradient id="{name}-lit" cx="34%" cy="30%" r="78%">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.92"/>
      <stop offset="38%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="72%" stop-color="#000000" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.42"/>
    </radialGradient>
    <radialGradient id="{name}-base" cx="38%" cy="34%" r="75%">
      {base_stops}
    </radialGradient>'''
    if glow:
        s += f'''<radialGradient id="{name}-glow" cx="50%" cy="50%" r="50%">
          <stop offset="62%" stop-color="{glow}" stop-opacity="0"/>
          <stop offset="78%" stop-color="{glow}" stop-opacity="0.55"/>
          <stop offset="92%" stop-color="{glow}" stop-opacity="0.18"/>
          <stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
        </radialGradient>'''
    return s

def sphere(name, R, base_stops, texture="", glow=None, halo_r=32):
    """组装一个写实球体。texture 已带 clip（外部包 clipPath）。"""
    cx = cy = 32
    defs = _sphere_defs(name, base_stops, glow)
    clip = f'''<clipPath id="{name}-clip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'''
    out = f"<defs>{defs}{clip}</defs>"
    if glow:
        out += f'<circle cx="{cx}" cy="{cy}" r="{halo_r}" fill="url(#{name}-glow)"/>'
    out += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{name}-base)"/>'
    if texture:
        out += f'<g clip-path="url(#{name}-clip)">{texture}</g>'
    out += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{name}-lit)"/>'
    # 边缘暗化（terminator）
    out += (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" '
            f'stroke="#000" stroke-opacity="0.18" stroke-width="1.2"/>')
    return out

# 太阳：发光恒星
def icon_sun():
    body = '''<defs>
      <radialGradient id="sun-core" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#FFFDF0"/>
        <stop offset="45%" stop-color="#FFEC8A"/>
        <stop offset="78%" stop-color="#FFC83D"/>
        <stop offset="100%" stop-color="#FF9E22"/>
      </radialGradient>
      <radialGradient id="sun-corona" cx="50%" cy="50%" r="50%">
        <stop offset="40%" stop-color="#FFD23D" stop-opacity="0"/>
        <stop offset="58%" stop-color="#FFCE4D" stop-opacity="0.85"/>
        <stop offset="74%" stop-color="#FFA52F" stop-opacity="0.4"/>
        <stop offset="100%" stop-color="#FF9E22" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <circle cx="32" cy="32" r="31" fill="url(#sun-corona)"/>
    <circle cx="32" cy="32" r="20" fill="url(#sun-core)"/>
    <g fill="#C96E12" opacity="0.5">
      <circle cx="26" cy="30" r="1.8"/><circle cx="37" cy="35" r="1.4"/><circle cx="33" cy="25" r="1.2"/>
    </g>
    <circle cx="25" cy="25" r="6" fill="#FFF" opacity="0.35"/>'''
    return svg(body)

# 水星：灰岩石 + 陨石坑
def icon_mercury():
    tex = '''
      <path d="M14 30 Q22 24 30 30 Q26 38 18 37 Z" fill="#8A857E" opacity="0.55"/>
      <path d="M34 40 Q44 36 50 42 Q44 48 36 46 Z" fill="#7E7972" opacity="0.5"/>
      <g fill="#6E6962" opacity="0.6">
        <circle cx="24" cy="26" r="3.2"/><circle cx="40" cy="30" r="2.4"/>
        <circle cx="33" cy="38" r="1.8"/><circle cx="22" cy="42" r="2.2"/><circle cx="44" cy="22" r="1.6"/>
      </g>
      <g fill="#B8B3AC" opacity="0.6">
        <circle cx="23" cy="25" r="1.1"/><circle cx="39" cy="29" r="0.8"/><circle cx="21" cy="41" r="0.8"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#C9C4BC"/><stop offset="55%" stop-color="#9A958E"/>'
            '<stop offset="100%" stop-color="#6E6962"/>')
    return svg(sphere("mercury", 21, base, tex))

# 金星：奶油黄 + 浓厚云层 + 大气光晕
def icon_venus():
    tex = '''
      <g fill="none" stroke="#D9B45A" stroke-width="2.4" opacity="0.6" stroke-linecap="round">
        <path d="M12 24 Q32 19 52 24"/>
        <path d="M11 31 Q32 26 53 31"/>
        <path d="M12 38 Q32 33 52 38"/>
        <path d="M14 44 Q32 40 50 44"/>
      </g>
      <g fill="none" stroke="#FFF6D8" stroke-width="1.6" opacity="0.7" stroke-linecap="round">
        <path d="M14 22 Q30 18 48 22"/><path d="M13 35 Q32 31 51 35"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#FBEFC0"/><stop offset="55%" stop-color="#E8C97A"/>'
            '<stop offset="100%" stop-color="#C99E48"/>')
    return svg(sphere("venus", 23, base, tex, glow="#FFE9A8", halo_r=31))

# 地球：真实海洋 + 大陆 + 云层 + 蓝色大气（重点）
def icon_earth():
    # 视角：非洲居中、欧洲在北、阿拉伯半岛、右侧亚洲、左侧一点美洲
    tex = '''
      <!-- 大陆（受光面偏亮绿，背光面偏褐） -->
      <g>
        <!-- 欧洲 -->
        <path d="M27 17 Q31 14 34 17 Q33 22 29 22 Q26 20 27 17 Z" fill="#7BB863"/>
        <!-- 非洲 -->
        <path d="M26 23 Q32 20 37 24 Q39 30 36 37 Q33 44 30 43 Q26 36 25 30 Q24 26 26 23 Z" fill="#6FB457"/>
        <!-- 撒哈拉（北非偏黄） -->
        <path d="M27 23 Q33 21 36 24 Q33 27 28 26 Z" fill="#C9B463"/>
        <!-- 阿拉伯半岛 -->
        <path d="M38 25 Q42 25 43 29 Q40 31 38 29 Z" fill="#B8A85A"/>
        <!-- 亚洲 -->
        <path d="M40 17 Q48 16 50 23 Q47 27 42 25 Q39 21 40 17 Z" fill="#74B05C"/>
        <!-- 东南亚群岛 -->
        <path d="M42 31 Q47 31 48 34 Q45 36 42 34 Z" fill="#69AC54"/>
        <!-- 左侧美洲一角 -->
        <path d="M12 26 Q16 24 19 27 Q17 33 14 34 Q11 30 12 26 Z" fill="#74B05C"/>
        <!-- 南极一点 -->
        <path d="M26 49 Q32 48 38 50 L38 54 L26 54 Z" fill="#E8F0E8"/>
      </g>
      <!-- 云层 -->
      <g fill="#fff" opacity="0.78">
        <path d="M18 20 Q24 17 29 20 Q27 23 21 23 Z"/>
        <path d="M34 14 Q41 13 45 17 Q40 19 35 17 Z"/>
        <path d="M38 33 Q45 32 48 36 Q43 38 38 36 Z"/>
        <path d="M15 38 Q20 37 23 40 Q18 42 15 41 Z"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#3FA6E0"/><stop offset="45%" stop-color="#1E74C4"/>'
            '<stop offset="100%" stop-color="#0E4C8A"/>')
    return svg(sphere("earth", 25, base, tex, glow="#7FC8FF", halo_r=32))

# 火星：红橙 + 大流沙暗区 + 北极冰盖 + 陨石坑（重点）
def icon_mars():
    tex = '''
      <!-- 北极冰盖 -->
      <path d="M26 12 Q32 9 38 12 Q35 15 32 15 Q29 15 26 12 Z" fill="#F4EDE0"/>
      <!-- Syrtis Major 大流沙（暗区） -->
      <path d="M22 24 Q28 22 30 28 Q27 34 22 33 Q19 28 22 24 Z" fill="#8A4A36" opacity="0.7"/>
      <!-- 其他暗区 -->
      <path d="M36 36 Q44 34 47 40 Q42 44 36 41 Z" fill="#9A5440" opacity="0.55"/>
      <path d="M14 38 Q19 37 20 42 Q16 44 13 42 Z" fill="#9A5440" opacity="0.5"/>
      <!-- Hellas 盆地（亮） -->
      <ellipse cx="40" cy="46" rx="4" ry="3" fill="#E89078" opacity="0.7"/>
      <!-- 陨石坑 -->
      <g fill="#7A3E2E" opacity="0.5">
        <circle cx="34" cy="20" r="1.6"/><circle cx="44" cy="28" r="1.3"/><circle cx="26" cy="40" r="1.5"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#E89078"/><stop offset="50%" stop-color="#D06048"/>'
            '<stop offset="100%" stop-color="#9A3E2E"/>')
    return svg(sphere("mars", 22, base, tex, glow="#FF9A7A", halo_r=30))

# 木星：横向云带 + 大红斑
def icon_jupiter():
    tex = '''
      <g>
        <path d="M10 20 Q32 16 54 20 L54 25 Q32 21 10 25 Z" fill="#E8C99E" opacity="0.8"/>
        <path d="M10 27 Q32 24 54 27 L54 30 Q32 27 10 30 Z" fill="#B98F60" opacity="0.7"/>
        <path d="M10 33 Q32 30 54 33 L54 37 Q32 34 10 37 Z" fill="#D9B98A" opacity="0.8"/>
        <path d="M10 40 Q32 37 54 40 L54 44 Q32 41 10 44 Z" fill="#B98F60" opacity="0.65"/>
        <!-- 湍流 -->
        <g fill="none" stroke="#F7E6C8" stroke-width="1.4" opacity="0.6">
          <path d="M16 22 Q20 20 24 22M30 28 Q34 26 38 28M22 38 Q26 36 30 38"/>
        </g>
      </g>
      <!-- 大红斑 -->
      <ellipse cx="40" cy="40" rx="6" ry="3.6" fill="#D45A3E"/>
      <ellipse cx="40" cy="39" rx="4" ry="2" fill="#E88A6A" opacity="0.7"/>'''
    base = ('<stop offset="0" stop-color="#F2DDB8"/><stop offset="55%" stop-color="#DDB988"/>'
            '<stop offset="100%" stop-color="#B98F60"/>')
    return svg(sphere("jupiter", 24, base, tex))

# 土星：球 + 壮观环（前后）
def icon_saturn():
    name = "saturn"
    base = ('<stop offset="0" stop-color="#F2E0B0"/><stop offset="55%" stop-color="#E0C084"/>'
            '<stop offset="100%" stop-color="#B9955A"/>')
    tex = '''
      <g fill="none" stroke="#C9A868" stroke-width="1.6" opacity="0.6">
        <path d="M18 26 Q32 23 46 26"/><path d="M17 34 Q32 31 47 34"/><path d="M19 40 Q32 38 45 40"/>
      </g>'''
    inner = sphere(name, 20, base, tex)
    # 环：后半（在球后）+ 前半（在球前）
    ring_back = (f'<ellipse cx="32" cy="32" rx="29" ry="9" fill="none" '
                 f'stroke="#D9BC82" stroke-width="4.4" opacity="0.92" '
                 f'transform="rotate(-16 32 32)" stroke-dasharray="70 100"/>')
    ring_front = (f'<ellipse cx="32" cy="32" rx="29" ry="9" fill="none" '
                  f'stroke="#EBD29A" stroke-width="4.4" opacity="0.98" '
                  f'transform="rotate(-16 32 32)" stroke-dasharray="100 70" '
                  f'stroke-dashoffset="-70"/>')
    # 卡西尼缝（细线）
    seam = (f'<ellipse cx="32" cy="32" rx="29" ry="9" fill="none" '
            f'stroke="#A88858" stroke-width="0.8" opacity="0.7" transform="rotate(-16 32 32)"/>')
    return svg(f'<defs></defs>' + ring_back + inner + ring_front + seam)

# 天王星：淡青 + 弱环
def icon_uranus():
    tex = '''
      <g fill="none" stroke="#9AD0D8" stroke-width="1.6" opacity="0.6">
        <path d="M16 27 Q32 24 48 27"/><path d="M17 36 Q32 33 47 36"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#BCECEE"/><stop offset="55%" stop-color="#8AD0D8"/>'
            '<stop offset="100%" stop-color="#5CA0B0"/>')
    body = sphere("uranus", 21, base, tex, glow="#BCECEE", halo_r=29)
    ring = (f'<ellipse cx="32" cy="32" rx="27" ry="7" fill="none" stroke="#B8D8D8" '
            f'stroke-width="1.8" opacity="0.7" transform="rotate(-64 32 32)"/>')
    return svg(ring + body)

# 海王星：深蓝 + 大暗斑 + 白云
def icon_neptune():
    tex = '''
      <g fill="#fff" opacity="0.7">
        <path d="M14 24 Q24 21 30 24 Q26 27 18 27 Z"/>
        <path d="M34 30 Q44 28 49 32 Q43 34 35 33 Z"/>
      </g>
      <ellipse cx="30" cy="38" rx="5" ry="3" fill="#1B3E86"/>
      <ellipse cx="42" cy="26" rx="3.4" ry="2" fill="#4A7AD0" opacity="0.8"/>'''
    base = ('<stop offset="0" stop-color="#5A86E0"/><stop offset="55%" stop-color="#2F5BC0"/>'
            '<stop offset="100%" stop-color="#1B3878"/>')
    return svg(sphere("neptune", 21, base, tex, glow="#5A86E0", halo_r=29))

# 月球（满月）：灰 + 月海 + 陨石坑
def icon_moon():
    tex = '''
      <g fill="#8A8884" opacity="0.55">
        <ellipse cx="25" cy="26" rx="7" ry="6"/><ellipse cx="40" cy="36" rx="6" ry="5"/>
        <ellipse cx="38" cy="22" rx="4" ry="3.4"/>
      </g>
      <g fill="#6E6C68" opacity="0.5">
        <circle cx="22" cy="40" r="2.2"/><circle cx="44" cy="28" r="1.8"/><circle cx="30" cy="33" r="1.4"/>
      </g>
      <g fill="#B8B6B0" opacity="0.7">
        <circle cx="24" cy="24" r="1.4"/><circle cx="39" cy="34" r="1.2"/>
      </g>'''
    base = ('<stop offset="0" stop-color="#E0DED8"/><stop offset="55%" stop-color="#B8B6B0"/>'
            '<stop offset="100%" stop-color="#8A8884"/>')
    return svg(sphere("moon", 24, base, tex, glow="#E8E4D0", halo_r=31))

# 黑洞：事件视界 + 吸积盘 + 光子环（引力透镜）
def icon_blackhole():
    body = '''<defs>
      <linearGradient id="bh-disk" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#FF8A2A"/><stop offset="50" stop-color="#FFD96B"/>
        <stop offset="100" stop-color="#FFF3C4"/>
      </linearGradient>
      <radialGradient id="bh-core" cx="50%" cy="50%" r="50%">
        <stop offset="70%" stop-color="#000"/><stop offset="100%" stop-color="#0a0a12"/>
      </radialGradient>
    </defs>
    <!-- 吸积盘（后弧，从黑洞上方穿过，被透镜拉亮） -->
    <path d="M8 26 Q32 6 56 26" fill="none" stroke="url(#bh-disk)" stroke-width="4.6" stroke-linecap="round" opacity="0.95"/>
    <!-- 吸积盘（前弧） -->
    <ellipse cx="32" cy="33" rx="26" ry="8.5" fill="none" stroke="url(#bh-disk)" stroke-width="5" opacity="0.95"/>
    <!-- 外发光 -->
    <ellipse cx="32" cy="32" rx="26" ry="9" fill="none" stroke="#FFB24D" stroke-width="9" opacity="0.25"/>
    <!-- 事件视界 -->
    <circle cx="32" cy="31" r="14" fill="url(#bh-core)"/>
    <!-- 光子环 -->
    <circle cx="32" cy="31" r="14" fill="none" stroke="#FFE9A8" stroke-width="1.4" opacity="0.9"/>
    <circle cx="32" cy="31" r="15.5" fill="none" stroke="#FFC84D" stroke-width="1" opacity="0.5"/>'''
    return svg(body)

# 彗星：彗核 + 彗发 + 离子尾/尘埃尾
def icon_comet():
    body = '''<defs>
      <radialGradient id="comet-halo" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#fff" stop-opacity="0.95"/>
        <stop offset="45%" stop-color="#BFE4FF" stop-opacity="0.6"/>
        <stop offset="100%" stop-color="#8FC8FF" stop-opacity="0"/>
      </radialGradient>
      <linearGradient id="comet-ion" x1="1" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#9FD0FF" stop-opacity="0.85"/>
        <stop offset="100%" stop-color="#9FD0FF" stop-opacity="0"/>
      </linearGradient>
      <linearGradient id="comet-dust" x1="1" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff" stop-opacity="0.8"/>
        <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <!-- 离子尾（蓝、直） -->
    <path d="M36 30 Q22 38 8 50 Q14 38 30 32 Z" fill="url(#comet-ion)"/>
    <!-- 尘埃尾（白、弯） -->
    <path d="M38 33 Q26 44 16 56 Q24 44 34 36 Z" fill="url(#comet-dust)"/>
    <!-- 彗发 -->
    <circle cx="40" cy="27" r="16" fill="url(#comet-halo)"/>
    <!-- 彗核 -->
    <circle cx="40" cy="27" r="5" fill="#F2F6FA"/>
    <circle cx="38" cy="25" r="2" fill="#fff"/>'''
    return svg(body)

# 流星：亮头 + 渐变尾迹
def icon_meteor():
    body = '''<defs>
      <linearGradient id="met-tail" x1="1" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff" stop-opacity="0.95"/>
        <stop offset="100%" stop-color="#FFD96B" stop-opacity="0"/>
      </linearGradient>
      <radialGradient id="met-head" cx="40%" cy="35%" r="70%">
        <stop offset="0" stop-color="#fff"/><stop offset="100%" stop-color="#FFC84D"/>
      </radialGradient>
    </defs>
    <path d="M47 17 Q30 34 6 55 L12 58 Q34 40 51 22 Z" fill="url(#met-tail)"/>
    <path d="M47 18 Q34 32 16 48" fill="none" stroke="#fff" stroke-width="1.4" opacity="0.7" stroke-linecap="round"/>
    <circle cx="47" cy="17" r="7" fill="url(#met-head)"/>
    <circle cx="44.5" cy="14.5" r="2.2" fill="#fff"/>
    <circle cx="47" cy="17" r="10" fill="#FFD96B" opacity="0.2"/>'''
    return svg(body)

# 星系（旋涡）
def icon_milkyway():
    body = '''<defs>
      <radialGradient id="mw-core" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#FFFDF0"/><stop offset="55%" stop-color="#FFE9A8"/>
        <stop offset="100%" stop-color="#E8B868" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <g transform="rotate(-15 32 32)">
      <!-- 盘面 -->
      <ellipse cx="32" cy="32" rx="27" ry="15" fill="#352C68" opacity="0.4"/>
      <!-- 旋臂 A（从中心向外绕约 1.5 圈） -->
      <path d="M32 32 Q40 30 42 24 Q44 17 36 15 Q27 13 23 19 Q19 27 22 34 Q25 43 33 46 Q43 48 47 40"
            fill="none" stroke="#B8A8EC" stroke-width="4" stroke-linecap="round" opacity="0.85"/>
      <!-- 旋臂 B（相差 180°） -->
      <path d="M32 32 Q24 34 22 40 Q20 47 28 49 Q37 51 41 45 Q45 37 42 30 Q39 21 31 18 Q21 16 17 24"
            fill="none" stroke="#A898E0" stroke-width="4" stroke-linecap="round" opacity="0.8"/>
      <!-- 旋臂内缘亮线 -->
      <path d="M32 32 Q38 30 40 25 Q41 20 36 19" fill="none" stroke="#E8DFFF" stroke-width="1.6" opacity="0.8"/>
      <!-- 亮核 -->
      <circle cx="32" cy="32" r="10" fill="url(#mw-core)"/>
      <!-- 亮星 -->
      <g fill="#fff" opacity="0.9">
        <circle cx="42" cy="24" r="1.3"/><circle cx="23" cy="19" r="1.2"/><circle cx="33" cy="46" r="1.2"/><circle cx="41" cy="45" r="1.1"/>
      </g>
    </g>'''
    return svg(body)

# 北斗七星
def icon_bigdipper():
    pts = [(14,38),(24,34),(34,34),(42,26),(50,20),(52,30),(46,38)]
    line = "M" + " L".join(f"{x} {y}" for x,y in pts)
    stars = "".join(
        f'<circle cx="{x}" cy="{y}" r="3.2" fill="#FFF3C4"/><circle cx="{x}" cy="{y}" r="1.6" fill="#fff"/>'
        f'<circle cx="{x}" cy="{y}" r="5.5" fill="#FFE66D" opacity="0.25"/>' for x,y in pts)
    body = f'<path d="{line}" fill="none" stroke="#B8C8FF" stroke-width="1.4" opacity="0.8"/>{stars}'
    return svg(body)

# 宇航员（半写实）
def icon_astronaut():
    body = '''<defs>
      <radialGradient id="as-visor" cx="35%" cy="30%" r="80%">
        <stop offset="0" stop-color="#5A7AB0"/><stop offset="60%" stop-color="#1E3258"/>
        <stop offset="100%" stop-color="#0A1428"/>
      </radialGradient>
      <linearGradient id="as-suit" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff"/><stop offset="100%" stop-color="#D8DEE8"/>
      </linearGradient>
    </defs>
    <!-- 背包 -->
    <rect x="20" y="34" width="24" height="20" rx="6" fill="#B8C0CC"/>
    <!-- 身体 -->
    <rect x="22" y="36" width="20" height="22" rx="8" fill="url(#as-suit)"/>
    <rect x="28" y="40" width="8" height="6" rx="2" fill="#8A98B0"/>
    <!-- 手臂 -->
    <rect x="14" y="38" width="9" height="14" rx="4.5" fill="url(#as-suit)"/>
    <rect x="41" y="38" width="9" height="14" rx="4.5" fill="url(#as-suit)"/>
    <!-- 头盔 -->
    <circle cx="32" cy="24" r="16" fill="url(#as-suit)"/>
    <circle cx="32" cy="24" r="12" fill="url(#as-visor)"/>
    <path d="M24 18 Q26 15 30 15" fill="none" stroke="#fff" stroke-width="2" opacity="0.6"/>
    <circle cx="27" cy="20" r="1.6" fill="#9FC8FF" opacity="0.8"/>
    <!-- 腿 -->
    <rect x="24" y="56" width="8" height="8" rx="4" fill="#C8D0DC"/>
    <rect x="32" y="56" width="8" height="8" rx="4" fill="#C8D0DC"/>'''
    return svg(body)

# 火箭
def icon_rocket():
    body = '''<defs>
      <linearGradient id="rk-body" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff"/><stop offset="100%" stop-color="#E0E6F0"/>
      </linearGradient>
      <linearGradient id="rk-flame" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FFF3A0"/><stop offset="50" stop-color="#FFB24D"/>
        <stop offset="100%" stop-color="#FF6B4D" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <!-- 火焰 -->
    <path d="M26 50 Q28 58 32 62 Q36 58 38 50 Z" fill="url(#rk-flame)"/>
    <!-- 尾翼 -->
    <path d="M22 44 L16 54 L24 50 Z" fill="#FF6B6B"/>
    <path d="M42 44 L48 54 L40 50 Z" fill="#FF6B6B"/>
    <!-- 主体 -->
    <path d="M32 8 Q40 18 40 32 L40 50 L24 50 L24 32 Q24 18 32 8 Z" fill="url(#rk-body)"/>
    <!-- 圆窗 -->
    <circle cx="32" cy="28" r="6" fill="#4D96FF"/>
    <circle cx="32" cy="28" r="6" fill="none" stroke="#9B8A6A" stroke-width="2"/>
    <path d="M29 24 Q30 22 33 23" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.8"/>
    <!-- 红条纹 -->
    <rect x="24" y="44" width="16" height="5" fill="#FF6B6B"/>'''
    return svg(body)

# 卫星
def icon_satellite():
    body = '''<defs>
      <linearGradient id="sat-panel" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#3A66C8"/><stop offset="100%" stop-color="#1E3A8A"/>
      </linearGradient>
      <linearGradient id="sat-body" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#E8ECF2"/><stop offset="100" stop-color="#A8B0BC"/>
      </linearGradient>
    </defs>
    <!-- 太阳能板 -->
    <rect x="4" y="26" width="16" height="12" rx="2" fill="url(#sat-panel)"/>
    <rect x="44" y="26" width="16" height="12" rx="2" fill="url(#sat-panel)"/>
    <g stroke="#7FA8E8" stroke-width="0.8" opacity="0.7">
      <path d="M8 26v12M12 26v12M16 26v12M48 26v12M52 26v12M56 26v12"/>
    </g>
    <rect x="20" y="28" width="4" height="8" fill="#9AA0AC"/>
    <rect x="40" y="28" width="4" height="8" fill="#9AA0AC"/>
    <!-- 主体 -->
    <rect x="24" y="22" width="16" height="20" rx="4" fill="url(#sat-body)"/>
    <circle cx="32" cy="30" r="4" fill="#4D96FF"/>
    <!-- 天线 -->
    <path d="M32 22 L32 14" stroke="#9AA0AC" stroke-width="2" stroke-linecap="round"/>
    <circle cx="32" cy="12" r="2.4" fill="#E8ECF2"/>'''
    return svg(body)

# 望远镜
def icon_telescope():
    body = '''<defs>
      <linearGradient id="tl-tube" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#7FA8D8"/><stop offset="100%" stop-color="#3A5A96"/>
      </linearGradient>
    </defs>
    <!-- 镜筒（倾斜） -->
    <g transform="rotate(-32 32 32)">
      <rect x="22" y="14" width="16" height="30" rx="6" fill="url(#tl-tube)"/>
      <rect x="20" y="12" width="20" height="8" rx="4" fill="#2E4878"/>
      <rect x="24" y="16" width="12" height="4" rx="2" fill="#8FB8E8" opacity="0.7"/>
    </g>
    <!-- 支架 -->
    <path d="M32 40 L22 56 M32 40 L42 56 M32 40 L32 54" stroke="#6A5A48" stroke-width="3" stroke-linecap="round"/>
    <circle cx="32" cy="40" r="3" fill="#8A7A68"/>'''
    return svg(body)

# UFO
def icon_ufo():
    body = '''<defs>
      <linearGradient id="ufo-disk" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#C8D0DC"/><stop offset="100%" stop-color="#7A8290"/>
      </linearGradient>
      <radialGradient id="ufo-dome" cx="40%" cy="35%" r="70%">
        <stop offset="0" stop-color="#BFF0E8"/><stop offset="100%" stop-color="#4DA89C"/>
      </radialGradient>
      <linearGradient id="ufo-beam" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#BFF8E8" stop-opacity="0.7"/>
        <stop offset="100%" stop-color="#BFF8E8" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <!-- 光束 -->
    <path d="M26 38 L20 58 L44 58 L38 38 Z" fill="url(#ufo-beam)"/>
    <!-- 圆盘 -->
    <ellipse cx="32" cy="34" rx="26" ry="10" fill="url(#ufo-disk)"/>
    <!-- 穹顶 -->
    <path d="M22 32 Q22 18 32 18 Q42 18 42 32 Z" fill="url(#ufo-dome)"/>
    <path d="M26 24 Q28 21 32 21" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.7"/>
    <!-- 底灯 -->
    <g fill="#FFE66D">
      <circle cx="20" cy="36" r="2"/><circle cx="32" cy="39" r="2.2"/><circle cx="44" cy="36" r="2"/>
    </g>'''
    return svg(body)

# ======================================================================
# 写实地理 / 地貌
# ======================================================================
def icon_volcano():
    body = '''<defs>
      <linearGradient id="v-rock" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8A6A52"/><stop offset="100%" stop-color="#563C2C"/>
      </linearGradient>
      <radialGradient id="v-lava" cx="50%" cy="50%" r="60%">
        <stop offset="0" stop-color="#FFF0A0"/><stop offset="100%" stop-color="#FF6B2A"/>
      </radialGradient>
    </defs>
    <g fill="#C9C4BC" opacity="0.9">
      <circle cx="25" cy="11" r="6"/><circle cx="33" cy="7" r="7.5"/><circle cx="42" cy="11" r="6"/>
    </g>
    <path d="M6 56 L24 22 Q32 15 40 22 L58 56 Z" fill="url(#v-rock)"/>
    <path d="M6 56 L24 22 Q32 15 32 15 L32 56 Z" fill="#fff" opacity="0.1"/>
    <path d="M40 22 Q32 15 32 15 L32 56 L58 56 Z" fill="#000" opacity="0.12"/>
    <ellipse cx="32" cy="22" rx="8.5" ry="3.4" fill="url(#v-lava)"/>
    <path d="M27 24 Q26 34 23 44 Q26 34 30 26 Z" fill="#FF7A3A"/>
    <path d="M37 24 Q39 33 41 42 Q38 32 34 26 Z" fill="#FF8A4A"/>
    <g fill="#FFE98A"><circle cx="21" cy="14" r="1.4"/><circle cx="43" cy="12" r="1.2"/><circle cx="36" cy="6" r="1.1"/></g>
    <rect x="2" y="53" width="60" height="9" fill="#463127"/>'''
    return svg(body)

def icon_desert():
    body = '''<defs>
      <linearGradient id="d-sand" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F2D094"/><stop offset="100%" stop-color="#D69E52"/>
      </linearGradient>
      <radialGradient id="d-sun" cx="45%" cy="40%" r="60%">
        <stop offset="0" stop-color="#FFF8D8"/><stop offset="100%" stop-color="#FFD96B"/>
      </radialGradient>
    </defs>
    <circle cx="46" cy="15" r="11" fill="#FFD96B" opacity="0.28"/>
    <circle cx="46" cy="15" r="7.5" fill="url(#d-sun)"/>
    <path d="M2 42 Q18 30 34 42 Q48 32 62 42 L62 48 L2 48 Z" fill="#E8BC7E" opacity="0.85"/>
    <path d="M2 48 Q20 34 38 48 Q50 40 62 46 L62 60 L2 60 Z" fill="url(#d-sand)"/>
    <path d="M20 38 Q30 34 38 48" fill="none" stroke="#FFF0C8" stroke-width="2" opacity="0.7"/>
    <g fill="#6BA85A">
      <rect x="15" y="36" width="4" height="15" rx="2"/><rect x="11" y="41" width="3" ry="1.5" height="6"/><rect x="20" y="43" width="3" height="6" rx="1.5"/>
    </g>'''
    return svg(body)

def icon_wave():
    body = '''<defs>
      <linearGradient id="w-sea" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#4FB3E8"/><stop offset="100%" stop-color="#1660A0"/>
      </linearGradient>
    </defs>
    <path d="M4 60 L4 44 Q4 28 20 26 Q14 34 22 36 Q30 22 46 28 Q44 34 50 34 Q58 32 60 42 L60 60 Z" fill="url(#w-sea)"/>
    <path d="M20 26 Q9 24 6 36 Q11 30 19 33 Q12 36 12 43 Q21 35 27 38 Q26 30 20 26 Z" fill="#fff" opacity="0.96"/>
    <path d="M40 27 Q50 25 57 34 Q50 31 44 35 Q48 38 53 41 Q46 41 40 34 Z" fill="#fff" opacity="0.9"/>
    <path d="M4 50 Q16 45 28 50 Q42 55 56 48 L60 50 L60 60 L4 60 Z" fill="#fff" opacity="0.85"/>
    <g fill="#fff" opacity="0.9"><circle cx="30" cy="20" r="1.8"/><circle cx="42" cy="18" r="1.4"/><circle cx="13" cy="22" r="1.2"/><circle cx="38" cy="23" r="1"/></g>
    <rect x="2" y="56" width="60" height="6" fill="#10507F"/>'''
    return svg(body)

def icon_river():
    body = '''<defs>
      <linearGradient id="rv-bank" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8FC86B"/><stop offset="100%" stop-color="#5C9F46"/>
      </linearGradient>
      <linearGradient id="rv-water" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#86CCF0"/><stop offset="100%" stop-color="#2E78B8"/>
      </linearGradient>
    </defs>
    <rect x="2" y="4" width="60" height="58" rx="6" fill="url(#rv-bank)"/>
    <path d="M29 4 C16 18 39 24 28 36 C19 46 25 53 26 60 L40 60 C41 53 46 45 37 36 C26 24 50 18 37 4 Z" fill="url(#rv-water)"/>
    <path d="M31 14 C35 20 29 23 33 29 M28 42 C34 45 30 51 34 55" fill="none" stroke="#fff" stroke-width="1.5" opacity="0.7"/>
    <g fill="#fff" opacity="0.85"><circle cx="33" cy="25" r="1.3"/><circle cx="30" cy="38" r="1.2"/></g>
    <g fill="#4E8A38"><circle cx="10" cy="14" r="2"/><circle cx="54" cy="22" r="2"/><circle cx="9" cy="44" r="2"/></g>'''
    return svg(body)

def icon_everest():
    body = '''<defs>
      <linearGradient id="e-rock" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#A89888"/><stop offset="100%" stop-color="#665646"/>
      </linearGradient>
    </defs>
    <path d="M2 50 L18 28 L30 42 L2 46 Z" fill="#8A8278" opacity="0.7"/>
    <path d="M14 54 L30 12 L38 30 L46 20 L60 54 Z" fill="url(#e-rock)"/>
    <path d="M30 12 L34 24 L28 26 L32 30 L25 30 Z" fill="#fff"/>
    <path d="M46 20 L49 28 L41 29 Z" fill="#fff"/>
    <path d="M30 26 L35 50 L30 50 Z" fill="#E8F0F8" opacity="0.8"/>
    <path d="M30 12 L34 24 L32 26 Z" fill="#fff" opacity="0.5"/>
    <rect x="2" y="52" width="60" height="10" fill="#54453A"/>'''
    return svg(body)

def icon_fuji():
    body = '''<defs>
      <linearGradient id="fj-body" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#6B7AC0"/><stop offset="100%" stop-color="#36448C"/>
      </linearGradient>
    </defs>
    <g fill="#fff" opacity="0.9">
      <ellipse cx="15" cy="46" rx="12" ry="4"/><ellipse cx="49" cy="47" rx="14" ry="4"/>
    </g>
    <path d="M8 54 Q32 8 56 54 Z" fill="url(#fj-body)"/>
    <path d="M20 22 Q24 15 28 23 Q32 13 36 23 Q40 15 44 22 L43 29 Q40 24 36 29 Q32 20 28 29 Q24 24 21 29 Z" fill="#fff"/>
    <path d="M8 54 Q32 8 32 8 L32 54 Z" fill="#fff" opacity="0.1"/>
    <rect x="6" y="52" width="52" height="10" fill="#2C3878"/>'''
    return svg(body)

def icon_rock():
    body = '''<defs>
      <linearGradient id="rk-rock" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#B4B4B0"/><stop offset="100%" stop-color="#6E6E6A"/>
      </linearGradient>
    </defs>
    <path d="M12 50 L16 28 Q24 22 32 26 L48 24 Q57 30 52 42 L50 50 Z" fill="url(#rk-rock)"/>
    <path d="M16 28 Q24 22 32 26 L32 50 L14 50 Z" fill="#fff" opacity="0.12"/>
    <path d="M40 32 Q45 34 42 39" fill="none" stroke="#565652" stroke-width="1.6" opacity="0.6"/>
    <g fill="#565652" opacity="0.5"><circle cx="26" cy="34" r="1.2"/><circle cx="38" cy="42" r="1"/></g>
    <rect x="8" y="48" width="48" height="10" fill="#5C5A54"/>'''
    return svg(body)

def icon_snowflake():
    body = '''<g stroke="#7FC0F0" stroke-width="3.4" stroke-linecap="round">
      <path d="M32 8 V56 M11 19 L53 45 M53 19 L11 45"/>
    </g>
    <g stroke="#A8D8F4" stroke-width="2.2" stroke-linecap="round" fill="none">
      <path d="M26 15 L32 20 L38 15 M26 49 L32 44 L38 49 M14 27 L21 28 M50 27 L43 28 M14 37 L21 36 M50 37 L43 36"/>
    </g>
    <circle cx="32" cy="32" r="4" fill="#fff"/>
    <circle cx="32" cy="32" r="4" fill="none" stroke="#A8D8F4" stroke-width="1.4"/>'''
    return svg(body)

def icon_ice():
    body = '''<defs>
      <linearGradient id="ice-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F0FAFF"/><stop offset="100%" stop-color="#A6D8F2"/>
      </linearGradient>
    </defs>
    <rect x="12" y="12" width="40" height="40" rx="10" fill="url(#ice-g)"/>
    <rect x="12" y="12" width="40" height="40" rx="10" fill="none" stroke="#7FC8F0" stroke-width="2.4" opacity="0.7"/>
    <path d="M20 44 L44 20" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="0.75"/>
    <path d="M28 48 L48 28" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity="0.5"/>
    <path d="M18 20 L26 18" stroke="#fff" stroke-width="2" opacity="0.8"/>'''
    return svg(body)

def icon_flame():
    body = '''<defs>
      <linearGradient id="fl-out" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FFB25C"/><stop offset="60%" stop-color="#FF8A2A"/><stop offset="100%" stop-color="#F06A18"/>
      </linearGradient>
      <linearGradient id="fl-in" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FFF3A8"/><stop offset="100%" stop-color="#FFD93D"/>
      </linearGradient>
    </defs>
    <path d="M32 4 Q47 18 46 34 Q46 51 32 57 Q18 51 18 34 Q18 24 24 16 Q24 27 30 29 Q28 14 32 4 Z" fill="url(#fl-out)"/>
    <path d="M32 25 Q39 31 38 40 Q38 49 32 52 Q26 49 26 40 Q26 31 32 25 Z" fill="url(#fl-in)"/>
    <ellipse cx="32" cy="44" rx="4" ry="6" fill="#FFF8D0"/>
    <path d="M24 16 Q24 27 30 29" fill="none" stroke="#fff" stroke-width="1.4" opacity="0.5"/>'''
    return svg(body)

def icon_rainbow():
    body = '''<g fill="none" stroke-linecap="round">
      <path d="M7 54 Q32 5 57 54" stroke="#FF6B6B" stroke-width="5.4"/>
      <path d="M12 54 Q32 12 52 54" stroke="#FF9F43" stroke-width="5.4"/>
      <path d="M17 54 Q32 19 47 54" stroke="#FFD93D" stroke-width="5.4"/>
      <path d="M22 54 Q32 26 42 54" stroke="#6BCB77" stroke-width="5.4"/>
      <path d="M27 54 Q32 33 37 54" stroke="#4D96FF" stroke-width="5.4"/>
      <path d="M32 54 Q32 40 32 54" stroke="#9B7BF5" stroke-width="5.4"/>
    </g>
    <g fill="#fff"><ellipse cx="10" cy="55" rx="9" ry="5"/><ellipse cx="54" cy="55" rx="9" ry="5"/></g>
    <path d="M10 50 Q16 46 20 50" fill="#fff" opacity="0.8"/>'''
    return svg(body)

def icon_bolt():
    """闪电（手绘黄色锯齿，夜空放电）"""
    body = (
      f'<style>.st{{stroke:{INK};stroke-width:2.4;stroke-linejoin:round;stroke-linecap:round}}</style>'
      f'<circle cx="32" cy="32" r="27" fill="#4A4E8C"/>'
      f'<path d="M17 19 l1.1 3 3 1.1 -3 1.1 -1.1 3 -1.1 -3 -3 -1.1 3 -1.1 z" fill="#FFF6C8"/>'
      f'<path d="M47 45 l.9 2.4 2.4.9 -2.4.9 -.9 2.4 -.9 -2.4 -2.4 -.9 2.4 -.9 z" fill="#FFF6C8"/>'
      f'<path class="st" d="M35 9 L20 34 L29 34 L25 55 L45 25 L35 25 L40 9 Z" fill="#FFD93D"/>'
      f'<path d="M34 13 L25 31 L31 31 Z" fill="#FFF3A8" opacity="0.85"/>'
    )
    return svg(body)

def icon_crystal():
    body = '''<defs>
      <linearGradient id="cr-body" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#EDE4FC"/><stop offset="100%" stop-color="#937DE0"/>
      </linearGradient>
    </defs>
    <path d="M14 38 L20 26 L24 38 L20 50 Z" fill="#B8A5F0" opacity="0.85"/>
    <path d="M50 38 L44 26 L40 38 L44 50 Z" fill="#B8A5F0" opacity="0.85"/>
    <path d="M32 9 L42 27 L38 52 L26 52 L22 27 Z" fill="url(#cr-body)"/>
    <path d="M32 9 L32 52 M22 27 L42 27" stroke="#fff" stroke-width="1.3" opacity="0.6"/>
    <path d="M32 9 L26 52 L32 52 Z" fill="#fff" opacity="0.25"/>
    <path d="M28 15 L26 27" stroke="#fff" stroke-width="2" opacity="0.85"/>
    <path d="M16 30 L20 38" stroke="#fff" stroke-width="1.4" opacity="0.7"/>'''
    return svg(body)

# ======================================================================
# 写实地标 / 地图
# ======================================================================
def icon_greatwall():
    body = '''<defs>
      <linearGradient id="gw-wall" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#D2C2A2"/><stop offset="100%" stop-color="#9A8868"/>
      </linearGradient>
      <linearGradient id="gw-hill" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8FA878"/><stop offset="100%" stop-color="#5E7C4E"/>
      </linearGradient>
    </defs>
    <path d="M2 54 Q20 36 40 44 Q54 50 62 42 L62 60 L2 60 Z" fill="url(#gw-hill)"/>
    <path d="M6 46 Q22 38 36 44 Q48 48 58 40 L58 47 Q48 53 36 49 Q22 43 6 51 Z" fill="url(#gw-wall)"/>
    <g fill="#E0D2B2">
      <rect x="10" y="39" width="3" height="3"/><rect x="16" y="37" width="3" height="3"/>
      <rect x="22" y="36" width="3" height="3"/><rect x="34" y="42" width="3" height="3"/>
      <rect x="40" y="43" width="3" height="3"/><rect x="46" y="42" width="3" height="3"/>
    </g>
    <rect x="29" y="29" width="13" height="17" fill="#C9B89A"/>
    <rect x="27" y="26" width="17" height="4" rx="1" fill="#B8A682"/>
    <path d="M29 36 h13 M29 41 h13" stroke="#8A7858" stroke-width="0.8" opacity="0.5"/>
    <rect x="31" y="32" width="9" height="2.6" fill="#8A7858"/>'''
    return svg(body)

def icon_pyramid():
    body = '''<defs>
      <linearGradient id="py-lit" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="#F2D28A"/><stop offset="100%" stop-color="#E0B460"/>
      </linearGradient>
    </defs>
    <circle cx="50" cy="13" r="9" fill="#FFD96B" opacity="0.28"/>
    <circle cx="50" cy="13" r="6" fill="#FFD96B"/>
    <path d="M44 52 L54 36 L64 52 Z" fill="#C9A055" opacity="0.8"/>
    <path d="M12 54 L34 14 L34 54 Z" fill="#D8A868"/>
    <path d="M34 14 L56 54 L34 54 Z" fill="url(#py-lit)"/>
    <path d="M27 36 L43 36 M24 42 L48 42 M21 48 L51 48" stroke="#B88840" stroke-width="0.8" opacity="0.4"/>
    <rect x="2" y="52" width="60" height="8" fill="#E0BC7A"/>'''
    return svg(body)

def icon_eiffel():
    body = '''<defs>
      <linearGradient id="ef-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#9AA4BA"/><stop offset="100%" stop-color="#4E5668"/>
      </linearGradient>
    </defs>
    <rect x="31" y="6" width="2" height="7" fill="url(#ef-g)"/>
    <circle cx="32" cy="5" r="1.6" fill="#8A93A8"/>
    <path d="M30 12 L13 54 L20 54 L31 22 L33 22 L44 54 L51 54 L34 12 Z" fill="url(#ef-g)"/>
    <rect x="26" y="24" width="12" height="3" rx="1" fill="#5E6878"/>
    <rect x="17" y="38" width="30" height="4" rx="1.5" fill="#5E6878"/>
    <path d="M28 28 L36 28 M25 34 L39 34 M22 42 L42 42 M19 48 L45 48" stroke="#3E4654" stroke-width="0.8" opacity="0.7"/>
    <path d="M20 54 Q32 40 44 54" fill="none" stroke="#5E6878" stroke-width="3"/>
    <rect x="9" y="54" width="46" height="4" fill="#4E5668"/>'''
    return svg(body)

def icon_bigben():
    body = '''<defs>
      <linearGradient id="bb-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#DCCBA8"/><stop offset="100%" stop-color="#968564"/>
      </linearGradient>
    </defs>
    <path d="M27 9 L32 3 L37 9 Z" fill="#565F72"/>
    <rect x="25" y="8" width="14" height="6" rx="1" fill="#7A6E54"/>
    <rect x="23" y="14" width="18" height="27" rx="2" fill="url(#bb-g)"/>
    <circle cx="32" cy="22" r="7" fill="#FFF6D8"/>
    <circle cx="32" cy="22" r="7" fill="none" stroke="#6A5C3E" stroke-width="2"/>
    <path d="M32 22 L32 17 M32 22 L36 24" stroke="#3A2E2A" stroke-width="1.6" stroke-linecap="round"/>
    <rect x="30" y="31" width="4" height="7" rx="1.5" fill="#6A5C3E"/>
    <rect x="20" y="41" width="24" height="15" rx="2" fill="#C9B896"/>
    <rect x="28" y="44" width="8" height="12" rx="2" fill="#7A6E54"/>
    <rect x="14" y="56" width="36" height="4" fill="#6A5C3E"/>'''
    return svg(body)

def icon_libertystatue():
    body = '''<defs>
      <linearGradient id="ls-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8CC9B0"/><stop offset="100%" stop-color="#36806E"/>
      </linearGradient>
    </defs>
    <path d="M34 27 L42 16 L44 18 L36 29 Z" fill="#5EA08C"/>
    <rect x="42" y="9" width="2.6" height="9" rx="1.2" fill="#36806E"/>
    <path d="M43.3 9 Q40 5 43 2 Q44 6 47 5 Q47 9 43.3 9 Z" fill="#FFD96B"/>
    <circle cx="43.3" cy="7" r="4" fill="#FFE98A" opacity="0.5"/>
    <circle cx="30" cy="18" r="5.6" fill="url(#ls-g)"/>
    <path d="M24.6 15.4 L24 12 M26.8 13.6 L26.6 10 M29 13 L29 9 M31.2 13 L31.4 10 M33.4 14 L34 12" stroke="#2E6A5C" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M25 24 L20 52 L40 52 L35 24 Z" fill="url(#ls-g)"/>
    <path d="M27 26 L25 50 M30 26 L30 52 M33 26 L35 50" stroke="#2E6A5C" stroke-width="1" opacity="0.6"/>
    <path d="M25 28 L18 34 L20 37 L26 32 Z" fill="#5EA08C"/>
    <rect x="16" y="52" width="28" height="6" rx="1" fill="#8A8A82"/>'''
    return svg(body)

def icon_pisa():
    arches = ""
    bands = ""
    for y in [13, 21, 29, 37, 45]:
        bands += f'<path d="M26 {y+1} h12" stroke="#B8AA88" stroke-width="2"/>'
        for cx in [29, 34.5]:
            arches += (f'<path d="M{cx-1.5} {y+5} L{cx-1.5} {y+3} A1.5 1.5 0 0 1 {cx+1.5} {y+3} '
                       f'L{cx+1.5} {y+5} Z" fill="#A89878"/>')
    body = f'''<defs>
      <linearGradient id="ps-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F6F0E0"/><stop offset="100%" stop-color="#C9BCA0"/>
      </linearGradient>
    </defs>
    <g transform="rotate(-10 32 32)">
      <rect x="26" y="8" width="12" height="47" rx="3" fill="url(#ps-g)"/>
      <rect x="23" y="6" width="18" height="5" rx="2" fill="#E8E0CC"/>
      {bands}
      {arches}
    </g>
    <ellipse cx="33" cy="56" rx="18" ry="3" fill="#B8AA88" opacity="0.5"/>'''
    return svg(body)

def icon_taj():
    body = '''<defs>
      <linearGradient id="tj-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FEFCF6"/><stop offset="100%" stop-color="#D2C8AE"/>
      </linearGradient>
    </defs>
    <g fill="#E8E0CC">
      <rect x="9" y="24" width="4" height="28" rx="2"/><circle cx="11" cy="22" r="3.2"/>
      <rect x="51" y="24" width="4" height="28" rx="2"/><circle cx="53" cy="22" r="3.2"/>
    </g>
    <path d="M22 30 Q23 13 32 11 Q41 13 42 30 Z" fill="url(#tj-g)"/>
    <path d="M32 11 L32 6" stroke="#C9BFA4" stroke-width="1.6" stroke-linecap="round"/>
    <circle cx="32" cy="4" r="1.7" fill="#D8CFB8"/>
    <rect x="23" y="28" width="18" height="4" fill="#E8E0CC"/>
    <rect x="19" y="32" width="26" height="16" rx="2" fill="url(#tj-g)"/>
    <path d="M28 48 L28 39 Q32 33 36 39 L36 48 Z" fill="#B8A888"/>
    <path d="M19 32 Q22 25 25 32 Z" fill="#E8E0CC"/>
    <path d="M39 32 Q42 25 45 32 Z" fill="#E8E0CC"/>
    <rect x="8" y="48" width="48" height="4" fill="#D8CFB8"/>
    <rect x="8" y="52" width="48" height="6" fill="#9FC0D2"/>
    <rect x="14" y="53" width="36" height="3" fill="#FEFCF6" opacity="0.5"/>'''
    return svg(body)

def icon_torii():
    body = '''<defs>
      <linearGradient id="tor-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#EC7850"/><stop offset="100%" stop-color="#C2422E"/>
      </linearGradient>
    </defs>
    <path d="M4 9 L60 9 L57 5 L7 5 Z" fill="#3A2A24"/>
    <rect x="5" y="9" width="54" height="5" rx="1.5" fill="#3A2A24"/>
    <rect x="9" y="18" width="46" height="4" rx="1.5" fill="url(#tor-g)"/>
    <rect x="14" y="15" width="7" height="39" rx="2" fill="url(#tor-g)"/>
    <rect x="43" y="15" width="7" height="39" rx="2" fill="url(#tor-g)"/>
    <rect x="30" y="22" width="4" height="18" rx="1.5" fill="#D85A3A"/>
    <rect x="11" y="52" width="13" height="3" rx="1" fill="#9A3022"/>
    <rect x="40" y="52" width="13" height="3" rx="1" fill="#9A3022"/>'''
    return svg(body)

def icon_tiananmen():
    body = '''<defs>
      <linearGradient id="ta-roof" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F2C94E"/><stop offset="100%" stop-color="#D9A028"/>
      </linearGradient>
      <linearGradient id="ta-wall" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#DC4A3E"/><stop offset="100%" stop-color="#A82E28"/>
      </linearGradient>
    </defs>
    <path d="M14 16 L50 16 L47 10 L17 10 Z" fill="#F5D462"/>
    <path d="M10 22 L54 22 L50 16 L14 16 Z" fill="url(#ta-roof)"/>
    <rect x="18" y="22" width="28" height="9" fill="#C93A2E"/>
    <rect x="27" y="24" width="10" height="4.6" rx="1" fill="#F2C94E"/>
    <path d="M8 36 L56 36 L52 30 L12 30 Z" fill="url(#ta-roof)"/>
    <rect x="10" y="36" width="44" height="20" fill="url(#ta-wall)"/>
    <g fill="#5A1E18">
      <path d="M14 56 L14 47 Q18 42 22 47 L22 56 Z"/>
      <path d="M27 56 L27 45 Q32 39 37 45 L37 56 Z"/>
      <path d="M42 56 L42 47 Q46 42 50 47 L50 56 Z"/>
    </g>
    <rect x="11" y="38" width="2" height="18" fill="#8A2418"/>
    <rect x="51" y="38" width="2" height="18" fill="#8A2418"/>'''
    return svg(body)

def icon_ferris():
    body = '''<path d="M32 26 L18 56 L22 56 L32 34 L42 56 L46 56 Z" fill="#B8B2A8"/>
    <circle cx="32" cy="26" r="20" fill="none" stroke="#C9C4BA" stroke-width="3"/>
    <g stroke="#D8D2C8" stroke-width="1.4">
      <path d="M32 6 L32 46 M12 26 L52 26 M18 12 L46 40 M46 12 L18 40"/>
    </g>
    <g>
      <rect x="29" y="4" width="6" height="6" rx="1.5" fill="#FF8A6B"/>
      <rect x="29" y="42" width="6" height="6" rx="1.5" fill="#6BCB77"/>
      <rect x="10" y="23" width="6" height="6" rx="1.5" fill="#4D96FF"/>
      <rect x="48" y="23" width="6" height="6" rx="1.5" fill="#FFD93D"/>
      <rect x="15" y="9" width="6" height="6" rx="1.5" fill="#9B7BF5"/>
      <rect x="43" y="9" width="6" height="6" rx="1.5" fill="#FF6B9A"/>
      <rect x="15" y="37" width="6" height="6" rx="1.5" fill="#FFD93D"/>
      <rect x="43" y="37" width="6" height="6" rx="1.5" fill="#4D96FF"/>
    </g>
    <circle cx="32" cy="26" r="3.5" fill="#8A8478"/>
    <rect x="14" y="55" width="36" height="3" rx="1.5" fill="#9A9488"/>'''
    return svg(body)

def icon_tower():
    body = '''<defs>
      <linearGradient id="tw-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#EC82AE"/><stop offset="100%" stop-color="#B84878"/>
      </linearGradient>
    </defs>
    <rect x="31" y="2" width="2" height="5" fill="#8A93A8"/>
    <circle cx="32" cy="9" r="4" fill="#EC82AE"/>
    <path d="M29 12 L35 12 L34 22 L30 22 Z" fill="url(#tw-g)"/>
    <circle cx="32" cy="27" r="7" fill="url(#tw-g)"/>
    <circle cx="29" cy="24" r="2" fill="#fff" opacity="0.4"/>
    <path d="M28 34 L36 34 L35 42 L29 42 Z" fill="url(#tw-g)"/>
    <circle cx="32" cy="46" r="9" fill="url(#tw-g)"/>
    <circle cx="28" cy="42" r="2.6" fill="#fff" opacity="0.4"/>
    <path d="M24 54 L40 54 L38 60 L26 60 Z" fill="#A8406C"/>
    <rect x="22" y="59" width="20" height="3" rx="1" fill="#8A3058"/>'''
    return svg(body)

def icon_world_map():
    body = '''<defs>
      <linearGradient id="wm-ocean" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#5AB0E8"/><stop offset="100%" stop-color="#1E6AB4"/>
      </linearGradient>
      <linearGradient id="wm-land" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#7CC468"/><stop offset="100%" stop-color="#4EA844"/>
      </linearGradient>
      <clipPath id="wm-clip"><rect x="6" y="12" width="52" height="40" rx="8"/></clipPath>
    </defs>
    <rect x="6" y="12" width="52" height="40" rx="8" fill="url(#wm-ocean)"/>
    <g clip-path="url(#wm-clip)" fill="url(#wm-land)">
      <!-- 北美 -->
      <path d="M9 15 Q14 12 22 14 Q25 16 24 20 Q25 23 21 25 L24 27 Q22 29 19 27 L18 25 Q14 24 12 21 Q9 18 9 15 Z"/>
      <!-- 南美 -->
      <path d="M20 28 Q25 29 26 33 Q25 40 22 45 Q19 44 19 38 Q18 32 20 28 Z"/>
      <!-- 欧洲 -->
      <path d="M30 16 Q35 14 37 17 Q36 20 32 20 Z"/>
      <!-- 非洲 -->
      <path d="M29 22 Q37 21 38 27 Q37 35 34 40 Q30 38 29 31 Z"/>
      <!-- 亚洲 -->
      <path d="M37 13 Q48 12 51 19 Q50 25 46 27 Q42 28 40 25 Q43 29 42 32 Q39 31 38 27 Q36 22 37 13 Z"/>
      <!-- 澳洲 -->
      <path d="M44 39 Q51 38 52 43 Q49 46 45 45 Z"/>
      <!-- 日本 -->
      <path d="M50 23 L52 22 L52 27 L50 27 Z"/>
    </g>
    <rect x="6" y="12" width="52" height="40" rx="8" fill="none" stroke="#fff" stroke-width="1.6" opacity="0.6"/>'''
    return svg(body)

def icon_china_map():
    outline = ("M9 24 L11 14 L18 12 L26 11 L34 7 L44 6 L50 10 L53 15 L50 20 L46 22 L47 26 L49 29 "
               "L48 33 L47 37 L44 41 L40 43 L37 45 L33 44 L28 46 L24 43 L17 41 L11 34 Z")
    body = f'''<defs>
      <linearGradient id="cm-g" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F26B5A"/><stop offset="100%" stop-color="#D83A30"/>
      </linearGradient>
    </defs>
    <path d="{outline}" fill="url(#cm-g)" stroke="#C23028" stroke-width="1" stroke-linejoin="round"/>
    <ellipse cx="38" cy="48" rx="2" ry="2.8" fill="#E85048"/>
    <ellipse cx="48" cy="42" rx="1.5" ry="2.6" fill="#E85048"/>
    <path d="M14 18 Q26 12 40 12" fill="none" stroke="#fff" stroke-width="2" opacity="0.35"/>
    <path d="M18 28 Q30 24 42 28 M16 35 Q28 32 40 35" fill="none" stroke="#B82820" stroke-width="1" opacity="0.35"/>'''
    return svg(body)

def _moon_phase(kind):
    tex = '''<g fill="#7A7874" opacity="0.5">
      <ellipse cx="25" cy="26" rx="7" ry="6"/><ellipse cx="40" cy="36" rx="6" ry="5"/><ellipse cx="38" cy="22" rx="4" ry="3.4"/>
    </g>
    <g fill="#5E5C58" opacity="0.45"><circle cx="22" cy="40" r="2.2"/><circle cx="44" cy="28" r="1.8"/><circle cx="30" cy="33" r="1.4"/></g>
    <g fill="#A8A6A0" opacity="0.7"><circle cx="24" cy="24" r="1.4"/><circle cx="39" cy="34" r="1.2"/></g>'''
    if kind == "full":
        clip = '<circle cx="32" cy="32" r="24"/>'
    elif kind == "waxing":
        clip = '<path d="M32 8 A24 24 0 0 1 32 56 Z"/>'
    elif kind == "waning":
        clip = '<path d="M32 8 A24 24 0 0 0 32 56 Z"/>'
    else:
        clip = '<path d="M32 9 A23 23 0 0 1 32 55 A11 23 0 0 0 32 9 Z"/>'
    body = f'''<defs>
      <radialGradient id="mp-base" cx="38%" cy="32%" r="75%">
        <stop offset="0" stop-color="#E8E6E0"/><stop offset="60%" stop-color="#B8B6B0"/><stop offset="100%" stop-color="#86847E"/>
      </radialGradient>
      <clipPath id="mp-lit">{clip}</clipPath>
    </defs>
    <circle cx="32" cy="32" r="24" fill="#36404A" opacity="0.92"/>
    <g clip-path="url(#mp-lit)">
      <circle cx="32" cy="32" r="24" fill="url(#mp-base)"/>
      {tex}
    </g>
    <circle cx="32" cy="32" r="24" fill="none" stroke="#D8D6D0" stroke-width="1.2" opacity="0.6"/>'''
    return svg(body)

def icon_fullmoon(): return _moon_phase("full")
def icon_newmoon(): return _moon_phase("new")
def icon_waxing(): return _moon_phase("waxing")
def icon_waning(): return _moon_phase("waning")

def icon_sunrise():
    body = '''<defs>
      <radialGradient id="sr-sun" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#FFF6C0"/><stop offset="70%" stop-color="#FFD96B"/><stop offset="100%" stop-color="#FF9F43"/>
      </radialGradient>
    </defs>
    <rect x="4" y="18" width="56" height="30" rx="10" fill="#FFD9A0" opacity="0.45"/>
    <g stroke="#FFD96B" stroke-width="3" stroke-linecap="round" opacity="0.9">
      <path d="M32 12 L32 17 M13 26 L18 29 M51 26 L46 29 M20 36 L24 38 M44 36 L40 38"/>
    </g>
    <circle cx="32" cy="42" r="14" fill="url(#sr-sun)"/>
    <path d="M4 46 Q20 42 32 46 Q44 42 60 46 L60 60 L4 60 Z" fill="#7AA85C"/>
    <path d="M4 46 Q20 42 32 46 Q44 42 60 46" fill="none" stroke="#5E8A48" stroke-width="2"/>'''
    return svg(body)

def icon_sunrays():
    body = '''<defs>
      <radialGradient id="sr2-sun" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#FFF3A8"/><stop offset="100%" stop-color="#FFB23D"/>
      </radialGradient>
    </defs>
    <g stroke="#FFB23D" stroke-width="4" stroke-linecap="round">
      <path d="M32 6 L32 14 M32 50 L32 58 M6 32 L14 32 M50 32 L58 32 M13 13 L19 19 M45 45 L51 51 M13 51 L19 45 M45 19 L51 13"/>
    </g>
    <circle cx="32" cy="32" r="13" fill="url(#sr2-sun)"/>'''
    return svg(body)

def icon_planet():
    body = '''<defs>
      <radialGradient id="pl-g" cx="38%" cy="32%" r="75%">
        <stop offset="0" stop-color="#9BC0F0"/><stop offset="60%" stop-color="#6A8FD0"/><stop offset="100%" stop-color="#3A569A"/>
      </radialGradient>
    </defs>
    <ellipse cx="32" cy="32" rx="26" ry="9" fill="none" stroke="#B8A8D8" stroke-width="3.5" transform="rotate(-18 32 32)" opacity="0.85"/>
    <circle cx="32" cy="32" r="16" fill="url(#pl-g)"/>
    <g fill="#4E72B8" opacity="0.4"><ellipse cx="28" cy="28" rx="5" ry="3"/><ellipse cx="36" cy="37" rx="6" ry="3.4"/></g>
    <path d="M45 26 A16 16 0 0 1 47 40" fill="none" stroke="#3A569A" stroke-width="3" opacity="0.5"/>
    <ellipse cx="32" cy="32" rx="26" ry="9" fill="none" stroke="#E8DCF8" stroke-width="1.6" transform="rotate(-18 32 32)" opacity="0.7"/>'''
    return svg(body)

def icon_meteorite():
    body = '''<defs>
      <radialGradient id="mt-g" cx="38%" cy="30%" r="75%">
        <stop offset="0" stop-color="#9A8E80"/><stop offset="100%" stop-color="#463C34"/>
      </radialGradient>
      <linearGradient id="mt-trail" x1="0" y1="1" x2="1" y2="0">
        <stop offset="0" stop-color="#FF5A2A" stop-opacity="0"/>
        <stop offset="50%" stop-color="#FF9A4A" stop-opacity="0.8"/>
        <stop offset="100%" stop-color="#FFE98A" stop-opacity="0.95"/>
      </linearGradient>
    </defs>
    <path d="M12 56 L38 24 L44 26 L20 58 Z" fill="url(#mt-trail)"/>
    <path d="M20 58 L42 28 L46 32 L26 60 Z" fill="#FFE98A" opacity="0.35"/>
    <g fill="#FFD96B"><circle cx="22" cy="50" r="1.4"/><circle cx="18" cy="54" r="1.2"/><circle cx="28" cy="54" r="1.2"/></g>
    <path d="M36 20 Q31 14 36 9 Q39 14 41 16" fill="#FF7A3A"/>
    <path d="M40 14 Q50 16 50 28 Q48 38 38 36 Q30 34 32 24 Q33 15 40 14 Z" fill="url(#mt-g)"/>
    <g fill="#382E26" opacity="0.6"><circle cx="38" cy="24" r="2"/><circle cx="44" cy="28" r="1.5"/><circle cx="40" cy="31" r="1.2"/></g>'''
    return svg(body)

def icon_aurora():
    """极光：深蓝夜空 + 飘动的绿紫光带（窗帘状）+ 星星 + 雪山剪影。"""
    body = '''<defs>
      <linearGradient id="au-g1" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#8FFCD0" stop-opacity="0.98"/>
        <stop offset="0.55" stop-color="#56D9A8" stop-opacity="0.6"/>
        <stop offset="1" stop-color="#9B7BF5" stop-opacity="0.14"/>
      </linearGradient>
      <linearGradient id="au-g2" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#BFF0FF" stop-opacity="0.92"/>
        <stop offset="0.6" stop-color="#6FB7E8" stop-opacity="0.42"/>
        <stop offset="1" stop-color="#8A7BE0" stop-opacity="0.12"/>
      </linearGradient>
    </defs>
    <rect x="4" y="4" width="56" height="56" rx="12" fill="#0E1A3D"/>
    <g fill="#ffffff">
      <path d="M12 12 l1 2.2 L15.2 15 l-2.2 1 L12 18.2 l-1-2.2 L8.8 15 l2.2-1 Z"/>
      <circle cx="50" cy="12" r="1.3"/><circle cx="45" cy="21" r="1"/><circle cx="19" cy="24" r="1.1"/>
    </g>
    <path d="M9 10 Q20 22 13 46 L26 46 Q30 22 18 10 Z" fill="url(#au-g1)"/>
    <path d="M24 7 Q40 24 30 48 L45 48 Q52 24 38 7 Z" fill="url(#au-g2)"/>
    <path d="M40 10 Q52 22 46 44 L57 44 Q59 22 48 10 Z" fill="url(#au-g1)" opacity="0.6"/>
    <path d="M4 56 L16 42 L24 49 L34 40 L44 51 L52 44 L60 56 Z" fill="#16285C"/>
    <path d="M4 56 L60 56 L60 60 L4 60 Z" fill="#0C1530"/>'''
    return svg(body)

def icon_sunset():
    """日落：太阳半沉到地平线下，橙红暖色天空（与 sunrise 对称）。"""
    body = '''<defs>
      <radialGradient id="ss-sun" cx="50%" cy="50%" r="50%">
        <stop offset="0" stop-color="#FFE39A"/><stop offset="65%" stop-color="#FF9F43"/><stop offset="100%" stop-color="#F06A3C"/>
      </radialGradient>
    </defs>
    <rect x="4" y="16" width="56" height="34" rx="10" fill="#FFB074" opacity="0.5"/>
    <g stroke="#FF8A4C" stroke-width="3" stroke-linecap="round" opacity="0.85">
      <path d="M13 28 L18 30 M51 30 L46 28 M20 40 L24 42 M44 42 L40 40"/>
    </g>
    <circle cx="32" cy="44" r="14" fill="url(#ss-sun)"/>
    <path d="M4 44 Q20 40 32 44 Q44 40 60 44 L60 60 L4 60 Z" fill="#7A6A92"/>
    <path d="M4 44 Q20 40 32 44 Q44 40 60 44" fill="none" stroke="#5E5078" stroke-width="2"/>'''
    return svg(body)

REAL_ICONS = {
    "sun": icon_sun, "mercury": icon_mercury, "venus": icon_venus, "earth": icon_earth,
    "mars": icon_mars, "jupiter": icon_jupiter, "saturn": icon_saturn,
    "uranus": icon_uranus, "neptune": icon_neptune, "moon": icon_moon,
    "blackhole": icon_blackhole, "comet": icon_comet, "meteor": icon_meteor,
    "milkyway": icon_milkyway, "bigdipper": icon_bigdipper, "astronaut": icon_astronaut,
    "rocket": icon_rocket, "satellite": icon_satellite, "telescope": icon_telescope, "ufo": icon_ufo,
    "volcano": icon_volcano, "desert": icon_desert, "wave": icon_wave, "river": icon_river,
    "everest": icon_everest, "fuji": icon_fuji, "rock": icon_rock, "snowflake": icon_snowflake,
    "ice": icon_ice, "flame": icon_flame, "rainbow": icon_rainbow, "bolt": icon_bolt, "crystal": icon_crystal,
    "greatwall": icon_greatwall, "pyramid": icon_pyramid, "eiffel": icon_eiffel,
    "bigben": icon_bigben, "libertystatue": icon_libertystatue, "pisa": icon_pisa,
    "taj": icon_taj, "torii": icon_torii, "tiananmen": icon_tiananmen,
    "ferris": icon_ferris, "tower": icon_tower,
    "world-map": icon_world_map, "china-map": icon_china_map,
    "fullmoon": icon_fullmoon, "newmoon": icon_newmoon, "waxing": icon_waxing,
    "waning": icon_waning, "sunrise": icon_sunrise, "sunrays": icon_sunrays,
    "aurora": icon_aurora, "sunset": icon_sunset,
    "planet": icon_planet, "meteorite": icon_meteorite,
}

# ======================================================================
# 绘本手绘风：立式动物（72×96）
# 深棕描边 + 水彩平涂 + 圆润大头 + 可爱表情
# ======================================================================
INK = "#5B4636"
AVB = "0 0 72 96"

def _astyle():
    return (f'<style>.st{{stroke:{INK};stroke-width:2.3;stroke-linejoin:round;stroke-linecap:round}}'
            f'.th{{stroke:{INK};stroke-width:1.5;fill:none;stroke-linecap:round;stroke-linejoin:round}}</style>')

def _eyes(x=27, y=26, r=2.9, color="#3A2A20", gap=18):
    cx2 = x + gap
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<circle cx="{cx2}" cy="{y}" r="{r}" fill="{color}"/>'
            f'<circle cx="{x+0.9}" cy="{y-1}" r="{r*0.34}" fill="#fff"/>'
            f'<circle cx="{cx2+0.9}" cy="{y-1}" r="{r*0.34}" fill="#fff"/>')

def _blush(y=32):
    return (f'<ellipse cx="20" cy="{y}" rx="3.4" ry="2.4" fill="#FF9B8A" opacity="0.65"/>'
            f'<ellipse cx="52" cy="{y}" rx="3.4" ry="2.4" fill="#FF9B8A" opacity="0.65"/>')

def _animal(body, belly, ears, face, tail="", extra="", head_r=21, feet=None, arms=True):
    """通用立式动物。feet 可自定义脚部（如蹼、蹄）。"""
    p = [_astyle()]
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

# ---- 熊 ----
def icon_bear():
    body, belly = "#C68A52", "#EFD6AE"
    ears = (f'<circle class="st" cx="19" cy="12" r="7.5" fill="{body}"/><circle cx="19" cy="12" r="3.7" fill="#9C6230"/>'
            f'<circle class="st" cx="53" cy="12" r="7.5" fill="{body}"/><circle cx="53" cy="12" r="3.7" fill="#9C6230"/>')
    face = (f'<ellipse cx="36" cy="36" rx="10" ry="8" fill="{belly}"/>'
            + _eyes() +
            f'<ellipse cx="36" cy="33" rx="3.4" ry="2.7" fill="#3A2416"/>'
            '<path class="th" d="M36 36 L36 39 M36 39 Q33 41.5 31 39.5 M36 39 Q39 41.5 41 39.5"/>'
            + _blush())
    return _animal(body, belly, ears, face)

# ---- 猫 ----
def icon_cat():
    body, belly = "#FFB84D", "#FBE2B8"
    ears = (f'<path class="st" d="M18 20 L15 5 L29 14 Z" fill="{body}"/><path d="M19 16 L17 9 L25 13 Z" fill="#FF9B8A"/>'
            f'<path class="st" d="M54 20 L57 5 L43 14 Z" fill="{body}"/><path d="M53 16 L55 9 L47 13 Z" fill="#FF9B8A"/>')
    tail = f'<path class="st" d="M58 64 Q72 60 67 42 Q65 36 60 40 Q63 52 55 56 Z" fill="{body}"/>'
    face = (f'<path d="M20 34 L14 32 M20 37 L14 38 M52 34 L58 32 M52 37 L58 38" stroke="#C98A6A" stroke-width="1.3" stroke-linecap="round"/>'
            + _eyes() +
            f'<path d="M35 33 L37 33 L36 35 Z" fill="#E0766B"/>'
            '<path class="th" d="M36 35 L36 38 M36 38 Q33.5 40 32 38.5 M36 38 Q38.5 40 40 38.5"/>'
            + _blush())
    return _animal(body, belly, ears, face, tail=tail)

# ---- 兔 ----
def icon_rabbit():
    body, belly = "#F4F0EA", "#E2E8F0"
    ears = (f'<path class="st" d="M26 14 Q20 -4 27 2 Q32 8 31 18 Z" fill="{body}"/><path d="M27 10 Q24 2 28 6 Q29 10 29 15 Z" fill="#FFC4C0"/>'
            f'<path class="st" d="M46 14 Q52 -4 45 2 Q40 8 41 18 Z" fill="{body}"/><path d="M45 10 Q48 2 44 6 Q43 10 43 15 Z" fill="#FFC4C0"/>')
    face = (f'<ellipse cx="36" cy="35" rx="9" ry="7" fill="#fff"/>'
            + _eyes() +
            '<path d="M35 32 L37 32 L36 34.5 Z" fill="#E0766B"/>'
            '<path class="th" d="M36 34.5 L36 37.5 M36 37.5 Q33.5 39.5 32 38 M36 37.5 Q38.5 39.5 40 38"/>'
            + _blush())
    return _animal(body, belly, ears, face, head_r=20)

# ---- 熊猫 ----
def icon_panda():
    body, belly = "#FFFFFF", "#F2F2F2"
    ears = ('<circle class="st" cx="19" cy="12" r="7.5" fill="#3A3A3A"/>'
            '<circle class="st" cx="53" cy="12" r="7.5" fill="#3A3A3A"/>')
    face = ('<ellipse cx="27" cy="27" rx="6" ry="7" fill="#3A3A3A" transform="rotate(-18 27 27)"/>'
            '<ellipse cx="45" cy="27" rx="6" ry="7" fill="#3A3A3A" transform="rotate(18 45 27)"/>'
            '<circle cx="27" cy="26" r="2.9" fill="#fff"/><circle cx="45" cy="26" r="2.9" fill="#fff"/>'
            '<circle cx="27" cy="26" r="1.6" fill="#3A2A20"/><circle cx="45" cy="26" r="1.6" fill="#3A2A20"/>'
            '<circle cx="27.5" cy="25" r="0.6" fill="#fff"/><circle cx="45.5" cy="25" r="0.6" fill="#fff"/>'
            '<ellipse cx="36" cy="35" rx="6" ry="4.5" fill="#3A3A3A"/>'
            '<circle cx="34" cy="34" r="1.1" fill="#fff"/><circle cx="38" cy="34" r="1.1" fill="#fff"/>'
            '<path class="th" d="M36 36 L36 38.5 M36 38.5 Q33.5 40 32 39 M36 38.5 Q38.5 40 40 39"/>'
            + _blush(33))
    return _animal(body, belly, ears, face, head_r=21)

# ---- 北极熊 ----
def icon_polarbear():
    body, belly = "#EAF0F4", "#FFFFFF"
    ears = (f'<circle class="st" cx="19" cy="12" r="7.5" fill="{body}"/><circle cx="19" cy="12" r="3.7" fill="#D8E2E8"/>'
            f'<circle class="st" cx="53" cy="12" r="7.5" fill="{body}"/><circle cx="53" cy="12" r="3.7" fill="#D8E2E8"/>')
    face = (f'<ellipse cx="36" cy="36" rx="10" ry="8" fill="{belly}"/>' + _eyes()
            + f'<ellipse cx="36" cy="33" rx="3.2" ry="2.5" fill="#3A2A20"/>'
            '<path class="th" d="M36 36 L36 39 M36 39 Q33 41.5 31 39.5 M36 39 Q39 41.5 41 39.5"/>' + _blush())
    return _animal(body, belly, ears, face)

# ---- 狗 ----
def icon_dog():
    body, belly = "#E8A85C", "#F5D9AE"
    ears = (f'<path class="st" d="M16 20 Q9 18 11 31 Q12 37 19 33 Q21 26 20 20 Z" fill="#B87840"/>'
            f'<path class="st" d="M56 20 Q63 18 61 31 Q60 37 53 33 Q51 26 52 20 Z" fill="#B87840"/>')
    tail = f'<path class="st" d="M57 58 Q69 54 66 43 Q64 39 61 42 Q63 50 55 53 Z" fill="{body}"/>'
    face = (f'<ellipse cx="36" cy="36" rx="11" ry="9" fill="{belly}"/>' + _eyes()
            + '<ellipse cx="36" cy="34" rx="4" ry="3" fill="#5A3A28"/>'
            '<path class="th" d="M36 37 L36 40 M36 40 Q33 42.5 31 40.5 M36 40 Q39 42.5 41 40.5"/>'
            + _blush())
    return _animal(body, belly, ears, face, tail=tail)

# ---- 狐狸 ----
def icon_fox():
    body, belly = "#F08A3E", "#FBE8D0"
    ears = (f'<path class="st" d="M17 22 L13 4 L28 16 Z" fill="{body}"/><path d="M16 12 L14 6 L22 13 Z" fill="#3A2A20"/>'
            f'<path class="st" d="M55 22 L59 4 L44 16 Z" fill="{body}"/><path d="M58 12 L60 6 L52 13 Z" fill="#3A2A20"/>')
    tail = (f'<path class="st" d="M56 66 Q72 60 66 40 Q64 34 58 38 Q62 54 52 58 Z" fill="{body}"/>'
            '<path d="M65 41 Q67 35 63 38 Q63 44 60 48 Z" fill="#FBE8D0"/>')
    face = (f'<path d="M24 26 Q30 41 36 43 Q42 41 48 26 Q44 38 36 39 Q28 38 24 26 Z" fill="{belly}"/>'
            + _eyes(y=25) + '<path d="M34 32 L38 32 L36 36 Z" fill="#3A2A20"/>' + _blush(y=31))
    return _animal(body, belly, ears, face, tail=tail)

# ---- 老虎 ----
def icon_tiger():
    body, belly = "#F5A04A", "#FBE0BE"
    ears = (f'<circle class="st" cx="19" cy="12" r="7.5" fill="{body}"/><circle cx="19" cy="12" r="3.7" fill="#3A2A20"/>'
            f'<circle class="st" cx="53" cy="12" r="7.5" fill="{body}"/><circle cx="53" cy="12" r="3.7" fill="#3A2A20"/>')
    face = (f'<ellipse cx="36" cy="35" rx="11" ry="9" fill="{belly}"/>'
            '<path class="th" d="M31 18 L41 18 M32 21 L40 21 M33 24 L39 24" stroke="#3A2A20"/>'
            '<path class="th" d="M20 24 L25 26 M19 29 L24 30 M44 26 L49 24 M44 30 L49 29" stroke="#3A2A20"/>'
            + _eyes(y=27) + '<ellipse cx="36" cy="32" rx="3.2" ry="2.5" fill="#3A2A20"/>'
            '<path class="th" d="M36 35 L36 38 M36 38 Q33 40 31 38.5 M36 38 Q39 40 41 38.5"/>' + _blush(y=33))
    extra = '<path class="th" d="M24 56 L28 58 M22 64 L27 65 M48 56 L44 58 M50 64 L45 65" stroke="#3A2A20"/>'
    return _animal(body, belly, ears, face, extra=extra)

# ---- 狮子 ----
def icon_lion():
    body, belly, mane = "#F2C14E", "#FBE0AE", "#C68A3A"
    ears = (f'<circle class="st" cx="36" cy="28" r="26" fill="{mane}"/>'
            f'<g fill="#B87838"><circle cx="18" cy="18" r="4"/><circle cx="54" cy="18" r="4"/>'
            f'<circle cx="13" cy="30" r="4"/><circle cx="59" cy="30" r="4"/><circle cx="18" cy="42" r="4"/><circle cx="54" cy="42" r="4"/></g>'
            f'<circle cx="20" cy="16" r="5" fill="{body}"/><circle cx="52" cy="16" r="5" fill="{body}"/>')
    face = (f'<ellipse cx="36" cy="36" rx="10" ry="8" fill="{belly}"/>' + _eyes()
            + '<ellipse cx="36" cy="33" rx="3.2" ry="2.5" fill="#3A2A20"/>'
            '<path class="th" d="M36 36 L36 39 M36 39 Q33 41 31 39.5 M36 39 Q39 41 41 39.5"/>' + _blush())
    return _animal(body, belly, ears, face, head_r=20)

# ---- 猴子 ----
def icon_monkey():
    body, belly = "#A87042", "#E8C9A0"
    ears = (f'<circle class="st" cx="15" cy="20" r="8" fill="{body}"/><circle cx="15" cy="20" r="4.5" fill="#E8C9A0"/>'
            f'<circle class="st" cx="57" cy="20" r="8" fill="{body}"/><circle cx="57" cy="20" r="4.5" fill="#E8C9A0"/>')
    tail = '<path class="st" d="M56 62 Q72 62 67 42 Q65 36 61 40 Q63 52 55 56 Z" fill="'+body+'"/>'
    face = (f'<path d="M18 26 Q18 45 36 46 Q54 45 54 26 Q48 20 36 21 Q24 20 18 26 Z" fill="{belly}"/>'
            + _eyes(y=26) + '<ellipse cx="36" cy="36" rx="7" ry="5" fill="#D8A878"/>'
            '<circle cx="34" cy="35" r="1.2" fill="#3A2A20"/><circle cx="38" cy="35" r="1.2" fill="#3A2A20"/>'
            '<path class="th" d="M32 40 Q36 43 40 40"/>' + _blush(y=32))
    return _animal(body, belly, ears, face, tail=tail)

# ---- 奶牛 ----
def icon_cow():
    body, belly = "#F4F0EA", "#FFFFFF"
    horns = (f'<path class="st" d="M20 10 Q15 3 13 6 Q15 11 19 14 Z" fill="#E8D8B8"/>'
             f'<path class="st" d="M52 10 Q57 3 59 6 Q57 11 53 14 Z" fill="#E8D8B8"/>')
    ears = (horns + f'<path class="st" d="M14 22 Q7 24 8 31 Q14 30 18 25 Z" fill="{body}"/>'
            f'<path class="st" d="M58 22 Q65 24 64 31 Q58 30 54 25 Z" fill="{body}"/>')
    face = (f'<path d="M18 20 Q25 16 28 22 Q23 25 18 24 Z" fill="#3A2A20"/>'
            f'<path d="M46 22 Q50 16 55 21 Q50 25 47 24 Z" fill="#3A2A20"/>'
            f'<ellipse cx="36" cy="36" rx="12" ry="9" fill="#FFC4C0"/>' + _eyes(y=27)
            + '<circle cx="32" cy="36" r="1.6" fill="#B85450"/><circle cx="40" cy="36" r="1.6" fill="#B85450"/>')
    extra = ('<path d="M22 54 Q29 50 31 58 Q26 63 22 60 Z" fill="#3A2A20"/>'
             '<path d="M46 60 Q53 58 52 67 Q47 69 44 65 Z" fill="#3A2A20"/>')
    return _animal(body, belly, ears, face, extra=extra)

# ---- 猪 ----
def icon_pig():
    body, belly = "#F7A8B8", "#FCCED8"
    ears = (f'<path class="st" d="M18 20 L14 8 L27 16 Z" fill="{body}"/>'
            f'<path class="st" d="M54 20 L58 8 L45 16 Z" fill="{body}"/>')
    tail = '<path d="M57 60 Q66 60 63 52 Q60 50 58 53" fill="none" stroke="#D8788C" stroke-width="3" stroke-linecap="round"/>'
    face = (_eyes(y=25)
            + '<ellipse class="st" cx="36" cy="35" rx="7" ry="5" fill="#FCC0CC"/>'
            '<circle cx="33" cy="35" r="1.3" fill="#9A5050"/><circle cx="39" cy="35" r="1.3" fill="#9A5050"/>'
            '<path class="th" d="M32 41 Q36 44 40 41"/>' + _blush(y=30))
    return _animal(body, belly, ears, face, tail=tail)

# ---- 企鹅（特殊体型）----
def icon_penguin():
    p = [_astyle()]
    p += ['<ellipse class="st" cx="27" cy="88" rx="8" ry="4" fill="#FFA73D"/>',
          '<ellipse class="st" cx="45" cy="88" rx="8" ry="4" fill="#FFA73D"/>']
    p.append('<path class="st" d="M36 8 Q56 12 55 48 Q54 76 44 84 L28 84 Q18 76 17 48 Q16 12 36 8 Z" fill="#3B4758"/>')
    p.append('<path d="M36 18 Q48 22 48 46 Q47 70 41 78 L31 78 Q25 70 24 46 Q24 22 36 18 Z" fill="#fff"/>')
    p.append('<path class="st" d="M18 42 Q10 52 16 65 Q20 56 23 52 Z" fill="#2E3848"/>')
    p.append('<path class="st" d="M54 42 Q62 52 56 65 Q52 56 49 52 Z" fill="#2E3848"/>')
    p.append('<circle cx="29" cy="29" r="3.2" fill="#fff"/><circle cx="43" cy="29" r="3.2" fill="#fff"/>')
    p.append('<circle cx="29" cy="30" r="1.8" fill="#3A2A20"/><circle cx="43" cy="30" r="1.8" fill="#3A2A20"/>')
    p.append('<circle cx="29.6" cy="29" r="0.7" fill="#fff"/><circle cx="43.6" cy="29" r="0.7" fill="#fff"/>')
    p.append('<path class="st" d="M31 35 L41 35 L36 41 Z" fill="#FFA73D"/>')
    p.append('<ellipse cx="25" cy="37" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/><ellipse cx="47" cy="37" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 蜜蜂 ----
def icon_bee():
    p = [_astyle()]
    p.append('<ellipse cx="26" cy="20" rx="9" ry="12" fill="#D8EEF8" opacity="0.85" transform="rotate(-20 26 20)"/>')
    p.append('<ellipse cx="46" cy="20" rx="9" ry="12" fill="#D8EEF8" opacity="0.85" transform="rotate(20 46 20)"/>')
    p.append('<path d="M24 70 L22 78 M36 71 L36 80 M48 70 L50 78" stroke="#3A2A20" stroke-width="2.5" stroke-linecap="round"/>')
    p.append('<ellipse class="st" cx="36" cy="52" rx="18" ry="22" fill="#F5C243"/>')
    p.append('<path d="M19 44 Q36 50 53 44 L53 50 Q36 56 19 50 Z" fill="#3A2A20"/>')
    p.append('<path d="M20 60 Q36 66 52 60 L52 66 Q36 72 20 66 Z" fill="#3A2A20"/>')
    p.append('<circle class="st" cx="36" cy="28" r="14" fill="#3A2A20"/>')
    p.append('<circle cx="31" cy="26" r="2.6" fill="#fff"/><circle cx="41" cy="26" r="2.6" fill="#fff"/>')
    p.append('<circle cx="31" cy="27" r="1.4" fill="#3A2A20"/><circle cx="41" cy="27" r="1.4" fill="#3A2A20"/>')
    p.append('<path d="M31 15 Q28 9 26 8 M41 15 Q44 9 46 8" stroke="#3A2A20" stroke-width="2" fill="none" stroke-linecap="round"/>')
    p.append('<circle cx="26" cy="8" r="1.6" fill="#F5C243"/><circle cx="46" cy="8" r="1.6" fill="#F5C243"/>')
    p.append('<ellipse cx="26" cy="32" rx="2.6" ry="1.8" fill="#FF9B8A" opacity="0.6"/><ellipse cx="46" cy="32" rx="2.6" ry="1.8" fill="#FF9B8A" opacity="0.6"/>')
    return svg("".join(p), vb=AVB)

# ---- 小鸟 ----
def icon_bird():
    body = "#4FA9E8"
    p = [_astyle()]
    p.append('<path d="M28 80 L28 88 M44 80 L44 88" stroke="#E88A2A" stroke-width="2.5" stroke-linecap="round"/>')
    p.append('<ellipse class="st" cx="36" cy="60" rx="18" ry="20" fill="'+body+'"/>')
    p.append('<ellipse cx="36" cy="64" rx="11" ry="13" fill="#D8ECFA"/>')
    p.append('<path class="st" d="M52 56 L62 54 L60 62 L54 64 Z" fill="#3A86C4"/>')
    p.append('<path class="st" d="M24 52 Q14 56 18 68 Q24 62 28 58 Z" fill="#3A86C4"/>')
    p.append('<circle class="st" cx="36" cy="28" r="16" fill="'+body+'"/>')
    p.append('<circle cx="32" cy="26" r="3" fill="#fff"/><circle cx="32" cy="27" r="1.7" fill="#3A2A20"/><circle cx="32.6" cy="26" r="0.7" fill="#fff"/>')
    p.append('<path class="st" d="M46 28 L57 31 L46 34 Z" fill="#FFA73D"/>')
    p.append('<ellipse cx="27" cy="32" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 青蛙 ----
def icon_frog():
    body = "#6BCB77"
    p = [_astyle()]
    p.append('<ellipse class="st" cx="25" cy="88" rx="10" ry="5" fill="#57B063"/>')
    p.append('<ellipse class="st" cx="47" cy="88" rx="10" ry="5" fill="#57B063"/>')
    p.append('<ellipse class="st" cx="36" cy="66" rx="20" ry="18" fill="'+body+'"/>')
    p.append('<ellipse cx="36" cy="68" rx="13" ry="11" fill="#DDF5D8"/>')
    p.append('<path class="st" d="M24 26 Q36 22 48 26 Q52 42 46 45 Q36 41 26 45 Q20 42 24 26 Z" fill="'+body+'"/>')
    p.append('<circle class="st" cx="24" cy="20" r="10" fill="'+body+'"/>')
    p.append('<circle class="st" cx="48" cy="20" r="10" fill="'+body+'"/>')
    p.append('<circle cx="24" cy="21" r="5" fill="#fff"/><circle cx="48" cy="21" r="5" fill="#fff"/>')
    p.append('<circle cx="24" cy="22" r="2.6" fill="#3A2A20"/><circle cx="48" cy="22" r="2.6" fill="#3A2A20"/>')
    p.append('<circle cx="25" cy="21" r="1" fill="#fff"/><circle cx="49" cy="21" r="1" fill="#fff"/>')
    p.append('<path class="th" d="M28 42 Q36 47 44 42"/>')
    p.append('<ellipse cx="20" cy="40" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/><ellipse cx="52" cy="40" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 恐龙 ----
def icon_dino():
    body = "#7CC98A"
    p = [_astyle()]
    p.append('<path class="st" d="M56 62 Q72 64 68 50 Q64 54 54 56 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M30 16 L27 8 L34 15 Z" fill="#4FA860"/>')
    p.append('<path class="st" d="M22 46 L15 42 L22 52 Z" fill="#4FA860"/>')
    p.append('<path class="st" d="M50 46 L57 42 L50 52 Z" fill="#4FA860"/>')
    p.append('<ellipse class="st" cx="27" cy="88" rx="9" ry="5" fill="#5BAE6D"/>')
    p.append('<ellipse class="st" cx="46" cy="88" rx="9" ry="5" fill="#5BAE6D"/>')
    p.append('<ellipse class="st" cx="36" cy="62" rx="17" ry="20" fill="'+body+'"/>')
    p.append('<ellipse cx="36" cy="66" rx="10" ry="13" fill="#DDF5D8"/>')
    p.append('<path class="st" d="M21 52 Q15 55 18 61 Q22 58 24 55 Z" fill="'+body+'"/>')
    p.append('<circle class="st" cx="36" cy="26" r="18" fill="'+body+'"/>')
    p.append('<circle cx="31" cy="24" r="2.8" fill="#fff"/><circle cx="41" cy="24" r="2.8" fill="#fff"/>')
    p.append('<circle cx="31" cy="25" r="1.6" fill="#3A2A20"/><circle cx="41" cy="25" r="1.6" fill="#3A2A20"/>')
    p.append('<circle cx="31.6" cy="24" r="0.6" fill="#fff"/><circle cx="41.6" cy="24" r="0.6" fill="#fff"/>')
    p.append('<circle cx="46" cy="29" r="1.3" fill="#3A2A20"/><circle cx="49" cy="31" r="1.3" fill="#3A2A20"/>')
    p.append('<path class="th" d="M44 34 Q40 37 36 34"/>')
    p.append('<ellipse cx="24" cy="31" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 霸王龙（站立、大张嘴、短手粗尾）----
def icon_trex():
    body = "#B07A55"; dark = "#8F5E3C"; belly = "#E8C9A6"
    p = [_astyle()]
    # 大尾巴
    p.append('<path class="st" d="M31 58 Q12 64 6 51 Q17 49 29 48 Z" fill="'+body+'"/>')
    # 两只粗后腿
    p.append('<path class="st" d="M29 60 L23 88 L32 88 Q35 76 36 63 Z" fill="'+dark+'"/>')
    p.append('<path class="st" d="M40 60 L37 88 L49 88 Q51 74 49 62 Z" fill="'+body+'"/>')
    p.append('<ellipse class="st" cx="27" cy="89" rx="9" ry="4.3" fill="'+dark+'"/>')
    p.append('<ellipse class="st" cx="44" cy="89" rx="10" ry="4.5" fill="'+dark+'"/>')
    # 身体
    p.append('<path class="st" d="M26 45 Q24 62 41 64 Q53 62 51 47 Q49 39 40 39 Q30 39 26 45 Z" fill="'+body+'"/>')
    p.append('<path d="M39 47 Q49 51 47 62 Q41 60 39 52 Z" fill="'+belly+'"/>')
    # 小短手
    p.append('<path class="st" d="M45 47 Q54 48 52 56 Q47 55 46 51 Z" fill="'+body+'"/>')
    # 脖子
    p.append('<path class="st" d="M35 40 Q35 27 46 25 Q52 28 49 40 Q45 42 40 42 Z" fill="'+body+'"/>')
    # 大头（上颚）
    p.append('<path class="st" d="M41 14 Q62 12 65 26 Q65 33 57 35 Q45 37 41 31 Q37 22 41 14 Z" fill="'+body+'"/>')
    # 下颚（张开）
    p.append('<path class="st" d="M44 31 Q54 34 62 31 Q58 41 49 41 Q44 38 44 31 Z" fill="'+dark+'"/>')
    p.append('<path d="M47 33 Q54 35 59 33 Q56 38.5 50 38.5 Q47 37 47 33 Z" fill="#8E3B2E"/>')
    # 上牙
    p.append('<path d="M48 33 L49 37.5 L50 33 M53 33.5 L54 38 L55 33.5 M57.5 33 L58 36.5 L59 33" fill="#fff"/>')
    # 眼睛
    p.append('<circle cx="53" cy="23" r="3.2" fill="#fff"/><circle cx="53.6" cy="23.5" r="1.9" fill="#3A2A20"/>')
    p.append('<circle cx="54.3" cy="22.8" r="0.7" fill="#fff"/>')
    p.append('<circle cx="60.5" cy="27" r="1.2" fill="#3A2A20"/>')
    return svg("".join(p), vb=AVB)

# ---- 腕龙（超长脖子、小脑袋、四腿长尾）----
def icon_bronto():
    body = "#8AA9B8"; dark = "#6E8A9C"; belly = "#D6E4E8"
    p = [_astyle()]
    # 长尾巴
    p.append('<path class="st" d="M48 55 Q68 51 67 42 Q57 49 50 49 Z" fill="'+body+'"/>')
    # 四条柱状腿
    p.append('<path class="st" d="M20 62 L18 88 L26 88 L28 64 Z" fill="'+dark+'"/>')
    p.append('<path class="st" d="M48 62 L47 88 L54 88 L53 64 Z" fill="'+dark+'"/>')
    p.append('<path class="st" d="M27 62 L25 88 L34 88 L34 64 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M41 62 L40 88 L49 88 L48 64 Z" fill="'+body+'"/>')
    p.append('<ellipse class="st" cx="25" cy="89" rx="8" ry="4" fill="'+dark+'"/>')
    p.append('<ellipse class="st" cx="47" cy="89" rx="8" ry="4" fill="'+dark+'"/>')
    # 圆身体
    p.append('<ellipse class="st" cx="34" cy="55" rx="20" ry="18" fill="'+body+'"/>')
    p.append('<ellipse cx="34" cy="62" rx="11" ry="10" fill="'+belly+'"/>')
    # 超长脖子（向左上方弯起）
    p.append('<path class="st" d="M23 47 Q11 29 22 11 Q30 9 30 17 Q26 32 32 47 Z" fill="'+body+'"/>')
    # 小脑袋
    p.append('<path class="st" d="M17 7 Q31 4 34 12 Q34 18 25 19 Q16 17 17 7 Z" fill="'+body+'"/>')
    p.append('<circle cx="28" cy="11" r="2.3" fill="#fff"/><circle cx="28.5" cy="11.3" r="1.3" fill="#3A2A20"/>')
    p.append('<circle cx="21" cy="10" r="1" fill="#3A2A20"/>')
    p.append('<path class="th" d="M20 15 Q24 17 29 14.5"/>')
    p.append('<ellipse cx="23" cy="14" rx="2" ry="1.4" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 吼叫（恐龙头部特写，大张嘴 + 声波）----
def icon_roar():
    body = "#D8864A"; dark = "#B56A38"
    p = [_astyle()]
    # 三道声波（吻前方）
    p.append('<path d="M57 25 Q64 34 57 43" fill="none" stroke="#F2A65A" stroke-width="3.6" stroke-linecap="round"/>')
    p.append('<path d="M52 20 Q62 34 52 48" fill="none" stroke="#F2A65A" stroke-width="3.6" stroke-linecap="round" opacity="0.62"/>')
    p.append('<path d="M47 16 Q59 34 47 52" fill="none" stroke="#F2A65A" stroke-width="3.6" stroke-linecap="round" opacity="0.34"/>')
    # 上颚 + 头盖（朝右：脑后隆起、头顶平、吻部前突）
    p.append('<path class="st" d="M11 41 Q8 22 23 16 Q37 11 47 18 Q53 22 52 29 Q51 34 45 34 L17 37 Q11 38 11 41 Z" fill="'+body+'"/>')
    # 下颚（大张向下）
    p.append('<path class="st" d="M17 37 L45 34 Q46 49 30 49 Q18 48 17 37 Z" fill="'+dark+'"/>')
    # 口腔（深红）
    p.append('<path d="M21 37 L42 35 Q41 45 30 45 Q22 44 21 37 Z" fill="#8E3B2E"/>')
    # 上牙（向下）
    p.append('<path d="M24 36 L25 41 L26 36 M29 36 L30 41.5 L31 36 M34 35.6 L35 41 L36 35.6 M39 35 L39.8 39.5 L40.8 35" fill="#fff"/>')
    # 下牙（向上）
    p.append('<path d="M26 45 L27 39 L28 45 M32 45.5 L33 39.5 L34 45.5 M37 43.5 L37.8 39.5 L38.8 43.5" fill="#fff"/>')
    # 怒眉 + 眼睛（头顶靠后）
    p.append('<path d="M24 19 L33 21" stroke="#3A2A20" stroke-width="2.6" stroke-linecap="round"/>')
    p.append('<circle cx="29" cy="25.5" r="3.4" fill="#fff"/><circle cx="29.8" cy="26" r="2" fill="#3A2A20"/>')
    p.append('<circle cx="30.5" cy="25.2" r="0.8" fill="#fff"/>')
    # 鼻孔（吻端）
    p.append('<circle cx="46.5" cy="24" r="1.3" fill="#3A2A20"/>')
    return svg("".join(p), vb=AVB)

# ---- 袋鼠 ----
def icon_kangaroo():
    body = "#C89858"
    p = [_astyle()]
    p.append('<path class="st" d="M54 66 Q72 68 67 48 Q63 50 58 60 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M24 62 L21 84 L32 84 Q34 74 33 62 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M48 62 L51 84 L40 84 Q38 74 39 62 Z" fill="'+body+'"/>')
    p.append('<ellipse class="st" cx="25" cy="88" rx="9" ry="4" fill="#B88644"/>')
    p.append('<ellipse class="st" cx="47" cy="88" rx="9" ry="4" fill="#B88644"/>')
    p.append('<path class="st" d="M36 14 Q50 20 48 46 Q46 64 42 68 L30 68 Q26 64 24 46 Q22 20 36 14 Z" fill="'+body+'"/>')
    p.append('<path d="M36 28 Q44 32 43 52 Q40 64 36 65 Q32 64 29 52 Q28 32 36 28 Z" fill="#EFD6AE"/>')
    p.append('<path d="M30 50 Q36 54 42 50" fill="none" stroke="#A87844" stroke-width="1.5"/>')
    p.append('<path class="st" d="M24 38 Q18 42 20 50 Q25 48 26 42 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M48 38 Q54 42 52 50 Q47 48 46 42 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M30 16 Q26 0 31 2 Q35 8 34 16 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M42 16 Q46 0 41 2 Q37 8 38 16 Z" fill="'+body+'"/>')
    p.append('<path d="M31 12 Q29 5 31 6 Q33 10 33 14 Z" fill="#F0C4A8"/><path d="M41 12 Q43 5 41 6 Q39 10 39 14 Z" fill="#F0C4A8"/>')
    p.append('<circle class="st" cx="36" cy="22" r="14" fill="'+body+'"/>')
    p.append('<circle cx="31" cy="21" r="2.2" fill="#3A2A20"/><circle cx="41" cy="21" r="2.2" fill="#3A2A20"/>')
    p.append('<circle cx="31.7" cy="20" r="0.8" fill="#fff"/><circle cx="41.7" cy="20" r="0.8" fill="#fff"/>')
    p.append('<path d="M34 27 L38 27 L36 29 Z" fill="#3A2A20"/>')
    p.append('<path class="th" d="M36 29 L36 31 M36 31 Q34 33 33 31.5 M36 31 Q38 33 39 31.5"/>')
    p.append('<ellipse cx="27" cy="26" rx="2.4" ry="1.7" fill="#FF9B8A" opacity="0.6"/><ellipse cx="45" cy="26" rx="2.4" ry="1.7" fill="#FF9B8A" opacity="0.6"/>')
    return svg("".join(p), vb=AVB)

# ---- 大象 ----
def icon_elephant():
    body = "#A8B0B8"
    p = [_astyle()]
    p.append('<path class="st" d="M16 18 Q5 16 7 32 Q9 42 18 37 Z" fill="#98A0A8"/>')
    p.append('<path class="st" d="M56 18 Q67 16 65 32 Q63 42 54 37 Z" fill="#98A0A8"/>')
    p.append('<ellipse class="st" cx="25" cy="88" rx="10" ry="5" fill="#98A0A8"/>')
    p.append('<ellipse class="st" cx="47" cy="88" rx="10" ry="5" fill="#98A0A8"/>')
    p.append('<rect class="st" x="19" y="48" width="34" height="34" rx="17" fill="'+body+'"/>')
    p.append('<ellipse cx="36" cy="66" rx="12" ry="13" fill="#C4CCD2"/>')
    p.append('<ellipse class="st" cx="13" cy="58" rx="7" ry="8" fill="'+body+'"/>')
    p.append('<ellipse class="st" cx="59" cy="58" rx="7" ry="8" fill="'+body+'"/>')
    p.append('<circle class="st" cx="36" cy="28" r="20" fill="'+body+'"/>')
    p.append('<path class="st" d="M44 36 Q55 42 50 55 Q48 61 43 56 Q40 52 44 51 Q46 54 47 50 Z" fill="'+body+'"/>')
    p.append('<path d="M29 37 Q26 45 28 49 Q31 44 32 38 Z" fill="#F4F0E0"/>')
    p.append('<circle cx="28" cy="25" r="2.6" fill="#3A2A20"/><circle cx="42" cy="25" r="2.6" fill="#3A2A20"/>')
    p.append('<circle cx="28.8" cy="24" r="0.9" fill="#fff"/><circle cx="42.8" cy="24" r="0.9" fill="#fff"/>')
    p.append('<ellipse cx="22" cy="30" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/><ellipse cx="50" cy="30" rx="3" ry="2" fill="#FF9B8A" opacity="0.5"/>')
    return svg("".join(p), vb=AVB)

# ---- 鸭子 ----
def icon_duck():
    body = "#FFD93D"
    p = [_astyle()]
    p.append('<path class="st" d="M21 86 L18 91 L30 91 L28 86 Z" fill="#FFA73D"/>')
    p.append('<path class="st" d="M40 86 L41 91 L53 91 L49 86 Z" fill="#FFA73D"/>')
    # 身体+脖子+头 连贯轮廓
    p.append('<path class="st" d="M42 10 Q56 10 56 24 Q56 33 48 37 Q40 42 42 48 Q52 52 52 62 Q52 80 32 81 Q12 80 12 62 Q12 50 24 46 Q28 38 28 30 Q28 10 42 10 Z" fill="'+body+'"/>')
    p.append('<path class="st" d="M22 54 Q15 60 22 72 Q30 64 30 58 Z" fill="#F0B828"/>')
    p.append('<path class="st" d="M50 58 L59 53 L56 63 Z" fill="#F0B828"/>')
    p.append('<circle cx="45" cy="22" r="3" fill="#fff"/><circle cx="45.5" cy="22.5" r="1.7" fill="#3A2A20"/><circle cx="46" cy="21.5" r="0.7" fill="#fff"/>')
    p.append('<path class="st" d="M52 26 L63 28 L63 32 L52 33 Z" fill="#FF8A3D"/>')
    p.append('<ellipse cx="38" cy="29" rx="2.6" ry="1.8" fill="#FF9B8A" opacity="0.6"/>')
    return svg("".join(p), vb=AVB)

# ---- 鱼（横版，64 方形）----
def icon_fish():
    p = ['<style>.st{stroke:#5B4636;stroke-width:2.3;stroke-linejoin:round;stroke-linecap:round}</style>']
    p.append('<path class="st" d="M20 32 L6 20 L10 32 L6 44 L20 32 Z" fill="#F07848"/>')
    p.append('<path class="st" d="M18 32 Q30 12 48 20 Q58 26 56 32 Q58 38 48 44 Q30 52 18 32 Z" fill="#FF8A5C"/>')
    p.append('<path d="M24 38 Q38 47 48 40 Q40 46 30 42 Z" fill="#FFD0B0"/>')
    p.append('<path class="st" d="M34 20 Q38 12 42 20 Z" fill="#F07848"/>')
    p.append('<path class="st" d="M32 44 Q36 52 42 46 Z" fill="#F07848"/>')
    p.append('<path d="M44 24 Q42 32 44 40" fill="none" stroke="#D86038" stroke-width="2"/>')
    p.append('<circle cx="48" cy="29" r="3.2" fill="#fff"/><circle cx="48.5" cy="29.5" r="1.8" fill="#3A2A20"/><circle cx="49.2" cy="28.8" r="0.7" fill="#fff"/>')
    p.append('<path d="M30 28 Q33 31 30 34 M36 25 Q39 30 36 35 M36 30 Q39 35 36 40" fill="none" stroke="#E0683C" stroke-width="1.3" opacity="0.6"/>')
    p.append('<ellipse cx="48" cy="36" rx="3" ry="2" fill="#FF9B8A" opacity="0.6"/>')
    return svg("".join(p), vb=64)

CARTOON_ICONS = {
    "bear": icon_bear, "cat": icon_cat, "rabbit": icon_rabbit, "panda": icon_panda,
    "polarbear": icon_polarbear, "dog": icon_dog, "fox": icon_fox, "tiger": icon_tiger,
    "lion": icon_lion, "monkey": icon_monkey, "cow": icon_cow, "pig": icon_pig,
    "penguin": icon_penguin, "bee": icon_bee, "bird": icon_bird, "frog": icon_frog,
    "dino": icon_dino, "kangaroo": icon_kangaroo, "elephant": icon_elephant,
    "trex": icon_trex, "bronto": icon_bronto, "roar": icon_roar,
    "duck": icon_duck, "fish": icon_fish,
}

# ======================================================================
# 绘本手绘风：物品（64 方形）
# ======================================================================
def icon_apple():
    p = [_astyle()]
    p.append('<path class="st" d="M32 20 Q15 16 14 33 Q13 49 28 53 Q32 54 36 53 Q51 49 50 33 Q49 16 32 20 Z" fill="#E8654F"/>')
    p.append('<path d="M32 19 Q31 14 33 11" stroke="#8A5A32" stroke-width="3" fill="none" stroke-linecap="round"/>')
    p.append('<path class="st" d="M33 14 Q42 9 44 15 Q37 18 33 14 Z" fill="#7FC07F"/>')
    p.append('<ellipse cx="24" cy="30" rx="3" ry="6" fill="#fff" opacity="0.5"/>')
    return svg("".join(p))

def icon_banana():
    p = [_astyle()]
    p.append('<path class="st" d="M15 17 Q10 38 30 50 Q46 55 53 47 Q47 46 44 48 Q30 50 22 40 Q18 30 21 19 Q18 15 15 17 Z" fill="#F5C842"/>')
    p.append('<path d="M15 17 Q18 14 21 19 Q18 18 15 17 Z" fill="#8A5A32"/>')
    p.append('<path d="M44 48 Q49 46 53 47 Q49 50 44 48 Z" fill="#8A5A32"/>')
    p.append('<path d="M20 24 Q22 38 36 45" fill="none" stroke="#E0A828" stroke-width="2" stroke-linecap="round"/>')
    return svg("".join(p))

def icon_bread():
    p = [_astyle()]
    p.append('<path class="st" d="M16 30 Q16 17 32 17 Q48 17 48 30 L48 47 Q48 51 44 51 L20 51 Q16 51 16 47 Z" fill="#E8B878"/>')
    p.append('<path d="M20 32 Q20 23 32 23 Q44 23 44 32 L44 46 L20 46 Z" fill="#F5D9A8"/>')
    p.append('<path d="M26 28 Q28 32 26 36 M32 26 Q34 32 32 38 M38 28 Q40 32 38 36" fill="none" stroke="#C89058" stroke-width="2" stroke-linecap="round"/>')
    return svg("".join(p))

def icon_cake():
    p = [_astyle()]
    p.append('<path class="st" d="M12 38 L52 38 L52 48 Q52 52 48 52 L16 52 Q12 52 12 48 Z" fill="#F2A0B0"/>')
    p.append('<path d="M12 38 Q16 32 20 38 Q24 32 28 38 Q32 32 36 38 Q40 32 44 38 Q48 32 52 38 Z" fill="#FDE8EE"/>')
    p.append('<path class="st" d="M20 30 L44 30 L44 38 L20 38 Z" fill="#F7C8D4"/>')
    p.append('<rect x="30" y="18" width="4" height="12" fill="#6FA8D8"/>')
    p.append('<path d="M32 18 Q35 13 32 9 Q29 13 32 18 Z" fill="#F5A040"/>')
    p.append('<circle class="st" cx="24" cy="28" r="2.5" fill="#E8484F"/>')
    return svg("".join(p))

def icon_candy():
    p = [_astyle()]
    p.append('<path class="st" d="M17 32 L6 24 L10 32 L6 40 Z" fill="#F2A0B0"/>')
    p.append('<path class="st" d="M47 32 L58 24 L54 32 L58 40 Z" fill="#F2A0B0"/>')
    p.append('<circle class="st" cx="32" cy="32" r="14" fill="#F2A0B0"/>')
    p.append('<path d="M32 22 Q42 26 38 34 Q34 40 28 36 Q26 32 30 30" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>')
    return svg("".join(p))

def icon_egg():
    p = [_astyle()]
    p.append('<path class="st" d="M32 12 Q48 15 48 34 Q48 52 32 52 Q16 52 16 34 Q16 15 32 12 Z" fill="#FAF6EE"/>')
    p.append('<ellipse cx="26" cy="26" rx="3" ry="6" fill="#fff" opacity="0.9"/>')
    return svg("".join(p))

def icon_milk():
    p = [_astyle()]
    p.append('<path class="st" d="M21 16 L43 16 L46 24 L46 52 L18 52 L18 24 Z" fill="#6FA8D8"/>')
    p.append('<path d="M21 16 L43 16 L45 24 L19 24 Z" fill="#5A90C4"/>')
    p.append('<path d="M20 28 L44 28 L44 52 L20 52 Z" fill="#F7F1E3"/>')
    p.append('<rect x="26" y="33" width="12" height="11" rx="2" fill="#6FA8D8"/>')
    p.append('<circle cx="29" cy="38" r="1.5" fill="#F7F1E3"/><circle cx="35" cy="37" r="1.5" fill="#F7F1E3"/>')
    return svg("".join(p))

def icon_jar():
    p = [_astyle()]
    p.append('<path class="st" d="M20 26 L44 26 L46 52 Q46 56 42 56 L22 56 Q18 56 18 52 Z" fill="#F2A0B0"/>')
    p.append('<path d="M20 36 L44 36 L46 52 Q46 56 42 56 L22 56 Q18 56 18 52 Z" fill="#D86078"/>')
    p.append('<rect class="st" x="17" y="18" width="30" height="9" rx="2" fill="#9B88B8"/>')
    p.append('<rect x="22" y="28" width="4" height="22" fill="#fff" opacity="0.5"/>')
    return svg("".join(p))

def icon_cup():
    p = [_astyle()]
    p.append('<path class="st" d="M18 22 L20 50 Q20 54 24 54 L40 54 Q44 54 44 50 L46 22 Z" fill="#F2A0B0"/>')
    p.append('<path d="M46 28 Q54 29 53 37 Q52 44 45 42" fill="none" stroke="#5B4636" stroke-width="3" stroke-linecap="round"/>')
    p.append('<path d="M26 18 Q24 13 27 9 M33 18 Q31 13 34 9" fill="none" stroke="#C0B8A8" stroke-width="2" stroke-linecap="round"/>')
    p.append('<ellipse cx="32" cy="24" rx="13" ry="3" fill="#F7D8E0"/>')
    return svg("".join(p))

def icon_sugar():
    p = [_astyle()]
    p.append('<path class="st" d="M20 26 L44 26 L46 52 Q46 56 42 56 L22 56 Q18 56 18 52 Z" fill="#FAF6EE"/>')
    p.append('<rect class="st" x="18" y="18" width="28" height="8" rx="2" fill="#F5C842"/>')
    p.append('<rect class="st" x="26" y="34" width="12" height="12" rx="2" fill="#fff"/>')
    p.append('<rect x="22" y="28" width="3" height="20" fill="#fff" opacity="0.7"/>')
    return svg("".join(p))

def icon_salt():
    p = [_astyle()]
    p.append('<path class="st" d="M22 24 L42 24 L42 54 Q42 56 40 56 L24 56 Q22 56 22 54 Z" fill="#FAF6EE"/>')
    p.append('<rect class="st" x="20" y="16" width="24" height="9" rx="2" fill="#6FA8D8"/>')
    p.append('<circle cx="27" cy="12" r="1.2" fill="#C0B8A8"/><circle cx="32" cy="9" r="1.2" fill="#C0B8A8"/><circle cx="37" cy="12" r="1.2" fill="#C0B8A8"/>')
    p.append('<rect x="26" y="34" width="12" height="10" rx="2" fill="#6FA8D8"/>')
    return svg("".join(p))

def icon_sponge():
    p = [_astyle()]
    p.append('<path class="st" d="M10 24 L54 22 Q57 22 56 26 L54 46 Q54 50 50 50 L14 50 Q10 50 10 46 Z" fill="#F5C842"/>')
    p.append('<circle cx="20" cy="32" r="3.5" fill="#D89828"/><circle cx="34" cy="38" r="4" fill="#D89828"/><circle cx="44" cy="30" r="3" fill="#D89828"/><circle cx="27" cy="44" r="2.5" fill="#D89828"/>')
    return svg("".join(p))

OBJECT_ICONS = {
    "apple": icon_apple, "banana": icon_banana, "bread": icon_bread, "cake": icon_cake,
    "candy": icon_candy, "egg": icon_egg, "milk": icon_milk, "jar": icon_jar,
    "cup": icon_cup, "sugar": icon_sugar, "salt": icon_salt, "sponge": icon_sponge,
}

# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--group", default="all",
                    help="real|cartoon|object|nature|life|ui|game|concept|all")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_icons_nature as gn, gen_icons_life as gl, gen_icons_ui as gu, gen_icons_game as gg
    import gen_icons_concept as gc
    groups = {
        "real": REAL_ICONS,
        "cartoon": CARTOON_ICONS,
        "object": OBJECT_ICONS,
        "nature": gn.ICONS,
        "life": gl.ICONS,
        "ui": gu.ICONS,
        "game": gg.ICONS,
        "concept": gc.ICONS,
    }
    icons = {k: v for d in groups.values() for k, v in d.items()}
    if a.only:
        keys = a.only
    elif a.group in groups:
        keys = list(groups[a.group].keys())
    else:
        keys = list(icons.keys())
    for k in keys:
        if k not in icons:
            print("  跳过（未实现）：", k); continue
        content = icons[k]()
        with open(os.path.join(OUT, k + ".svg"), "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓", k)
    # 全部重生成时，连同背景山丘一起重绘
    if a.group == "all" and not a.only:
        gn.write_backgrounds()
    # 同步资产清单（扫描磁盘，不重绘）
    import icon_common as ic
    ic.sync_manifest()
    print("完成，共", len(keys), "个；输出目录：", OUT)

if __name__ == "__main__":
    main()
