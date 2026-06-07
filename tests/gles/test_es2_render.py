#! /usr/bin/env python3
"""GLES2: introspection (glGet*) plus programmable-pipeline array rendering.

Verifies, against a real OpenGL ES 2.0 context:

* ``glGetString`` / ``glGetIntegerv`` introspection returns sane values, and
* a vertex+fragment shader program can draw a triangle whose vertex data is
  fed from a VBO via ``glVertexAttribPointer`` + ``glDrawArrays``,

with the result confirmed by reading pixels back out of the framebuffer.
"""

import unittest
from arraycompat import np  # numpy, or a ctypes fallback when numpy is absent

from egltestcase import ESTestCase

from OpenGL.GLES2 import (
    GL_VERSION,
    GL_VENDOR,
    GL_RENDERER,
    GL_SHADING_LANGUAGE_VERSION,
    GL_MAX_TEXTURE_SIZE,
    GL_MAX_VERTEX_ATTRIBS,
    GL_MAX_VIEWPORT_DIMS,
    GL_FLOAT,
    GL_FALSE,
    GL_TRIANGLES,
    glUseProgram,
    glGetAttribLocation,
    glEnableVertexAttribArray,
    glVertexAttribPointer,
    glDrawArrays,
)
from OpenGL.arrays.vbo import VBO

VERTEX_SHADER = '''#version 100
attribute vec2 position;
void main() {
    gl_Position = vec4( position, 0.0, 1.0 );
}'''

FRAGMENT_SHADER = '''#version 100
precision mediump float;
void main() {
    gl_FragColor = vec4( 1.0, 0.5, 0.0, 1.0 );
}'''


class TestES2Render(ESTestCase):
    api = 'gles'
    gl_version = (2, 0)

    def test_introspection(self):
        """glGetString / glGetIntegerv expose a usable ES context."""
        version = self.getString(GL_VERSION)
        self.assertTrue(version, 'empty GL_VERSION')
        self.assertIn('OpenGL ES', version)
        # vendor / renderer / GLSL version should all be non-empty strings
        for enum in (GL_VENDOR, GL_RENDERER, GL_SHADING_LANGUAGE_VERSION):
            self.assertTrue(self.getString(enum))

        self.assertGreaterEqual(self.getInteger(GL_MAX_TEXTURE_SIZE), 64)
        # ES2 guarantees at least 8 vertex attributes
        self.assertGreaterEqual(self.getInteger(GL_MAX_VERTEX_ATTRIBS), 8)
        dims = self.getInteger(GL_MAX_VIEWPORT_DIMS, count=2)
        self.assertGreaterEqual(dims[0], self.width)
        self.assertGreaterEqual(dims[1], self.height)
        self.check_error('introspection')

    def test_draw_triangle(self):
        """A VBO-fed triangle renders the expected colour in the framebuffer."""
        program = self.compile_program(VERTEX_SHADER, FRAGMENT_SHADER)
        # Centred triangle: covers the middle of the viewport but not the
        # bottom-left corner, so we can tell drawn pixels from cleared ones.
        vbo = VBO(
            np.array(
                [(0.0, 0.8), (-0.8, -0.8), (0.8, -0.8)],
                dtype='f',
            )
        )
        glUseProgram(program)
        position = glGetAttribLocation(program, 'position')
        self.assertNotEqual(position, -1, 'position attribute optimised out')
        with vbo:
            glEnableVertexAttribArray(position)
            glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 2 * 4, vbo)
            glDrawArrays(GL_TRIANGLES, 0, 3)
        self.check_error('draw')

        cx, cy = self.width // 2, self.height // 2
        # Centre is inside the triangle -> fragment colour (255, 128, 0)
        self.assert_pixel(cx, cy, (255, 128, 0, 255))
        # Bottom-left corner is outside the triangle -> clear colour (0,0,64)
        self.assert_pixel(2, 2, (0, 0, 64, 255))


if __name__ == '__main__':
    unittest.main()
