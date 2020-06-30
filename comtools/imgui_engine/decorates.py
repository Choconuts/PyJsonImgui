from __future__ import absolute_import
import sys
import OpenGL.GL as gl
import imgui
from PIL import Image, ImageFile
import numpy as np
from contextlib import contextmanager
from comtools.imgui_engine.gui_tools import *
from functools import wraps
from multiprocessing import Process


class FuncUI:

    def __init__(self, window='functions', args=[], kwargs={}):
        self.window = window
        self.args = args
        self.kwargs = kwargs
        self.processes = []
        _fuis.append(self)

    def __call__(self, func):
        self.func = func
        return func

    def render(self):
        with MenuWindow(self.window) as succ:
            if succ:
                if imgui.button(self.func.__name__):
                    p = Process(target=self.func, args=self.args, kwargs=self.kwargs)
                    self.processes.append(p)
                    p.start()

_fuis = []


def render_fui():
    for fui in _fuis:
        fui.render()
