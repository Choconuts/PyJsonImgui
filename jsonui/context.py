#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : context.py
@Author: Chen Yanzhen
@Date  : 2020/6/29 16:48
@Desc  : 
"""

from comtools.imgui_engine import *
from comtools.json_caching import *
from enum import Enum
from itertools import chain
from functools import lru_cache


class NoNoneDict(dict):

    def __init__(self, default_value_type):
        self.default = default_value_type

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except IndexError:
            return self.default()


class Window:

    def __init__(self, w, h):
        self.size = [w, h]
        self.glfw_window = None

    def current_size(self):
        import glfw
        size = glfw.get_window_size(self.glfw_window)
        return size

    def show(self):
        impl, self.glfw_window = glfw_imgui_init(*self.size)

        while not glfw.window_should_close(self.glfw_window):
            with glfw_frame(impl, self.glfw_window):
                if self.refresh:
                    self.refresh()
        glfw_imgui_shutdown(impl)

    def refresh(self):
        pass


class UI:

    class Match:

        def __init__(self, expr):
            self.type = expr

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return self.type == other.type
            return super.__eq__(other)

        def __hash__(self):
            return self.type.__hash__()

    class Handling:

        def __init__(self, key, ref, handler):
            self.key = key
            self.ref = ref
            self.handler = handler

    ANY = Match('any')

    def __init__(self, handlers):
        self.handlers = [h() if isinstance(h, type) else h for h in handlers]
        self._key_map = {}
        self._value_type_map = {}
        for h in self.handlers:
            assert isinstance(h, Handler)
            tmp = h.register_keys(self)
            if not isinstance(tmp, (tuple, list)):
                tmp = [tmp]
            for k in tmp:
                if k not in self._key_map:
                    self._key_map[k] = []
                self._key_map[k].append(h)

            tmp = h.register_value_types(self)
            if not isinstance(tmp, (tuple, list)):
                tmp = [tmp]
            for v in tmp:
                if v not in self._value_type_map:
                    self._value_type_map[v] = []
                self._value_type_map[v].append(h)

        self.stack = [self.Handling('$', None, Handler())]
        self.current_ref_type = ''
        self.dirty_levels = {0:False}
        self.state = {}

    def input(self, key, ref):
        for h in set(chain(
                self._key_map[key] if key in self._key_map else [],
                self._value_type_map[type(ref)] if type(ref) in self._value_type_map else [],
                self._key_map[UI.ANY] if UI.ANY in self._key_map else [],
                self._value_type_map[UI.ANY] if UI.ANY in self._value_type_map else [])):
            if h.can_handle(key, ref, self):
                self.stack.append(self.Handling(key, ref, h))
                ref = h.input(key, ref, self)
                self.stack.pop(-1)
                break
        return ref

    def mark_dirty(self, dirty=True, level=0):
        if level not in self.dirty_levels:
            self.dirty_levels[level] = False
        self.dirty_levels[level] = self.dirty_levels[level] or dirty

    def is_dirty(self, level=0) -> bool:
        return self.dirty_levels[level]


class Handler:

    def register_keys(self, context: UI) -> list:
        """
        :param: context:
        :return: keys(array of strings)
        """
        return [context.ANY]

    def register_value_types(self, context: UI) -> list:
        """

        :param context:
        :return: value types(array of value type)
        """
        return [context.ANY]

    def can_handle(self, key, ref, context: UI) -> bool:
        import logging
        logging.warning(f'info not handled [{key}]:\n {ref}')
        return True

    def input(self, key, ref, context: UI):
        return ref
