#! /usr/bin/env python3
"""GL 4.4 (core): immutable buffer storage, texture clears, multi-bind."""

import unittest
import ctypes
import numpy as np

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403


def _ssize(*vals):
    return (ctypes.c_ssize_t * len(vals))(*vals)


class TestGL44(GLTestCase):
    profile = 'core'
    gl_version = (4, 5)

    def test_buffer_storage_and_clear(self):
        buf = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, buf)
        glBufferStorage(
            GL_ARRAY_BUFFER, 64, None, GL_MAP_READ_BIT | GL_DYNAMIC_STORAGE_BIT
        )
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, 16, 16)
        glClearTexImage(tex, 0, GL_RGBA, GL_UNSIGNED_BYTE, np.zeros(4, 'B'))
        glClearTexSubImage(
            tex, 0, 0, 0, 0, 8, 8, 1, GL_RGBA, GL_UNSIGNED_BYTE, np.zeros(4, 'B')
        )
        self.check_error('storage/clear')

    def test_multi_bind(self):
        glBindVertexArray(int(glGenVertexArrays(1)))
        bufs = glGenBuffers(2)
        ids = np.array([int(b) for b in bufs], 'I')
        for b in ids:
            glBindBuffer(GL_UNIFORM_BUFFER, int(b))
            glBufferData(GL_UNIFORM_BUFFER, 64, None, GL_STATIC_DRAW)
        glBindBuffersBase(GL_UNIFORM_BUFFER, 0, 2, ids)
        # GLintptr*/GLsizeiptr* args need ctypes arrays (numpy not accepted);
        # PyOpenGL types offsets as c_ssize_t and sizes as c_ulong
        glBindBuffersRange(
            GL_UNIFORM_BUFFER, 0, 2, ids, _ssize(0, 0), (ctypes.c_ulong * 2)(64, 64)
        )
        texs = np.array([int(t) for t in glGenTextures(2)], 'I')
        for t in texs:
            glBindTexture(GL_TEXTURE_2D, int(t))
            glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, 4, 4)
        glBindTextures(0, 2, texs)
        samplers = np.array([int(s) for s in glGenSamplers(2)], 'I')
        glBindSamplers(0, 2, samplers)
        glBindImageTextures(0, 2, texs)
        vbufs = glGenBuffers(2)
        vids = np.array([int(b) for b in vbufs], 'I')
        for b in vids:
            glBindBuffer(GL_ARRAY_BUFFER, int(b))
            glBufferData(GL_ARRAY_BUFFER, 64, None, GL_STATIC_DRAW)
        glBindVertexBuffers(0, 2, vids, _ssize(0, 0), (ctypes.c_int * 2)(16, 16))
        self.check_error('multi bind')


if __name__ == '__main__':
    unittest.main()
