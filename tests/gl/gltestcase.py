#! /usr/bin/env python3
"""Reusable base TestCase for desktop OpenGL rendering tests.

A test declares the context it needs via class attributes -- ``profile``
(``'core'`` / ``'compatibility'``), ``gl_version``, colour/depth/stencil sizes --
and gets a current, cleared context to render into.  :class:`BaseGLTestCase` is
toolkit-agnostic and defers window/context creation to a backend mixin
(currently :class:`gltestcase_glfw.GLFWBackend`).  The backend is chosen by
``TEST_WINDOWING`` (only ``glfw`` today).

    from gltestcase import GLTestCase

    class TestThing(GLTestCase):
        profile = 'core'
        gl_version = (3, 3)
        def test_it(self):
            ...
"""

from __future__ import print_function
import os
import ctypes
import time
import unittest
import contextlib

from OpenGL import GL as _gl


class BaseGLTestCase(unittest.TestCase):
    """Toolkit-agnostic base class for desktop-OpenGL tests."""

    #: 'core' or 'compatibility' (a.k.a. full) profile.
    profile = 'compatibility'
    #: (major, minor) version to request.
    gl_version = (2, 1)
    red_size = green_size = blue_size = alpha_size = 8
    depth_size = 24
    stencil_size = 8
    #: accumulation-buffer bits (legacy; request a non-zero value to use glAccum).
    accum_size = 0
    width = height = 128
    visible = os.environ.get('TEST_VISIBLE', '1').lower() not in ('0', 'false', 'no')
    dwell = 0.2

    # --- backend hooks (a mixin must implement these) --------------------
    def _create_context(self):
        raise NotImplementedError(
            'No windowing backend mixed in; use GLTestCase or a backend subclass'
        )

    def _swap(self):
        raise NotImplementedError

    def _destroy_context(self):
        raise NotImplementedError

    # --- fixture ----------------------------------------------------------
    def setUp(self):
        self._create_context()
        # the core profile requires a bound VAO for any vertex operation
        self._vao = None
        if self.profile.lower() == 'core' and self.gl_version >= (3, 0):
            self._vao = _gl.glGenVertexArrays(1)
            _gl.glBindVertexArray(self._vao)
        _gl.glViewport(0, 0, self.width, self.height)
        _gl.glClearColor(0.0, 0.0, 0.25, 1.0)
        _gl.glClear(_gl.GL_COLOR_BUFFER_BIT | _gl.GL_DEPTH_BUFFER_BIT)
        self.check_error('setUp')

    def tearDown(self):
        try:
            self._swap()
            if self.visible and self.dwell:
                time.sleep(self.dwell)
        finally:
            self._destroy_context()

    # --- introspection helpers -------------------------------------------
    def getString(self, enum):
        value = _gl.glGetString(enum)
        if isinstance(value, bytes):
            return value.decode('ascii', 'replace')
        return value

    def getStringi(self, enum, index):
        value = _gl.glGetStringi(enum, index)
        if isinstance(value, bytes):
            return value.decode('ascii', 'replace')
        return value

    def getInteger(self, enum, count=1):
        buf = (ctypes.c_int * count)()
        _gl.glGetIntegerv(enum, buf)
        return buf[0] if count == 1 else list(buf)

    def version(self):
        """Return the context version as an (major, minor) int tuple."""
        major = self.getInteger(_gl.GL_MAJOR_VERSION)
        minor = self.getInteger(_gl.GL_MINOR_VERSION)
        return (major, minor)

    def extensions(self):
        if self.gl_version >= (3, 0):
            count = self.getInteger(_gl.GL_NUM_EXTENSIONS)
            return {self.getStringi(_gl.GL_EXTENSIONS, i) for i in range(count)}
        raw = self.getString(_gl.GL_EXTENSIONS) or ''
        return set(raw.split())

    def require_extension(self, name):
        if name not in self.extensions():
            self.skipTest('extension %s not available' % (name,))

    def require_version(self, major, minor):
        if self.version() < (major, minor):
            self.skipTest('GL %d.%d required' % (major, minor))

    @contextlib.contextmanager
    def allow_missing(self):
        """Skip the test if an entry point is not exported by the driver."""
        from OpenGL import error

        try:
            yield
        except error.NullFunctionError as err:
            self.skipTest('entry point not exported: %s' % (err,))

    @contextlib.contextmanager
    def exercise(self):
        """Smoke-test extension entry points: skip if unexported, tolerate GLErrors."""
        from OpenGL import error

        try:
            yield
        except error.NullFunctionError as err:
            self.skipTest('entry point not exported: %s' % (err,))
        except error.GLError:
            pass
        while _gl.glGetError() != _gl.GL_NO_ERROR:
            pass

    # --- error / pixel helpers -------------------------------------------
    def check_error(self, context=''):
        err = _gl.glGetError()
        self.assertEqual(
            err, _gl.GL_NO_ERROR, 'GL error 0x%x during %s' % (err, context or '?')
        )

    def read_pixel(self, x, y):
        buf = (ctypes.c_ubyte * 4)()
        _gl.glReadPixels(x, y, 1, 1, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, buf)
        self.check_error('glReadPixels')
        return tuple(buf)

    def read_image(self, x=0, y=0, width=None, height=None):
        width = self.width if width is None else width
        height = self.height if height is None else height
        image = _gl.glReadPixels(
            x, y, width, height, _gl.GL_RGBA, _gl.GL_UNSIGNED_BYTE, outputType=None
        )
        self.check_error('glReadPixels')
        return image

    def assert_pixel(self, x, y, expected, tolerance=8):
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
        from OpenGL.GL import shaders, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER

        stages = [
            shaders.compileShader(vertex_src, GL_VERTEX_SHADER),
            shaders.compileShader(fragment_src, GL_FRAGMENT_SHADER),
        ]
        for stage_enum, source in extra_stages:
            stages.append(shaders.compileShader(source, stage_enum))
        program = shaders.compileProgram(*stages)
        self.check_error('compile_program')
        return program


_REQUESTED = os.environ.get('TEST_WINDOWING', '').strip().lower() or 'glfw'

if _REQUESTED == 'glfw':
    from gltestcase_glfw import GLFWBackend

    class GLTestCase(GLFWBackend, BaseGLTestCase):
        """Desktop-OpenGL test case backed by glfw."""

else:
    raise ImportError(
        'TEST_WINDOWING=%s is not supported for GL tests yet (only "glfw")'
        % (_REQUESTED,)
    )
