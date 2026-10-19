"""RhinoCommon in-memory helpers. No mutations or implicit ActiveDoc.

Rhino Python3 required. Removed in 1.0: unverified place_pictureframe command
builder. Use explicit Plane geometry, then a currently verified image tool.
"""
import math
from itertools import permutations
import Rhino
from outline_metrics import silhouette_iou, distance_to_polyline
G = Rhino.Geometry


def _positive(value, name):
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(name + ' must be finite and positive')
    return float(value)


def _degree(value):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 11:
        raise ValueError('degree must be an integer from 1 to 11')
    return value


def _curve(curve):
    if not isinstance(curve, G.Curve) or not curve.IsValid or curve.GetLength() <= 0:
        raise ValueError('Valid nonzero curve required')
    return curve


def _point(p):
    point = G.Point3d(p) if isinstance(p, G.Point3d) else G.Point3d(*p)
    if not point.IsValid:
        raise ValueError('Invalid point')
    return point


def _tolerance(doc, value=None):
    if doc is None:
        raise ValueError('Explicit injected document required')
    return _positive(doc.ModelAbsoluteTolerance if value is None else value, 'tolerance')


def make_curve(doc, points, degree=3, periodic=False):
    """Control-point NURBS. periodic is periodic construction, not a cap."""
    _tolerance(doc)
    degree = _degree(degree)
    pts = [_point(p) for p in points]
    if len(pts) < degree + 1:
        raise ValueError('Insufficient control points')
    return _curve(G.NurbsCurve.Create(bool(periodic), degree, pts))


def interpolate_curve(points, degree=3, style=None):
    degree = _degree(degree)
    pts = [_point(p) for p in points]
    if len(pts) < degree + 1:
        raise ValueError('Insufficient interpolation points')
    if style is None:
        style = G.CurveKnotStyle.Chord
    return _curve(G.Curve.CreateInterpolatedCurve(pts, degree, style))


def rebuild_to_single_span(curve, degree=3, doc=None, max_deviation=None):
    """Open curve candidate checked by Rhino curve-distance estimator.

    Explicit project length budget required. Does not preserve endpoint tangents
    or certify exact Hausdorff distance. Raises on failure or measured excess.
    """
    _curve(curve)
    degree = _degree(degree)
    tol = _tolerance(doc)
    if max_deviation is None:
        raise ValueError('Explicit max_deviation budget required')
    budget = _positive(max_deviation, 'max_deviation')
    if curve.IsClosed:
        raise ValueError('Closed input needs separate seam/periodic strategy')
    result = _curve(curve.Rebuild(degree + 1, degree, False))
    if result.SpanCount != 1:
        raise ValueError('Rebuild did not produce one span')
    check = G.Curve.GetDistancesBetweenCurves(curve, result, min(tol, budget / 10.0))
    if not check[0] or not math.isfinite(check[1]):
        raise ValueError('Curve distance estimation failed')
    if check[1] > budget:
        raise ValueError('Rebuild deviation %.9g exceeds budget %.9g' % (check[1], budget))
    return result


def curve_quality(curve):
    _curve(curve)
    n = curve.ToNurbsCurve()
    return {'degree': n.Degree, 'spans': n.SpanCount,
            'control_points': n.Points.Count, 'rational': n.IsRational,
            'closed': curve.IsClosed, 'periodic': curve.IsPeriodic,
            'length': curve.GetLength()}


def _edge_surface(doc, curves, tol=None):
    """Arrange a closed chain of boundaries without altering caller geometry."""
    tol = _tolerance(doc, tol)
    curves = [_curve(c) for c in curves]
    for order in permutations(range(len(curves))):
        copies = [curves[i].DuplicateCurve() for i in order]
        for i in range(1, len(copies)):
            if copies[i - 1].PointAtEnd.DistanceTo(copies[i].PointAtStart) > tol:
                copies[i].Reverse()
            if copies[i - 1].PointAtEnd.DistanceTo(copies[i].PointAtStart) > tol:
                break
        else:
            if copies[-1].PointAtEnd.DistanceTo(copies[0].PointAtStart) <= tol:
                result = G.Brep.CreateEdgeSurface(copies)
                if result is not None and result.IsValid:
                    return result
    raise ValueError('Cannot form a valid edge surface from the closed chain')


def edge_srf_4(doc, c1, c2, c3, c4, tol=None):
    """Four-edge Brep. Different U/V degrees allowed. No G1/G2 claim."""
    return _edge_surface(doc, [c1, c2, c3, c4], tol)


def edge_srf_3(doc, c1, c2, c3, tol=None):
    """Three boundaries may produce a singular side; inspect before use."""
    return _edge_surface(doc, [c1, c2, c3], tol)


def ruled_2(c1, c2):
    """Caller must align directions and seams."""
    result = G.NurbsSurface.CreateRuledSurface(_curve(c1), _curve(c2))
    if result is None or not result.IsValid:
        raise ValueError('Ruled surface failed')
    return result


