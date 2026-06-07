#! /usr/bin/env python3
"""Reusable base TestCase for desktop OpenGL rendering tests.

A test declares the context it needs via class attributes -- ``profile``
(``'core'`` / ``'compatibility'``), ``gl_version``, colour/depth/stencil sizes --
and gets a current, cleared context to render into.

The implementation now lives in the shared :mod:`glcontext` framework:
:class:`glcontext_desktop.DesktopGLTestCaseBase` supplies the desktop-GL API and
helpers, while the windowing backend (glfw or pygame) is chosen by
:func:`glcontext.pick_backend` from the ``TEST_WINDOWING`` environment variable.

    from gltestcase import GLTestCase

    class TestThing(GLTestCase):
        profile = 'core'
        gl_version = (3, 3)
        def test_it(self):
            ...
"""

from __future__ import print_function

from glcontext import pick_backend
from glcontext_desktop import DesktopGLTestCaseBase

#: backwards-compatible alias for the toolkit-agnostic API base.
BaseGLTestCase = DesktopGLTestCaseBase


class GLTestCase(pick_backend(), DesktopGLTestCaseBase):
    """Desktop-OpenGL test case backed by the selected windowing toolkit."""
