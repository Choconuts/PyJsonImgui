#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : state_ui.py
@Author: Chen Yanzhen
@Date  : 2020/6/21 18:16
@Desc  : 
"""

from comtools.imgui_engine import *
from comtools.json_caching import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--state', type=str, help='Target state file path')
args = parser.parse_args()


class Window:

    def __init__(self, w, h):
        self.size = [w, h]
        self.refresh = None
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


class Node:

    def __init__(self):
        pass

    def to_json(self):
        pass

    def from_json(self, json):
        pass


class UI:

    def __init__(self, handlers):
        self.handlers = [h() if isinstance(h, type) else h for h in handlers]
        self.stack = []
        self.current_ref_type = ''
        self.dirty = False
        self.state = {}

    def input(self, key, ref):
        self.stack.append([key, ref])
        for h in self.handlers:
            if h.can_handle(key, ref, self):
                ref = h.input(key, ref, self)
                break
        self.stack.pop(-1)
        return ref

    def mark_dirty(self, dirty=True):
        self.dirty = self.dirty or dirty


class Handler:

    def can_handle(self, key, ref, context: UI) -> bool:
        pass

    def input(self, key, ref, context: UI):
        pass

    @contextmanager
    def label_wrap(self, label, label_width_percent=0.4):
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


class VecHandler(Handler):

    def can_handle(self, key, value, context: UI) -> bool:
        if isinstance(value, list) and len(value) == 4:
            c = True
            for k in value:
                c = c and isinstance(k, float)
            return c

    def input(self, key, ref, context: UI):
        with self.label_wrap(key):
            if 'color' in key.lower():
                c, v = imgui.drag_float4('vec4', *ref, 0.05, 0, 2)
            else:
                c, v = imgui.input_float4('vec4', *ref, '%.3f')
            context.mark_dirty(c)
            return list(v)


class ScalarHandler(Handler):

    def can_handle(self, key, value, context: UI) -> bool:
        return isinstance(value, (int, float))

    def input(self, key, ref, context: UI):
        if isinstance(ref, int):
            with self.label_wrap(key):
                c, v = imgui.input_int('int', ref)
        else:
            with self.label_wrap(key):
                c, v = imgui.input_float('float', ref, 0, 0, '%.6f')
        context.mark_dirty(c)
        return v


class HiddenHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return key in ['type', 'count', 'descType'] or key.startswith('_')

    def input(self, key, ref, context: UI):
        return ref


class DictHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return isinstance(ref, dict)

    def input(self, key, ref: dict, context: UI):
        if imgui.tree_node(key):
            for k, v in ref.items():
                ref[k] = context.input(k, v)
            imgui.tree_pop()
        return ref


class NodesHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return isinstance(ref, dict) and key in ['nodes']

    def input(self, key, ref: dict, context: UI):
        with id_scope(key):
            imgui.text(key)
            for k, v in ref.items():
                with self.label_wrap('', 0.08):
                    if k in context.state and context.state[k][1]:
                        if imgui.button('close [' + k + ']'):
                            context.state[k][1] = False
                        else:
                            context.state[k] = list(imgui.begin(k, True))
                            ref[k] = context.input(k, v)
                            imgui.end()
                    else:
                        if imgui.button(f'[{k}]'):
                            context.state[k] = [True, True]
        return ref


class UnnamedDictHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return isinstance(ref, dict) and \
               (key in ['entries', 'state', 'data'] or context.stack[-2][0] == 'nodes')

    def input(self, key, ref: dict, context: UI):
        with id_scope(key):
            for k, v in ref.items():
                ref[k] = context.input(k, v)
        return ref


class SingleValueHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return isinstance(ref, dict) and 'type' in ref and 'value' in ref and 'count' not in ref

    def input(self, key, ref, context: UI):
        ref['value'] = context.input(key, ref['value'])
        return ref


class MultiValueHandler(Handler):

    def can_handle(self, key, ref, context: UI) -> bool:
        return isinstance(ref, dict) and 'type' in ref and 'value' in ref and 'count' in ref

    def input(self, key, ref, context: UI):
        tmp_item = None
        import copy
        if 'template' in ref:
            tmp_item = copy.deepcopy(ref['template'])
        with self.label_wrap(key):
            ref['count'] = imgui.input_int('len', ref['count'])[1]
            origin_value = ref['value']
            if not isinstance(origin_value, list):
                origin_value = [origin_value]
            ref['value'] = [tmp_item] * ref['count']
        for i in range(ref['count']):
            with id_scope(f'{i}'):
                if i < len(origin_value):
                    ref['value'][i] = context.input(key, origin_value[i])
        return ref


if __name__ == '__main__':
    state = load_json(args.state)
    ui = UI([
        # HiddenHandler,
        NodesHandler,
        UnnamedDictHandler,
        SingleValueHandler,
        # MultiValueHandler,
        # VecHandler,
        ScalarHandler,
        DictHandler,
    ])

    def refresh():
        global state

        # imgui.set_next_window_position(0, 0)
        # imgui.set_next_window_size(*window.current_size())
        imgui.begin('State', False)
        state = ui.input('state', state)
        if imgui.button('apply') or ui.dirty:
            save_json(state, args.state)
            ui.dirty = False

        # imgui.button('a')
        # io = imgui.get_io()
        # imgui.get_overlay_draw_list().add_line(
        #     *imgui.get_cursor_pos(), *io.mouse_pos, imgui.get_color_u32_rgba(1, 1, 0, 1), 3)

        imgui.end()

    window = Window(800, 600)
    window.refresh = refresh

    window.show()

