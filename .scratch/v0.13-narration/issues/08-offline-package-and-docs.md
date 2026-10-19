Type: task
Status: resolved
Blocked by: 06, 07

# 重打离线包并更新文档

## Question

收尾三件事（按 AGENTS.md §3）：

1. 按 06 的结论把语速/停顿调完，回归六科各 3 关
2. **先删旧包**再打包（否则改名/删除的文件会留成残条）：
   `rm -f 探险岛-HTML离线包.zip` → `zip -rq ... design ios/preview/index.html ...`，
   核对包内 `index.html` 与工作区 `md5` 一致
3. 更新 `ios/docs/工作进展与待办-v0.12.md`（或新建 v0.13 文档）与 `探险岛-iPad使用说明.txt`：
   写清「现在会自动念题，怎么关」，不留虚假的已完成声明

若 07 判定要补数据，先跑完 `gen_content.py` → `gen_preview_data.py` → 三门闸门再打包。

## Answer

代码侧收尾完成：按 AGENTS.md §3 先删旧包再重打离线包，核对了包内 `index.html` 与工作区 md5 一致；
`ios/docs/工作进展与待办-v0.12.md` 新增「九、v0.13 自动朗读」，`探险岛-iPad使用说明.txt` 补了「进关自动念 / 怎么关」。
唯一没做的是「按 06 的结论调语速」——那要等 06 的实听结果，届时只需改 `S.voice.rate` 默认值并重打包。
