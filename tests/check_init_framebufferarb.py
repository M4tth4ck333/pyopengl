import checkutils

checkutils.require('pygame')
import pygame as pg
import OpenGL

OpenGL.setPlatform("wayland")
import OpenGL.GL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.framebuffer_object import glInitFramebufferObjectARB


def main():
    try:
        pg.init()
        pg.display.set_mode((50, 50), DOUBLEBUF | OPENGL)
        pg.display.init()
    except pg.error as err:
        # e.g. older pygame/SDL builds report "wayland not available"; the
        # display backend simply isn't usable here, so skip rather than fail.
        checkutils.skip('pygame could not open a display: %s' % (err,))
    OpenGL.GL.glGetString(OpenGL.GL.GL_VERSION)
    if not glInitFramebufferObjectARB:
        print("SKIP")
        return
    print(glInitFramebufferObjectARB())
    print(OpenGL.__version__)
    print('OK')


if __name__ == "__main__":
    main()
