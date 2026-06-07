"""Root pytest configuration shared by tests/ and accelerate/tests/.

Adds the ``tests/`` directory to ``sys.path`` so the shared ``arraycompat``
helper (numpy, or a ctypes fallback when numpy is absent) is importable from
every test sub-directory regardless of which one pytest happens to be
collecting.
"""
import os
import sys

_TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)
