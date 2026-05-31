#! /usr/bin/env python3
"""glfw windowing backend for the EGL/OpenGL-ES test base class.

:class:`GLFWBackend` implements the ``_create_context`` / ``_swap`` /
``_destroy_context`` hooks of :class:`egltestcase.BaseESTestCase` using glfw
window hints.  The context is created through EGL so ES contexts work on desktop
drivers; an unavailable context skips the test rather than failing it.
"""
from __future__ import print_function

import glfw

# Map the abstract ``api`` attribute to the glfw client-API enum.
_CLIENT_API = {
    'gles': glfw.OPENGL_ES_API,
    'es': glfw.OPENGL_ES_API,
    'gl': glfw.OPENGL_API,
    'opengl': glfw.OPENGL_API,
}

_glfw_ready = False


def _ensure_glfw():
    global _glfw_ready
    if not _glfw_ready:
        if not glfw.init():
            raise RuntimeError('Failed to initialise glfw')
        _glfw_ready = True


class GLFWBackend(object):
    """Mixin supplying glfw-backed context creation for ``BaseESTestCase``."""

    _window = None

    def _create_context(self):
        _ensure_glfw()
        glfw.default_window_hints()

        try:
            client_api = _CLIENT_API[self.api.lower()]
        except KeyError:
            raise ValueError('Unknown api %r' % (self.api,))

        glfw.window_hint(glfw.CLIENT_API, client_api)
        # Force EGL context creation so ES contexts work on desktop drivers.
        glfw.window_hint(glfw.CONTEXT_CREATION_API, glfw.EGL_CONTEXT_API)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, self.gl_version[0])
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, self.gl_version[1])

        glfw.window_hint(glfw.RED_BITS, self.red_size)
        glfw.window_hint(glfw.GREEN_BITS, self.green_size)
        glfw.window_hint(glfw.BLUE_BITS, self.blue_size)
        glfw.window_hint(glfw.ALPHA_BITS, self.alpha_size)
        glfw.window_hint(glfw.DEPTH_BITS, self.depth_size)
        glfw.window_hint(glfw.STENCIL_BITS, self.stencil_size)
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE if self.visible else glfw.FALSE)

        try:
            window = glfw.create_window(
                self.width, self.height, self._window_title(), None, None
            )
        except glfw.GLFWError as err:
            window = None
            reason = str(err)
        else:
            reason = 'driver did not provide the requested context'

        if not window:
            self.skipTest(
                'Could not create a %s %d.%d context via glfw/EGL: %s'
                % (self.api, self.gl_version[0], self.gl_version[1], reason)
            )

        self._window = window
        glfw.make_context_current(window)

    def _window_title(self):
        return '%s (%s %d.%d)' % (
            type(self).__name__,
            self.api,
            self.gl_version[0],
            self.gl_version[1],
        )

    def _swap(self):
        if self._window is not None:
            glfw.swap_buffers(self._window)

    def _destroy_context(self):
        if self._window is not None:
            glfw.destroy_window(self._window)
            self._window = None
