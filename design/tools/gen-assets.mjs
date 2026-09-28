/* ==========================================================
   资产生成器 · 幼小衔接 App
   运行：node tools/gen-assets.mjs
   产出：design/assets/icons/*.svg（每个图标内嵌自身渐变，可独立使用）
         design/assets/bg/hills-back.svg · hills-front.svg
         design/assets/manifest.json
   说明：本文件是全部自产美术资产的唯一源；页面通过 <img src="assets/icons/x.svg"> 引用。
   ========================================================== */
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ICONS = join(ROOT, 'assets', 'icons');
const BG = join(ROOT, 'assets', 'bg');
mkdirSync(ICONS, { recursive: true });
mkdirSync(BG, { recursive: true });

/* ---------- 渐变库 ---------- */
const GRADS = {
  'g-red': ['#FF8A7A', '#E8564A'], 'g-coral': ['#FFA793', '#F0705F'],
  'g-orange': ['#FFB25C', '#F08C1F'], 'g-orangedk': ['#F5A623', '#D97706'],
  'g-gold': ['#FFE58A', '#F7B32B'], 'g-golddk': ['#F5C243', '#E5A916'],
  'g-yellow': ['#FFDD7A', '#F5A623'],
  'g-green': ['#8CE08A', '#46B45A'], 'g-greendk': ['#6FCB6A', '#3BA851'],
  'g-leaf': ['#B4E465', '#56AB2F'],
  'g-blue': ['#7CC4F5', '#3D8FD1'], 'g-sky': ['#C9ECFB', '#8ED8F6'],
  'g-purple': ['#C7B4FF', '#8F6BE8'], 'g-lav': ['#E6DEFC', '#B7A5F0'],
  'g-pink': ['#FFC1D4', '#F76EA0'], 'g-rose': ['#FFD9E4', '#FF9EBE'],
  'g-gray': ['#DDE4EA', '#9AA7B4'], 'g-graydk': ['#B9C4CE', '#7E8B98'],
  'g-brown': ['#D9A066', '#A9743B'], 'g-mtn': ['#C08552', '#8F5A33'],
  'g-cream': ['#FFFDF4', '#FFE9C2'], 'g-white': ['#FFFFFF', '#E9EDF2'],
  'g-ice': ['#EAF9FF', '#A8DCF5'],
  'g-skin': ['#FFEFD9', '#FFD3AE'], 'g-hair': ['#9C6B44', '#7A4E2C'],
  'g-pblack': ['#6A6A78', '#3A3A46'],
};

/* ---------- 图标体（viewBox 0 0 64 64） ---------- */
const S = {};

S.girl = `
  <circle cx="9" cy="36" r="8.5" fill="url(#g-hair)"/><circle cx="55" cy="36" r="8.5" fill="url(#g-hair)"/>
  <circle cx="32" cy="33" r="23" fill="url(#g-hair)"/>
  <circle cx="32" cy="38" r="18.5" fill="url(#g-skin)"/>
  <path d="M13 31 Q16 13 32 13 Q48 13 51 31 Q45 24 39 26 Q36 20 32 21 Q28 20 25 26 Q19 24 13 31 Z" fill="url(#g-hair)"/>
  <circle cx="25.5" cy="38" r="2.7" fill="#5B4636"/><circle cx="38.5" cy="38" r="2.7" fill="#5B4636"/>
  <circle cx="26.4" cy="37.1" r=".9" fill="#fff"/><circle cx="39.4" cy="37.1" r=".9" fill="#fff"/>
  <circle cx="20.5" cy="44" r="3.2" fill="#FF9E8E" opacity=".55"/><circle cx="43.5" cy="44" r="3.2" fill="#FF9E8E" opacity=".55"/>
  <path d="M28.5 45 Q32 48.5 35.5 45" stroke="#5B4636" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  <ellipse cx="23" cy="17" rx="6.5" ry="3.2" fill="#fff" opacity=".4" transform="rotate(-18 23 17)"/>`;

S.panda = `
  <circle cx="14" cy="14" r="9" fill="url(#g-pblack)"/><circle cx="50" cy="14" r="9" fill="url(#g-pblack)"/>
  <ellipse cx="32" cy="36" rx="26" ry="24" fill="url(#g-white)"/>
  <ellipse cx="22" cy="32" rx="7" ry="9" fill="url(#g-pblack)" transform="rotate(-14 22 32)"/>
  <ellipse cx="42" cy="32" rx="7" ry="9" fill="url(#g-pblack)" transform="rotate(14 42 32)"/>
  <circle cx="23" cy="31" r="2.8" fill="#fff"/><circle cx="41" cy="31" r="2.8" fill="#fff"/>
  <circle cx="23.6" cy="31.4" r="1.4" fill="#26262E"/><circle cx="40.4" cy="31.4" r="1.4" fill="#26262E"/>
  <ellipse cx="32" cy="40" rx="3.4" ry="2.6" fill="#33333D"/>
  <path d="M28.5 45 Q32 48 35.5 45" stroke="#33333D" stroke-width="2" fill="none" stroke-linecap="round"/>
  <circle cx="15" cy="40" r="3" fill="#FF9E8E" opacity=".45"/><circle cx="49" cy="40" r="3" fill="#FF9E8E" opacity=".45"/>
  <ellipse cx="22" cy="20" rx="7" ry="3.5" fill="#fff" opacity=".55" transform="rotate(-18 22 20)"/>`;

S.fox = `
  <path d="M10 7 L27 16 L14 27 Z" fill="url(#g-orange)"/><path d="M54 7 L37 16 L50 27 Z" fill="url(#g-orange)"/>
  <path d="M14 12 L23 17 L16 22 Z" fill="#FFE3C8"/><path d="M50 12 L41 17 L48 22 Z" fill="#FFE3C8"/>
  <path d="M32 12 C46 12 56 24 56 36 C56 48 44 56 32 56 C20 56 8 48 8 36 C8 24 18 12 32 12 Z" fill="url(#g-orange)"/>
  <ellipse cx="32" cy="43" rx="14" ry="10" fill="url(#g-cream)"/>
  <circle cx="24" cy="32" r="2.8" fill="#5B4636"/><circle cx="40" cy="32" r="2.8" fill="#5B4636"/>
  <circle cx="24.9" cy="31.1" r=".9" fill="#fff"/><circle cx="40.9" cy="31.1" r=".9" fill="#fff"/>
  <ellipse cx="32" cy="40" rx="3" ry="2.4" fill="#5B4636"/>
  <path d="M29 45 Q32 47.5 35 45" stroke="#5B4636" stroke-width="2" fill="none" stroke-linecap="round"/>
  <ellipse cx="22" cy="20" rx="6" ry="3" fill="#fff" opacity=".35" transform="rotate(-18 22 20)"/>`;

