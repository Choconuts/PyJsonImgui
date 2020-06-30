#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : utils.py
@Author: Chen Yanzhen
@Date  : 2020/6/29 17:24
@Desc  : 
"""

from jsonui.context import *


default_handlers = []


@contextmanager
def label_wrap(label, label_width_percent=0.4):
    imgui.push_id(label)
    imgui.columns(2, None, False)
    w = imgui.get_window_content_region_width() * label_width_percent - imgui.get_cursor_pos()[0]
    imgui.set_column_width(0, w)
    imgui.text(label)
    imgui.same_line()
    imgui.next_column()
    yield None
    imgui.pop_id()
    imgui.columns(1, None, False)


@contextmanager
def as_default_handler(handler_class):
    default_handlers.append(handler_class)


