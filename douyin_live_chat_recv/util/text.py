#!/usr/bin/env python3
# coding: utf-8

__all__ = ["text_within", "text_to_dict", "dict_to_text", 'add_space_to_text']

from collections import Counter
from random import randint, choices
from re import Pattern, sub
from typing import AnyStr, Union


def text_within(
    text: AnyStr, 
    left: Union[AnyStr, Pattern[AnyStr], None] = None, 
    right: Union[AnyStr, Pattern[AnyStr], None] = None, 
    with_left: bool = False, 
    with_right: bool = False, 
) -> AnyStr:
    empty_s: AnyStr = b"" if isinstance(text, bytes) else ""
    start_idx, stop_idx = 0, len(text)
    if left is not None:
        if isinstance(left, Pattern):
            match = left.search(text)
            if match is None:
                return empty_s
            start_idx = match.start() if with_left else match.end()
        else:
            idx = text.find(left)
            if idx == -1:
                return empty_s
            if with_left:
                start_idx = idx
            else:
                start_idx = idx + len(left)
    if right is not None:
        if isinstance(right, Pattern):
            match = right.search(text, start_idx)
            if match is None:
                return empty_s
            stop_idx = match.end() if with_right else match.start()
        else:
            idx = text.find(right, start_idx)
            if idx == -1:
                return empty_s
            if with_right:
                stop_idx = idx + len(right)
            else:
                stop_idx = idx
    return text[start_idx:stop_idx]


def text_to_dict(
    text: AnyStr, 
    kvsep: Union[AnyStr, Pattern[AnyStr]], 
    lsep: Union[AnyStr, Pattern[AnyStr]], 
    with_end_lsep: bool = False, 
) -> dict[AnyStr, AnyStr]:
    ls: list[AnyStr]
    if isinstance(lsep, Pattern):
        if with_end_lsep:
            if isinstance(text, str):
                text = sub(lsep.pattern+r"\Z", "", text, lsep.flags)
            else:
                text = sub(lsep.pattern+br"\Z", b"", text, lsep.flags)
        ls = lsep.split(text)
    else:
        if with_end_lsep:
            text = text.removesuffix(lsep)
        ls = text.split(lsep)
    if isinstance(kvsep, Pattern):
        split1 = kvsep.split
        return dict(split1(l, 1) for l in ls) # type: ignore
    else:
        split2 = str.split
        return dict(split2(l, kvsep, 1) for l in ls) # type: ignore


def dict_to_text(
    d: dict[AnyStr, AnyStr], 
    kvsep: AnyStr, 
    lsep: AnyStr, 
    with_end_lsep: bool = False, 
) -> AnyStr:
    text = lsep.join(k+kvsep+v for k, v in d.items())
    if with_end_lsep:
        text += lsep
    return text


def add_space_to_text(
    text: str, 
    k: int = 1, 
) -> str:
    if k <= 0:
        return text
    elif k == 1:
        idx = randint(0, len(text)+1)
        return text[:idx] + ' ' + text[idx:]
    else:
        def helper():
            counter = Counter(choices(range(len(text)+1), k=k))
            idx_count_tuples = sorted(
                counter.items(), key=lambda e: e[0])
            start = 0
            for stop, count in idx_count_tuples:
                yield text[start:stop]
                yield ' '*count
                start = stop
            else:
                yield text[start:]
        return "".join(helper())

