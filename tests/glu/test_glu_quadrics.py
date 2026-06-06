#! /usr/bin/env python3
"""GLU quadric objects: gluNewQuadric / gluDeleteQuadric, the gluQuadric*
state setters, the gluQuadricCallback error hook, and the gluSphere / gluCylinder
/ gluDisk / gluPartialDisk primitives."""

import unittest

from glutestcase import GLUTestCase
from OpenGL.GL import glMatrixMode, glLoadIdentity, GL_MODELVIEW, GL_TRUE
from OpenGL.GLU import (
    gluNewQuadric,
    gluDeleteQuadric,
    gluQuadricDrawStyle,
    gluQuadricNormals,
    gluQuadricOrientation,
    gluQuadricTexture,
    gluQuadricCallback,
    gluSphere,
    gluCylinder,
    gluDisk,
    gluPartialDisk,
    GLU_FILL,
    GLU_LINE,
    GLU_SILHOUETTE,
    GLU_POINT,
    GLU_SMOOTH,
    GLU_FLAT,
    GLU_NONE,
    GLU_OUTSIDE,
    GLU_INSIDE,
    GLU_ERROR,
)


class TestGLUQuadrics(GLUTestCase):
    def setUp(self):
        super(TestGLUQuadrics, self).setUp()
        self.set_projection()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def test_new_delete(self):
        q = gluNewQuadric()
        self.assertIsNotNone(q)
        gluDeleteQuadric(q)
        self.check_error('new/delete quadric')

    def test_state_setters(self):
        q = self.quadric()
        for style in (GLU_FILL, GLU_LINE, GLU_SILHOUETTE, GLU_POINT):
            gluQuadricDrawStyle(q, style)
        for normals in (GLU_NONE, GLU_FLAT, GLU_SMOOTH):
            gluQuadricNormals(q, normals)
        for orient in (GLU_OUTSIDE, GLU_INSIDE):
            gluQuadricOrientation(q, orient)
        gluQuadricTexture(q, GL_TRUE)
        self.check_error('quadric state setters')

    def test_callback_registration(self):
        # gluQuadricCallback installs a GLU_ERROR handler; we only require that
        # registration succeeds and the reference is retained on the object.
        q = self.quadric()
        recorded = []
        gluQuadricCallback(q, GLU_ERROR, lambda code: recorded.append(code))
        self.assertIn(GLU_ERROR, q.callbacks)
        self.check_error('gluQuadricCallback')

    def test_sphere(self):
        q = self.quadric()
        gluQuadricNormals(q, GLU_SMOOTH)
        gluSphere(q, 1.0, 24, 16)
        self.check_error('gluSphere')

    def test_cylinder(self):
        q = self.quadric()
        gluCylinder(q, 1.0, 0.5, 2.0, 24, 4)
        self.check_error('gluCylinder')

    def test_disk(self):
        q = self.quadric()
        gluDisk(q, 0.25, 1.0, 24, 4)
        self.check_error('gluDisk')

    def test_partial_disk(self):
        q = self.quadric()
        gluPartialDisk(q, 0.25, 1.0, 24, 4, 0.0, 180.0)
        self.check_error('gluPartialDisk')

    def test_textured_quadric(self):
        q = self.quadric()
        gluQuadricTexture(q, GL_TRUE)
        gluQuadricNormals(q, GLU_SMOOTH)
        gluSphere(q, 0.8, 16, 12)
        self.check_error('textured quadric')


if __name__ == '__main__':
    unittest.main()
