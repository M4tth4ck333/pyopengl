#! /usr/bin/env python3
"""Core-context legacy/aliased extensions: transform feedback, integer texture
params, shading-language include, debug-output, indexed blend, conditional
render, timer query, instanced draws, KHR_debug aliases and assorted singles."""

import unittest
import ctypes
import numpy as np

from gltestcase import GLTestCase
from OpenGL.GL import *  # noqa: F401,F403
from OpenGL.GL.EXT.transform_feedback import *  # noqa: F401,F403
from OpenGL.GL.EXT.texture_integer import *  # noqa: F401,F403
from OpenGL.GL.ARB.shading_language_include import *  # noqa: F401,F403
from OpenGL.GL.ARB.debug_output import *  # noqa: F401,F403
from OpenGL.GL.ARB.draw_buffers_blend import *  # noqa: F401,F403
from OpenGL.GL.AMD.draw_buffers_blend import *  # noqa: F401,F403
from OpenGL.GL.NV.conditional_render import *  # noqa: F401,F403
from OpenGL.GL.EXT.timer_query import *  # noqa: F401,F403
from OpenGL.GL.EXT.draw_instanced import *  # noqa: F401,F403
from OpenGL.GL.ARB.draw_instanced import (
    glDrawArraysInstancedARB,
    glDrawElementsInstancedARB,
)  # noqa: F401
from OpenGL.GL.EXT.debug_label import *  # noqa: F401,F403
from OpenGL.GL.KHR.debug import *  # noqa: F401,F403
from OpenGL.GL.MESA.framebuffer_flip_y import *  # noqa: F401,F403
from OpenGL.GL.OVR.multiview import *  # noqa: F401,F403

VS = '#version 150\nin vec4 p; out float v; void main(){ v = p.x; gl_Position = p; }'
FS = '#version 150\nout vec4 c; void main(){ c = vec4(1.0); }'


def _first(ids):
    return int(ids[0]) if hasattr(ids, '__len__') else int(ids)


def _char_pp(strings):
    arr = (ctypes.c_char_p * len(strings))(*strings)
    return ctypes.cast(arr, ctypes.POINTER(ctypes.POINTER(ctypes.c_char)))


