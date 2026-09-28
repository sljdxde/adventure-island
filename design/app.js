/* ==========================================================
   幼小衔接 App · 设计稿共享交互脚本
   舞台缩放 / Toast / 彩带 / 语音 / 音效
   ========================================================== */

// ---------- iPad 舞台自适应缩放 ----------
function fitStage() {
  const st = document.querySelector('.stage');
  if (!st) return;
  const s = Math.min(window.innerWidth / 1060, window.innerHeight / 810, 1);
  st.style.transform = 'scale(' + s + ')';
}
window.addEventListener('resize', fitStage);
document.addEventListener('DOMContentLoaded', fitStage);

// ---------- Toast ----------
let _toastTimer = null;
function toast(msg, ms) {
  let t = document.querySelector('.toast');
  if (!t) {
    t = document.createElement('div');
    t.className = 'toast';
    document.querySelector('.stage').appendChild(t);
  }
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => t.classList.remove('show'), ms || 1800);
}

// ---------- 彩带庆祝（自产图标） ----------
function confetti() {
  const stage = document.querySelector('.stage');
  const icons = ['star', 'sparkle', 'coin', 'heart', 'party', 'starface'];
  for (let i = 0; i < 26; i++) {
    const c = document.createElement('span');
    c.className = 'confetti';
    const size = 22 + Math.random() * 22;
    c.style.width = c.style.height = size + 'px';
    c.innerHTML = `<img src="assets/icons/${icons[i % icons.length]}.svg" alt="" style="width:100%;height:100%">`;
    c.style.left = (60 + Math.random() * 900) + 'px';
    c.style.top = (60 + Math.random() * 120) + 'px';
    c.style.animationDelay = (Math.random() * 0.35) + 's';
    stage.appendChild(c);
    setTimeout(() => c.remove(), 2100);
  }
}

// ---------- 语音朗读（系统 TTS，离线可用） ----------
function speak(text) {
  try {
    if (!window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'zh-CN';
    u.rate = 0.85;
    u.pitch = 1.15;
    speechSynthesis.cancel();
    speechSynthesis.speak(u);
  } catch (e) { /* 无语音环境时静默 */ }
}

// ---------- 简单音效（WebAudio，无外部文件） ----------
let _actx = null;
function tone(freq, when, dur, type, vol) {
  if (!_actx) _actx = new (window.AudioContext || window.webkitAudioContext)();
  const t = _actx.currentTime + (when || 0);
  const o = _actx.createOscillator();
  const g = _actx.createGain();
  o.type = type || 'sine';
  o.frequency.value = freq;
  g.gain.setValueAtTime(vol || 0.12, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + (dur || 0.18));
  o.connect(g); g.connect(_actx.destination);
  o.start(t); o.stop(t + (dur || 0.18) + 0.05);
}
function dingOK() { tone(523, 0, .16); tone(784, .12, .22); }
function dingNO() { tone(240, 0, .2, 'triangle', .08); }

// ---------- 演示页面通用：返回主页 ----------
function goHome() { window.location.href = '01-home.html'; }
