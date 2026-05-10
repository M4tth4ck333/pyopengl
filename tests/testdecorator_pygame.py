"""Pygame-backed GL test decorator.

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

Each invocation creates a fresh context, so this is intended for one-off
checks rather than large test suites.
"""
import pygame, pygame.display
from functools import wraps

SCREEN = None


def gltest(maybe_function=None, *, size=(300, 300), name=None):
    """Decorator/factory to run a function under a Pygame OpenGL context.

    Supports both ``@gltest`` and ``@gltest(size=..., name=...)`` forms.
    """

    def make_wrapper(function):
        @wraps(function)
        def test_function(*args, **named):
            global SCREEN
            pygame.display.init()
            SCREEN = pygame.display.set_mode(
                size,
                pygame.OPENGL | pygame.DOUBLEBUF,
            )
            pygame.display.set_caption(name or function.__name__)
            pygame.key.set_repeat(500, 30)
            try:
                return function(*args, **named)
            finally:
                pygame.display.flip()
                pygame.display.quit()
                pygame.quit()

        return test_function

    if callable(maybe_function):
        return make_wrapper(maybe_function)
    return make_wrapper
