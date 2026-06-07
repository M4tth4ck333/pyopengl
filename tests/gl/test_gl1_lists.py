#! /usr/bin/env python3
"""GL 1.0 (compatibility): display lists, selection, feedback, accumulation."""

import unittest
from arraycompat import np  # numpy, or a ctypes fallback when numpy is absent

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403


class TestGL1Lists(GLTestCase):
    profile = 'compatibility'
    gl_version = (2, 1)
    accum_size = 16

    def test_display_lists(self):
        base = glGenLists(2)
        self.assertTrue(base)
        glNewList(base, GL_COMPILE)
        glColor3f(1.0, 0.0, 0.0)
        glEndList()
        self.assertTrue(glIsList(base))
        glCallList(base)
        glListBase(base)
        glCallLists(1, GL_UNSIGNED_BYTE, np.array([0], 'B'))
        glDeleteLists(base, 2)
        self.check_error('display lists')

    def test_selection_feedback(self):
        glSelectBuffer(64, np.zeros(64, 'I'))
        glRenderMode(GL_SELECT)
        glInitNames()
        glPushName(1)
        glLoadName(2)
        glPopName()
        glRenderMode(GL_RENDER)
        feedback = np.zeros(64, 'f')
        glFeedbackBuffer(64, GL_2D, feedback)
        glRenderMode(GL_FEEDBACK)
        glPassThrough(1.0)
        glRenderMode(GL_RENDER)
        self.check_error('selection/feedback')

    def test_accumulation(self):
        if self.getInteger(GL_ACCUM_RED_BITS) < 1:
            self.skipTest('no accumulation buffer available')
        glClear(GL_ACCUM_BUFFER_BIT)
        glAccum(GL_ACCUM, 1.0)
        glAccum(GL_RETURN, 1.0)
        self.check_error('accumulation')


if __name__ == '__main__':
    unittest.main()
