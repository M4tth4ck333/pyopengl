#! /usr/bin/env python3
"""Headless EGL-device backend for :class:`glcontext.ContextTestCase`.

Creates contexts directly on an EGL device (the GPU) with a pbuffer surface and
no window system at all -- the right path for containers / CI where the on-screen
compositor is software-rendered (llvmpipe) but the real GPU is reachable via the
``EGL_EXT_platform_device`` extension.  It serves both desktop OpenGL and
OpenGL-ES, honouring ``api`` / ``profile`` / ``gl_version`` / the
colour-depth-stencil sizes; a context the driver will not provide skips the test.

Selected with ``TEST_WINDOWING=egl``.  ``conftest.py`` forces
``PYOPENGL_PLATFORM=egl`` for that case so the GL entry points load through EGL.
Set ``TEST_EGL_DEVICE=<index>`` to pin a specific device; by default the first
non-software device is used (falling back to device 0).

There is no window, so this backend is always headless: ``visible`` is forced
False and the inter-test dwell is skipped.
"""

from __future__ import print_function

import os
import ctypes
import logging

from OpenGL.EGL import (
    EGLint,
    EGLConfig,
    EGL_NONE,
    EGL_NO_CONTEXT,
    EGL_NO_SURFACE,
    EGL_NO_DISPLAY,
    EGL_HEIGHT,
    EGL_WIDTH,
    EGL_SURFACE_TYPE,
    EGL_PBUFFER_BIT,
    EGL_RENDERABLE_TYPE,
    EGL_OPENGL_BIT,
    EGL_OPENGL_ES2_BIT,
    EGL_OPENGL_ES3_BIT,
    EGL_OPENGL_API,
    EGL_OPENGL_ES_API,
    EGL_RED_SIZE,
    EGL_GREEN_SIZE,
    EGL_BLUE_SIZE,
    EGL_ALPHA_SIZE,
    EGL_DEPTH_SIZE,
    EGL_STENCIL_SIZE,
    EGL_CONTEXT_MAJOR_VERSION,
    EGL_CONTEXT_MINOR_VERSION,
    EGL_CONTEXT_OPENGL_PROFILE_MASK,
    EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
    EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT,
    eglInitialize,
    eglChooseConfig,
    eglBindAPI,
    eglCreateContext,
    eglCreatePbufferSurface,
    eglMakeCurrent,
    eglDestroyContext,
    eglDestroySurface,
    eglQueryString,
    EGL_VENDOR,
)
from OpenGL.EGL.EXT.device_enumeration import eglQueryDevicesEXT
from OpenGL.EGL.EXT.device_base import EGLDeviceEXT, eglQueryDeviceStringEXT
from OpenGL.EGL.EXT.platform_base import eglGetPlatformDisplayEXT
from OpenGL.EGL.EXT.platform_device import EGL_PLATFORM_DEVICE_EXT

log = logging.getLogger(__name__)

_ES_APIS = ('gles', 'es')

# EGL_EXT_device_query / device_string tokens (not always exported by name).
_EGL_DRIVER_NAME_EXT = 0x335F
_SOFTWARE_MARKERS = ('llvmpipe', 'swrast', 'softpipe', 'software')

#: cached (display) once initialised -- the device display is reused per test.
_display = None


def _enumerate_devices():
    num = EGLint()
    if not eglQueryDevicesEXT(0, None, num) or num.value < 1:
        raise RuntimeError('eglQueryDevicesEXT reported no EGL devices')
    devices = (EGLDeviceEXT * num.value)()
    eglQueryDevicesEXT(num.value, devices, num)
    return [devices[i] for i in range(num.value)]


def _device_label(device):
    """Best-effort human label for an EGL device (may be empty)."""
    for token in (_EGL_DRIVER_NAME_EXT,):
        try:
            value = eglQueryDeviceStringEXT(device, token)
        except Exception:
            value = None
        if value:
            return value.decode('ascii', 'replace') if isinstance(value, bytes) else str(value)
    return ''


def _pick_device(devices):
    """Choose the device to render on.

    ``TEST_EGL_DEVICE`` pins an explicit index; otherwise prefer the first
    device that does not look software-rendered, falling back to device 0.
    """
    override = os.environ.get('TEST_EGL_DEVICE')
    if override is not None:
        return devices[int(override)], int(override)
    for index, device in enumerate(devices):
        label = _device_label(device).lower()
        if label and not any(marker in label for marker in _SOFTWARE_MARKERS):
            return device, index
    return devices[0], 0