class TestMiscCore(GLTestCase):
    profile = 'core'
    gl_version = (3, 3)

    def test_transform_feedback_ext(self):
        self.require_extension('GL_EXT_transform_feedback')
        with self.allow_missing():
            from OpenGL.GL import shaders

            vs = shaders.compileShader(VS, GL_VERTEX_SHADER)
            fs = shaders.compileShader(FS, GL_FRAGMENT_SHADER)
            prog = glCreateProgram()
            glAttachShader(prog, vs)
            glAttachShader(prog, fs)
            glTransformFeedbackVaryingsEXT(
                prog, 1, _char_pp([b'v']), GL_INTERLEAVED_ATTRIBS
            )
            glLinkProgram(prog)
            glUseProgram(prog)
            glGetTransformFeedbackVaryingEXT(
                prog,
                0,
                64,
                np.zeros(1, 'i'),
                np.zeros(1, 'i'),
                np.zeros(1, 'I'),
                (ctypes.c_char * 64)(),
            )
            buf = int(glGenBuffers(1))
            glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER, buf)
            glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER, 64, None, GL_DYNAMIC_DRAW)
            glBindBufferBaseEXT(GL_TRANSFORM_FEEDBACK_BUFFER, 0, buf)
            glBindBufferRangeEXT(GL_TRANSFORM_FEEDBACK_BUFFER, 0, buf, 0, 64)
            glBindBufferOffsetEXT(GL_TRANSFORM_FEEDBACK_BUFFER, 0, buf, 0)
            glBeginTransformFeedbackEXT(GL_POINTS)
            glEndTransformFeedbackEXT()

    def test_texture_integer_ext(self):
        self.require_extension('GL_EXT_texture_integer')
        with self.allow_missing():
            tex = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D, tex)
            glTexParameterIivEXT(
                GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.zeros(4, 'i')
            )
            glTexParameterIuivEXT(
                GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.zeros(4, 'I')
            )
            glGetTexParameterIivEXT(
                GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.zeros(4, 'i')
            )
            glGetTexParameterIuivEXT(
                GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.zeros(4, 'I')
            )
            glClearColorIiEXT(0, 0, 0, 0)
            glClearColorIuiEXT(0, 0, 0, 0)

    def test_shading_language_include_arb(self):
        self.require_extension('GL_ARB_shading_language_include')
        with self.allow_missing():
            name = b'/inc.glsl'
            body = b'float k(){ return 1.0; }'
            glNamedStringARB(GL_SHADER_INCLUDE_ARB, len(name), name, len(body), body)
            self.assertTrue(glIsNamedStringARB(len(name), name))
            glGetNamedStringARB(
                len(name), name, 256, np.zeros(1, 'i'), (ctypes.c_char * 256)()
            )
            glGetNamedStringivARB(
                len(name), name, GL_NAMED_STRING_LENGTH_ARB, np.zeros(1, 'i')
            )
            glDeleteNamedStringARB(len(name), name)
        # glCompileShaderIncludeARB's include-path tree validation is finicky;
        # the call drives the wrapper and exercise() tolerates the GLError
        with self.exercise():
            sh = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(
                sh,
                '#version 420\n#extension GL_ARB_shading_language_include : require\n'
                '#include "/inc.glsl"\nout vec4 c; void main(){ c = vec4(1.0); }',
            )
            glCompileShaderIncludeARB(sh, 1, _char_pp([b'/']), None)

    def test_debug_output_arb(self):
        self.require_extension('GL_ARB_debug_output')
        with self.allow_missing():

            @GLDEBUGPROCARB
            def cb(source, t, i, sev, length, message, user):
                return None

            self._cb = cb
            glDebugMessageCallbackARB(cb, None)
            glDebugMessageControlARB(
                GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, GL_TRUE
            )
            glDebugMessageInsertARB(
                GL_DEBUG_SOURCE_APPLICATION_ARB,
                GL_DEBUG_TYPE_OTHER_ARB,
                1,
                GL_DEBUG_SEVERITY_LOW_ARB,
                -1,
                b'hi',
            )
            glGetDebugMessageLogARB(
                4,
                256,
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'i'),
                (ctypes.c_char * 256)(),
            )

    def test_indexed_blend(self):
        self.require_extension('GL_ARB_draw_buffers_blend')
        with self.allow_missing():
            glBlendEquationiARB(0, GL_FUNC_ADD)
            glBlendEquationSeparateiARB(0, GL_FUNC_ADD, GL_FUNC_ADD)
            glBlendFunciARB(0, GL_ONE, GL_ZERO)
            glBlendFuncSeparateiARB(0, GL_ONE, GL_ZERO, GL_ONE, GL_ZERO)
        with self.allow_missing():
            self.require_extension('GL_AMD_draw_buffers_blend')
            glBlendEquationIndexedAMD(0, GL_FUNC_ADD)
            glBlendEquationSeparateIndexedAMD(0, GL_FUNC_ADD, GL_FUNC_ADD)
            glBlendFuncIndexedAMD(0, GL_ONE, GL_ZERO)
            glBlendFuncSeparateIndexedAMD(0, GL_ONE, GL_ZERO, GL_ONE, GL_ZERO)

    def test_conditional_render_nv(self):
        self.require_extension('GL_NV_conditional_render')
        with self.allow_missing():
            q = _first(glGenQueries(1))
            glBeginQuery(GL_SAMPLES_PASSED, q)
            glEndQuery(GL_SAMPLES_PASSED)
            glBeginConditionalRenderNV(q, GL_QUERY_WAIT_NV)
            glEndConditionalRenderNV()

    def test_timer_query_ext(self):
        self.require_extension('GL_EXT_timer_query')
        with self.allow_missing():
            q = _first(glGenQueries(1))
            glBeginQuery(GL_TIME_ELAPSED, q)
            glEndQuery(GL_TIME_ELAPSED)
            glGetQueryObjecti64vEXT(q, GL_QUERY_RESULT, np.zeros(1, 'q'))
            glGetQueryObjectui64vEXT(q, GL_QUERY_RESULT, np.zeros(1, 'Q'))

    def test_draw_instanced(self):
        self.require_extension('GL_EXT_draw_instanced')
        with self.allow_missing():
            prog = self.compile_program(
                '#version 150\nin vec4 p; void main(){ gl_Position = p; }', FS
            )
            glUseProgram(prog)
            buf = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glBufferData(
                GL_ARRAY_BUFFER,
                np.array([(-1, -1), (1, -1), (0, 1)], 'f'),
                GL_STATIC_DRAW,
            )
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
            glDrawArraysInstancedEXT(GL_TRIANGLES, 0, 3, 2)
            idx = np.array([0, 1, 2], 'I')
            ibo = int(glGenBuffers(1))
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, idx, GL_STATIC_DRAW)
            glDrawElementsInstancedEXT(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None, 2)
            glDrawArraysInstancedARB(GL_TRIANGLES, 0, 3, 2)
            glDrawElementsInstancedARB(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None, 2)

    def test_debug_label_ext(self):
        self.require_extension('GL_EXT_debug_label')
        with self.allow_missing():
            buf = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glLabelObjectEXT(
                GL_BUFFER_OBJECT_EXT, buf, 0, b'mybuf'
            )  # EXT length 0 = null-terminated
            glGetObjectLabelEXT(
                GL_BUFFER_OBJECT_EXT, buf, 64, np.zeros(1, 'i'), (ctypes.c_char * 64)()
            )

    def test_khr_debug_aliases(self):
        self.require_extension('GL_KHR_debug')
        with self.allow_missing():

            @GLDEBUGPROC
            def cb(source, t, i, sev, length, message, user):
                return None

            self._cb = cb
            glDebugMessageCallbackKHR(cb, None)
            glDebugMessageControlKHR(
                GL_DONT_CARE, GL_DONT_CARE, GL_DONT_CARE, 0, None, GL_TRUE
            )
            glDebugMessageInsertKHR(
                GL_DEBUG_SOURCE_APPLICATION,
                GL_DEBUG_TYPE_OTHER,
                1,
                GL_DEBUG_SEVERITY_NOTIFICATION,
                -1,
                b'hi',
            )
            glPushDebugGroupKHR(GL_DEBUG_SOURCE_APPLICATION, 0, -1, b'g')
            glPopDebugGroupKHR()
            buf = int(glGenBuffers(1))
            glBindBuffer(GL_ARRAY_BUFFER, buf)
            glObjectLabelKHR(GL_BUFFER, buf, -1, b'l')
            glGetObjectLabelKHR(
                GL_BUFFER, buf, 64, (ctypes.c_int * 1)(), (ctypes.c_char * 64)()
            )
            sync = glFenceSync(GL_SYNC_GPU_COMMANDS_COMPLETE, 0)
            glObjectPtrLabelKHR(sync, -1, b's')
            glGetObjectPtrLabelKHR(
                sync, 64, (ctypes.c_int * 1)(), (ctypes.c_char * 64)()
            )
            ptr = ctypes.c_void_p()
            glGetPointervKHR(GL_DEBUG_CALLBACK_FUNCTION, ctypes.byref(ptr))
            glDeleteSync(sync)
            glGetDebugMessageLogKHR(
                4,
                256,
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'I'),
                np.zeros(4, 'i'),
                (ctypes.c_char * 256)(),
            )

    def test_framebuffer_flip_y_mesa(self):
        self.require_extension('GL_MESA_framebuffer_flip_y')
        with self.allow_missing():
            fbo = int(glGenFramebuffers(1))
            glBindFramebuffer(GL_FRAMEBUFFER, fbo)
            glFramebufferParameteriMESA(
                GL_FRAMEBUFFER, GL_FRAMEBUFFER_FLIP_Y_MESA, GL_TRUE
            )
            glGetFramebufferParameterivMESA(
                GL_FRAMEBUFFER, GL_FRAMEBUFFER_FLIP_Y_MESA, np.zeros(1, 'i')
            )

    def test_multiview_ovr(self):
        self.require_extension('GL_OVR_multiview')
        with self.allow_missing():
            arr = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D_ARRAY, arr)
            glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, 16, 16, 2)
            fbo = int(glGenFramebuffers(1))
            glBindFramebuffer(GL_FRAMEBUFFER, fbo)
            glFramebufferTextureMultiviewOVR(
                GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, arr, 0, 0, 2
            )
        # the DSA multiview form is not implemented here; the call drives the
        # wrapper and exercise() tolerates the GLError
        with self.exercise():
            glNamedFramebufferTextureMultiviewOVR(
                int(glGenFramebuffers(1)), GL_COLOR_ATTACHMENT0, arr, 0, 0, 2
            )


if __name__ == '__main__':
    unittest.main()
