"""GLFW-backed GL test decorator (mirror of testdecorator_pygame).

Usage:

    from testdecorator import gltest
    @gltest
    def function():
        '''Run under a GL context with default 300x300 size and the
        function name as the window title.'''
        return None

    @gltest(size=(640, 480), name='Cool Test')
    def function():
        '''Run under a specifically configured context'''
        return None

Each invocation creates a fresh GLFW window and tears it down afterwards,
so this is intended for one-off checks rather than large test suites.
"""
import glfw
from functools import wraps

SCREEN = None


def gltest(maybe_function=None, *, size=(300, 300), name=None):
    """Decorator/factory to run a function under a GLFW OpenGL context.

    Supports both ``@gltest`` and ``@gltest(size=..., name=...)`` forms.
    """

    def make_wrapper(function):
        @wraps(function)
        def test_function(*args, **named):
            global SCREEN
            if not glfw.init():
                raise RuntimeError('Failed to initialise GLFW')
            try:
                glfw.default_window_hints()
                SCREEN = glfw.create_window(
                    size[0], size[1],
                    name or function.__name__,
                    None, None,
                )
                if not SCREEN:
                    raise RuntimeError('Failed to create GLFW window')
                glfw.make_context_current(SCREEN)
                try:
                    return function(*args, **named)
                finally:
                    glfw.destroy_window(SCREEN)
                    SCREEN = None
            finally:
                glfw.terminate()

        return test_function

    if callable(maybe_function):
        return make_wrapper(maybe_function)
    return make_wrapper
