"""Image-handling support for OpenGL ES.

Registers the image format/type tables (so array allocation works without
importing desktop ``OpenGL.GL``), provides an auto-allocating ``glReadPixels``,
and size-validates the 2D texture-upload entry points, mirroring
``OpenGL/GL/images.py`` but using ES entry points.
"""
import ctypes
from OpenGL.raw.GLES2.VERSION import GLES2_2_0 as _simple
from OpenGL import images, arrays, error
from OpenGL.arrays import arraydatatype as _adt
from OpenGL._bytes import integer_types

# Format -> components-per-pixel and type -> array storage type.  Values are
# shared with desktop GL; updates here are additive and value-compatible.
images.COMPONENT_COUNTS.update({
    _simple.GL_RGBA: 4,
    _simple.GL_RGB: 3, # testing suggests this isn't well supported in e.g. glReadPixels
    _simple.GL_LUMINANCE_ALPHA: 2,
    _simple.GL_LUMINANCE: 1,
    _simple.GL_ALPHA: 1,
})
images.TYPE_TO_ARRAYTYPE.update({
    _simple.GL_UNSIGNED_BYTE: _simple.GL_UNSIGNED_BYTE,
    _simple.GL_UNSIGNED_SHORT_5_6_5: _simple.GL_UNSIGNED_SHORT,
    _simple.GL_UNSIGNED_SHORT_4_4_4_4: _simple.GL_UNSIGNED_SHORT,
    _simple.GL_UNSIGNED_SHORT_5_5_5_1: _simple.GL_UNSIGNED_SHORT,
    _simple.GL_FLOAT: _simple.GL_FLOAT,
    _simple.GL_UNSIGNED_INT: _simple.GL_UNSIGNED_INT,
})
images.TIGHT_PACK_FORMATS.update({
    _simple.GL_UNSIGNED_SHORT_5_6_5: 3,
    _simple.GL_UNSIGNED_SHORT_4_4_4_4: 4,
    _simple.GL_UNSIGNED_SHORT_5_5_5_1: 4,
})

__all__ = (
    'glReadPixels',
    'glTexImage2D',
    'glTexSubImage2D',
    'glCompressedTexImage2D',
)

# bytes per storage unit, e.g. GL_UNSIGNED_BYTE -> 1, GL_UNSIGNED_SHORT -> 2
_TYPE_BYTES = {}
for _storage in set(images.TYPE_TO_ARRAYTYPE.values()):
    try:
        _TYPE_BYTES[_storage] = _adt.ArrayDatatype.arrayByteCount(
            arrays.GL_CONSTANT_TO_ARRAY_TYPE[_storage].zeros((1,))
        )
    except Exception:
        pass


def _coerce_image(dims, format, type, pixels):
    """Coerce ``pixels`` to an array and check it holds enough data for ``dims``.

    Returns ``pixels`` unchanged for null/offset uploads or anything we can't
    measure (so PBO offsets and exotic buffers still pass through).  Forces
    UNPACK_ALIGNMENT to 1 so the tight byte count is exactly what GL will read.
    """
    if pixels is None or isinstance(pixels, integer_types):
        return pixels
    storage = images.TYPE_TO_ARRAYTYPE.get(type, type)
    try:
        arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[storage]
        array = arrayType.asArray(pixels)
    except (KeyError, error.Error):
        return pixels
    try:
        _simple.glPixelStorei(_simple.GL_UNPACK_ALIGNMENT, 1)
    except error.GLError:
        pass
    components = images.COMPONENT_COUNTS.get(format)
    per_pixel = _TYPE_BYTES.get(storage)
    if components is not None and per_pixel is not None:
        if type not in images.TIGHT_PACK_FORMATS:
            per_pixel *= components
        needed = per_pixel
        for d in dims:
            needed *= int(d)
        have = _adt.ArrayDatatype.arrayByteCount(array)
        if have < needed:
            raise ValueError(
                'Image data too small: %d bytes for a %s %s/%s image needs %d'
                % (have, 'x'.join(str(int(d)) for d in dims), format, type, needed)
            )
    return array


def glTexImage2D(target, level, internalformat, width, height, border, format, type, pixels=None):
    pixels = _coerce_image((width, height), format, type, pixels)
    return _simple.glTexImage2D(
        target, level, internalformat, width, height, border, format, type, pixels
    )


def glTexSubImage2D(target, level, xoffset, yoffset, width, height, format, type, pixels):
    pixels = _coerce_image((width, height), format, type, pixels)
    return _simple.glTexSubImage2D(
        target, level, xoffset, yoffset, width, height, format, type, pixels
    )


def glCompressedTexImage2D(target, level, internalformat, width, height, border, imageSize, data):
    if data is not None and not isinstance(data, integer_types):
        data = _adt.ArrayDatatype.asArray(data)
        have = _adt.ArrayDatatype.arrayByteCount(data)
        if have < int(imageSize):
            raise ValueError(
                'Compressed image data too small: %d bytes < imageSize %d'
                % (have, int(imageSize))
            )
    return _simple.glCompressedTexImage2D(
        target, level, internalformat, width, height, border, imageSize, data
    )


def glReadPixels(x, y, width, height, format, type, array=None, outputType=bytes):
    """Read a block of pixels, allocating the result array when not supplied.

    Mirrors ``OpenGL.GL.glReadPixels`` for ES: returns a numpy array (or bytes,
    per ``OpenGL.UNSIGNED_BYTE_IMAGES_AS_STRING``) when ``array`` is omitted.
    """
    x, y, width, height = int(x), int(y), int(width), int(height)
    if array is None:
        # ES lacks most GL_PACK_* state; alignment is the one that matters here.
        try:
            _simple.glPixelStorei(_simple.GL_PACK_ALIGNMENT, 1)
        except error.GLError:
            pass
        array = images.createTargetArray(format, (width, height), type)
        imageData = array
        owned = True
    else:
        if isinstance(array, integer_types):
            imageData = ctypes.c_void_p(array)
        else:
            arrayType = arrays.GL_CONSTANT_TO_ARRAY_TYPE[
                images.TYPE_TO_ARRAYTYPE.get(type, type)
            ]
            array = arrayType.asArray(array)
            imageData = array
        owned = False

    _simple.glReadPixels(x, y, width, height, format, type, imageData)
    if owned and outputType is bytes:
        return images.returnFormat(array, type)
    return array
