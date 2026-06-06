#! /usr/bin/env python3
"""Measure desktop-OpenGL entry-point test coverage for this checkout.

Counts the ``gl*`` commands defined per GL version (and per supported extension
module), scans the ``test_*.py`` tests for the commands they call, and reports
coverage.  Run directly for a summary; ``--uncovered`` lists missing per-version
commands, ``--ext`` / ``--ext-uncovered`` report extensions.
"""

import os
import re
import sys
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # repo root holding ``OpenGL``

# All GL version modules, in order.  The platform here tops out at 4.5; 4.6 is
# listed for completeness but is not the coverage target.
_VERSION_GLOB = os.path.join(ROOT, 'OpenGL/raw/GL/VERSION/GL_*.py')

_DEF = re.compile(r'^def (gl[A-Za-z0-9_]+)\(', re.MULTILINE)
_CALL = re.compile(r'\b(gl[A-Z][A-Za-z0-9_]*)\b')


def defined_funcs(path):
    try:
        with open(path) as fh:
            return set(_DEF.findall(fh.read()))
    except IOError:
        return set()


def version_sources():
    out = []
    for path in sorted(
        glob.glob(_VERSION_GLOB),
        key=lambda p: [int(x) for x in os.path.basename(p)[3:-3].split('_')],
    ):
        name = os.path.basename(path)[:-3]  # GL_1_0
        out.append((name, path))
    return out


def called_funcs():
    used = set()
    paths = glob.glob(os.path.join(HERE, 'test_*.py'))
    paths += [os.path.join(HERE, 'gltestcase.py')]
    for path in paths:
        with open(path) as fh:
            used.update(_CALL.findall(fh.read()))
    return used


def level_report():
    used = called_funcs()
    rows = []
    for name, path in version_sources():
        defined = defined_funcs(path)
        rows.append((name, defined, defined & used))
    return used, rows


def extension_report(used):
    path = os.path.join(HERE, 'supported_extensions.json')
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        snap = json.load(fh)['with_funcs']
    total = sorted(set().union(*snap.values())) if snap else []
    covered = [f for f in total if f in used]
    per_ext = [
        (ext, funcs, [f for f in funcs if f in used])
        for ext, funcs in sorted(snap.items())
    ]
    return total, covered, per_ext


def main():
    used, rows = level_report()
    print('%-8s %6s %7s %6s' % ('version', 'total', 'covered', 'pct'))
    tot = cov = 0
    for name, defined, covered in rows:
        pct = (100.0 * len(covered) / len(defined)) if defined else 0.0
        print('%-8s %6d %7d %5.1f%%' % (name, len(defined), len(covered), pct))
        tot += len(defined)
        cov += len(covered)
    print('%-8s %6d %7d %5.1f%%' % ('TOTAL', tot, cov, 100.0 * cov / tot if tot else 0))

    ext = extension_report(used)
    if ext:
        total, covered, per_ext = ext
        pct = (100.0 * len(covered) / len(total)) if total else 0.0
        print(
            '%-8s %6d %7d %5.1f%%  (supported extensions)'
            % ('EXT', len(total), len(covered), pct)
        )
        if '--ext' in sys.argv:
            for name, funcs, c in per_ext:
                print('  %-46s %2d/%2d' % (name, len(c), len(funcs)))

    if '--uncovered' in sys.argv:
        for name, defined, covered in rows:
            missing = sorted(defined - covered)
            if missing:
                print('\n# %s uncovered (%d):' % (name, len(missing)))
                print(' '.join(missing))
    if '--ext-uncovered' in sys.argv and ext:
        for name, funcs, c in ext[2]:
            missing = [f for f in funcs if f not in used]
            if missing:
                print('# %s (%d left): %s' % (name, len(missing), ' '.join(missing)))


if __name__ == '__main__':
    main()
