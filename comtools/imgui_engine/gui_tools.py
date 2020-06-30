from __future__ import absolute_import
import sys
import OpenGL.GL as gl
import imgui
from PIL import Image, ImageFile
import numpy as np
from contextlib import contextmanager


class Texture:

    def __init__(self, width, height=None):
        self._id = gl.glGenTextures(1)
        if height is None:
            height = width
        self.size = width, height
        self.filename = None
        self.loaded = False

    def load(self, filename):
        if self.filename == filename:
            return self
        self.filename = filename
        self.loaded = False
        return self

    @property
    def id(self):
        if self.filename and not self.loaded:
            self._load(self.filename)
            self.loaded = True
        return self._id

    def _load(self, filename):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        img = Image.open(filename).resize(self.size)

        width, height = img.size
        data = np.array(list(img.getdata()), dtype=np.uint8)

        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)
        return self

    @property
    def param(self):
        return self.id, self.size[0], self.size[1]

    def __del__(self):
        gl.glDeleteTextures(gl.GLuint(self._id))


class MenuWindow:

    def __init__(self, name, controller=None, denote_item=0, position=None, size=None, collapsed=False):
        self.name = name
        self.position = position
        self.size = size
        self.collapsed = collapsed
        if controller is None:
            controller = [True]
        self.controller = controller
        self.denote_item = denote_item
        self.open = False

    def __enter__(self):
        if self.position:
            imgui.set_next_window_position(*self.position)
        if self.size:
            imgui.set_next_window_size(*self.size)
        if self.collapsed:
            imgui.set_next_window_collapsed(self.collapsed)
        controller = self.controller
        denote_item = self.denote_item
        if controller[denote_item]:
            expanded, opened = imgui.begin(self.name, True)
            self.open = True
            if not opened:
                controller[denote_item] = False
        return controller[denote_item]

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.open:
            imgui.end()
            self.open = False


@contextmanager
def id_scope(nid):
    imgui.push_id(nid)
    yield None
    imgui.pop_id()


def gl_white_clear():
    gl.glClearColor(1, 1, 1, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)


def item_like_attributes(cls):
    cls.__getitem__ = lambda *x: getattr(*x)
    cls.__setitem__ = lambda *x: setattr(*x)
    return cls


if __name__ == '__main__':
    pass

