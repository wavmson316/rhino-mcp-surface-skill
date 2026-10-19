"""Release gate: fail on encoding damage and bilingual drift.

Both problems showed up repeatedly in this package:
* U+FFFD replacement characters introduced while editing Chinese prose
* the English tree silently missing content the Chinese tree has

This runs in `check_release.py` so a damaged file cannot be published.
"""
import glob
import io
import os
import sys

REPLACEMENT = chr(0xFFFD)   # kept as a code point so this file is clean
SKIP_DIRS = {'.git', '__pycache__'}


def scan_replacement_chars(root):
    """Return {relative_path: count} for every file containing U+FFFD."""
    bad = {}
    for path in walk(root):
        if not path.endswith(('.md', '.json', '.py')):
            continue
        try:
            text = io.open(path, encoding='utf-8').read()
        except (UnicodeDecodeError, IOError) as exc:
            bad[rel(path, root)] = 'unreadable: %s' % exc
            continue
        n = text.count(REPLACEMENT)
        if n:
            bad[rel(path, root)] = n
    return bad


def scan_bilingual_drift(root):
    """Report reference files present in the Chinese tree but not the English one."""
    cn_dir = os.path.join(root, 'references')
    en_dir = os.path.join(root, 'en', 'rhino-mcp-surface-skill', 'references')
    if not (os.path.isdir(cn_dir) and os.path.isdir(en_dir)):
        return {}
    cn = {os.path.basename(p) for p in glob.glob(os.path.join(cn_dir, '*.md'))}
    en = {os.path.basename(p) for p in glob.glob(os.path.join(en_dir, '*.md'))}
    return {'missing_in_en': sorted(cn - en)}


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield os.path.join(dirpath, name)


def rel(path, root):
    return os.path.relpath(path, root).replace('\\', '/')


def run(root='.'):
    result = {'replacement_chars': scan_replacement_chars(root),
              'bilingual': scan_bilingual_drift(root),
              'ok': True, 'errors': []}
    for path, info in result['replacement_chars'].items():
        result['errors'].append('%s contains %s U+FFFD' % (path, info))
    for name in result['bilingual'].get('missing_in_en', []):
        result['errors'].append('%s exists in references/ but not in en/' % name)
    result['ok'] = not result['errors']
    return result


if __name__ == '__main__':
    out = run(sys.argv[1] if len(sys.argv) > 1 else '.')
    print(out)
    sys.exit(0 if out['ok'] else 1)