"""Standalone 2D metrics. No Rhino or third-party dependencies.

Two entry points:
  silhouette_iou(a, b)   - single simple ring each, the original fast path
  region_iou(A, B)       - multi-component shapes with holes

Both require all rings in the SAME coordinate system; no alignment is performed.
Crossing, touching and retracing rings are rejected, not resolved. Coordinates
use ordinary floating-point predicates: normalize extreme-scale/near-degenerate
data first. Raster estimates are not dimension certificates.
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
    if len(set(pts)) != len(pts) or _self_intersects(pts):
        raise ValueError('Repeated, touching, retracing or self-intersecting ring')
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
    if not pts[0]:
        raise ValueError('Empty ring or point')
    if isinstance(pts[0][0], (int, float)):   # a bare ring: [(x, y), ...]
        return [pts]
    return pts                              # already [[(x, y), ...], ...]


def _rings(rings):
    """Largest-area outer ring with strictly internal, disjoint holes.

    Even-odd filling is winding-independent. Nested islands are new components.
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
        if _rings_intersect(out[0],r) or not _is_inside([out[0]],r[0]):
            raise ValueError('Hole must be strictly inside outer boundary')
        if any(_rings_intersect(h,r) or _is_inside([h],r[0]) or _is_inside([r],h[0]) for h in out[1:]):
            raise ValueError('Holes must be disjoint and not nested; islands are separate components')
        out.append(r)
    return out


def _signed_area(poly):
    n = len(poly)
    x0,y0=poly[0]
    return 0.5*sum((poly[i][0]-x0)*(poly[(i+1) % n][1]-y0) - (poly[(i+1) % n][0]-x0)*(poly[i][1]-y0)
                   for i in range(n))


def _is_inside(rings, p):
    """Even-odd fill rule across all rings.

    Ring winding does not affect membership.
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
    """IoU between two shapes, each a list of components.

    shapes_a / shapes_b: [ [ring, ...], ... ] — one entry per connected component.
    A component is a bare ring or a list of rings in any order. The largest
    encloses disjoint holes. Winding does not matter; separate components union.

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
    xs = [p[0] for r in allrings for p in r]
    ys = [p[1] for r in allrings for p in r]
    x0, y0 = min(xs), min(ys)
    dx, dy = (max(xs)-x0)/samples, (max(ys)-y0)/samples
    if not math.isfinite(dx) or not math.isfinite(dy) or min(dx, dy) <= 0:
        raise ValueError('Invalid raster bounds')
    inter = union = 0
    for rr in range(samples):
        py = y0+(rr+0.5)*dy
        a,b=[_region_scanline(s,py,x0,dx,samples) for s in (ra,rb)]
        inter+=sum(x and y for x,y in zip(a,b))
        union+=sum(x or y for x,y in zip(a,b))
    if union == 0:
        raise ValueError('No occupied cells; increase resolution or inspect rings')
    return {'iou': inter/union, 'grid': samples*samples, 'inter': inter, 'union': union,
            'components_a': len(ra), 'components_b': len(rb),
            'cell_size': [dx,dy], 'bounds': [x0,y0,max(xs),max(ys)],
            'note': 'Raster estimate over multi-ring regions. Not depth, dimensions or continuity.'}


def _region_scanline(components,py,x0,dx,width):
    out=bytearray(width)
    for rings in components:
        comp=bytearray(width)
        for ring in rings: comp=bytearray(a^b for a,b in zip(comp,_scanline(ring,py,x0,dx,width)))
        out=bytearray(a|b for a,b in zip(out,comp))
    return out


def _orient(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _segments_intersect(a,b,c,d):
    def on(p,q,r):
        return min(p[0],q[0])<=r[0]<=max(p[0],q[0]) and min(p[1],q[1])<=r[1]<=max(p[1],q[1])
    o1,o2,o3,o4=_orient(a,b,c),_orient(a,b,d),_orient(c,d,a),_orient(c,d,b)
    if ((o1>0 and o2<0) or (o1<0 and o2>0)) and ((o3>0 and o4<0) or (o3<0 and o4>0)): return True
    return ((o1==0 and on(a,b,c)) or (o2==0 and on(a,b,d)) or
            (o3==0 and on(c,d,a)) or (o4==0 and on(c,d,b)))


def _rings_intersect(a,b):
    return any(_segments_intersect(p,a[(i+1)%len(a)],q,b[(j+1)%len(b)])
               for i,p in enumerate(a) for j,q in enumerate(b))


def _self_intersects(ring):
    """Nonadjacent touching/crossing and adjacent collinear retracing test."""
    n = len(ring)
    if n < 4:
        return False

    for i in range(n):
        p1, p2 = ring[i], ring[(i+1) % n]
        p3=ring[(i+2)%n]
        if p1==p2: return True
        if _orient(p1,p2,p3)==0 and (p2[0]-p1[0])*(p3[0]-p2[0])+(p2[1]-p1[1])*(p3[1]-p2[1])<0: return True
        for j in range(i+1, n):
            if j == i or (j+1) % n == i or j == (i+1) % n:
                continue
            p3, p4 = ring[j], ring[(j+1) % n]
            if _segments_intersect(p1, p2, p3, p4):
                return True
    return False
