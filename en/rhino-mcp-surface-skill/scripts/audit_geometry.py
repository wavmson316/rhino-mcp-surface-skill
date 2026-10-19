"""Read-only RhinoCommon structure audit. No continuity/solid requirement inferred."""
import Rhino
import System

def audit_geometry(geometry):
    g = geometry
    if g is None:
        raise ValueError("Geometry is required")
    result = {"type": g.GetType().Name, "valid": bool(g.IsValid)}
    if not g.IsValid:
        result["error"] = "Invalid geometry; further audit not performed"
        return result
    if isinstance(g, Rhino.Geometry.Curve):
        n = g.ToNurbsCurve()
        result.update(degree=n.Degree, spans=n.SpanCount,
                      control_points=n.Points.Count, rational=n.IsRational,
                      closed=g.IsClosed, periodic=g.IsPeriodic, length=g.GetLength())
        return result
    if isinstance(g, Rhino.Geometry.Extrusion):
        g = g.ToBrep()
    elif isinstance(g, Rhino.Geometry.Surface):
        g = g.ToBrep()
    if not isinstance(g, Rhino.Geometry.Brep):
        result["note"] = "Not a NURBS curve/surface/Brep; no surface audit performed."
        return result
    result.update(solid=g.IsSolid, orientation=str(g.SolidOrientation),
                  face_count=g.Faces.Count,
                  naked_edges=sum(e.Valence == Rhino.Geometry.EdgeAdjacency.Naked for e in g.Edges),
                  nonmanifold_edges=sum(e.Valence == Rhino.Geometry.EdgeAdjacency.NonManifold for e in g.Edges))
    result["faces"] = []
    for face in g.Faces:
        s = face.UnderlyingSurface()
        n = s.ToNurbsSurface()
        result["faces"].append({
            "index": face.FaceIndex,
            "degree": [n.Degree(0), n.Degree(1)],
            "spans": [n.SpanCount(0), n.SpanCount(1)],
            "control_points": [n.Points.CountU, n.Points.CountV],
            "singular_sides": [i for i in range(4) if s.IsSingular(i)],
            "reversed": face.OrientationIsReversed,
            "trim_loops": face.Loops.Count})
    result["continuity"] = "not evaluated"
    return result

def audit_ids(doc, ids):
    if doc is None:
        raise ValueError("An explicit injected document is required")
    out = {"units": str(doc.ModelUnitSystem),
           "absolute_tolerance": doc.ModelAbsoluteTolerance,
           "angle_tolerance_degrees": doc.ModelAngleToleranceDegrees,
           "objects": []}
    for object_id in ids:
        obj = doc.Objects.FindId(System.Guid(str(object_id)))
        if obj is None:
            out["objects"].append({"id": str(object_id), "error": "not found"})
            continue
        r = audit_geometry(obj.Geometry)
        r.update(id=str(obj.Id), name=obj.Attributes.Name,
                 layer_index=obj.Attributes.LayerIndex)
        out["objects"].append(r)
    return out