def loft_surface(curves, closed=False, cap=False, loft_type=None, tolerance=None):
    """Brep list. closed joins loft ends, not section-curve endpoints.

    Does not auto-reverse sections or move seams. cap requires explicit length
    tolerance and fails rather than silently returning uncapped shells.
    """
    curves = [_curve(c) for c in curves]
    if len(curves) < (3 if closed else 2):
        raise ValueError('Insufficient loft sections')
    if loft_type is None:
        loft_type = G.LoftType.Normal
    result = G.Brep.CreateFromLoft(curves, G.Point3d.Unset, G.Point3d.Unset,
                                 loft_type, bool(closed))
    if not result or any(not b.IsValid for b in result):
        raise ValueError('Loft failed')
    if cap:
        if tolerance is None:
            raise ValueError('Explicit tolerance required for capping')
        tol = _positive(tolerance, 'cap tolerance')
        result = [b.CapPlanarHoles(tol) for b in result]
        if any(b is None or not b.IsValid or not b.IsSolid for b in result):
            raise ValueError('Cannot cap loft into valid solids')
    return list(result)


def surface_spans(brep, face_index=0):
    if not isinstance(brep, G.Brep) or not 0 <= face_index < brep.Faces.Count:
        raise ValueError('Invalid Brep or face index')
    s = brep.Faces[face_index].UnderlyingSurface().ToNurbsSurface()
    return {'u_spans': s.SpanCount(0), 'v_spans': s.SpanCount(1),
            'u_degree': s.Degree(0), 'v_degree': s.Degree(1),
            'u_points': s.Points.CountU, 'v_points': s.Points.CountV}


def surface_curvature(surface, pt):
    """Nearest underlying-surface evaluation, NOT trim-aware or fairness test.

    Signed values follow parameter orientation, not solid outward orientation.
    """
    pt = _point(pt)
    ok, u, v = surface.ClosestPoint(pt)
    if not ok:
        raise ValueError('Surface closest point failed')
    c = surface.CurvatureAt(u, v)
    normal = surface.NormalAt(u, v)
    if c is None or not normal.IsValid or not normal.Unitize():
        raise ValueError('Curvature undefined at singular/invalid point')
    evaluated = surface.PointAt(u, v)
    values = [c.Mean, c.Kappa(0), c.Kappa(1), c.Gaussian]
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Nonfinite curvature')
    return {'point': [evaluated.X, evaluated.Y, evaluated.Z], 'uv': [u, v],
            'projection_gap': evaluated.DistanceTo(pt), 'mean': values[0],
            'k1': values[1], 'k2': values[2], 'gaussian': values[3],
            'normal': [normal.X, normal.Y, normal.Z],
            'note': 'Underlying surface, not trim-aware; not a fairness/G2 test.'}


def pictureframe_points(plane, width, height):
    """Four reference-plane corners in model units; never loads an image."""
    width, height = _positive(width, 'width'), _positive(height, 'height')
    if not isinstance(plane, G.Plane) or not plane.IsValid:
        raise ValueError('Explicit valid image plane required')
    return [plane.PointAt(x, y) for x, y in
            [(0, 0), (width, 0), (width, height), (0, height)]]


def boundary_continuity(doc, curve_a, curve_b, at='end_to_start',
                        tol=None, angle_tolerance_degrees=0.1):
    """Open curve endpoint G0/directed tangent check, NOT surface G1/G2.

    end_to_start tests a then b; start_to_end tests b then a.
    A 180-degree reversal is rejected, not treated as a smooth join.
    """
    tol = _tolerance(doc, tol)
    for curve in [curve_a, curve_b]:
        _curve(curve)
        if curve.IsClosed:
            raise ValueError('Closed curves need an explicit seam strategy')
    if not math.isfinite(angle_tolerance_degrees) or not 0 <= angle_tolerance_degrees < 180:
        raise ValueError('Invalid angle tolerance')
    if at == 'end_to_start':
        p1, p2 = curve_a.PointAtEnd, curve_b.PointAtStart
        t1, t2 = curve_a.TangentAtEnd, curve_b.TangentAtStart
    elif at == 'start_to_end':
        p1, p2 = curve_b.PointAtEnd, curve_a.PointAtStart
        t1, t2 = curve_b.TangentAtEnd, curve_a.TangentAtStart
    else:
        raise ValueError('Unknown endpoint pairing')
    if not t1.IsValid or not t2.IsValid or not t1.Unitize() or not t2.Unitize():
        raise ValueError('Undefined endpoint tangent')
    gap = p1.DistanceTo(p2)
    angle = math.degrees(math.acos(max(-1.0, min(1.0, t1 * t2))))
    return {'gap': gap, 'g0_ok': gap <= tol, 'tangent_angle_deg': angle,
            'g1_candidate': gap <= tol and angle <= angle_tolerance_degrees,
            'g2': 'NOT EVALUATED', 'note': 'Directed curve endpoint check; not surface continuity.'}
