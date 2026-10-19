"""Standalone 2D metrics. No Rhino or third-party dependencies.

Two entry points:
  silhouette_iou(a, b)   - single simple ring each, the original fast path
  region_iou(A, B)       - multi-component shapes with holes

Both require all rings in the SAME coordinate system; no alignment is performed.
Self-intersecting rings are rejected rather than resolved. Raster estimates are
not dimension certificates.
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


def _as_component(shape):
    """Accept either a bare ring or a list of rings, so a single-component
    shape can be passed without extra nesting."""
    pts = list(shape)
    if not pts:
        raise ValueError('Empty shape')
    if isinstance(pts[0][0], (int, float)):   # a bare ring: [(x, y), ...]
        return [pts]
    return pts                              # already [[(x, y), ...], ...]


def _rings(rings):
    """Normalise one component's rings and enforce winding.

    Ring order is meaningful: the largest-|area| ring is the outer boundary,
    the rest are holes and get REVERSED if needed. Two rings wound the same way
    do not describe a hole -- under the even-odd rule the inner one fills solid,
    which silently inflates area. Normalising here removes that trap.
    """
    cleaned = [_ring(r) for r in rings]
    if not cleaned:
        raise ValueError('At least one ring required')
    areas = [abs(_signed_area(r)) for r in cleaned]
    outer = max(range(len(cleaned)), key=lambda i: areas[i])
    out = [cleaned[outer]]
    for i, r in enumerate(cleaned):
        if i == outer:
            continue
        out.append(list(reversed(r)) if _signed_area(r) * _signed_area(cleaned[outer]) > 0 else r)
    return out


def _signed_area(poly):
    n = len(poly)
    return 0.5*sum(poly[i][0]*poly[(i+1) % n][1] - poly[(i+1) % n][0]*poly[i][1]
                   for i in range(n))


def _is_inside(rings, p):
    """Even-odd fill rule across all rings.

    Works for multi-component outlines and for holes, provided the caller has
    oriented rings consistently (outer counter-clockwise, holes clockwise).
    Orientation is auto-detected from signed area, so callers need not care.
    """
    x, y = p
    hits = 0
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]
            x2, y2 = ring[(i+1) % n]
            if (y1 > y) != (y2 > y):
                xin = x1 + (y-y1)*(x2-x1)/(y2-y1)
                if x < xin:
                    hits += 1
    return hits % 2 == 1


def region_iou(shapes_a, shapes_b, samples=400):
    """IoU between two multi-ring shapes. Each shape is a list of rings.

    shapes_a / shapes_b: [ [ring, ...], ... ] — one entry per connected component.
    Rings inside one component may include holes; orientation is auto-detected.

    Raises if the ring sets are self-intersecting: that needs an explicit
    boolean operation, and guessing would silently produce wrong areas.
    """
    if isinstance(samples, bool) or not isinstance(samples, int) or not 16 <= samples <= 4096:
        raise ValueError('samples must be an integer from 16 to 4096')
    if not shapes_a or not shapes_b:
        raise ValueError('Both shapes need at least one component')
    ra = [_rings(_as_component(s)) for s in shapes_a]
    rb = [_rings(_as_component(s)) for s in shapes_b]
    allrings = [r for comp in ra+rb for r in comp]
    for r in allrings:
        if _self_intersects(r):
            raise ValueError('Self-intersecting ring; resolve topology before comparing')
    xs = [p[0] for r in allrings for p in r]
    ys = [p[1] for r in allrings for p in r]
    x0, y0 = min(xs), min(ys)
    dx, dy = (max(xs)-x0)/samples, (max(ys)-y0)/samples
    if not math.isfinite(dx) or not math.isfinite(dy) or min(dx, dy) <= 0:
        raise ValueError('Invalid raster bounds')
    inter = union = 0
    for rr in range(samples):
        py = y0+(rr+0.5)*dy
        for cc in range(samples):
            px = x0+(cc+0.5)*dx
            a = any(_is_inside(comp, (px, py)) for comp in ra)
            b = any(_is_inside(comp, (px, py)) for comp in rb)
            if a or b:
                union += 1
                if a and b:
                    inter += 1
    if union == 0:
        raise ValueError('No occupied cells; increase resolution or inspect rings')
    return {'iou': inter/union, 'grid': samples*samples, 'inter': inter, 'union': union,
            'components_a': len(ra), 'components_b': len(rb),
            'note': 'Raster estimate over multi-ring regions. Not depth, dimensions or continuity.'}


def _self_intersects(ring):
    """O(n^2) proper-crossing test. Adjacent edges may touch at shared vertices."""
    n = len(ring)
    if n < 4:
        return False

    def seg_cross(p1, p2, p3, p4):
        d1x, d1y = p2[0]-p1[0], p2[1]-p1[1]
        d2x, d2y = p4[0]-p3[0], p4[1]-p3[1]
        den = d1x*d2y - d1y*d2x
        if den == 0:
            return None
        ua = ((p3[0]-p1[0])*d2y - (p3[1]-p1[1])*d2x)/den
        ub = ((p3[0]-p1[0])*d1y - (p3[1]-p1[1])*d1x)/den
        if 1e-12 < ua < 1-1e-12 and 1e-12 < ub < 1-1e-12:
            return True
        return None
    for i in range(n):
        p1, p2 = ring[i], ring[(i+1) % n]
        for j in range(i+1, n):
            if j == i or (j+1) % n == i or j == (i+1) % n:
                continue
            p3, p4 = ring[j], ring[(j+1) % n]
            if seg_cross(p1, p2, p3, p4):
                return True
    return False