def _ensure_display():
    global _display
    if _display is None:
        devices = _enumerate_devices()
        device, index = _pick_device(devices)
        display = eglGetPlatformDisplayEXT(EGL_PLATFORM_DEVICE_EXT, device, None)
        if display == EGL_NO_DISPLAY:
            raise RuntimeError('eglGetPlatformDisplayEXT returned EGL_NO_DISPLAY')
        major, minor = EGLint(), EGLint()
        if not eglInitialize(display, major, minor):
            raise RuntimeError('eglInitialize failed for the EGL device display')
        vendor = eglQueryString(display, EGL_VENDOR)
        log.info(
            'EGL device backend: device[%d] %r, EGL %d.%d, vendor=%r',
            index, _device_label(devices[index]) or '<unknown>',
            major.value, minor.value, vendor,
        )
        _display = display
    return _display


def _attrib_array(pairs):
    flat = []
    for key, value in pairs:
        flat.extend((key, value))
    flat.append(EGL_NONE)
    return (EGLint * len(flat))(*flat)


class EGLDeviceBackend(object):
    """Mixin supplying headless EGL-device context creation (desktop GL or ES)."""

    backend_name = 'egl'

    #: there is no window, so this backend is always headless.
    visible = False

    _egl_context = None
    _egl_surface = None

    def _create_context(self):
        display = _ensure_display()
        api = getattr(self, 'api', 'gl').lower()
        major, minor = self.gl_version

        if api in _ES_APIS:
            eglBindAPI(EGL_OPENGL_ES_API)
            renderable = EGL_OPENGL_ES3_BIT if major >= 3 else EGL_OPENGL_ES2_BIT
        else:
            eglBindAPI(EGL_OPENGL_API)
            renderable = EGL_OPENGL_BIT

        config_attrs = _attrib_array([
            (EGL_SURFACE_TYPE, EGL_PBUFFER_BIT),
            (EGL_RENDERABLE_TYPE, renderable),
            (EGL_RED_SIZE, self.red_size),
            (EGL_GREEN_SIZE, self.green_size),
            (EGL_BLUE_SIZE, self.blue_size),
            (EGL_ALPHA_SIZE, self.alpha_size),
            (EGL_DEPTH_SIZE, self.depth_size),
            (EGL_STENCIL_SIZE, self.stencil_size),
        ])
        config = (EGLConfig * 1)()
        num_config = EGLint()
        if not eglChooseConfig(display, config_attrs, config, 1, num_config) or num_config.value < 1:
            self.skipTest(
                'No EGL pbuffer config for %s %d.%d with the requested buffer sizes'
                % (api, major, minor)
            )

        context_pairs = [
            (EGL_CONTEXT_MAJOR_VERSION, major),
            (EGL_CONTEXT_MINOR_VERSION, minor),
        ]
        # GL profiles only exist for desktop GL >= 3.2.
        if api not in _ES_APIS and (major, minor) >= (3, 2):
            profile = getattr(self, 'profile', 'compatibility').lower()
            context_pairs.append((
                EGL_CONTEXT_OPENGL_PROFILE_MASK,
                EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT
                if profile == 'core'
                else EGL_CONTEXT_OPENGL_COMPATIBILITY_PROFILE_BIT,
            ))
        context_attrs = _attrib_array(context_pairs)

        context = eglCreateContext(display, config[0], EGL_NO_CONTEXT, context_attrs)
        if context == EGL_NO_CONTEXT:
            self.skipTest(
                'Driver did not provide an EGL %s %d.%d context' % (api, major, minor)
            )

        surface = eglCreatePbufferSurface(
            display, config[0],
            _attrib_array([(EGL_WIDTH, self.width), (EGL_HEIGHT, self.height)]),
        )
        if surface == EGL_NO_SURFACE:
            eglDestroyContext(display, context)
            self.skipTest('Could not create a %dx%d EGL pbuffer' % (self.width, self.height))

        if not eglMakeCurrent(display, surface, surface, context):
            eglDestroySurface(display, surface)
            eglDestroyContext(display, context)
            self.skipTest('eglMakeCurrent failed for the EGL device context')

        self._egl_context = context
        self._egl_surface = surface

    def _swap(self):
        # Offscreen pbuffer: nothing to present.  Tests read back with
        # glReadPixels, which implicitly finishes the pipeline.
        pass

    def _destroy_context(self):
        display = _display
        if display is None:
            return
        eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT)
        if self._egl_surface is not None:
            eglDestroySurface(display, self._egl_surface)
            self._egl_surface = None
        if self._egl_context is not None:
            eglDestroyContext(display, self._egl_context)
            self._egl_context = None
