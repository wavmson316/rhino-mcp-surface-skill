"""Bidirectional sampled edge gap and face normal diagnostics, NOT G2 certification.
Call sample_seam(brep_a, edge_a, face_a, brep_b, edge_b, face_b,
                 distance_tolerance, angle_tolerance_degrees, samples=41).
Face indices are explicit, especially for edges shared by multiple faces.
Normal angle is unoriented (tangent planes); overlap/fold checks remain required.

Runtime requirement: this module imports only `math`, so it CAN be imported
outside Rhino. That is deliberate -- it accepts any object exposing the
RhinoCommon surface it needs (duck typing), which is what makes it unit-testable
with fakes. It still REQUIRES real RhinoCommon geometry to produce meaningful
numbers; passing plain data fails inside the geometry calls, not at import.
"""
import math

def _angle(a, b):
    if not a.Unitize() or not b.Unitize():
        raise ValueError("Degenerate face normal")
    return math.degrees(math.acos(min(1.0, max(0.0, abs(a * b)))))

def _normal(face, point):
    ok, u, v = face.ClosestPoint(point)
    if not ok:
        raise ValueError("Face closest-point failed")
    return face.NormalAt(u, v)

def _pass(source, edge_i, face_i, target, edge_j, face_j, count):
    for brep, ei, fi in ((source, edge_i, face_i), (target, edge_j, face_j)):
        if brep is None or not brep.IsValid:
            raise ValueError("Valid Brep required")
        if (isinstance(ei, bool) or not isinstance(ei, int) or not 0 <= ei < brep.Edges.Count or
                isinstance(fi, bool) or not isinstance(fi, int) or not 0 <= fi < brep.Faces.Count):
            raise ValueError("Invalid edge or face index")
    edge, other = source.Edges[edge_i], target.Edges[edge_j]
    if edge.IsClosed or other.IsClosed:
        raise ValueError("Closed edges require an explicit seam-aware pairing strategy")
    face, other_face = source.Faces[face_i], target.Faces[face_j]
    if face_i not in list(edge.AdjacentFaces()) or face_j not in list(other.AdjacentFaces()):
        raise ValueError("Selected face is not adjacent to selected edge")
    rows = []
    for i in range(count):
        f = i / float(count - 1)
        point = edge.PointAt(edge.Domain.ParameterAt(f))
        ok, t = other.ClosestPoint(point)
        if not ok:
            raise ValueError("Edge closest-point failed at sample %s" % i)
        paired = other.PointAt(t)
        rows.append({"fraction": f, "gap": point.DistanceTo(paired),
                     "normal_angle_degrees": _angle(_normal(face, point), _normal(other_face, paired)),
                     "paired_fraction": other.Domain.NormalizedParameterAt(t)})
    seq = [r["paired_fraction"] for r in rows]
    monotone = (all(seq[i+1] >= seq[i]-1e-9 for i in range(count-1)) or
                all(seq[i+1] <= seq[i]+1e-9 for i in range(count-1)))
    coverage = max(seq) - min(seq)
    return {"rows": rows, "monotone": monotone, "parameter_coverage": coverage}

def sample_seam(a, edge_a, face_a, b, edge_b, face_b,
                distance_tolerance, angle_tolerance_degrees, samples=41):
    if (isinstance(samples, bool) or not isinstance(samples, int) or not 3 <= samples <= 10001 or
            not math.isfinite(distance_tolerance) or distance_tolerance <= 0 or
            not math.isfinite(angle_tolerance_degrees) or not 0 <= angle_tolerance_degrees < 90):
        raise ValueError("Invalid sampling or tolerances")
    forward = _pass(a, edge_a, face_a, b, edge_b, face_b, samples)
    reverse = _pass(b, edge_b, face_b, a, edge_a, face_a, samples)
    rows = forward["rows"] + reverse["rows"]
    gap = max(r["gap"] for r in rows)
    angle = max(r["normal_angle_degrees"] for r in rows)
    paired = all(p["monotone"] and p["parameter_coverage"] >= 0.999 for p in (forward, reverse))
    return {"sampled_max_gap": gap, "sampled_max_normal_angle_degrees": angle,
            "sampled_g0_within_tolerance": paired and gap <= distance_tolerance,
            "sampled_tangent_planes_within_tolerance": paired and gap <= distance_tolerance and angle <= angle_tolerance_degrees,
            "pairing_checks_passed": paired, "forward": forward, "reverse": reverse,
            "g2": "NOT EVALUATED",
            "limitations": "Finite uniform parameter sampling; verify knots/corners, overlap, side orientation and reflection separately."}