S.robot = `
  <circle cx="32" cy="5" r="3.5" fill="url(#g-coral)"/><rect x="30.5" y="7" width="3" height="6" rx="1.5" fill="url(#g-graydk)"/>
  <rect x="10" y="12" width="44" height="42" rx="14" fill="url(#g-lav)"/>
  <rect x="17" y="22" width="30" height="16" rx="8" fill="#3E3564"/>
  <circle cx="26" cy="30" r="3.4" fill="#8FF4FF"/><circle cx="38" cy="30" r="3.4" fill="#8FF4FF"/>
  <circle cx="27.1" cy="28.9" r="1.1" fill="#fff"/><circle cx="39.1" cy="28.9" r="1.1" fill="#fff"/>
  <rect x="26" y="44" width="12" height="3.5" rx="1.75" fill="#7C68D8"/>
  <circle cx="13.5" cy="33" r="2.5" fill="#9C8BE0"/><circle cx="50.5" cy="33" r="2.5" fill="#9C8BE0"/>
  <ellipse cx="20" cy="17" rx="7" ry="3" fill="#fff" opacity=".5" transform="rotate(-15 20 17)"/>`;

S.duck = `
  <path d="M10 36 Q4 26 13 23 Q11 30 16 33 Z" fill="url(#g-golddk)"/>
  <ellipse cx="30" cy="40" rx="20" ry="14" fill="url(#g-yellow)"/>
  <ellipse cx="26" cy="41" rx="9" ry="6" fill="#EFA22A" opacity=".85" transform="rotate(-12 26 41)"/>
  <circle cx="44" cy="22" r="12" fill="url(#g-yellow)"/>
  <path d="M54 20 Q63 23 54 29 Q50 28 50 24 Z" fill="url(#g-orangedk)"/>
  <circle cx="46" cy="19" r="2.4" fill="#5B4636"/><circle cx="46.8" cy="18.2" r=".8" fill="#fff"/>
  <circle cx="43" cy="26" r="2.6" fill="#FF9E8E" opacity=".5"/>
  <ellipse cx="38" cy="14" rx="5" ry="2.6" fill="#fff" opacity=".5" transform="rotate(-20 38 14)"/>
  <ellipse cx="22" cy="33" rx="7" ry="3.4" fill="#fff" opacity=".4" transform="rotate(-14 22 33)"/>`;

S.school = `
  <rect x="12" y="30" width="40" height="26" rx="6" fill="url(#g-cream)"/>
  <path d="M6 32 L32 10 L58 32 Z" fill="url(#g-red)"/>
  <rect x="27" y="40" width="10" height="16" rx="5" fill="url(#g-brown)"/>
  <rect x="17" y="36" width="8" height="8" rx="2.5" fill="url(#g-sky)"/><rect x="39" y="36" width="8" height="8" rx="2.5" fill="url(#g-sky)"/>
  <path d="M32 10 L32 2" stroke="#D97706" stroke-width="2.4" stroke-linecap="round"/>
  <path d="M32 2 L43 5.5 L32 9 Z" fill="url(#g-coral)"/>
  <circle cx="32" cy="26" r="4" fill="#fff"/><circle cx="32" cy="26" r="1.4" fill="#E8564A"/>
  <path d="M14 30 L32 15 L38 20 L22 33 Z" fill="#fff" opacity=".18"/>`;

S.ferris = `
  <path d="M24 58 L32 36 L40 58" stroke="url(#g-blue)" stroke-width="5" fill="none" stroke-linecap="round"/>
  <circle cx="32" cy="26" r="19" fill="none" stroke="url(#g-blue)" stroke-width="4.5"/>
  <path d="M32 7 L32 45 M13 26 L51 26 M18.6 12.6 L45.4 39.4 M45.4 12.6 L18.6 39.4" stroke="#9AD4F7" stroke-width="2.6"/>
  <circle cx="32" cy="26" r="4.5" fill="#3D8FD1"/>
  <circle cx="32" cy="7" r="4.5" fill="url(#g-coral)"/><circle cx="51" cy="26" r="4.5" fill="url(#g-gold)"/>
  <circle cx="32" cy="45" r="4.5" fill="url(#g-green)"/><circle cx="13" cy="26" r="4.5" fill="url(#g-purple)"/>
  <path d="M18 12 A19 19 0 0 1 30 7.2" stroke="#fff" stroke-width="3" fill="none" opacity=".6" stroke-linecap="round"/>`;

S.volcano = `
  <path d="M8 56 L24 20 Q32 12 40 20 L56 56 Z" fill="url(#g-mtn)"/>
  <ellipse cx="32" cy="19" rx="9" ry="4" fill="url(#g-coral)"/>
  <path d="M26 21 Q26 30 24 35 Q22 29 23 21 Z" fill="#F0705F"/><path d="M37 21 Q38 32 40 37 Q42 30 40 21 Z" fill="#F0705F"/>
  <path d="M31 22 Q31 34 30 40 Q28 33 29 22 Z" fill="#FF8A7A"/>
  <circle cx="29" cy="8" r="5" fill="url(#g-white)" opacity=".95"/><circle cx="38" cy="6" r="4" fill="url(#g-white)" opacity=".85"/><circle cx="35" cy="12" r="3.2" fill="url(#g-white)" opacity=".8"/>
  <path d="M24 22 L12 52 L20 52 L29 26 Z" fill="#fff" opacity=".16"/>`;

