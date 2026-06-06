#! /usr/bin/env python3
"""GL 1.0 (compatibility): texture images, parameters, env, texgen, queries."""

import unittest
import numpy as np

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403


class TestGL1Texture(GLTestCase):
    profile = 'compatibility'
    gl_version = (2, 1)

    def test_image_and_parameters(self):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            4,
            4,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            np.zeros((4, 4, 4), 'B'),
        )
        glTexImage1D(
            GL_TEXTURE_1D,
            0,
            GL_RGBA,
            4,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            np.zeros((4, 4), 'B'),
        )
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, float(GL_NEAREST))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.zeros(4, 'f'))
        glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, np.array([GL_REPEAT], 'i'))
        glGetTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, np.zeros(1, 'f'))
        glGetTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, np.zeros(1, 'i'))
        glGetTexLevelParameterfv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, np.zeros(1, 'f'))
        glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, np.zeros(1, 'i'))
        data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        self.assertTrue(len(data) > 0)
        self.check_error('texture image/params')

    def test_texenv_texgen(self):
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, float(GL_MODULATE))
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, np.zeros(4, 'f'))
        glTexEnviv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, np.array([GL_DECAL], 'i'))
        glGetTexEnvfv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_COLOR, np.zeros(4, 'f'))
        glGetTexEnviv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, np.zeros(1, 'i'))
        glTexGend(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGenf(GL_T, GL_TEXTURE_GEN_MODE, float(GL_OBJECT_LINEAR))
        glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR)
        glTexGendv(GL_S, GL_OBJECT_PLANE, np.array([1, 0, 0, 0], 'd'))
        glTexGenfv(GL_T, GL_OBJECT_PLANE, np.array([0, 1, 0, 0], 'f'))
        glTexGeniv(GL_S, GL_TEXTURE_GEN_MODE, np.array([GL_EYE_LINEAR], 'i'))
        glGetTexGendv(GL_S, GL_OBJECT_PLANE, np.zeros(4, 'd'))
        glGetTexGenfv(GL_T, GL_OBJECT_PLANE, np.zeros(4, 'f'))
        glGetTexGeniv(GL_S, GL_TEXTURE_GEN_MODE, np.zeros(1, 'i'))
        self.check_error('texenv/texgen')


if __name__ == '__main__':
    unittest.main()
