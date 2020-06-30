#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File  : test_ui.py
@Author: Chen Yanzhen
@Date  : 2020/6/29 17:16
@Desc  : 
"""

from jsonui import *

"""" test prefab """

state = {
    'students': {
        'dict': {
            'x': {

            }
        },
        'template': {
            'Name': 'CYZ',
            'Age': 21,
            'Birth': [19., 98., 7., 7.],
            'Hobby': {
                'Entertain': ['Game', 'Paint']
            }
        }
    },

}


@utils.as_default_handler
class DictHandler(Handler):

    def register_keys(self, context: UI) -> list:
        return []

    def register_value_types(self, context: UI) -> list:
        return dict

    def can_handle(self, key, ref, context: UI) -> bool:
        return True

    def input(self, key, ref, context: UI):
        if imgui.tree_node(key):
            for k, v in ref.items():
                ref[k] = context.input(k, v)
            imgui.tree_pop()
        return ref


@utils.as_default_handler
class Value(Handler):

    def register_value_types(self, context: UI) -> list:
        return [int, float]

    def can_handle(self, key, value, context: UI) -> bool:
        return isinstance(value, (int, float))

    def input(self, key, ref, context: UI):
        if isinstance(ref, int):
            with utils.label_wrap(key):
                c, v = imgui.input_int('int', ref)
        else:
            with utils.label_wrap(key):
                c, v = imgui.input_float('float', ref, 0, 0, '%.6f')
        context.mark_dirty(c)
        return v


ui_context = UI(utils.default_handlers)


class MyWindow(Window):

    def refresh(self):
        global state
        imgui.begin('State', False)
        state = ui_context.input('state', state)
        imgui.end()


window = MyWindow(800, 600)

if __name__ == '__main__':
    window.show()
