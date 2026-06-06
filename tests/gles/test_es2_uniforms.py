#! /usr/bin/env python3
"""GLES2: uniform setters (all glUniform* variants) and vertex-attrib state."""

import unittest
import numpy as np

from egltestcase import ESTestCase

from OpenGL.GLES2 import (
    GL_CURRENT_VERTEX_ATTRIB,
    GL_VERTEX_ATTRIB_ARRAY_ENABLED,
    GL_VERTEX_ATTRIB_ARRAY_POINTER,
    glUseProgram,
    glGetUniformLocation,
    glUniform1f,
    glUniform2f,
    glUniform3f,
    glUniform4f,
    glUniform1i,
    glUniform2i,
    glUniform3i,
    glUniform4i,
    glUniform1fv,
    glUniform2fv,
    glUniform3fv,
    glUniform4fv,
    glUniform1iv,
    glUniform2iv,
    glUniform3iv,
    glUniform4iv,
    glUniformMatrix2fv,
    glUniformMatrix3fv,
    glUniformMatrix4fv,
    glGetUniformfv,
    glGetUniformiv,
    glVertexAttrib1f,
    glVertexAttrib2f,
    glVertexAttrib3f,
    glVertexAttrib4f,
    glVertexAttrib1fv,
    glVertexAttrib2fv,
    glVertexAttrib3fv,
    glVertexAttrib4fv,
    glDisableVertexAttribArray,
    glGetVertexAttribfv,
    glGetVertexAttribiv,
    glGetVertexAttribPointerv,
)

VERTEX = '''#version 100
attribute vec4 position;
void main() { gl_Position = position; }'''

FRAGMENT = '''#version 100
precision mediump float;
uniform float uf;
uniform vec2 uv2; uniform vec3 uv3; uniform vec4 uv4;
uniform int ui; uniform ivec2 ui2; uniform ivec3 ui3; uniform ivec4 ui4;
uniform mat2 um2; uniform mat3 um3; uniform mat4 um4;
void main() {
    float s = uf + uv2.x + uv3.y + uv4.z
        + float(ui + ui2.x + ui3.y + ui4.z)
        + um2[0][0] + um3[1][1] + um4[2][2];
    gl_FragColor = vec4( s );
}'''


class TestES2Uniforms(ESTestCase):
    api = 'gles'
    gl_version = (2, 0)

    def test_uniform_setters(self):
        program = self.compile_program(VERTEX, FRAGMENT)
        glUseProgram(program)
        def loc(n):
            return glGetUniformLocation(program, n)

        glUniform1f(loc('uf'), 1.0)
        glUniform2f(loc('uv2'), 1.0, 2.0)
        glUniform3f(loc('uv3'), 1.0, 2.0, 3.0)
        glUniform4f(loc('uv4'), 1.0, 2.0, 3.0, 4.0)
        glUniform1i(loc('ui'), 1)
        glUniform2i(loc('ui2'), 1, 2)
        glUniform3i(loc('ui3'), 1, 2, 3)
        glUniform4i(loc('ui4'), 1, 2, 3, 4)
        self.check_error('scalar uniforms')

        glUniform1fv(loc('uf'), 1, np.array([2.0], 'f'))
        glUniform2fv(loc('uv2'), 1, np.array([2.0, 3.0], 'f'))
        glUniform3fv(loc('uv3'), 1, np.array([2.0, 3.0, 4.0], 'f'))
        glUniform4fv(loc('uv4'), 1, np.array([2.0, 3.0, 4.0, 5.0], 'f'))
        glUniform1iv(loc('ui'), 1, np.array([2], 'i'))
        glUniform2iv(loc('ui2'), 1, np.array([2, 3], 'i'))
        glUniform3iv(loc('ui3'), 1, np.array([2, 3, 4], 'i'))
        glUniform4iv(loc('ui4'), 1, np.array([2, 3, 4, 5], 'i'))
        self.check_error('vector uniforms')

        glUniformMatrix2fv(loc('um2'), 1, False, np.eye(2, dtype='f'))
        glUniformMatrix3fv(loc('um3'), 1, False, np.eye(3, dtype='f'))
        glUniformMatrix4fv(loc('um4'), 1, False, np.eye(4, dtype='f'))
        self.check_error('matrix uniforms')

        # read back two of them (params is a caller-supplied buffer here)
        fbuf = np.zeros(1, 'f')
        glGetUniformfv(program, loc('uf'), fbuf)
        self.assertAlmostEqual(float(fbuf[0]), 2.0, places=4)
        ibuf = np.zeros(1, 'i')
        glGetUniformiv(program, loc('ui'), ibuf)
        self.assertEqual(int(ibuf[0]), 2)

    def test_vertex_attrib_state(self):
        glVertexAttrib1f(1, 0.5)
        glVertexAttrib2f(1, 0.5, 0.5)
        glVertexAttrib3f(1, 0.5, 0.5, 0.5)
        glVertexAttrib4f(1, 0.1, 0.2, 0.3, 0.4)
        glVertexAttrib1fv(1, np.array([0.5], 'f'))
        glVertexAttrib2fv(1, np.array([0.5, 0.5], 'f'))
        glVertexAttrib3fv(1, np.array([0.5, 0.5, 0.5], 'f'))
        glVertexAttrib4fv(1, np.array([0.1, 0.2, 0.3, 0.4], 'f'))
        glDisableVertexAttribArray(1)
        self.check_error('vertex attribs')

        current = glGetVertexAttribfv(1, GL_CURRENT_VERTEX_ATTRIB)
        self.assertEqual(len(current), 4)
        self.assertFalse(int(glGetVertexAttribiv(1, GL_VERTEX_ATTRIB_ARRAY_ENABLED)[0]))
        glGetVertexAttribPointerv(1, GL_VERTEX_ATTRIB_ARRAY_POINTER)
        self.check_error('attrib queries')


if __name__ == '__main__':
    unittest.main()
