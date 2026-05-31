#! /usr/bin/env python3
"""Reusable base TestCase for EGL / OpenGL-ES rendering tests.

A test declares the context it needs via class attributes (api, gl_version,
colour/depth/stencil sizes) and gets a current, cleared context to render into.
:class:`BaseESTestCase` is toolkit-agnostic and defers window/context creation
to a backend mixin (currently :class:`egltestcase_glfw.GLFWBackend`) via the
``_create_context`` / ``_swap`` / ``_destroy_context`` hooks.  The backend is
chosen by ``TEST_WINDOWING`` (only ``glfw`` today), mirroring basetestcase.py.

    from egltestcase import ESTestCase

    class TestThing(ESTestCase):
        gl_version = (3, 0)
        def test_it(self):
            ...
"""
from __future__ import print_function
import os
import ctypes
import time
import unittest

# OpenGL-ES is reached through the EGL platform; make sure that is selected
# before anything pulls in ``OpenGL`` for the first time.
os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')

# The generic GL entry points we use for introspection / readback all live in
# (and are shared by) the GLES2 namespace; individual tests still import the
# specific GLES1/GLES2/GLES3 module that matches their tier.
from OpenGL import GLES2 as _gl
from OpenGL import GLES3 as _gl3


class BaseESTestCase(unittest.TestCase):
    """Toolkit-agnostic base class for OpenGL-ES rendering tests.

    Override the context-requirement attributes on a subclass to ask for a
    particular kind of context.  A backend mixin supplies the actual window /
    context creation.
    """

    # --- context requirements (override on subclasses) -------------------
    #: 'gles' for OpenGL-ES, 'gl' for desktop OpenGL (future backends).
    api = 'gles'
    #: (major, minor) client version to request.
    gl_version = (2, 0)
    #: framebuffer sizes requested from the config/visual.
    red_size = green_size = blue_size = alpha_size = 8
    depth_size = 24
    stencil_size = 0
    #: window dimensions / whether the window should be shown on screen.
    width = height = 128
    #: show the window by default (set TEST_VISIBLE=0 for headless/CI runs).
    visible = os.environ.get('TEST_VISIBLE', '1').lower() not in ('0', 'false', 'no')
    #: seconds to leave a visible window on screen after rendering.
    dwell = 0.2

    # --- backend hooks (a mixin must implement these) --------------------
    def _create_context(self):
        raise NotImplementedError(
            'No windowing backend mixed in; use ESTestCase or a backend subclass'
        )

    def _swap(self):
        raise NotImplementedError

    def _destroy_context(self):
        raise NotImplementedError

    # --- fixture ----------------------------------------------------------
    def setUp(self):
        """Create the requested context and leave it current and cleared."""
        self._create_context()
        _gl.glViewport(0, 0, self.width, self.height)
        _gl.glClearColor(0.0, 0.0, 0.25, 1.0)
        _gl.glClear(_gl.GL_COLOR_BUFFER_BIT | _gl.GL_DEPTH_BUFFER_BIT)
        self.check_error('setUp')

    def tearDown(self):
        try:
            self._swap()  # present, so a visible run shows the frame
            if self.visible and self.dwell:
                time.sleep(self.dwell)
        finally:
            self._destroy_context()

    # --- introspection helpers -------------------------------------------
    def getString(self, enum):
        """Return a ``glGetString`` value decoded to ``str`` (or ``None``)."""
        value = _gl.glGetString(enum)
        if isinstance(value, bytes):
            return value.decode('ascii', 'replace')
        return value

    def getStringi(self, enum, index):
        """Return an indexed ``glGetStringi`` value decoded to ``str`` (ES3+)."""
        value = _gl3.glGetStringi(enum, index)
        if isinstance(value, bytes):
            return value.decode('ascii', 'replace')
        return value

    def getInteger(self, enum, count=1):
        """Return ``glGetIntegerv`` as an ``int`` (count==1) or list of ints."""
        buf = (ctypes.c_int * count)()
        _gl.glGetIntegerv(enum, buf)
        return buf[0] if count == 1 else list(buf)

    def extensions(self):
        """Return the set of supported extension strings.

        Uses the ES3+ indexed query when available, falling back to the
        space-separated ``GL_EXTENSIONS`` string used by ES1/ES2.
        """
        if self.gl_version >= (3, 0):
            count = self.getInteger(_gl3.GL_NUM_EXTENSIONS)
            return {self.getStringi(_gl3.GL_EXTENSIONS, i) for i in range(count)}
        raw = self.getString(_gl.GL_EXTENSIONS) or ''
        return set(raw.split())

    def require_extension(self, name):
        """Skip the test unless ``name`` is an advertised extension."""
        if name not in self.extensions():
            self.skipTest('extension %s not available' % (name,))

    # --- error / pixel helpers -------------------------------------------
    def check_error(self, context=''):
        """Assert that no GL error is pending, reporting ``context`` on failure."""
        err = _gl.glGetError()
        self.assertEqual(
            err, _gl.GL_NO_ERROR, 'GL error 0x%x during %s' % (err, context or '?')
        )

    def read_pixel(self, x, y):
        """Return the ``(r, g, b, a)`` bytes of the framebuffer pixel at x, y."""
        buf = (ctypes.c_ubyte * 4)()
        _gl.glReadPixels(
            x, y, 1, 1, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, buf
        )
        self.check_error('glReadPixels')
        return tuple(buf)

    def read_image(self, x=0, y=0, width=None, height=None):
        """Return an ``(h, w, 4)`` RGBA uint8 image via auto-allocating readback.

        Exercises the ES ``glReadPixels`` array-return path (no caller buffer).
        """
        width = self.width if width is None else width
        height = self.height if height is None else height
        image = _gl.glReadPixels(
            x, y, width, height, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, outputType=None
        )
        self.check_error('glReadPixels')
        return image

    def assert_pixel(self, x, y, expected, tolerance=8):
        """Assert the pixel at x, y matches ``expected`` within ``tolerance``."""
        actual = self.read_pixel(x, y)
        for chan, (a, e) in enumerate(zip(actual, expected)):
            self.assertLessEqual(
                abs(a - e),
                tolerance,
                'pixel (%d,%d) channel %d = %r, expected ~%r (got %r)'
                % (x, y, chan, a, e, actual),
            )

    # --- shader helper ----------------------------------------------------
    def compile_program(self, vertex_src, fragment_src, extra_stages=()):
        """Compile + link a program from GLSL source for the current context.

        ``extra_stages`` is a sequence of ``(stage_enum, source)`` pairs for
        additional stages (e.g. a geometry shader).
        """
        from OpenGL.GLES2 import shaders

        stages = [
            shaders.compileShader(vertex_src, _gl.GL_VERTEX_SHADER),
            shaders.compileShader(fragment_src, _gl.GL_FRAGMENT_SHADER),
        ]
        for stage_enum, source in extra_stages:
            stages.append(shaders.compileShader(source, stage_enum))
        program = shaders.compileProgram(*stages)
        self.check_error('compile_program')
        return program

    def compile_compute(self, source):
        """Compile + link a compute-only program (ES3.1+)."""
        from OpenGL.GLES2 import shaders
        from OpenGL.GLES3 import GL_COMPUTE_SHADER

        program = shaders.compileProgram(
            shaders.compileShader(source, GL_COMPUTE_SHADER)
        )
        self.check_error('compile_compute')
        return program


# ---------------------------------------------------------------------------
# Backend selection (mirrors basetestcase.py).  Only glfw is wired up so far;
# xlib / Qt / pygame backends can register themselves here as they appear.
# ---------------------------------------------------------------------------
_REQUESTED = os.environ.get('TEST_WINDOWING', '').strip().lower() or 'glfw'

if _REQUESTED == 'glfw':
    from egltestcase_glfw import GLFWBackend

    class ESTestCase(GLFWBackend, BaseESTestCase):
        """OpenGL-ES test case backed by glfw."""

else:
    raise ImportError(
        'TEST_WINDOWING=%s is not supported for EGL tests yet (only "glfw")'
        % (_REQUESTED,)
    )
