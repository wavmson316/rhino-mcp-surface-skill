"""Standalone 2D metrics. No Rhino or third-party dependencies.

Single simple polygon rings in SAME coordinates only. Holes, components and
self-intersections unsupported. Raster estimates are not dimension certificates.
"""
import math


def _ring(points):
    pts = [tuple(float(v) for v in p) for p in points]
    if any(len(p) != 2 or not all(math.isfinite(v) for v in p) for p in pts):
        raise ValueError('Finite 2D points required')
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()
    if len(set(pts)) < 3:
        raise ValueError('At least three distinct polygon vertices required')
    x0, y0 = pts[0]
    area2 = sum((pts[i][0]-x0)*(pts[(i+1) % len(pts)][1]-y0) -
                (pts[(i+1) % len(pts)][0]-x0)*(pts[i][1]-y0)
                for i in range(len(pts)))
    if not math.isfinite(area2) or area2 == 0:
        raise ValueError('Degenerate polygon')
    return pts


def distance_to_polyline(poly, p):
    """Distance to closed polygon boundary, not to filled interior."""
    poly = _ring(poly)
    if len(p) != 2 or not all(math.isfinite(v) for v in p):
        raise ValueError('Finite 2D query point required')
    best = float('inf')
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i+1) % len(poly)]
        dx, dy = x2-x1, y2-y1
        length2 = dx*dx+dy*dy
        t = 0 if length2 == 0 else max(0, min(1, ((p[0]-x1)*dx+(p[1]-y1)*dy)/length2))
        best = min(best, math.hypot(p[0]-(x1+t*dx), p[1]-(y1+t*dy)))
    return best


def _scanline(poly, py, x0, dx, width):
    crossings = []
    for i, (x1, y1) in enumerate(poly):
        x2, y2 = poly[(i+1) % len(poly)]
        if (y1 > py) != (y2 > py):
            crossings.append(x1+(py-y1)*(x2-x1)/(y2-y1))
    crossings.sort()
    if len(crossings) % 2:
        raise ValueError('Invalid polygon scanline')
    row = bytearray(width)
    for i in range(0, len(crossings), 2):
        lo = max(0, min(width, math.ceil((crossings[i]-x0)/dx-0.5)))
        hi = max(0, min(width, math.ceil((crossings[i+1]-x0)/dx-0.5)))
        row[lo:hi] = b'\x01' * max(0, hi-lo)
    return row


def silhouette_iou(curve_a_points, curve_b_points, samples=400, tolerance=0.0):
    """Shared-grid pixel-center fill, no alignment or buffering.

    samples is per bounding-box axis, 16..4096. Narrow features can be missed;
    compare higher resolution. Positive old tolerance buffering is rejected.
    """
    if not math.isfinite(tolerance) or tolerance != 0:
        raise ValueError('Buffering unsupported; compare unbuffered aligned outlines')
    if isinstance(samples, bool) or not isinstance(samples, int) or not 16 <= samples <= 4096:
        raise ValueError('samples must be an integer from 16 to 4096')
    a, b = _ring(curve_a_points), _ring(curve_b_points)
    xs, ys = [p[0] for p in a+b], [p[1] for p in a+b]
    x0, y0 = min(xs), min(ys)
    dx, dy = (max(xs)-x0)/samples, (max(ys)-y0)/samples
    if not math.isfinite(dx) or not math.isfinite(dy) or min(dx, dy) <= 0:
        raise ValueError('Invalid raster bounds')
    inter = union = 0
    for r in range(samples):
        py = y0+(r+0.5)*dy
        ra, rb = _scanline(a, py, x0, dx, samples), _scanline(b, py, x0, dx, samples)
        inter += sum(x and y for x, y in zip(ra, rb))
        union += sum(x or y for x, y in zip(ra, rb))
    if union == 0:
        raise ValueError('No occupied cells; increase resolution or inspect polygons')
    return {'iou': inter/union, 'grid': samples*samples, 'inter': inter, 'union': union,
            'cell_size': [dx, dy], 'bounds': [x0, y0, max(xs), max(ys)],
            'note': 'Raster estimate, single simple rings only. Not depth, dimensions or continuity.'}
