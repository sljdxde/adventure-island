#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 iOS Resources 的内容 JSON 注入浏览器模拟器（ios/preview/index.html）。

模拟器与 Swift 工程从此共用同一份关卡/收集册/实验数据：
  1. 先运行 gen_content.py 生成 Resources/*.json
  2. 再运行本脚本，把 JSON 写入 index.html 的 DATA 段
模拟器渲染层直接消费这些 step 对象（与 SwiftUI 同构），不再手工镜像。
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 项目根
RES = os.path.join(ROOT, "ios", "AdventureIsland", "Resources")
PREVIEW = os.path.join(ROOT, "ios", "preview", "index.html")

docs = {}
KEYMAP = {"cn_levels": "cn", "math_levels": "math", "pinyin_levels": "pinyin",
          "english_levels": "english", "astro_levels": "astro",
          "collection": "collection", "experiments": "experiments"}
for name, key in KEYMAP.items():
    with open(os.path.join(RES, name + ".json"), encoding="utf-8") as f:
        docs[key] = json.load(f)

data_js = "const CONTENT = " + json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";"

html = open(PREVIEW, encoding="utf-8").read()
new, n = re.subn(r"/\* === DATA-BEGIN === \*/.*?/\* === DATA-END === \*/",
                 "/* === DATA-BEGIN === */\n" + data_js + "\n/* === DATA-END === */",
                 html, flags=re.S)
if n != 1:
    raise SystemExit(f"DATA 段标记异常：匹配到 {n} 处（应为 1）")
open(PREVIEW, "w", encoding="utf-8").write(new)
print(f"preview index.html 数据注入完成：{sum(len(v.get('levels', v.get('groups', v.get('experiments', [])))) for v in docs.values())} 个条目")
