from comtools.imgui_engine.gui_tools import *
from comtools.imgui_engine import *
from comtools.imgui_engine.glfw_init import *


if __name__ == '__main__':
    impl, window = glfw_imgui_init(1280, 720)

    while not glfw.window_should_close(window):
        with glfw_frame(impl, window):
            with MenuWindow('1'):
                pass

    glfw_imgui_shutdown(impl)
