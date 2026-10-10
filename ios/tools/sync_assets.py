#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 design/assets 的 SVG 同步到 iOS 工程（gen-assets.mjs 之后运行）。

做两件事，保证「美术唯一源」四处同步中的两处：
  1. 为 design/assets/icons 下每个 SVG 在 Assets.xcassets 建/更新 <name>.imageset
     （拷贝 SVG + 生成 Contents.json，preserves-vector-representation）
  2. 用 manifest 重新生成 Tests/AdventureIslandTests/icon_names.json 夹具

其余两处（Common.swift 的 IconEmoji、index.html 的 EMOJI）需手工补 emoji 映射。
用法：python3 ios/tools/sync_assets.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ios/
DESIGN = os.path.dirname(ROOT)                                      # 项目根
ICONS = os.path.join(DESIGN, "design", "assets", "icons")
MANIFEST = os.path.join(DESIGN, "design", "assets", "manifest.json")
CATALOG = os.path.join(ROOT, "AdventureIsland", "Assets.xcassets")
FIXTURE = os.path.join(ROOT, "Tests", "AdventureIslandTests", "icon_names.json")

CONTENTS = {
    "images": [{"filename": None, "idiom": "universal"}],
    "info": {"author": "xcode", "version": 1},
    "properties": {"preserves-vector-representation": True, "single-scale": True},
}

def icon_names():
    man = json.load(open(MANIFEST, encoding="utf-8"))
    icons = {p.split("/")[1].replace(".svg", "") for p in man["icons"]}
    bgs = {p.split("/")[1].replace(".svg", "") for p in man.get("bg", [])}
    return sorted(icons | bgs)

def sync_xcassets(names):
    made = 0
    for name in names:
        src = os.path.join(ICONS, name + ".svg")
        if not os.path.exists(src):
            print("WARN 缺 SVG:", name); continue
        d = os.path.join(CATALOG, name + ".imageset")
        os.makedirs(d, exist_ok=True)
        shutil.copyfile(src, os.path.join(d, name + ".svg"))
        cj = json.loads(json.dumps(CONTENTS))
        cj["images"][0]["filename"] = name + ".svg"
        with open(os.path.join(d, "Contents.json"), "w", encoding="utf-8") as f:
            json.dump(cj, f, ensure_ascii=False, indent=2)
        made += 1
    return made

def sync_fixture(names):
    with open(FIXTURE, "w", encoding="utf-8") as f:
        json.dump({"icons": names}, f, ensure_ascii=False, indent=2)

def main():
    names = icon_names()
    made = sync_xcassets(names)
    sync_fixture(names)
    print(f"同步完成：{made} 个 imageset，夹具 {len(names)} 图标")

if __name__ == "__main__":
    main()
