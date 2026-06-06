#! /usr/bin/env python3
"""GLES2: fixed-function state setters/getters (blend, depth, stencil, etc.).

Exercises the per-context state entry points; verification is "the call leaves
no GL error" plus a few read-back state checks.
"""

import unittest
import ctypes

from egltestcase import ESTestCase

from OpenGL.GLES2 import (
    GL_BLEND,
    GL_DEPTH_TEST,
    GL_STENCIL_TEST,
    GL_CULL_FACE,
    GL_SCISSOR_TEST,
    GL_DITHER,
    GL_SAMPLE_COVERAGE,
    GL_POLYGON_OFFSET_FILL,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_ONE,
    GL_ZERO,
    GL_FUNC_ADD,
    GL_FUNC_SUBTRACT,
    GL_LESS,
    GL_LEQUAL,
    GL_ALWAYS,
    GL_KEEP,
    GL_REPLACE,
    GL_FRONT,
    GL_BACK,
    GL_FRONT_AND_BACK,
    GL_CW,
    GL_CCW,
    GL_GENERATE_MIPMAP_HINT,
    GL_NICEST,
    GL_FASTEST,
    GL_UNPACK_ALIGNMENT,
    GL_PACK_ALIGNMENT,
    GL_TRUE,
    glEnable,
    glDisable,
    glIsEnabled,
    glBlendColor,
    glBlendEquation,
    glBlendEquationSeparate,
    glBlendFunc,
    glBlendFuncSeparate,
    glClearDepthf,
    glClearStencil,
    glColorMask,
    glCullFace,
    glFrontFace,
    glDepthFunc,
    glDepthMask,
    glDepthRangef,
    glHint,
    glLineWidth,
    glPixelStorei,
    glPolygonOffset,
    glSampleCoverage,
    glScissor,
    glStencilFunc,
    glStencilFuncSeparate,
    glStencilMask,
    glStencilMaskSeparate,
    glStencilOp,
    glStencilOpSeparate,
    glFinish,
    glFlush,
    glGetBooleanv,
    glGetFloatv,
    GL_DEPTH_WRITEMASK,
    GL_LINE_WIDTH,
)


class TestES2State(ESTestCase):
    api = 'gles'
    gl_version = (2, 0)

    def test_capabilities(self):
        for cap in (
            GL_BLEND,
            GL_DEPTH_TEST,
            GL_STENCIL_TEST,
            GL_CULL_FACE,
            GL_SCISSOR_TEST,
            GL_DITHER,
            GL_SAMPLE_COVERAGE,
            GL_POLYGON_OFFSET_FILL,
        ):
            glEnable(cap)
            self.assertEqual(glIsEnabled(cap), GL_TRUE)
            glDisable(cap)
            self.assertFalse(glIsEnabled(cap))
        self.check_error('capabilities')

    def test_blend_and_depth(self):
        glBlendColor(0.1, 0.2, 0.3, 0.4)
        glBlendEquation(GL_FUNC_ADD)
        glBlendEquationSeparate(GL_FUNC_ADD, GL_FUNC_SUBTRACT)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ZERO)
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_TRUE)
        glDepthRangef(0.0, 1.0)
        glClearDepthf(1.0)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        self.check_error('blend/depth')

        mask = (ctypes.c_ubyte * 1)()
        glGetBooleanv(GL_DEPTH_WRITEMASK, mask)
        self.assertTrue(mask[0])

    def test_stencil(self):
        glClearStencil(0)
        glStencilFunc(GL_ALWAYS, 1, 0xFF)
        glStencilFuncSeparate(GL_FRONT, GL_LESS, 0, 0xFF)
        glStencilMask(0xFF)
        glStencilMaskSeparate(GL_BACK, 0xFF)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glStencilOpSeparate(GL_FRONT, GL_KEEP, GL_KEEP, GL_KEEP)
        self.check_error('stencil')

    def test_rasterizer_and_misc(self):
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glFrontFace(GL_CW)
        glLineWidth(1.0)
        glPolygonOffset(1.0, 1.0)
        glSampleCoverage(1.0, False)
        glScissor(0, 0, self.width, self.height)
        glHint(GL_GENERATE_MIPMAP_HINT, GL_NICEST)
        glHint(GL_GENERATE_MIPMAP_HINT, GL_FASTEST)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glFinish()
        glFlush()
        self.check_error('rasterizer/misc')

        line = (ctypes.c_float * 1)()
        glGetFloatv(GL_LINE_WIDTH, line)
        self.assertGreater(line[0], 0.0)


if __name__ == '__main__':
    unittest.main()