S.castle = `
  <rect x="10" y="24" width="12" height="32" rx="3" fill="url(#g-rose)"/>
  <rect x="42" y="24" width="12" height="32" rx="3" fill="url(#g-rose)"/>
  <rect x="20" y="32" width="24" height="24" rx="4" fill="url(#g-pink)"/>
  <rect x="10" y="18" width="4" height="8" rx="1.5" fill="url(#g-rose)"/><rect x="18" y="18" width="4" height="8" rx="1.5" fill="url(#g-rose)"/>
  <rect x="42" y="18" width="4" height="8" rx="1.5" fill="url(#g-rose)"/><rect x="50" y="18" width="4" height="8" rx="1.5" fill="url(#g-rose)"/>
  <path d="M28 56 L28 44 Q32 38 36 44 L36 56 Z" fill="url(#g-purple)"/>
  <circle cx="16" cy="32" r="2.6" fill="#fff" opacity=".9"/><circle cx="48" cy="32" r="2.6" fill="#fff" opacity=".9"/>
  <path d="M16 18 L16 8 L24 11 L16 14" fill="url(#g-coral)"/><path d="M48 18 L48 8 L56 11 L48 14" fill="url(#g-coral)"/>
  <rect x="23" y="36" width="5" height="6" rx="2" fill="#fff" opacity=".85"/><rect x="36" y="36" width="5" height="6" rx="2" fill="#fff" opacity=".85"/>`;

S.apple = `
  <path d="M32 18 C22 10 10 18 10 32 C10 46 20 56 32 54 C44 56 54 46 54 32 C54 18 42 10 32 18 Z" fill="url(#g-red)"/>
  <path d="M32 16 Q31 10 34 7" stroke="#8A5A3B" stroke-width="3" fill="none" stroke-linecap="round"/>
  <path d="M35 12 Q44 5 49 11 Q42 18 35 12 Z" fill="url(#g-leaf)"/>
  <ellipse cx="21" cy="27" rx="5" ry="8" fill="#fff" opacity=".45" transform="rotate(18 21 27)"/>`;

S.banana = `
  <path d="M12 20 Q10 44 34 50 Q50 54 56 42 Q58 37 53 38 Q40 44 28 36 Q18 30 18 20 Q18 13 12 20 Z" fill="url(#g-yellow)"/>
  <circle cx="13" cy="18" r="2.6" fill="#8A5A3B"/><circle cx="55" cy="40" r="2.4" fill="#8A5A3B"/>
  <path d="M16 24 Q19 35 30 41" stroke="#fff" stroke-width="3" fill="none" opacity=".5" stroke-linecap="round"/>`;

S.rock = `
  <polygon points="10,46 6,32 16,16 34,10 50,18 56,34 46,50 24,52" fill="url(#g-gray)"/>
  <polygon points="16,16 34,10 38,24 22,28" fill="#E2E8EE"/>
  <polygon points="38,24 50,18 56,34 44,38" fill="#C3CBD4" opacity=".8"/>`;

S.wood = `
  <rect x="8" y="22" width="40" height="22" rx="11" fill="url(#g-brown)"/>
  <ellipse cx="48" cy="33" rx="8" ry="11" fill="#E8B77E"/>
  <ellipse cx="48" cy="33" rx="4" ry="6" fill="none" stroke="#C08552" stroke-width="2.5"/>
  <path d="M14 30 Q24 28 34 30" stroke="#8A5A3B" stroke-width="2" fill="none" opacity=".4" stroke-linecap="round"/>
  <path d="M16 38 Q26 40 36 38" stroke="#8A5A3B" stroke-width="2" fill="none" opacity=".3" stroke-linecap="round"/>
  <rect x="13" y="25" width="24" height="5" rx="2.5" fill="#fff" opacity=".3"/>`;

S.key = `
  <path fill-rule="evenodd" d="M18 21 a11 11 0 1 0 0 22 a11 11 0 1 0 0 -22 Z M18 27.5 a4.5 4.5 0 1 1 0 9 a4.5 4.5 0 1 1 0 -9 Z" fill="url(#g-golddk)"/>
  <rect x="26" y="28" width="28" height="8" rx="4" fill="url(#g-golddk)"/>
  <rect x="44" y="34" width="5" height="10" rx="2" fill="url(#g-golddk)"/>
  <rect x="51" y="34" width="4" height="8" rx="2" fill="url(#g-golddk)"/>
  <path d="M11 28 A11 11 0 0 1 18 21" stroke="#fff" stroke-width="3" fill="none" opacity=".55" stroke-linecap="round"/>`;

S.sponge = `
  <rect x="8" y="20" width="48" height="28" rx="10" fill="url(#g-yellow)"/>
  <circle cx="20" cy="30" r="4" fill="#D98A0F" opacity=".5"/><circle cx="34" cy="38" r="5" fill="#D98A0F" opacity=".45"/>
  <circle cx="44" cy="28" r="3.5" fill="#D98A0F" opacity=".5"/><circle cx="27" cy="42" r="2.6" fill="#D98A0F" opacity=".4"/>
  <rect x="12" y="23" width="20" height="6" rx="3" fill="#fff" opacity=".45"/>`;

S.balloon = `
  <ellipse cx="32" cy="26" rx="16" ry="19" fill="url(#g-red)"/>
  <path d="M32 44 L27 50 L37 50 Z" fill="#E8564A"/>
  <path d="M32 50 Q28 56 33 61" stroke="#E8564A" stroke-width="2.2" fill="none" stroke-linecap="round"/>
  <ellipse cx="25" cy="17" rx="5" ry="7" fill="#fff" opacity=".5" transform="rotate(20 25 17)"/>`;

S.ice = `
  <rect x="12" y="12" width="40" height="40" rx="10" fill="url(#g-ice)"/>
  <rect x="12" y="12" width="40" height="40" rx="10" fill="none" stroke="#7FCDF4" stroke-width="2.5" opacity=".7"/>
  <path d="M20 44 L44 20" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity=".75"/>
  <path d="M28 48 L48 28" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".5"/>`;

S.magnet = `
  <path d="M16 14 L16 34 Q16 48 32 48 Q48 48 48 34 L48 14 L38 14 L38 34 Q38 38 32 38 Q26 38 26 34 L26 14 Z" fill="url(#g-red)"/>
  <rect x="15" y="8" width="12" height="10" rx="2.5" fill="url(#g-gray)"/>
  <rect x="37" y="8" width="12" height="10" rx="2.5" fill="url(#g-gray)"/>
  <path d="M19 20 L19 34" stroke="#fff" stroke-width="3" opacity=".35" stroke-linecap="round"/>`;

