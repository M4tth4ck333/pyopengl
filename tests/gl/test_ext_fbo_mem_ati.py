#! /usr/bin/env python3
"""GL_EXT_framebuffer_object (pre-core FBOs), GL_EXT_memory_object (external
memory queries) and GL_ATI_fragment_shader (legacy register combiners)."""

import unittest
import numpy as np

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403
from OpenGL.GL.EXT.framebuffer_object import *  # noqa: F401,F403
from OpenGL.GL.EXT.memory_object import *  # noqa: F401,F403
from OpenGL.GL.ATI.fragment_shader import *  # noqa: F401,F403


class TestEXTFramebufferObject(GLTestCase):
    profile = 'compatibility'
    gl_version = (2, 1)

    def test_framebuffer_object(self):
        self.require_extension('GL_EXT_framebuffer_object')
        with self.allow_missing():
            fbo = int(glGenFramebuffersEXT(1))
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo)
            self.assertTrue(glIsFramebufferEXT(fbo))
            rbo = int(glGenRenderbuffersEXT(1))
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, rbo)
            self.assertTrue(glIsRenderbufferEXT(rbo))
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_RGBA8, 16, 16)
            glGetRenderbufferParameterivEXT(
                GL_RENDERBUFFER_EXT, GL_RENDERBUFFER_WIDTH_EXT, np.zeros(1, 'i')
            )
            glFramebufferRenderbufferEXT(
                GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_RENDERBUFFER_EXT, rbo
            )
            tex = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexImage2D(
                GL_TEXTURE_2D, 0, GL_RGBA8, 16, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, None
            )
            glFramebufferTexture2DEXT(
                GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, tex, 0
            )
            glGetFramebufferAttachmentParameterivEXT(
                GL_FRAMEBUFFER_EXT,
                GL_COLOR_ATTACHMENT0_EXT,
                GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE_EXT,
                np.zeros(1, 'i'),
            )
            glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
            glGenerateMipmapEXT(GL_TEXTURE_2D)
            t1 = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_1D, t1)
            glTexImage1D(
                GL_TEXTURE_1D, 0, GL_RGBA8, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, None
            )
            f1 = int(glGenFramebuffersEXT(1))
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, f1)
            glFramebufferTexture1DEXT(
                GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_1D, t1, 0
            )
            t3 = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_3D, t3)
            glTexImage3D(
                GL_TEXTURE_3D,
                0,
                GL_RGBA8,
                16,
                16,
                2,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                None,
            )
            f3 = int(glGenFramebuffersEXT(1))
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, f3)
            glFramebufferTexture3DEXT(
                GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_3D, t3, 0, 0
            )
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
            glDeleteFramebuffersEXT(1, [fbo])
            glDeleteRenderbuffersEXT(1, [rbo])
        self.check_error('EXT framebuffer object')


