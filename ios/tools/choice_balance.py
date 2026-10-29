#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""选择题正确项位置均衡工具。

生成器和验收脚本共用同一套“正确答案在选项里的哪个位置”判定，
避免数据换序后，生成端与闸门对“正确答案”的理解不一致。
"""
import random


def _find_value(values, target):
    for i, value in enumerate(values):
        if value == target:
            return i
    return None


def correct_choice(step):
    """返回 (字段名, 选项列表, 正确项当前下标, 是否用 answer 存下标)。"""
    kind = step.get("kind")
    if kind in {"quiz", "listen", "blend", "clock", "muldiv", "pattern", "shadow"}:
        options = step.get("options")
        answer = step.get("answer")
        if isinstance(options, list) and isinstance(answer, int) and 0 <= answer < len(options):
            return "options", options, answer, True
        return None

    if kind == "neighbor":
        options = step.get("arithOptions")
        answer = step.get("answer")
        if isinstance(options, list) and isinstance(answer, int) and 0 <= answer < len(options):
            return "arithOptions", options, answer, True
        return None

    if kind in {"count", "dice"}:
        options = step.get("countOptions")
        target = step.get("count")
        index = _find_value(options, target) if isinstance(options, list) else None
        return ("countOptions", options, index, False) if index is not None else None

    if kind == "compare":
        options = step.get("compareOptions")
        target = step.get("answerKey")
        if isinstance(options, list):
            index = next((i for i, option in enumerate(options)
                          if isinstance(option, dict) and option.get("key") == target), None)
            if index is not None:
                return "compareOptions", options, index, False
        return None

    if kind == "arith":
        options = step.get("arithOptions")
        left = step.get("leftCount")
        right = step.get("rightCount")
        op = step.get("op")
        if isinstance(options, list) and isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if op == "+":
                target = left + right
            elif op == "-":
                target = left - right
            else:
                return None
            index = _find_value(options, target)
            return ("arithOptions", options, index, False) if index is not None else None
        return None

    if kind == "split":
        options = step.get("arithOptions")
        total = step.get("total")
        part = step.get("part")
        if isinstance(options, list) and isinstance(total, int) and isinstance(part, int):
            index = _find_value(options, total - part)
            return ("arithOptions", options, index, False) if index is not None else None

    return None


def iter_steps_in_play_order(levels):
    """按棋盘实际出场顺序遍历步骤；没有棋盘的关卡直接用 steps 顺序。"""
    for level in levels:
        steps = level.get("steps", [])
        by_id = {step.get("id"): step for step in steps if step.get("id")}
        seen = set()
        for space in (level.get("board") or {}).get("spaces", []):
            if space.get("type") != "question":
                continue
            step = by_id.get(space.get("step"))
            if step is None or id(step) in seen:
                continue
            seen.add(id(step))
            yield step
        for step in steps:
            if id(step) in seen:
                continue
            seen.add(id(step))
            yield step


def balance_answer_positions(levels):
    """按实际出场顺序打散正确项；各位置总数最多相差 1。"""
    groups = {}
    for step in iter_steps_in_play_order(levels):
        info = correct_choice(step)
        if not info:
            continue
        _, options, _, _ = info
        if len(options) >= 2:
            groups.setdefault(len(options), []).append(step)

    seed = "choice-balance:" + "|".join(str(level.get("id", "")) for level in levels)
    rng = random.Random(seed)
    moved = 0
    for choice_count in sorted(groups):
        slots = [i % choice_count for i in range(len(groups[choice_count]))]
        rng.shuffle(slots)
        for step, target in zip(groups[choice_count], slots):
            info = correct_choice(step)
            if not info:
                continue
            _, options, current, uses_answer_index = info
            if current == target:
                continue
            options[current], options[target] = options[target], options[current]
            if uses_answer_index:
                step["answer"] = target
            moved += 1
    return moved
