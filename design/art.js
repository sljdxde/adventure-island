/* ==========================================================
   幼小衔接 App · 插画助手 v4
   全部美术资产为自产 SVG 文件，存放于 assets/（由 tools/gen-assets.mjs 生成）
   icon(id) 返回 <img> 引用；静态写法：<img class="ic" src="assets/icons/x.svg" alt="">
   尺寸由父级 font-size 控制（.ic = 1em）
   ========================================================== */
window.icon = function (id, cls) {
  return `<img class="ic${cls ? ' ' + cls : ''}" src="assets/icons/${id}.svg" alt="">`;
};
