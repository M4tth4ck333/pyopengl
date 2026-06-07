"""Make the shared tests/ helper modules importable from every sub-suite.

The gl / glu / gles suites live in sub-directories and import shared modules
(glcontext, glcontext_desktop, ...) by bare name.  pytest's prepend import mode
adds each test file's own directory to sys.path but not necessarily this one, so
add it here explicitly.  This conftest is loaded before any test under tests/.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# The headless EGL-device backend (TEST_WINDOWING=egl) loads the GL entry points
# through EGL, so PYOPENGL_PLATFORM must be 'egl' before anything imports OpenGL.
# conftest runs before any test module, so this is the safe place to set it.
if os.environ.get('TEST_WINDOWING', '').strip().lower() == 'egl':
    os.environ.setdefault('PYOPENGL_PLATFORM', 'egl')
