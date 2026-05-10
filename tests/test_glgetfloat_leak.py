#!/usr/bin/python
from __future__ import print_function
import sys, os, math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import psutil


def main():
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    glClearColor(1.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    proc = psutil.Process(os.getpid())
    mem = None
    for i in range(0, 500):
        if i == 10:
            mem = proc.memory_percent()
        if i > 400:
            new_mem = proc.memory_percent()
            # Allow small allocator/GC noise; a real leak grows orders of magnitude more.
            assert math.isclose(new_mem, mem, rel_tol=1e-3), (new_mem, mem)
            break

        modelview_matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        assert modelview_matrix is not None

    sys.stdout.write('OK\n')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
