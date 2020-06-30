import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer
from contextlib import contextmanager


def impl_glfw_init(width, height):
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window


def glfw_imgui_init(width, height):
    imgui.create_context()
    window = impl_glfw_init(width, height)
    return GlfwRenderer(window), window


@contextmanager
def glfw_frame(impl, window, clear=[1, 1, 1, 1], auto_flip=True):
    try:
        try:
            glfw.poll_events()
            impl.process_inputs()

            imgui.new_frame()
            yield None
        except Exception as e:
            raise e
        if clear:
            gl.glClearColor(*clear)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())

        if auto_flip:
            glfw.swap_buffers(window)
    except Exception as e:
        raise e


def glfw_imgui_shutdown(impl):
    impl.shutdown()
    glfw.terminate()
