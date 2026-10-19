"""Tests for multi-ring silhouette comparison (region_iou).

Every expected value is derived analytically from areas, so a failure means the
geometry code changed behaviour — not that the expectation drifted.
No Rhino or third-party dependency.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outline_metrics import region_iou, _signed_area  # noqa: E402


def sq(x0, y0, s):
    return [(x0, y0), (x0+s, y0), (x0+s, y0+s), (x0, y0+s)]


def circle(r, n=200):
    return [(r*math.cos(2*math.pi*i/n), r*math.sin(2*math.pi*i/n)) for i in range(n)]


CASES = []
FAILED = []


def expect(name, shapes_a, shapes_b, theory, tol=0.02):
    try:
        got = region_iou(shapes_a, shapes_b)['iou']
    except Exception as exc:                                    # noqa: BLE001
        CASES.append(name)
        FAILED.append((name, 'raised %s: %s' % (type(exc).__name__, exc)))
        return
    CASES.append(name)
    if abs(got - theory) > tol:
        FAILED.append((name, 'got %.4f expected %.4f' % (got, theory)))


def expect_reject(name, fn):
    CASES.append(name)
    try:
        fn()
    except ValueError:
        return
    except Exception as exc:                                    # noqa: BLE001
        FAILED.append((name, 'raised %s not ValueError: %s' % (type(exc).__name__, exc)))
        return
    FAILED.append((name, 'accepted invalid input'))


def run():
    R10, R6 = circle(10), circle(6)
    a10, a6 = abs(_signed_area(R10)), abs(_signed_area(R6))
    ring = a10 - a6
    o = sq(0, 0, 10)

    expect('single ring identical', [o], [o], 1.0)
    expect('annulus identical', [[R10, R6]], [[R10, R6]], 1.0)
    expect('annulus vs filled disc', [[R10, R6]], [R10], ring/a10)
    expect('annulus vs inner disc (disjoint)', [[R10, R6]], [R6], 0.0)
    expect('one square hole vs filled', [[o, sq(3, 3, 4)]], [o], 84/100)
    expect('two square holes vs filled', [[o, sq(1, 1, 2), sq(7, 7, 2)]], [o], 92/100)
    expect('two components vs one', [o, sq(15, 0, 10)], [o], 0.5)
    expect('square vs centred small square', [o], [sq(3, 3, 4)], 16/100)

    bow = [(0, 0), (10, 10), (10, 0), (0, 10)]
    degenerate = [(0, 0), (1, 1), (2, 2)]
    expect_reject('self-intersecting ring', lambda: region_iou([[bow]], [o]))
    expect_reject('empty shape list', lambda: region_iou([], [o]))
    expect_reject('resolution too low', lambda: region_iou([o], [o], samples=5))
    expect_reject('resolution too high', lambda: region_iou([o], [o], samples=99999))
    expect_reject('degenerate ring', lambda: region_iou([[degenerate]], [o]))

    return {'passed': len(CASES)-len(FAILED), 'total': len(CASES),
            'failed': [{'case': n, 'reason': r} for n, r in FAILED],
            'cases': CASES,
            'scope': 'Analytic area cases on simple multi-ring regions. '
                     'Raster estimate; self-intersections are rejected, not resolved.'}


if __name__ == '__main__':
    result = run()
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(1 if result['failed'] else 0)
