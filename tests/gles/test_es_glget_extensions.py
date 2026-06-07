#! /usr/bin/env python3
"""Live glGet size coverage across every OpenGL-ES version and extension the
driver advertises.

The ES counterpart of ``gl/test_glget_extensions.py``: data-driven from
``gles/glget_groups.json`` (generated from the Khronos registry for the ``gles2``
API).  For each supported ES version and extension, every ``state`` pname it
defines is read with the correct getter and its returned size is checked against
``glgetsizes.csv``.  A pname the driver does not serve as a global query is
skipped; a wrong-sized return fails (a CSV bug to fix, then ``src/regen_glgets.py``).

Runs on both backends: ``TEST_WINDOWING=glfw`` (llvmpipe ES via EGL) and ``=egl``
(the GPU).
"""

import unittest

from egltestcase import ESTestCase
from glget_check import GLGetCheckMixin


class TestESExtensionGLGets(GLGetCheckMixin, ESTestCase):
    gl_version = (3, 2)            # widest ES pname set both drivers provide
    glget_suite = 'gles'

    def test_supported_extension_state_pnames(self):
        checked, exts, object_scoped = self.sweep_present('extensions')
        self.assertTrue(exts, 'no advertised ES extensions matched the registry map')
        print('\n[glget/es] extensions: %d supported, %d state pnames checked, '
              '%d object-scoped pnames deferred' % (exts, checked, len(object_scoped)))

    def test_core_version_state_pnames(self):
        checked, feats, object_scoped = self.sweep_present('features')
        self.assertTrue(feats, 'no ES versions matched the registry map')
        print('\n[glget/es] core versions: %d supported, %d state pnames checked, '
              '%d object-scoped pnames deferred' % (feats, checked, len(object_scoped)))


if __name__ == '__main__':
    unittest.main()
