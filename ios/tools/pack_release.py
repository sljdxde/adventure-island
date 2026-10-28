#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""探险岛 · 离线包打包（v1.0.2 起包名带版本号）

用法：
    python3 ios/tools/pack_release.py 1.0.2      # 版本号＝ tag 去掉 v，v1.0.2 → 1.0.2

产物：仓库根目录 `探险岛-HTML离线包-v<版本>.zip`，结构：
    探险岛-HTML离线包-v1.0.2.zip
      ├─ design/…                     设计稿与图标（应用运行时要读）
      └─ ios/preview/index.html       单文件游戏本体

为什么包内不再套一层版本目录：
iPad「文件」App 点一下解压时，会用**zip 的文件名**建同名文件夹（旧包就是解压出
「探险岛-HTML离线包」目录，再进入 ios → preview），所以包名带版本号之后，解压出来的
目录天然带版本号；再套一层就会出现「v1.0.2 里面还有 v1.0.2」的套娃。
zip 内 design/ 与 ios/ 必须保持同级——index.html 里是 ../../design/... 的相对引用。

校验（脚本自己做完，任一不通过退出码 1）：
  · zip 内的 ios/preview/index.html 与本地 md5 一致
  · zip 内 design 文件数与源目录（排除 .DS_Store / __pycache__ / *.pyc）一致

不负责：commit 与打 tag（跑完打 `git tag -a v<版本>`）。
"""
import hashlib
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESIGN = os.path.join(ROOT, "design")
PREVIEW = os.path.join(ROOT, "ios", "preview", "index.html")
LEGACY_ZIP = os.path.join(ROOT, "探险岛-HTML离线包.zip")
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {".DS_Store"}
SKIP_EXTS = {".pyc"}


def md5_bytes(b):
    return hashlib.md5(b).hexdigest()


def md5_file(path):
    with open(path, "rb") as f:
        return md5_bytes(f.read())


def design_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(DESIGN):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name in SKIP_FILES or os.path.splitext(name)[1] in SKIP_EXTS:
                continue
            full = os.path.join(dirpath, name)
            out.append(os.path.relpath(full, DESIGN))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit("用法：python3 ios/tools/pack_release.py <版本号>   例：python3 ios/tools/pack_release.py 1.0.2")
    ver = sys.argv[1].strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
        sys.exit(f"版本号格式应为 X.Y.Z（不带 v），收到：{ver!r}")
    if not os.path.exists(PREVIEW):
        sys.exit(f"找不到 {PREVIEW}")
    if not os.path.isdir(DESIGN):
        sys.exit(f"找不到 {DESIGN}")

    zip_name = f"探险岛-HTML离线包-v{ver}.zip"
    out = os.path.join(ROOT, zip_name)
    if os.path.exists(out):
        os.remove(out)                       # 先删旧包，避免改名/删除的文件留成残条
        print(f"  已删除旧包 {zip_name}")
    if os.path.exists(LEGACY_ZIP):
        print("  [WARN] 仓库根目录还有旧命名的「探险岛-HTML离线包.zip」——删掉它，"
              "否则 iPad 上会出现两个分不清的包")

    files = design_files()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in files:
            z.write(os.path.join(DESIGN, rel), arcname="design/" + rel.replace(os.sep, "/"))
        z.write(PREVIEW, arcname="ios/preview/index.html")

    # ---- 校验 ----
    with zipfile.ZipFile(out) as z:
        got = z.read("ios/preview/index.html")
        names = z.namelist()
    n_design = sum(1 for n in names if n.startswith("design/") and not n.endswith("/"))
    bad = []
    if md5_bytes(got) != md5_file(PREVIEW):
        bad.append("zip 内 index.html 与本地 md5 不一致")
    if n_design != len(files):
        bad.append(f"zip 内 design 文件数 {n_design} ≠ 源目录 {len(files)}")
    if not any(n.startswith("design/assets/icons/") for n in names):
        bad.append("zip 里没有 design/assets/icons/（图标会全变 ❓）")
    if bad:
        os.remove(out)
        for b in bad:
            print(f"  [FAIL] {b}")
        sys.exit(1)

    size_mb = os.path.getsize(out) / 1024 / 1024
    print(f"  OK  {zip_name}  {size_mb:.2f} MB  {len(files)+1} 个文件  v{ver}")
    print(f"      index.html md5 {md5_file(PREVIEW)}（zip 内外一致）")
    print(f"  iPad 解压后目录名就是 {os.path.splitext(zip_name)[0]}/，进去用 ios/preview/index.html")
    print(f"  下一步：git add {zip_name} && git commit && git tag -a v{ver}")


if __name__ == "__main__":
    main()
