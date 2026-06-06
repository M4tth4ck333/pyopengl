#! /usr/bin/env python3
"""Reusable base TestCase for GLU (OpenGL Utility library) tests.

GLU rides on a desktop compatibility-profile GL context: gluProject and friends
read the fixed-function ``GL_MODELVIEW_MATRIX`` / ``GL_PROJECTION_MATRIX``, and
quadrics / tessellation / NURBS emit immediate-mode geometry.  A test therefore
gets a current, cleared compatibility context plus GLU-specific conveniences
(quadric/tess/nurbs factories with cleanup, a default projection helper).  The
class is toolkit-agnostic and defers window/context creation to a backend mixin
(currently :class:`glutestcase_glfw.GLFWBackend`), chosen by ``TEST_WINDOWING``
(only ``glfw`` today), mirroring the tests/gl and tests/gles suites.

    from glutestcase import GLUTestCase

    class TestThing(GLUTestCase):
        def test_it(self):
            q = self.quadric()
            ...
"""

from __future__ import print_function
import os
import ctypes
import time
import unittest
import contextlib

from OpenGL import GL as _gl
from OpenGL import GLU as _glu


class BaseGLUTestCase(unittest.TestCase):
    """Toolkit-agnostic base class for GLU tests."""

    #: GLU needs the fixed-function pipeline, so always a compatibility context.
    profile = 'compatibility'
    #: (major, minor) version to request; 2.1 is the highest pure-compat target.
    gl_version = (2, 1)
    red_size = green_size = blue_size = alpha_size = 8
    depth_size = 24
    stencil_size = 8
    accum_size = 0
    width = height = 128
    visible = os.environ.get('TEST_VISIBLE', '1').lower() not in ('0', 'false', 'no')
    dwell = 0.2

    # --- backend hooks (a mixin must implement these) --------------------
    def _create_context(self):
        raise NotImplementedError(
            'No windowing backend mixed in; use GLUTestCase or a backend subclass'
        )

    def _swap(self):
        raise NotImplementedError

    def _destroy_context(self):
        raise NotImplementedError

    # --- fixture ----------------------------------------------------------
    def setUp(self):
        self._create_context()
        self._cleanup = []
        _gl.glViewport(0, 0, self.width, self.height)
        _gl.glClearColor(0.0, 0.0, 0.25, 1.0)
        _gl.glClear(_gl.GL_COLOR_BUFFER_BIT | _gl.GL_DEPTH_BUFFER_BIT)
        self.check_error('setUp')

    def tearDown(self):
        try:
            for fn in reversed(getattr(self, '_cleanup', [])):
                try:
                    fn()
                except Exception:
                    pass
            self._swap()
            if self.visible and self.dwell:
                time.sleep(self.dwell)
        finally:
            self._destroy_context()

    # --- GLU object factories (registered for teardown cleanup) ----------
    def quadric(self):
        """Return a fresh GLUquadric, deleted automatically at teardown."""
        q = _glu.gluNewQuadric()
        self._cleanup.append(lambda: _glu.gluDeleteQuadric(q))
        return q

    def tessellator(self):
        """Return a fresh GLUtesselator, deleted automatically at teardown."""
        tess = _glu.gluNewTess()
        self._cleanup.append(lambda: _glu.gluDeleteTess(tess))
        return tess

    def nurbs(self):
        """Return a fresh GLUnurbs renderer, deleted automatically at teardown."""
        nurb = _glu.gluNewNurbsRenderer()
        self._cleanup.append(lambda: _glu.gluDeleteNurbsRenderer(nurb))
        return nurb

    # --- matrix helpers ---------------------------------------------------
    def set_projection(self, fovy=40.0, near=0.1, far=100.0):
        """Install a gluPerspective projection and an identity modelview.

        Leaves the matrix mode at GL_MODELVIEW (the usual drawing state) so the
        projection / unprojection helpers have well-defined matrices to read.
        """
        aspect = float(self.width) / float(self.height or 1)
        _gl.glMatrixMode(_gl.GL_PROJECTION)
        _gl.glLoadIdentity()
        _glu.gluPerspective(fovy, aspect, near, far)
        _gl.glMatrixMode(_gl.GL_MODELVIEW)
        _gl.glLoadIdentity()
        self.check_error('set_projection')

    # --- introspection helpers -------------------------------------------
    def getString(self, enum):
        value = _gl.glGetString(enum)
        if isinstance(value, bytes):
            return value.decode('ascii', 'replace')
        return value

    def getInteger(self, enum, count=1):
        buf = (ctypes.c_int * count)()
        _gl.glGetIntegerv(enum, buf)
        return buf[0] if count == 1 else list(buf)

    def gluVersion(self):
        """Return the GLU library version as an (major, minor) int tuple."""
        raw = _glu.gluGetString(_glu.GLU_VERSION)
        if isinstance(raw, bytes):
            raw = raw.decode('ascii', 'replace')
        parts = (raw or '0.0').split('.')
        return tuple(int(p) for p in parts[:2])

    @contextlib.contextmanager
    def allow_missing(self):
        """Skip the test if an entry point is not exported by the driver."""
        from OpenGL import error

        try:
            yield
        except error.NullFunctionError as err:
            self.skipTest('entry point not exported: %s' % (err,))

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

    def assert_pixel(self, x, y, expected, tolerance=8):
        actual = self.read_pixel(x, y)
        for chan, (a, e) in enumerate(zip(actual, expected)):
            self.assertLessEqual(
                abs(a - e),
                tolerance,
                'pixel (%d,%d) channel %d = %r, expected ~%r (got %r)'
                % (x, y, chan, a, e, actual),
            )


_REQUESTED = os.environ.get('TEST_WINDOWING', '').strip().lower() or 'glfw'

if _REQUESTED == 'glfw':
    from glutestcase_glfw import GLFWBackend

    class GLUTestCase(GLFWBackend, BaseGLUTestCase):
        """GLU test case backed by glfw (compatibility-profile desktop GL)."""

else:
    raise ImportError(
        'TEST_WINDOWING=%s is not supported for GLU tests yet (only "glfw")'
        % (_REQUESTED,)
    )
