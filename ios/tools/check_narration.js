#!/usr/bin/env node
/* 探险岛 · 朗读稿质检（v0.13）
 *
 * 目的：自动朗读最容易出的两类错是「没东西可念」和「把答案念出来」。
 * 前者让孩子卡死，后者直接把题做废（听音找图、看影子、找规律的选项内容就是答案）。
 * 本脚本不启动浏览器：把 index.html 里的朗读模块切出来，在 node 里对着
 * Resources/*.json 的 2102 步逐条算朗读稿，断言：
 *
 *   1) 每一步都能算出非空朗读稿；
 *   2) listen / shadow / spotlight / pattern 四类题，选项内容绝不出现在朗读稿里；
 *   3) clock 的选项不许出现冒号（"3:00" 必须转写成「3 点」）；
 *   4) teach / letter 卡必须有字/词，不能只剩标点。
 *
 * 用法：node ios/tools/check_narration.js   退出码 0 = 全部通过。
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.dirname(path.dirname(path.resolve(__filename)));   // ios/
const HTML = path.join(ROOT, 'preview', 'index.html');
const RES = path.join(ROOT, 'AdventureIsland', 'Resources');

const SUBJECTS = {
  cn: 'cn_levels.json', math: 'math_levels.json', pinyin: 'pinyin_levels.json',
  english: 'english_levels.json', astro: 'astro_levels.json', geo: 'geo_levels.json',
};

/* ---------- 从 index.html 切出朗读模块 ---------- */
const html = fs.readFileSync(HTML, 'utf8');
const START = html.indexOf('const VOICE={key:null');
const ENDMARK = 'document.addEventListener("pointerdown"';
const endIdx = html.indexOf(ENDMARK, START);
if (START < 0 || endIdx < 0) {
  console.error('[FAIL] index.html 里找不到朗读模块（const VOICE={...} / pointerdown 兜底监听）');
  process.exit(1);
}
const block = html.slice(START, html.indexOf('\n', endIdx));

/* ---------- 最小运行环境 ---------- */
const spoken = [];
const ctx = {
  S: { lv: { subject: 'cn', index: 0 }, voice: { on: true, rate: 0.8 }, timeouts: [] },
  pyConvert: (t) => t,
  curLevelObj: () => ({ steps: [] }),
  currentStepObj: () => null,
  document: { addEventListener() {}, getElementById() { return null; } },
  speechSynthesis: { speak(u) { spoken.push(u.text); }, cancel() {}, getVoices() { return []; }, speaking: false, pending: false },
  SpeechSynthesisUtterance: function (text) { this.text = text; },
  setTimeout, clearTimeout, console, Math, String, Array, Object, JSON,
};
ctx.window = ctx;
vm.createContext(ctx);
try {
  vm.runInContext(block, ctx);
} catch (e) {
  console.error('[FAIL] 朗读模块无法在 node 里运行：', e.message);
  process.exit(1);
}
if (typeof ctx.voiceScript !== 'function') {
  console.error('[FAIL] 朗读模块没有导出 voiceScript()');
  process.exit(1);
}

/* ---------- 逐关逐题算朗读稿 ---------- */
const fails = [];
let steps = 0;
const ANSWER_KINDS = new Set(['listen', 'shadow', 'spotlight', 'pattern']);

for (const [sub, file] of Object.entries(SUBJECTS)) {
  const data = JSON.parse(fs.readFileSync(path.join(RES, file), 'utf8'));
  for (const lv of data.levels) {
    for (const st of lv.steps) {
      steps++;
      const where = `${sub}/${lv.id}/${st.id}`;
      let text = '';
      try {
        text = ctx.voiceScript(sub, st) || '';
      } catch (e) {
        fails.push(`${where} 抛异常：${e.message}`);
        continue;
      }
      const bare = text.replace(/[，。！？、：\s]/g, '');
      if (!bare) { fails.push(`${where}（${st.kind}）朗读稿为空`); continue; }

      if (ANSWER_KINDS.has(st.kind)) {
        /* 答案型选项：选项内容一个字都不许进朗读稿，只报位置 */
        const optLine = ctx.voiceOptionText(st) || '';
        if (optLine) fails.push(`${where}（${st.kind}）选项内容被念出来了：${optLine}`);
        const n = Array.isArray(st.options) ? st.options.length : 0;
        if (n > 0 && !text.includes('第 1 张')) fails.push(`${where}（${st.kind}）没有报出选项位置`);
      } else if (Array.isArray(st.options) && st.options.length) {
        /* 普通题：有文字的选项必须被念到 */
        for (const o of st.options) {
          const label = o && typeof o === 'object' ? (o.text || o.say || o.label) : null;
          if (label && !text.includes(String(label))) {
            fails.push(`${where}（${st.kind}）选项「${label}」没被念出来`);
          }
        }
      }
      if (st.kind === 'clock' && text.includes(':')) {
        fails.push(`${where}（clock）朗读稿里有冒号：${text}`);
      }
      if ((st.kind === 'teach' || st.kind === 'letter') && !/[^\s，。]/.test(text)) {
        fails.push(`${where}（${st.kind}）卡片没有可念的字/词`);
      }
    }
  }
}

/* 冒烟：一个典型选择题要同时念题面和选项 */
const probe = { id: 'probe-q', kind: 'quiz', question: '中国的首都是哪座城市？', options: [{ icon: 'tiananmen', text: '北京' }, { icon: 'castle' }, { icon: 'school' }] };
const probeText = ctx.voiceScript('geo', probe);
if (!probeText.includes('北京') || !probeText.includes('第 2 张')) {
  fails.push(`选择题冒烟失败：${probeText}`);
}
const listenProbe = ctx.voiceScript('cn', { id: 'p', kind: 'listen', question: '哪张图片是「日」？', options: [{ icon: 'sunrise', text: '日' }, { icon: 'moon' }] });
if (!listenProbe.includes('第 2 张')) fails.push(`listen 冒烟失败（应只报位置）：${listenProbe}`);
if (listenProbe.indexOf('，日，') >= 0) fails.push(`listen 冒烟失败（选项内容被念出）：${listenProbe}`);

console.log(`扫描 ${steps} 步`);
if (fails.length) {
  fails.slice(0, 40).forEach((f) => console.log('  [FAIL] ' + f));
  console.log(`\n结果: ${fails.length} 项不通过`);
  process.exit(1);
}
console.log('结果: 全部通过（每步都有朗读稿；答案型选项不念内容；时钟不念冒号）');
