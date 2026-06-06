#! /usr/bin/env python3
"""glfw windowing backend for the desktop-OpenGL test base class.

Implements the ``_create_context`` / ``_swap`` / ``_destroy_context`` hooks of
:class:`glutestcase.BaseGLUTestCase` using glfw window hints, honouring the
``profile`` (core / compatibility) and ``gl_version`` requirements.  A context
that the driver will not provide skips the test rather than failing it.
"""

from __future__ import print_function

import glfw

_PROFILES = {
    'core': glfw.OPENGL_CORE_PROFILE,
    'compatibility': glfw.OPENGL_COMPAT_PROFILE,
    'compat': glfw.OPENGL_COMPAT_PROFILE,
    'any': glfw.OPENGL_ANY_PROFILE,
}

_glfw_ready = False


def _ensure_glfw():
    global _glfw_ready
    if not _glfw_ready:
        if not glfw.init():
            raise RuntimeError('Failed to initialise glfw')
        _glfw_ready = True


class GLFWBackend(object):
    """Mixin supplying glfw-backed desktop-GL context creation."""

    _window = None

    def _create_context(self):
        _ensure_glfw()
        glfw.default_window_hints()
        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)

        major, minor = self.gl_version
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)

        profile = self.profile.lower()
        # GL profiles are only defined for >= 3.2
        if (major, minor) >= (3, 2):
            glfw.window_hint(glfw.OPENGL_PROFILE, _PROFILES[profile])
            if profile == 'core':
                glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

        glfw.window_hint(glfw.RED_BITS, self.red_size)
        glfw.window_hint(glfw.GREEN_BITS, self.green_size)
        glfw.window_hint(glfw.BLUE_BITS, self.blue_size)
        glfw.window_hint(glfw.ALPHA_BITS, self.alpha_size)
        glfw.window_hint(glfw.DEPTH_BITS, self.depth_size)
        glfw.window_hint(glfw.STENCIL_BITS, self.stencil_size)
        for hint in (
            'ACCUM_RED_BITS',
            'ACCUM_GREEN_BITS',
            'ACCUM_BLUE_BITS',
            'ACCUM_ALPHA_BITS',
        ):
            glfw.window_hint(getattr(glfw, hint), self.accum_size)
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
                'Could not create a %s %d.%d context via glfw: %s'
                % (self.profile, self.gl_version[0], self.gl_version[1], reason)
            )

        self._window = window
        glfw.make_context_current(window)

    def _window_title(self):
        return '%s (GL %d.%d %s)' % (
            type(self).__name__,
            self.gl_version[0],
            self.gl_version[1],
            self.profile,
        )

    def _swap(self):
        if self._window is not None:
            glfw.swap_buffers(self._window)

    def _destroy_context(self):
        if self._window is not None:
            glfw.destroy_window(self._window)
            self._window = None
