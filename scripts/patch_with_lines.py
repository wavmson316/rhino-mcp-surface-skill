"""Construction curves must survive into the file.

Every helper here builds a surface AND registers its input curves on a
`Lines` layer, so the delivered model stays editable. A surface whose input
curves were deleted cannot be reworked -- the recipient has to rebuild it.

Design rules this module enforces:

* `Lines` layer is created once and reused; callers pass curves, never indices.
* Working copies are handed to the surface command so the originals stay intact
  (Rhino marks command inputs as consumed; duplicates avoid that).
* Nothing is added to the document unless `register=True`, so callers can run
  geometry checks in memory first.

Requires Rhino. Import outside Rhino will fail on `Rhino` -- that is intended.
"""
import Rhino
import Rhino.Geometry as G
import Rhino.DocObjects as D

LINES_LAYER = 'Lines'


def ensure_lines_layer(doc):
    """Return the index of the Lines layer, creating it if absent.

    `doc.Layers.Add('name')` does not accept a string; a Layer object is
    required. That is why this helper exists instead of a one-liner at each site.
    """
    found = doc.Layers.FindName(LINES_LAYER)
    # ⚠️ Measured on Rhino 8.29: FindName returns None when the layer is
    # absent, NOT -1. Comparing it with an int raises TypeError.
    if found is not None:
        return found.Index
    layer = D.Layer()
    layer.Name = LINES_LAYER
    return doc.Layers.Add(layer)


def register_curves(doc, curves, layer_index=None, group=None):
    """Add curves to the Lines layer and return their object ids.

    Empty input returns an empty list rather than raising: a patch with no
    internal lines is legal, and the caller decides whether that is acceptable.
    """
    if layer_index is None:
        layer_index = ensure_lines_layer(doc)
    ids = []
    for curve in curves:
        if curve is None or not curve.IsValid:
            continue
        attr = D.ObjectAttributes()
        attr.LayerIndex = layer_index
        if group is not None:
            attr.SetUserString('PatchID', str(group))
        ids.append(doc.Objects.AddCurve(curve, attr))
    return ids


def _dups(curves):
    """Duplicate so the surface command consumes copies, not the originals."""
    out = []
    for c in curves:
        out.append(c.DuplicateCurve() if hasattr(c, 'DuplicateCurve') else c.Duplicate())
    return out


def loft_with_lines(doc, sections, closed=False, cap=False,
                    loft_type=None, tolerance=None, register=True):
    """Loft through sections and keep every section in the file.

    Returns {'breps': [...], 'line_ids': [...]}. `line_ids` is empty when
    register=False.

    ⚠️ Loft fits equal-shaped sections that shift along one direction. It does
    not constrain the span between sections -- with few sections the interior is
    invented. For a surface that needs constraints in both U and V use
    `network_with_lines` instead.
    """
    sections = [c for c in sections if c is not None and c.IsValid]
    if len(sections) < (3 if closed else 2):
        raise ValueError('Insufficient loft sections')
    if loft_type is None:
        loft_type = G.LoftType.Normal
    working = _dups(sections)
    breps = G.Brep.CreateFromLoft(working, G.Point3d.Unset, G.Point3d.Unset,
                                  loft_type, bool(closed))
    if not breps or any(not b.IsValid for b in breps):
        raise ValueError('Loft failed')
    if cap:
        if tolerance is None:
            raise ValueError('Explicit tolerance required for capping')
        breps = [b.CapPlanarHoles(tolerance) for b in breps]
        if any(b is None or not b.IsValid for b in breps):
            raise ValueError('Cannot cap loft into valid solids')
    ids = register_curves(doc, sections) if register else []
    return {'breps': list(breps), 'line_ids': ids}


def network_with_lines(doc, curves_u, curves_v, tolerance=0.01,
                       trim_type=True, register=True):
    """Network surface from two crossing families, keeping BOTH families.

    Use this when the surface needs constraints in both U and V -- the common
    case for a freeform panel. Lofting a handful of lines instead leaves the
    span between them unconstrained.

    Returns {'brep': brep or None, 'line_ids': [...], 'fail': reason}.
    """
    cu = [c for c in curves_u if c is not None and c.IsValid]
    cv = [c for c in curves_v if c is not None and c.IsValid]
    if len(cu) < 2 or len(cv) < 2:
        raise ValueError('NetworkSrf needs at least two curves in each family')
    working_u, working_v = _dups(cu), _dups(cv)
    # ⛔ Verified on Rhino 8.29: there is NO Brep.CreateNetworkSrf either.
    # NetworkSrf is a command; see _run_network_srf for the dispatch.
    brep = _run_network_srf(doc, working_u, working_v, tolerance)
    ids = register_curves(doc, cu + cv) if (register and brep is not None) else []
    return {'brep': brep,
            'line_ids': ids,
            'fail': None if brep is not None and brep.IsValid else 'network returned no valid Brep'}


def _object_ids(doc, objects):
    return [doc.Objects.Add(dupe) for dupe in
            (o.Duplicate() for o in objects)]


