#! /usr/bin/env python3
"""bool(fn) is a reliable availability check for ES extension entry points.

Regression guard for the checkExtension name-normalisation fix: before it,
every ES extension function resolved to a null function, so ``bool(fn)`` (the
universal "is this available?" idiom) returned False even for entry points that
called successfully.  Now ``bool(fn)`` is True iff the extension is supported and
the entry point is exported.
"""

import os
import json
import importlib
import unittest

from egltestcase import ESTestCase

HERE = os.path.dirname(os.path.abspath(__file__))


def _module_for(ext):
    """OpenGL module object for a 'GL_VENDOR_name' extension string, or None."""
    body = ext[3:]
    vendor, name = body.split('_', 1)
    for pkg in ('OpenGL.GLES2', 'OpenGL.GLES3'):
        try:
            return importlib.import_module('%s.%s.%s' % (pkg, vendor, name))
        except ImportError:
            continue
    return None


class TestExtensionAvailability(ESTestCase):
    api = 'gles'
    gl_version = (3, 0)

    def test_bool_true_for_supported_extensions(self):
        """Every supported extension's entry points report bool(fn) == True."""
        with open(os.path.join(HERE, 'supported_extensions.json')) as fh:
            with_funcs = json.load(fh)['with_funcs']
        available = self.extensions()
        checked = 0
        for ext, funcs in with_funcs.items():
            if ext not in available:
                continue
            module = _module_for(ext)
            if module is None:
                continue
            for fname in funcs:
                fn = getattr(module, fname, None)
                if fn is None:
                    continue
                self.assertTrue(
                    bool(fn), '%s: bool() False but %s is supported' % (fname, ext)
                )
                checked += 1
        self.assertGreater(checked, 0, 'no supported extension functions checked')

    def test_bool_false_for_unsupported_extension(self):
        """An entry point of an unsupported extension reports bool(fn) == False."""
        available = self.extensions()
        candidates = [
            (
                'GL_APPLE_framebuffer_multisample',
                'OpenGL.GLES2.APPLE.framebuffer_multisample',
                'glRenderbufferStorageMultisampleAPPLE',
            ),
            (
                'GL_IMG_multisampled_render_to_texture',
                'OpenGL.GLES2.IMG.multisampled_render_to_texture',
                'glRenderbufferStorageMultisampleIMG',
            ),
        ]
        for ext, modname, fname in candidates:
            if ext in available:
                continue
            module = importlib.import_module(modname)
            self.assertFalse(
                bool(getattr(module, fname)),
                '%s: bool() True but %s is not supported' % (fname, ext),
            )
            return
        self.skipTest('no known-unsupported extension available to test against')


if __name__ == '__main__':
    unittest.main()
