Type: task
Status: resolved
Blocked by: —
Parent: 05

# 10: 进关就念第一题（最小闭环）

**What to build:** 点关卡进入任意一关，第一题立刻被念出来；孩子点任一选项，朗读立刻停；
系统不支持语音或设备被静音时，游戏完全不报错、照常可玩。

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 进关那一下点击的同步栈里起念（不能等定时器），刷新后重新进关仍然出声
- [ ] 后续每题渲染后约 0.4 秒自动念，同一道题只念一次
- [ ] 点任一选项立刻安静，不残留半句、不吞掉下一题
- [ ] 自动批跑模式（`?AISolve=1`）全程不出声
- [ ] 语音不可用 / 被静音 / 抛错时静默降级：不弹错、不卡关
- [ ] 三门闸门全绿，`preview_sweep --steps=2` 不新增失败

## Answer

落地在 `ios/preview/index.html` 的「v0.13 自动朗读」块：
- 进关那次点击的同步栈里 `voiceSpeakStep(true)` 开口（`enterLevel` / `restartLevel`），解禁后整局有效；
- 之后各题由 `afterStepRender → voiceNarrateSoon` 在 400ms 后念，`VOICE.key` 保证同一道题只念一次；
- 捕获阶段 `pointerdown` 统一 `voiceCancel()`，点哪都立刻闭嘴；
- `voiceEnabled()` 里 `!S.autoSolve`，`?AISolve=1` 批跑全程静音；
- `speechSynthesis` 缺失 / 抛错 / 静音一律 try-catch 静默降级。
验证：`node ios/tools/check_narration.js` 扫 2102 步全过；`preview_sweep.py --steps=2` 1193 步 0 弹回 0 越界。
