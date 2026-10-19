"""Executable construction example: a crowned rectangular product enclosure.

Scope: editable parent/blockout stage, six faces, intentional G0 shoulder edges.
This is NOT a mouse reconstruction, G2 blend, offset-thickness or molded design.
All construction is in memory; no active document, scene, layers or units edited.
"""
import math
import Rhino
from audit_geometry import audit_geometry

G = Rhino.Geometry


def build_shell(doc, length=120.0, width=70.0, height=40.0, shoulder_height=10.0):
    if doc is None:
        raise ValueError('Explicit document required')
    values = [length, width, height, shoulder_height, doc.ModelAbsoluteTolerance]
    if any(not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('Dimensions and tolerance must be finite and positive')
    if height <= shoulder_height:
        raise ValueError('Crown height must exceed shoulder height')
    tol = doc.ModelAbsoluteTolerance
    if min(length, width, shoulder_height, height-shoulder_height) <= 10*tol:
        raise ValueError('Example dimensions too close to document tolerance')

    # P01: U follows length; V follows width. 4x5 CP, degree3x4, one span each.
    # z = shoulder + amplitude * cubic(U) * quartic(V).
    # Bernstein control coefficients [0,1,1,0] and [0,1,1,1,0] peak at
    # 3/4 and 7/8 respectively at normalized parameter 1/2. Thus the actual
    # surface crown (not the control hull) equals the requested height.
    surface = G.NurbsSurface.Create(3, False, 4, 5, 4, 5)
    surface.KnotsU.CreateUniformKnots(1.0)
    surface.KnotsV.CreateUniformKnots(1.0)
    amplitude = (height-shoulder_height)/(0.75*0.875)
    au, bv = [0,1,1,0], [0,1,1,1,0]
    for i in range(4):
        for j in range(5):
            surface.Points.SetPoint(i,j,G.Point3d(
                length*i/3.0, width*(j/4.0-0.5),
                shoulder_height+amplitude*au[i]*bv[j]))
    top = surface.ToBrep()
    if not top.IsValid:
        raise ValueError('Invalid crowned parent surface')
    patches = [('P01_CrownedTop',top)]
    planar_edges = []
    projection = G.Transform.PlanarProjection(G.Plane.WorldXY)
    # P02-P05: derive walls from the SAME parent boundary, avoiding redraw drift.
    for index, edge in enumerate(top.Edges):
        upper = edge.DuplicateCurve()
        lower = upper.DuplicateCurve()
        if not lower.Transform(projection):
            raise ValueError('Boundary projection failed')
        wall = G.NurbsSurface.CreateRuledSurface(upper,lower).ToBrep()
        if not wall.IsValid:
            raise ValueError('Invalid wall')
        patches.append(('P%02d_Wall'%(index+2),wall))
        planar_edges.append(lower)
    loops = G.Curve.JoinCurves(planar_edges,tol)
    if len(loops)!=1 or not loops[0].IsClosed:
        raise ValueError('Bottom boundary is not one closed loop')
    bottoms = G.Brep.CreatePlanarBreps(loops[0],tol)
    if not bottoms or len(bottoms)!=1:
        raise ValueError('Planar bottom construction failed')
    patches.append(('P06_Bottom',bottoms[0]))
    joined = G.Brep.JoinBreps([b for _,b in patches],tol)
    if not joined or len(joined)!=1 or not joined[0].IsValid or not joined[0].IsSolid:
        raise ValueError('Parent faces did not join into one valid solid')
    solid = joined[0]
    if solid.SolidOrientation == G.BrepSolidOrientation.Inward:
        solid.Flip()
    return {'solid':solid,'patches':patches,'top_surface':surface,
            'parameters':{'length':length,'width':width,'height':height,
                          'shoulder_height':shoulder_height,
                          'units':str(doc.ModelUnitSystem)},
            'intended_continuity':'G0 at shoulder/base; no G2 or wall thickness claim'}


def run_example_tests(doc):
    state = lambda:(doc.Objects.Count,str(doc.ModelUnitSystem),
                   doc.ModelAbsoluteTolerance,doc.ModelAngleToleranceDegrees)
    before = state()
    result = build_shell(doc)
    s, body = result['top_surface'], result['solid']
    center = s.PointAt(s.Domain(0).Mid,s.Domain(1).Mid)
    facts = audit_geometry(body)
    expected = {
        'six_named_parent_patches':len(result['patches'])==6,
        'one_valid_closed_solid':body.IsValid and body.IsSolid,
        'six_joined_faces':body.Faces.Count==6,
        'zero_naked_edges':facts['naked_edges']==0,
        'zero_nonmanifold_edges':facts['nonmanifold_edges']==0,
        'outward_orientation':body.SolidOrientation==G.BrepSolidOrientation.Outward,
        'one_span_each_direction':s.SpanCount(0)==1 and s.SpanCount(1)==1,
        'degree_3_by_4':s.Degree(0)==3 and s.Degree(1)==4,
        'actual_center_crown_40':abs(center.Z-40)<1e-9,
        'positive_volume':G.VolumeMassProperties.Compute(body).Volume>0,
    }
    invalid_rejected=False
    try:build_shell(doc,height=5,shoulder_height=10)
    except ValueError:invalid_rejected=True
    expected['invalid_dimensions_rejected']=invalid_rejected
    expected['document_unchanged']=state()==before
    if not all(expected.values()):
        raise AssertionError(str(expected))
    return {'passed':sum(expected.values()),'total':len(expected),'cases':expected,
            'parameters':result['parameters'],'face_count':body.Faces.Count,
            'actual_crown_point':[center.X,center.Y,center.Z],
            'limitations':result['intended_continuity'],
            'reference_image_reconstruction':'NOT TESTED'}
