#! /usr/bin/env python3
"""Reusable base TestCase for GLU (OpenGL Utility library) tests.

GLU rides on a desktop compatibility-profile GL context: gluProject and friends
read the fixed-function ``GL_MODELVIEW_MATRIX`` / ``GL_PROJECTION_MATRIX``, and
quadrics / tessellation / NURBS emit immediate-mode geometry.  A test therefore
gets a current, cleared compatibility context plus GLU-specific conveniences
(quadric/tess/nurbs factories with cleanup, a default projection helper).

The implementation now lives in the shared :mod:`glcontext` framework:
:class:`glcontext_desktop.GLUTestCaseBase` supplies the GL+GLU API and helpers,
while the windowing backend (glfw or pygame) is chosen by
:func:`glcontext.pick_backend` from the ``TEST_WINDOWING`` environment variable.

    from glutestcase import GLUTestCase

    class TestThing(GLUTestCase):
        def test_it(self):
            q = self.quadric()
            ...
"""

from __future__ import print_function

from glcontext import pick_backend
from glcontext_desktop import GLUTestCaseBase

#: backwards-compatible alias for the toolkit-agnostic API base.
BaseGLUTestCase = GLUTestCaseBase


class GLUTestCase(pick_backend(), GLUTestCaseBase):
    """GLU test case backed by the selected windowing toolkit."""
