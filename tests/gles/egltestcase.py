#! /usr/bin/env python3
"""Reusable base TestCase for EGL / OpenGL-ES rendering tests.

A test declares the context it needs via class attributes (api, gl_version,
colour/depth/stencil sizes) and gets a current, cleared context to render into.

The implementation now lives in the shared :mod:`glcontext` framework:
:class:`glcontext_es.ESTestCaseBase` supplies the OpenGL-ES API and helpers,
while the windowing backend is chosen by :func:`glcontext.pick_backend` from the
``TEST_WINDOWING`` environment variable.  ES contexts require EGL, so the ES
suite only runs under the glfw backend (it skips under pygame).

    from egltestcase import ESTestCase

    class TestThing(ESTestCase):
        gl_version = (3, 0)
        def test_it(self):
            ...
"""

from __future__ import print_function

from glcontext import pick_backend
from glcontext_es import ESTestCaseBase

#: backwards-compatible alias for the toolkit-agnostic API base.
BaseESTestCase = ESTestCaseBase


class ESTestCase(pick_backend(), ESTestCaseBase):
    """OpenGL-ES test case backed by the selected windowing toolkit."""
