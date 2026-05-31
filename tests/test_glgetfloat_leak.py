#!/usr/bin/python
from __future__ import print_function
import os, math, unittest
from basetestcase import BaseTest
from OpenGL.GL import *

try:
    import psutil
except ImportError:
    psutil = None


class TestGLGetFloatLeak(BaseTest):
    @unittest.skipUnless(psutil, "psutil not installed")
    def test_glGetFloatv_no_leak(self):
        """Repeated glGetFloatv(GL_MODELVIEW_MATRIX) must not leak memory"""
        proc = psutil.Process(os.getpid())
        mem = None
        for i in range(0, 500):
            if i == 10:
                mem = proc.memory_percent()
            if i > 400:
                new_mem = proc.memory_percent()
                # Allow small allocator/GC noise; a real leak grows orders of
                # magnitude more.
                assert math.isclose(new_mem, mem, rel_tol=1e-3), (new_mem, mem)
                break
            modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
            assert modelview_matrix is not None


if __name__ == '__main__':
    unittest.main()
