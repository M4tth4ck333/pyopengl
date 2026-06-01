"""3D texture-upload size validation for OpenGL ES 3.

Wraps glTexImage3D / glTexSubImage3D with the same size check as the 2D
entry points (see OpenGL/GLES2/images.py).
"""
from OpenGL.raw.GLES3.VERSION import GLES3_3_0 as _simple
from OpenGL.GLES2.images import _coerce_image

__all__ = ('glTexImage3D', 'glTexSubImage3D')


def glTexImage3D(
    target, level, internalformat, width, height, depth, border, format, type, pixels=None
):
    pixels = _coerce_image((width, height, depth), format, type, pixels)
    return _simple.glTexImage3D(
        target, level, internalformat, width, height, depth, border, format, type, pixels
    )


def glTexSubImage3D(
    target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels
):
    pixels = _coerce_image((width, height, depth), format, type, pixels)
    return _simple.glTexSubImage3D(
        target, level, xoffset, yoffset, zoffset, width, height, depth, format, type, pixels
    )