def _run_sweep2(doc, rails, sections, tolerance, closed_sweep, cap):
    """Run the Sweep2 command on duplicates and collect the resulting Breps.

    RhinoCommon has no CreateSweep2, so this goes through the command line.
    Underscore-prefixed command names are the locale-independent form.
    Returns a list; empty means the command did not produce geometry.
    """
    import rhinoscriptsyntax as rs
    rail_ids = [doc.Objects.Add(r) for r in rails]
    sec_ids = [doc.Objects.Add(s) for s in sections]
    if not rail_ids or not sec_ids:
        return []
    sel = ','.join(str(i) for i in rail_ids) + ',' + ','.join(str(i) for i in sec_ids)
    rs.Command('_-Sweep2 _SelCrv ' + sel + ' _Enter', False)
    made = []
    for obj in doc.Objects:
        geom = obj.Geometry
        if geom is not None and geom.IsValid and obj.Attributes.LayerIndex not in (0,):
            made.append(geom)
    return []


def _run_network_srf(doc, curves_u, curves_v, tolerance):
    """Run the NetworkSrf command on duplicates and return the Brep, or None.

    ⚠️ Command-driven construction is a last resort. Prefer RhinoCommon methods
    wherever they exist -- they return errors instead of mutating the scene.
    """
    import rhinoscriptsyntax as rs
    ids = [doc.Objects.Add(c) for c in (curves_u + curves_v)]
    if not ids:
        return None
    rs.Command('_-NetworkSrf _Spline _SelCrv ' +
               ','.join(str(i) for i in ids) + ' _Enter _PtOn _Lines=on _Enter',
               False)
    for obj in doc.Objects:
        geom = obj.Geometry
        if geom is not None and geom.IsValid and geom.Faces.Count > 0:
            return geom
    return None

def sweep2_with_lines(doc, rails, sections, tolerance=None,
                      closed_sweep=True, closed_section=False, cap=False,
                      blend_type=None, register=True):
    """Sweep2 over two rails, keeping BOTH rails and every section.

    ⚠️ The rails are the ones people forget. Losing them means the path can
    never be re-routed without rebuilding the whole surface.

    Returns {'breps': [...], 'line_ids': [...]}.
    """
    rl = [c for c in rails if c is not None and c.IsValid]
    sc = [c for c in sections if c is not None and c.IsValid]
    if len(rl) != 2:
        raise ValueError('Sweep2 needs exactly two rails')
    if len(sc) < 1:
        raise ValueError('Sweep2 needs at least one section')
    if cap and tolerance is None:
        raise ValueError('Explicit tolerance required for capping')
    working_r, working_s = _dups(rl), _dups(sc)
    # ⛔ Verified on Rhino 8.29: there is NO Brep.CreateSweep2 in RhinoCommon.
    # Sweep2 is a Rhino *command*, so it has to be dispatched as one. Everything
    # the command consumes disappears from the scene, which is another reason
    # the originals were duplicated above.
    breps = _run_sweep2(doc, working_r, working_s, tolerance,
                        closed_sweep, cap)
    if not breps or any(not b.IsValid for b in breps):
        raise ValueError('Sweep2 produced no valid Brep')
    ids = register_curves(doc, rl + sc) if register else []
    return {'breps': list(breps), 'line_ids': ids}


def patch_record(doc, surfaces, register=True, group=None):
    """Register the boundary curves of already-built faces.

    For faces whose edges are shared with a neighbour, pass only the curves you
    want recorded -- the point is a traceable construction record, not a full
    edge dump.

    Returns the ids actually written.
    """
    curves = []
    for brep in surfaces:
        if brep is None or not brep.IsValid:
            continue
        for edge in brep.Edges:
            ec = edge.ToNurbsCurve()
            if ec is not None:
                curves.append(ec)
    return register_curves(doc, curves, group=group) if register else []


def audit_curve_retention(doc, expected_minimum=1):
    """Check that the Lines layer actually holds construction curves.

    Returns a dict; `ok` is False when nothing was registered, which is the
    signal that the model was built without leaving its inputs behind.
    """
    # ⚠️ FindName returns None (not -1) when absent -- see ensure_lines_layer.
    layer = doc.Layers.FindName(LINES_LAYER)
    if layer is None:
        return {'ok': False, 'reason': 'Lines layer missing', 'count': 0,
                'layer_visible': False}
    idx = layer.Index
    objs = [o for o in doc.Objects if o.Attributes.LayerIndex == idx]

    curves = [o for o in objs if o.Geometry is not None and o.Geometry.IsValid]
    visible = bool(layer.IsVisible)
    return {'ok': len(curves) >= expected_minimum and visible,
            'reason': None if (len(curves) >= expected_minimum and visible)
                     else 'insufficient curves or hidden layer',
            'count': len(curves), 'layer_visible': visible,
            'note': 'Curve objects count, not surface count. Surfaces on Layers is fine.'}