"""Dispatch BaseTest to a windowing-system specific implementation.

Selection order:

1. Determine which backends are importable (``pygame``, ``glfw``).
2. If the ``TEST_WINDOWING`` env var is set, honour it when that backend
   is available; otherwise fall through to the first available backend.
3. Default preference when ``TEST_WINDOWING`` is unset: glfw, then pygame.
"""

from __future__ import print_function
import os
import importlib.util


def _installed(name):
    """Check whether ``name`` is importable without actually importing it.

    Importing pygame/glfw has side effects (initialises subsystems, allocates
    memory), so we only probe for the package metadata here.
    """
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


_AVAILABLE = [name for name in ('glfw', 'pygame') if _installed(name)]

if not _AVAILABLE:
    raise ImportError(
        'No windowing backend available for tests; install pygame or glfw'
    )

_REQUESTED = os.environ.get('TEST_WINDOWING', '').strip().lower() or None
if _REQUESTED and _REQUESTED not in ('pygame', 'glfw', 'egl'):
    raise ValueError(
        'TEST_WINDOWING=%r is not recognised (expected "pygame", "glfw" or "egl")'
        % (_REQUESTED,)
    )
if _REQUESTED == 'egl':
    # The headless egl backend forces PYOPENGL_PLATFORM=egl process-wide; these
    # legacy root-level tests create their own *windowed* GL context, which is
    # incompatible with that platform (a window + egl-device platform segfaults).
    # There is no windowed equivalent here, so provide a BaseTest that skips.
    import unittest

    class BaseTest(unittest.TestCase):
        """Placeholder under TEST_WINDOWING=egl: windowed tests can't run headless."""

        def setUp(self):
            self.skipTest('windowed BaseTest is unavailable under the headless egl backend')

    _BACKEND = 'egl'
else:
    if _REQUESTED and _REQUESTED not in _AVAILABLE:
        raise ImportError(
            'TEST_WINDOWING=%s requested but %s is not installed' % (_REQUESTED, _REQUESTED)
        )
    _BACKEND = _REQUESTED or _AVAILABLE[0]

if _BACKEND == 'egl':
    pass
elif _BACKEND == 'pygame':
    from basetestcase_pygame import *  # noqa: F401,F403
    from basetestcase_pygame import BaseTest  # noqa: F401
elif _BACKEND == 'glfw':
    from basetestcase_glfw import *  # noqa: F401,F403
    from basetestcase_glfw import BaseTest  # noqa: F401
else:
    raise RuntimeError('Unhandled backend: %s' % (_BACKEND,))
