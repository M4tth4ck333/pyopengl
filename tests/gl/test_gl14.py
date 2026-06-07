#! /usr/bin/env python3
"""GL 1.4 (compatibility): blend, fog coord, multi-draw, point params,
secondary color, window pos."""

import unittest
import ctypes
from arraycompat import np  # numpy, or a ctypes fallback when numpy is absent

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403


class TestGL14(GLTestCase):
    profile = 'compatibility'
    gl_version = (2, 1)

    def test_blend_and_point(self):
        glBlendColor(0.1, 0.2, 0.3, 0.4)
        glBlendEquation(GL_FUNC_ADD)
        glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO)
        glPointParameterf(GL_POINT_SIZE_MIN, 1.0)
        glPointParameteri(GL_POINT_SPRITE_COORD_ORIGIN, GL_LOWER_LEFT)
        glPointParameterfv(GL_POINT_DISTANCE_ATTENUATION, np.array([1, 0, 0], 'f'))
        glPointParameteriv(GL_POINT_FADE_THRESHOLD_SIZE, np.array([1], 'i'))
        self.check_error('blend/point')

    def test_fog_coord(self):
        glFogCoordf(1.0)
        glFogCoordd(1.0)
        glFogCoordfv(np.array([1.0], 'f'))
        glFogCoorddv(np.array([1.0], 'd'))
        glEnableClientState(GL_FOG_COORD_ARRAY)
        glFogCoordPointer(GL_FLOAT, 0, np.array([1.0, 1.0, 1.0], 'f'))
        glDisableClientState(GL_FOG_COORD_ARRAY)
        self.check_error('fog coord')

    def test_secondary_color(self):
        glBegin(GL_POINTS)
        glSecondaryColor3b(0, 0, 0)
        glSecondaryColor3s(0, 0, 0)
        glSecondaryColor3i(0, 0, 0)
        glSecondaryColor3f(0.0, 0.0, 0.0)
        glSecondaryColor3d(0.0, 0.0, 0.0)
        glSecondaryColor3ub(0, 0, 0)
        glSecondaryColor3us(0, 0, 0)
        glSecondaryColor3ui(0, 0, 0)
        glSecondaryColor3bv(np.zeros(3, 'b'))
        glSecondaryColor3sv(np.zeros(3, 'h'))
        glSecondaryColor3iv(np.zeros(3, 'i'))
        glSecondaryColor3fv(np.zeros(3, 'f'))
        glSecondaryColor3dv(np.zeros(3, 'd'))
        glSecondaryColor3ubv(np.zeros(3, 'B'))
        glSecondaryColor3usv(np.zeros(3, 'H'))
        glSecondaryColor3uiv(np.zeros(3, 'I'))
        glEnd()
        glEnableClientState(GL_SECONDARY_COLOR_ARRAY)
        glSecondaryColorPointer(3, GL_FLOAT, 0, np.zeros((3, 3), 'f'))
        glDisableClientState(GL_SECONDARY_COLOR_ARRAY)
        self.check_error('secondary color')

    def test_window_pos(self):
        glWindowPos2s(0, 0)
        glWindowPos2i(0, 0)
        glWindowPos2f(0.0, 0.0)
        glWindowPos2d(0.0, 0.0)
        glWindowPos3s(0, 0, 0)
        glWindowPos3i(0, 0, 0)
        glWindowPos3f(0.0, 0.0, 0.0)
        glWindowPos3d(0.0, 0.0, 0.0)
        glWindowPos2sv(np.zeros(2, 'h'))
        glWindowPos2iv(np.zeros(2, 'i'))
        glWindowPos2fv(np.zeros(2, 'f'))
        glWindowPos2dv(np.zeros(2, 'd'))
        glWindowPos3sv(np.zeros(3, 'h'))
        glWindowPos3iv(np.zeros(3, 'i'))
        glWindowPos3fv(np.zeros(3, 'f'))
        glWindowPos3dv(np.zeros(3, 'd'))
        self.check_error('window pos')

    def test_multi_draw(self):
        verts = np.array([(-1, -1), (1, -1), (0, 1)], 'f')
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(2, GL_FLOAT, 0, verts)
        glMultiDrawArrays(GL_TRIANGLES, np.array([0], 'i'), np.array([3], 'i'), 1)
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, np.array([0, 1, 2], 'I'), GL_STATIC_DRAW)
        # const void*const* indices -> array of byte offsets into the bound EBO
        offsets = (ctypes.c_void_p * 1)(0)
        glMultiDrawElements(
            GL_TRIANGLES, np.array([3], 'i'), GL_UNSIGNED_INT, offsets, 1
        )
        glDisableClientState(GL_VERTEX_ARRAY)
        self.check_error('multi draw')


if __name__ == '__main__':
    unittest.main()