class TestEXTMemoryObject(GLTestCase):
    profile = 'core'
    gl_version = (4, 5)

    def test_memory_object(self):
        self.require_extension('GL_EXT_memory_object')
        with self.allow_missing():
            n = self.getInteger(GL_NUM_DEVICE_UUIDS_EXT)
            glGetUnsignedBytevEXT(GL_DRIVER_UUID_EXT, np.zeros(16, 'B'))
            if n > 0:
                glGetUnsignedBytei_vEXT(GL_DEVICE_UUID_EXT, 0, np.zeros(16, 'B'))
            mids = np.zeros(1, 'I')
            glCreateMemoryObjectsEXT(1, mids)
            mem = int(mids[0])
            self.assertTrue(glIsMemoryObjectEXT(mem))
            glMemoryObjectParameterivEXT(
                mem, GL_DEDICATED_MEMORY_OBJECT_EXT, np.array([GL_FALSE], 'i')
            )
            glGetMemoryObjectParameterivEXT(
                mem, GL_DEDICATED_MEMORY_OBJECT_EXT, np.zeros(1, 'i')
            )
            glDeleteMemoryObjectsEXT(1, [mem])
        # storage-from-memory needs an imported allocation we cannot make here,
        # so the calls fail GL validation -- but they still drive the wrapper's
        # argument marshalling, which is what we are testing; exercise() tolerates
        with self.exercise():
            mids2 = np.zeros(1, 'I')
            glCreateMemoryObjectsEXT(1, mids2)
            m2 = int(mids2[0])
            buf = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glBufferStorageMemEXT(GL_ARRAY_BUFFER, 64, m2, 0)
            glNamedBufferStorageMemEXT(int(glGenBuffers(1)), 64, m2, 0)
            glBindTexture(GL_TEXTURE_1D, int(glGenTextures(1)))
            glTexStorageMem1DEXT(GL_TEXTURE_1D, 1, GL_RGBA8, 4, m2, 0)
            glBindTexture(GL_TEXTURE_2D, int(glGenTextures(1)))
            glTexStorageMem2DEXT(GL_TEXTURE_2D, 1, GL_RGBA8, 4, 4, m2, 0)
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, int(glGenTextures(1)))
            glTexStorageMem2DMultisampleEXT(
                GL_TEXTURE_2D_MULTISAMPLE, 4, GL_RGBA8, 4, 4, GL_TRUE, m2, 0
            )
            glBindTexture(GL_TEXTURE_3D, int(glGenTextures(1)))
            glTexStorageMem3DEXT(GL_TEXTURE_3D, 1, GL_RGBA8, 4, 4, 4, m2, 0)
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE_ARRAY, int(glGenTextures(1)))
            glTexStorageMem3DMultisampleEXT(
                GL_TEXTURE_2D_MULTISAMPLE_ARRAY, 4, GL_RGBA8, 4, 4, 2, GL_TRUE, m2, 0
            )
            glTextureStorageMem1DEXT(int(glGenTextures(1)), 1, GL_RGBA8, 4, m2, 0)
            glTextureStorageMem2DEXT(int(glGenTextures(1)), 1, GL_RGBA8, 4, 4, m2, 0)
            glTextureStorageMem2DMultisampleEXT(
                int(glGenTextures(1)), 4, GL_RGBA8, 4, 4, GL_TRUE, m2, 0
            )
            glTextureStorageMem3DEXT(int(glGenTextures(1)), 1, GL_RGBA8, 4, 4, 4, m2, 0)
            glTextureStorageMem3DMultisampleEXT(
                int(glGenTextures(1)), 4, GL_RGBA8, 4, 4, 2, GL_TRUE, m2, 0
            )


class TestATIFragmentShader(GLTestCase):
    profile = 'compatibility'
    gl_version = (2, 1)

    def test_ati_fragment_shader(self):
        self.require_extension('GL_ATI_fragment_shader')
        with self.allow_missing():
            sid = glGenFragmentShadersATI(1)
            glBindFragmentShaderATI(sid)
            glBeginFragmentShaderATI()
            glPassTexCoordATI(GL_REG_0_ATI, GL_TEXTURE0, GL_SWIZZLE_STR_ATI)
            glSampleMapATI(GL_REG_1_ATI, GL_TEXTURE0, GL_SWIZZLE_STR_ATI)
            glColorFragmentOp1ATI(
                GL_MOV_ATI,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
            )
            glColorFragmentOp2ATI(
                GL_ADD_ATI,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_1_ATI,
                GL_NONE,
                GL_NONE,
            )
            glColorFragmentOp3ATI(
                GL_MAD_ATI,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_1_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
            )
            glAlphaFragmentOp1ATI(
                GL_MOV_ATI, GL_REG_0_ATI, GL_NONE, GL_REG_0_ATI, GL_NONE, GL_NONE
            )
            glAlphaFragmentOp2ATI(
                GL_ADD_ATI,
                GL_REG_0_ATI,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_1_ATI,
                GL_NONE,
                GL_NONE,
            )
            glAlphaFragmentOp3ATI(
                GL_MAD_ATI,
                GL_REG_0_ATI,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_1_ATI,
                GL_NONE,
                GL_NONE,
                GL_REG_0_ATI,
                GL_NONE,
                GL_NONE,
            )
            glEndFragmentShaderATI()
            glSetFragmentShaderConstantATI(GL_CON_0_ATI, np.zeros(4, 'f'))
            glDeleteFragmentShaderATI(sid)
        self.check_error('ATI fragment shader')


if __name__ == '__main__':
    unittest.main()