S.rainbow = `
  <path d="M8 52 Q32 6 56 52" stroke="url(#g-coral)" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M15 52 Q32 18 49 52" stroke="url(#g-gold)" stroke-width="7" fill="none" stroke-linecap="round"/>
  <path d="M22 52 Q32 30 42 52" stroke="url(#g-blue)" stroke-width="7" fill="none" stroke-linecap="round"/>
  <circle cx="8" cy="52" r="6" fill="#fff"/><circle cx="56" cy="52" r="6" fill="#fff"/>`;

S.sprout = `
  <path d="M32 56 Q32 42 32 32" stroke="#3BA851" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M32 34 Q14 32 12 17 Q28 17 32 30 Z" fill="url(#g-leaf)"/>
  <path d="M32 28 Q48 26 50 11 Q34 11 32 24 Z" fill="url(#g-green)"/>
  <path d="M22 24 Q27 26 30 30" stroke="#fff" stroke-width="2" fill="none" opacity=".5" stroke-linecap="round"/>`;

S.sun = `
  <path d="M32 4 L32 12 M32 52 L32 60 M4 32 L12 32 M52 32 L60 32 M12 12 L18 18 M46 46 L52 52 M12 52 L18 46 M46 18 L52 12" stroke="#F5A623" stroke-width="6" stroke-linecap="round"/>
  <circle cx="32" cy="32" r="17" fill="url(#g-gold)"/>
  <circle cx="26" cy="26" r="5" fill="#FFF3C4" opacity=".85"/>`;

S.sunrays = `
  <path d="M32 4 L32 12 M32 52 L32 60 M4 32 L12 32 M52 32 L60 32 M12 12 L18 18 M46 46 L52 52 M12 52 L18 46 M46 18 L52 12" stroke="#F5A623" stroke-width="6" stroke-linecap="round"/>`;

S.sunface = `
  <circle cx="32" cy="32" r="17" fill="url(#g-gold)"/>
  <circle cx="26.5" cy="30" r="2.2" fill="#B06A00"/><circle cx="37.5" cy="30" r="2.2" fill="#B06A00"/>
  <path d="M27 36 Q32 40 37 36" stroke="#B06A00" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <circle cx="22" cy="35" r="2.4" fill="#FF9E8E" opacity=".6"/><circle cx="42" cy="35" r="2.4" fill="#FF9E8E" opacity=".6"/>
  <ellipse cx="24" cy="22" rx="4.5" ry="3" fill="#FFF3C4" opacity=".9" transform="rotate(-20 24 22)"/>`;

S.moon = `
  <path d="M42 6 Q12 14 12 32 Q12 50 42 58 Q26 46 26 32 Q26 18 42 6 Z" fill="url(#g-gold)"/>
  <circle cx="20" cy="26" r="3" fill="#E5A916" opacity=".5"/><circle cx="17.5" cy="38" r="2.4" fill="#E5A916" opacity=".45"/><circle cx="24" cy="47" r="2" fill="#E5A916" opacity=".4"/>
  <path d="M50 12 L51.6 16.4 L56 18 L51.6 19.6 L50 24 L48.4 19.6 L44 18 L48.4 16.4 Z" fill="#FFF3C4"/>`;

