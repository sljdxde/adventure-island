Type: task
Status: resolved
Blocked by: 10
Parent: 05

# 14: 「再念一遍」按钮与看门狗

**What to build:** 每道题旁边常驻一个 🔊，孩子听漏了点一下就能重听整题；
如果因为解禁失败等原因没出声，这个按钮会在 800ms 内自己亮出来，孩子能自己救。

**Blocked by:** 10

**Status:** ready-for-agent

- [ ] 点 🔊 重念整题，不与正在播的声音叠加
- [ ] 快速连点 5 次后仍然能出声（不会永久哑掉）
- [ ] 800ms 没进入发声状态就把按钮显眼化，出声后恢复常态
- [ ] 按钮位置不压选项、不挡角色，横屏竖屏都够得着

## Answer

HUD 右上角 `#vbtn`（`onclick="voiceReplay()"`）常驻；`voiceWatch()` 在 800ms 内没进入 speaking 就给它加 `vpulse`
（3 次脉冲后停，点任何位置清除）。重念走 `voiceSpeakStep(true)`：先 cancel 再 90ms 后开口，不会叠加也不会永久哑掉。