S.wave = `
  <path d="M4 40 Q14 28 24 40 Q34 52 44 40 Q52 30 60 38 L60 58 L4 58 Z" fill="url(#g-blue)" opacity=".85"/>
  <path d="M4 47 Q14 37 24 47 Q34 57 44 47 Q52 39 60 45 L60 58 L4 58 Z" fill="#3D8FD1"/>
  <circle cx="14" cy="37" r="3.6" fill="#fff" opacity=".95"/><circle cx="44" cy="37" r="3.6" fill="#fff" opacity=".95"/><circle cx="29" cy="44" r="2.6" fill="#fff" opacity=".8"/>
  <circle cx="50" cy="22" r="7" fill="url(#g-sky)"/><path d="M46 22 Q50 16 55 20" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;

S.sunrise = `
  <path d="M32 10 L32 17 M12 20 L17 25 M52 20 L47 25" stroke="#F5A623" stroke-width="4" stroke-linecap="round"/>
  <path d="M16 44 A16 16 0 0 1 48 44 Z" fill="url(#g-gold)"/>
  <rect x="6" y="44" width="52" height="6" rx="3" fill="url(#g-orangedk)"/>
  <rect x="14" y="54" width="10" height="4" rx="2" fill="url(#g-blue)" opacity=".7"/>
  <rect x="29" y="54" width="14" height="4" rx="2" fill="url(#g-blue)" opacity=".7"/>
  <rect x="48" y="54" width="8" height="4" rx="2" fill="url(#g-blue)" opacity=".7"/>`;

S.cake = `
  <ellipse cx="32" cy="54" rx="24" ry="6" fill="url(#g-white)"/>
  <rect x="12" y="34" width="40" height="20" rx="6" fill="url(#g-pink)"/>
  <path d="M12 38 Q16 29 20 38 Q24 29 28 38 Q32 29 36 38 Q40 29 44 38 Q48 29 52 38 L52 42 L12 42 Z" fill="url(#g-white)"/>
  <rect x="30" y="18" width="4" height="12" rx="2" fill="url(#g-blue)"/>
  <ellipse cx="32" cy="13" rx="3" ry="4.5" fill="url(#g-gold)"/><ellipse cx="32" cy="14" rx="1.4" ry="2.4" fill="#FFF3C4"/>
  <circle cx="20" cy="47" r="1.8" fill="#fff" opacity=".8"/><circle cx="32" cy="49" r="1.8" fill="#fff" opacity=".8"/><circle cx="44" cy="47" r="1.8" fill="#fff" opacity=".8"/>`;

S.calendar = `
  <rect x="10" y="12" width="44" height="42" rx="8" fill="url(#g-white)"/>
  <path d="M10 20 Q10 12 18 12 L46 12 Q54 12 54 20 L54 24 L10 24 Z" fill="url(#g-red)"/>
  <rect x="18" y="6" width="4" height="10" rx="2" fill="url(#g-graydk)"/><rect x="42" y="6" width="4" height="10" rx="2" fill="url(#g-graydk)"/>
  <circle cx="20" cy="32" r="2.6" fill="#C9D2DA"/><circle cx="32" cy="32" r="2.6" fill="#C9D2DA"/><circle cx="44" cy="32" r="2.6" fill="#C9D2DA"/>
  <circle cx="20" cy="43" r="2.6" fill="#C9D2DA"/><circle cx="32" cy="43" r="2.6" fill="#C9D2DA"/>
  <circle cx="44" cy="43" r="4" fill="url(#g-coral)"/>`;

S.star = `
  <path d="M32 6 L39.6 23.2 L58 25.4 L44.4 38 L48.4 56 L32 46.8 L15.6 56 L19.6 38 L6 25.4 L24.4 23.2 Z" fill="url(#g-gold)"/>
  <ellipse cx="26" cy="22" rx="4" ry="6" fill="#fff" opacity=".45" transform="rotate(15 26 22)"/>`;

S.medal = `
  <path d="M20 4 L32 22 L26 26 L14 9 Z" fill="url(#g-coral)"/>
  <path d="M44 4 L32 22 L38 26 L50 9 Z" fill="url(#g-red)"/>
  <circle cx="32" cy="38" r="16" fill="url(#g-gold)"/>
  <circle cx="32" cy="38" r="11" fill="#FFE9A8"/>
  <path d="M32 30 L34.6 35.6 L40.6 36.3 L36.2 40.4 L37.4 46.2 L32 43.3 L26.6 46.2 L27.8 40.4 L23.4 36.3 L29.4 35.6 Z" fill="url(#g-orangedk)"/>
  <path d="M20 30 A16 16 0 0 1 28 23" stroke="#fff" stroke-width="3" fill="none" opacity=".6" stroke-linecap="round"/>`;

S.gift = `
  <rect x="10" y="26" width="44" height="30" rx="6" fill="url(#g-coral)"/>
  <rect x="7" y="18" width="50" height="12" rx="5" fill="url(#g-red)"/>
  <rect x="28" y="18" width="8" height="38" fill="url(#g-gold)"/>
  <path d="M32 18 Q22 5 15 11 Q11 18 24 18 Z" fill="url(#g-gold)"/>
  <path d="M32 18 Q42 5 49 11 Q53 18 40 18 Z" fill="url(#g-golddk)"/>
  <circle cx="32" cy="17" r="4" fill="url(#g-golddk)"/>
  <rect x="14" y="32" width="6" height="18" rx="3" fill="#fff" opacity=".3"/>`;

S.clip = `
  <rect x="12" y="8" width="40" height="50" rx="7" fill="url(#g-brown)"/>
  <rect x="17" y="14" width="30" height="38" rx="4" fill="url(#g-white)"/>
  <rect x="25" y="4" width="14" height="9" rx="4" fill="url(#g-gray)"/><circle cx="32" cy="8" r="2.5" fill="#6E7A86"/>
  <rect x="22" y="22" width="20" height="3.5" rx="1.75" fill="#C9D2DA"/>
  <rect x="22" y="30" width="20" height="3.5" rx="1.75" fill="#C9D2DA"/>
  <path d="M24 42 L28 46 L37 37" stroke="url(#g-green)" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>`;

S.lock = `
  <path d="M20 30 L20 22 Q20 10 32 10 Q44 10 44 22 L44 30" stroke="url(#g-graydk)" stroke-width="7" fill="none" stroke-linecap="round"/>
  <rect x="12" y="28" width="40" height="28" rx="9" fill="url(#g-gold)"/>
  <circle cx="32" cy="40" r="4.5" fill="#8A5B00"/><rect x="30" y="42" width="4" height="8" rx="2" fill="#8A5B00"/>
  <rect x="16" y="32" width="6" height="16" rx="3" fill="#fff" opacity=".4"/>`;

S.speaker = `
  <path d="M12 26 L22 26 L36 14 L36 50 L22 38 L12 38 Z" fill="url(#g-blue)"/>
  <path d="M44 24 Q50 32 44 40" stroke="url(#g-blue)" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M50 18 Q58 32 50 46" stroke="url(#g-blue)" stroke-width="4" fill="none" opacity=".55" stroke-linecap="round"/>`;

S.home = `
  <path d="M8 30 L32 10 L56 30 Z" fill="url(#g-orange)"/>
  <rect x="14" y="28" width="36" height="26" rx="5" fill="url(#g-cream)"/>
  <rect x="27" y="38" width="10" height="16" rx="4.5" fill="url(#g-orangedk)"/>
  <rect x="18" y="34" width="7" height="7" rx="2" fill="url(#g-sky)"/><rect x="39" y="34" width="7" height="7" rx="2" fill="url(#g-sky)"/>`;

S.back = `<path d="M39 12 L21 32 L39 52" fill="none" stroke="#F08C1F" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>`;

S.fire = `
  <path d="M32 4 Q46 18 46 34 Q46 50 32 56 Q18 50 18 34 Q18 24 24 16 Q24 26 30 28 Q28 14 32 4 Z" fill="url(#g-orange)"/>
  <path d="M32 26 Q38 32 38 40 Q38 48 32 51 Q26 48 26 40 Q26 32 32 26 Z" fill="url(#g-gold)"/>
  <ellipse cx="32" cy="42" rx="4" ry="5" fill="#FFF3C4"/>`;

S.goggles = `
  <rect x="6" y="26" width="52" height="10" rx="5" fill="#7C5CE0"/>
  <rect x="12" y="22" width="17" height="18" rx="7" fill="url(#g-sky)" stroke="#fff" stroke-width="3"/>
  <rect x="35" y="22" width="17" height="18" rx="7" fill="url(#g-sky)" stroke="#fff" stroke-width="3"/>
  <rect x="28" y="28" width="8" height="5" rx="2.5" fill="#fff"/>
  <path d="M16 27 L22 33" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".9"/>
  <path d="M39 27 L45 33" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".9"/>`;

S.flask = `
  <path d="M26 8 L26 24 L12 48 Q9 56 18 56 L46 56 Q55 56 52 48 L38 24 L38 8 Z" fill="url(#g-ice)" opacity=".92"/>
  <path d="M18 38 L46 38 L52 48 Q55 56 46 56 L18 56 Q9 56 12 48 Z" fill="url(#g-purple)"/>
  <circle cx="26" cy="46" r="3" fill="#fff" opacity=".6"/><circle cx="36" cy="44" r="2.2" fill="#fff" opacity=".5"/>
  <rect x="23" y="4" width="18" height="6" rx="3" fill="url(#g-gray)"/>
  <path d="M23 30 L18 41" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".8"/>`;

S.book = `
  <path d="M32 14 Q22 8 8 10 L8 48 Q22 46 32 52 Q42 46 56 48 L56 10 Q42 8 32 14 Z" fill="url(#g-blue)"/>
  <path d="M32 16 Q24 11 12 13 L12 46 Q24 44 32 49 Q40 44 52 46 L52 13 Q40 11 32 16 Z" fill="url(#g-white)"/>
  <path d="M32 16 L32 49" stroke="#C9D2DA" stroke-width="2"/>
  <path d="M17 22 L27 21 M17 29 L27 28 M37 21 L47 22 M37 28 L47 29" stroke="#C9D2DA" stroke-width="2" stroke-linecap="round"/>`;

S.sparkle = `
  <path d="M32 6 Q34 26 54 32 Q34 38 32 58 Q30 38 10 32 Q30 26 32 6 Z" fill="url(#g-gold)"/>
  <circle cx="48" cy="14" r="3" fill="url(#g-gold)" opacity=".85"/><circle cx="16" cy="48" r="2.5" fill="url(#g-gold)" opacity=".8"/>
  <circle cx="32" cy="32" r="3" fill="#fff" opacity=".75"/>`;

S.crystal = `
  <circle cx="32" cy="28" r="18" fill="url(#g-lav)"/>
  <path d="M24 32 Q32 24 40 32" stroke="#fff" stroke-width="3" fill="none" opacity=".55" stroke-linecap="round"/>
  <ellipse cx="25" cy="20" rx="5" ry="7" fill="#fff" opacity=".6" transform="rotate(20 25 20)"/>
  <path d="M20 44 Q32 52 44 44 L46 52 Q32 60 18 52 Z" fill="url(#g-golddk)"/>`;

S.flower = `
  <circle cx="32" cy="16" r="9" fill="url(#g-pink)"/><circle cx="47" cy="27" r="9" fill="url(#g-pink)"/>
  <circle cx="41" cy="45" r="9" fill="url(#g-pink)"/><circle cx="23" cy="45" r="9" fill="url(#g-pink)"/><circle cx="17" cy="27" r="9" fill="url(#g-pink)"/>
  <circle cx="32" cy="32" r="8" fill="url(#g-gold)"/>
  <circle cx="29" cy="13" r="3" fill="#fff" opacity=".55"/>`;

S.leaf = `
  <path d="M32 6 Q54 20 50 40 Q46 56 32 58 Q18 56 14 40 Q10 20 32 6 Z" fill="url(#g-leaf)"/>
  <path d="M32 14 L32 52" stroke="#3E8E2E" stroke-width="2.5" opacity=".55" stroke-linecap="round"/>
  <path d="M32 26 L22 22 M32 36 L42 32 M32 44 L24 41" stroke="#3E8E2E" stroke-width="2" opacity=".45" stroke-linecap="round"/>
  <ellipse cx="24" cy="18" rx="5" ry="3" fill="#fff" opacity=".4" transform="rotate(-30 24 18)"/>`;

S.rocket = `
  <path d="M32 4 Q44 16 44 34 L44 46 L20 46 L20 34 Q20 16 32 4 Z" fill="url(#g-white)"/>
  <path d="M32 4 Q40 12 42 22 L22 22 Q24 12 32 4 Z" fill="url(#g-coral)"/>
  <circle cx="32" cy="32" r="6.5" fill="url(#g-sky)" stroke="#fff" stroke-width="3"/>
  <path d="M20 38 L10 52 L20 50 Z" fill="url(#g-coral)"/><path d="M44 38 L54 52 L44 50 Z" fill="url(#g-coral)"/>
  <rect x="20" y="42" width="24" height="4" fill="url(#g-coral)" opacity=".85"/>
  <path d="M26 47 Q32 60 38 47 Q35 51 32 50 Q29 51 26 47 Z" fill="url(#g-gold)"/>`;

S.party = `
  <path d="M10 54 L34 22 L42 34 Z" fill="url(#g-gold)"/>
  <path d="M17 45 L27 32" stroke="url(#g-coral)" stroke-width="4" stroke-linecap="round"/>
  <path d="M23 50 L35 34" stroke="url(#g-blue)" stroke-width="4" stroke-linecap="round"/>
  <circle cx="46" cy="14" r="3" fill="url(#g-coral)"/><circle cx="54" cy="24" r="2.5" fill="url(#g-blue)"/>
  <circle cx="40" cy="8" r="2.5" fill="url(#g-green)"/>
  <rect x="48" y="32" width="5" height="5" rx="1.5" fill="url(#g-purple)" transform="rotate(20 50 34)"/>
  <path d="M56 10 L57.2 13.3 L60.5 14.5 L57.2 15.7 L56 19 L54.8 15.7 L51.5 14.5 L54.8 13.3 Z" fill="url(#g-golddk)"/>`;

S.question = `<text x="32" y="45" text-anchor="middle" font-size="40" font-weight="900" fill="#C9BBA0" font-family="YouYuan, Microsoft YaHei, sans-serif">?</text>`;

S.clock = `
  <circle cx="14" cy="12" r="7" fill="url(#g-blue)"/><circle cx="50" cy="12" r="7" fill="url(#g-blue)"/>
  <path d="M16 54 L12 60 M48 54 L52 60" stroke="url(#g-blue)" stroke-width="5" stroke-linecap="round"/>
  <circle cx="32" cy="34" r="24" fill="url(#g-white)" stroke="url(#g-blue)" stroke-width="5"/>
  <path d="M32 34 L32 20" stroke="#5B4636" stroke-width="4" stroke-linecap="round"/>
  <path d="M32 34 L42 38" stroke="#5B4636" stroke-width="4" stroke-linecap="round"/>
  <circle cx="32" cy="34" r="3" fill="url(#g-coral)"/>`;

S.shield = `
  <path d="M32 4 L54 12 Q54 40 32 60 Q10 40 10 12 Z" fill="url(#g-blue)"/>
  <path d="M22 32 L29 40 L43 24" stroke="#fff" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M14 14 L14 30 Q14 40 22 48" stroke="#fff" stroke-width="3" fill="none" opacity=".3" stroke-linecap="round"/>`;

S.chart = `
  <rect x="10" y="34" width="10" height="22" rx="4" fill="url(#g-blue)"/>
  <rect x="27" y="22" width="10" height="34" rx="4" fill="url(#g-gold)"/>
  <rect x="44" y="12" width="10" height="44" rx="4" fill="url(#g-coral)"/>
  <rect x="6" y="56" width="52" height="5" rx="2.5" fill="url(#g-gray)"/>`;

S.slider = `
  <rect x="8" y="18" width="48" height="6" rx="3" fill="#DCE4EC"/>
  <rect x="8" y="40" width="48" height="6" rx="3" fill="#DCE4EC"/>
  <rect x="8" y="18" width="26" height="6" rx="3" fill="url(#g-blue)"/>
  <rect x="8" y="40" width="36" height="6" rx="3" fill="url(#g-coral)"/>
  <circle cx="34" cy="21" r="7" fill="#fff" stroke="url(#g-blue)" stroke-width="4"/>
  <circle cx="44" cy="43" r="7" fill="#fff" stroke="url(#g-coral)" stroke-width="4"/>`;

S.bulb = `
  <path d="M32 2 L32 8 M12 10 L16 14 M52 10 L48 14 M6 26 L12 26 M58 26 L52 26" stroke="url(#g-golddk)" stroke-width="4" stroke-linecap="round"/>
  <circle cx="32" cy="26" r="16" fill="url(#g-gold)"/>
  <path d="M28 28 Q32 22 36 28" stroke="#E5A916" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <rect x="25" y="40" width="14" height="6" rx="3" fill="url(#g-gray)"/>
  <rect x="27" y="47" width="10" height="5" rx="2.5" fill="url(#g-graydk)"/>
  <ellipse cx="26" cy="19" rx="4" ry="5.5" fill="#fff" opacity=".55" transform="rotate(20 26 19)"/>`;

S.heart = `
  <path d="M32 56 Q8 40 8 24 Q8 10 20 10 Q28 10 32 18 Q36 10 44 10 Q56 10 56 24 Q56 40 32 56 Z" fill="url(#g-red)"/>
  <ellipse cx="20" cy="20" rx="5" ry="7" fill="#fff" opacity=".45" transform="rotate(20 20 20)"/>`;

S.equal = `
  <rect x="12" y="22" width="40" height="8" rx="4" fill="url(#g-blue)"/>
  <rect x="12" y="36" width="40" height="8" rx="4" fill="url(#g-blue)"/>`;

S.hanzi = `
  <rect x="12" y="8" width="40" height="48" rx="8" fill="url(#g-white)"/>
  <rect x="18" y="14" width="28" height="36" rx="3" fill="none" stroke="#F0A898" stroke-width="2" opacity=".7"/>
  <text x="32" y="42" text-anchor="middle" font-size="26" font-weight="700" fill="#E2582A" font-family="Kaiti SC, KaiTi, STKaiti, serif">字</text>`;

/* ---------- 派对棋盘元素 ---------- */
S.block = `
  <rect x="6" y="6" width="52" height="52" rx="10" fill="url(#g-gold)"/>
  <rect x="6" y="6" width="52" height="52" rx="10" fill="none" stroke="#B8770A" stroke-width="3.5"/>
  <circle cx="13" cy="13" r="2.6" fill="#FFF6D0"/><circle cx="51" cy="13" r="2.6" fill="#FFF6D0"/>
  <circle cx="13" cy="51" r="2.6" fill="#FFF6D0"/><circle cx="51" cy="51" r="2.6" fill="#FFF6D0"/>
  <text x="32" y="45" text-anchor="middle" font-size="34" font-weight="900" fill="#fff" font-family="YouYuan, Microsoft YaHei, sans-serif" style="paint-order:stroke" stroke="#B8770A" stroke-width="5" stroke-linejoin="round">?</text>
  <path d="M12 16 Q12 12 16 12 L30 12" stroke="#fff" stroke-width="4" fill="none" opacity=".55" stroke-linecap="round"/>`;

S.blockok = `
  <rect x="6" y="6" width="52" height="52" rx="10" fill="url(#g-green)"/>
  <rect x="6" y="6" width="52" height="52" rx="10" fill="none" stroke="#2E8A40" stroke-width="3.5"/>
  <circle cx="13" cy="13" r="2.6" fill="#EAFBEA"/><circle cx="51" cy="13" r="2.6" fill="#EAFBEA"/>
  <circle cx="13" cy="51" r="2.6" fill="#EAFBEA"/><circle cx="51" cy="51" r="2.6" fill="#EAFBEA"/>
  <path d="M21 33 L29 41 L44 24" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 16 Q12 12 16 12 L30 12" stroke="#fff" stroke-width="4" fill="none" opacity=".5" stroke-linecap="round"/>`;

S.blocklock = `
  <rect x="6" y="6" width="52" height="52" rx="10" fill="url(#g-gray)"/>
  <rect x="6" y="6" width="52" height="52" rx="10" fill="none" stroke="#7E8B98" stroke-width="3.5"/>
  <circle cx="13" cy="13" r="2.6" fill="#F2F6F9"/><circle cx="51" cy="13" r="2.6" fill="#F2F6F9"/>
  <circle cx="13" cy="51" r="2.6" fill="#F2F6F9"/><circle cx="51" cy="51" r="2.6" fill="#F2F6F9"/>
  <path d="M25 34 L25 29 Q25 22 32 22 Q39 22 39 29 L39 34" stroke="#6E7A86" stroke-width="4.5" fill="none" stroke-linecap="round"/>
  <rect x="21" y="33" width="22" height="16" rx="5" fill="#6E7A86"/>
  <path d="M12 16 Q12 12 16 12 L30 12" stroke="#fff" stroke-width="4" fill="none" opacity=".5" stroke-linecap="round"/>`;

S.coin = `
  <ellipse cx="32" cy="32" rx="20" ry="26" fill="url(#g-gold)"/>
  <ellipse cx="32" cy="32" rx="20" ry="26" fill="none" stroke="#B8770A" stroke-width="3.5"/>
  <ellipse cx="32" cy="32" rx="11" ry="17" fill="none" stroke="#D98A0F" stroke-width="3.5"/>
  <path d="M24 14 Q20 20 20 28" stroke="#fff" stroke-width="4" fill="none" opacity=".7" stroke-linecap="round"/>`;

S.dice = `
  <rect x="7" y="7" width="50" height="50" rx="12" fill="url(#g-white)"/>
  <rect x="7" y="7" width="50" height="50" rx="12" fill="none" stroke="#8E99A4" stroke-width="3.5"/>
  <circle cx="21" cy="21" r="5" fill="#E8382E"/><circle cx="43" cy="21" r="5" fill="#E8382E"/>
  <circle cx="32" cy="32" r="5" fill="#E8382E"/>
  <circle cx="21" cy="43" r="5" fill="#E8382E"/><circle cx="43" cy="43" r="5" fill="#E8382E"/>
  <path d="M13 17 Q13 13 17 13 L28 13" stroke="#fff" stroke-width="4" fill="none" opacity=".8" stroke-linecap="round"/>`;

const PIPE = (color) => `
  <rect x="8" y="6" width="48" height="16" rx="6" fill="${color}"/>
  <rect x="13" y="20" width="38" height="38" rx="4" fill="${color}"/>
  <rect x="8" y="6" width="48" height="16" rx="6" fill="none" stroke="rgba(0,0,0,.28)" stroke-width="3"/>
  <rect x="13" y="20" width="38" height="38" rx="4" fill="none" stroke="rgba(0,0,0,.28)" stroke-width="3"/>
  <rect x="14" y="9" width="8" height="10" rx="4" fill="#fff" opacity=".45"/>
  <rect x="19" y="24" width="7" height="30" rx="3.5" fill="#fff" opacity=".3"/>
  <rect x="8" y="19" width="48" height="4" fill="rgba(0,0,0,.18)"/>`;
S['pipe-red'] = PIPE('#F0705F');
S['pipe-blue'] = PIPE('#4FA9E8');
S['pipe-purple'] = PIPE('#9B7BF5');

S.flag = `
  <path d="M14 6 L14 58" stroke="#5B4636" stroke-width="4.5" stroke-linecap="round"/>
  <circle cx="14" cy="6" r="4" fill="url(#g-gold)"/>
  <path d="M16 9 L54 9 L54 33 L16 33 Z" fill="url(#g-white)"/>
  <path d="M16 9 L54 9 L54 33 L16 33 Z" fill="none" stroke="#8E99A4" stroke-width="2.5"/>
  <path d="M16 9 h9.5 v12 h-9.5 Z M35 9 h9.5 v12 h-9.5 Z M25.5 21 h9.5 v12 h-9.5 Z M44.5 21 h9.5 v12 h-9.5 Z" fill="#3A3A46"/>
  <path d="M10 58 L18 58" stroke="#5B4636" stroke-width="4.5" stroke-linecap="round"/>`;

S.starface = `
  <path d="M32 5 L39.8 22.6 L58.5 24.8 L44.6 37.7 L48.7 56 L32 46.6 L15.3 56 L19.4 37.7 L5.5 24.8 L24.2 22.6 Z" fill="url(#g-gold)" stroke="#B8770A" stroke-width="3" stroke-linejoin="round"/>
  <ellipse cx="26.5" cy="31" rx="2.4" ry="3.4" fill="#5B4636"/><ellipse cx="37.5" cy="31" rx="2.4" ry="3.4" fill="#5B4636"/>
  <circle cx="27.3" cy="29.8" r=".9" fill="#fff"/><circle cx="38.3" cy="29.8" r=".9" fill="#fff"/>
  <path d="M28 38 Q32 41.5 36 38" stroke="#5B4636" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <circle cx="21.5" cy="35" r="2.6" fill="#FF9E8E" opacity=".6"/><circle cx="42.5" cy="35" r="2.6" fill="#FF9E8E" opacity=".6"/>`;

S.brick = `
  <rect x="6" y="10" width="52" height="44" rx="8" fill="url(#g-coral)"/>
  <rect x="6" y="10" width="52" height="44" rx="8" fill="none" stroke="#B0402F" stroke-width="3.5"/>
  <path d="M6 25 L58 25 M6 40 L58 40 M22 10 L22 25 M42 10 L42 25 M14 25 L14 40 M32 25 L32 40 M50 25 L50 40 M22 40 L22 54 M42 40 L42 54" stroke="#B0402F" stroke-width="3"/>
  <path d="M12 16 Q12 14 15 14 L26 14" stroke="#fff" stroke-width="3.5" fill="none" opacity=".45" stroke-linecap="round"/>`;

/* ---------- 背景 ---------- */
const HILLS_BACK = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300"><circle cx="90" cy="330" r="170" fill="#ACE27E"/><circle cx="430" cy="345" r="210" fill="#ACE27E"/><circle cx="780" cy="330" r="180" fill="#ACE27E"/><circle cx="1110" cy="345" r="200" fill="#ACE27E"/></svg>`;
const HILLS_FRONT = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="250" viewBox="0 0 1200 250"><rect y="150" width="1200" height="100" fill="#6FCC44"/><circle cx="0" cy="165" r="150" fill="#6FCC44"/><circle cx="330" cy="175" r="180" fill="#6FCC44"/><circle cx="690" cy="168" r="160" fill="#6FCC44"/><circle cx="1030" cy="175" r="180" fill="#6FCC44"/><circle cx="165" cy="150" r="120" fill="#7ED451"/><circle cx="520" cy="158" r="130" fill="#7ED451"/><circle cx="870" cy="152" r="120" fill="#7ED451"/></svg>`;

/* ---------- 写出 ---------- */
function standalone(body) {
  const used = [...new Set([...body.matchAll(/url\(#([\w-]+)\)/g)].map(m => m[1]))];
  const defs = used.map(id => {
    const [a, b] = GRADS[id];
    return `<linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>`;
  }).join('');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">${defs ? `<defs>${defs}</defs>` : ''}${body}</svg>\n`;
}

const manifest = { icons: [], bg: ['bg/hills-back.svg', 'bg/hills-front.svg'] };
for (const [id, body] of Object.entries(S)) {
  writeFileSync(join(ICONS, id + '.svg'), standalone(body));
  manifest.icons.push('icons/' + id + '.svg');
}
writeFileSync(join(BG, 'hills-back.svg'), HILLS_BACK);
writeFileSync(join(BG, 'hills-front.svg'), HILLS_FRONT);
writeFileSync(join(ROOT, 'assets', 'manifest.json'), JSON.stringify(manifest, null, 2));
console.log('assets generated:', manifest.icons.length, 'icons + 2 bg');
