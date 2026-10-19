"""Rhino Python3 regression suite. All geometry stays in memory.

Call run_tests(injected_doc). Raises on any failed test; prints no fake success.
"""
import json
import math
import Rhino
import System
import nbs_geometry as N
from audit_geometry import audit_geometry, audit_ids
from sample_seam_g1 import sample_seam

G = Rhino.Geometry


def run_tests(doc):
    if doc is None:
        raise ValueError('Explicit document required')
    state = lambda: (doc.Objects.Count, str(doc.ModelUnitSystem),
                     doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
    before = state()
    rows = []

    def test(name, action):
        try:
            if not action():
                raise AssertionError('Predicate failed')
            rows.append({'case': name, 'passed': True})
        except Exception as e:
            rows.append({'case': name, 'passed': False,
                         'error': type(e).__name__ + ': ' + str(e)})

    def rejects(action):
        try:
            action()
        except ValueError:
            return True
        return False

    def face(points):
        return G.NurbsSurface.CreateFromCorners(*[G.Point3d(*p) for p in points]).ToBrep()

    def edge(brep, p):
        p = G.Point3d(*p)
        return min(range(brep.Edges.Count), key=lambda i:
                   brep.Edges[i].PointAt(brep.Edges[i].Domain.Mid).DistanceTo(p))

    a = face([(0,0,0),(10,0,0),(10,10,0),(0,10,0)])
    b = face([(0,0,0),(10,0,0),(10,-10,0),(0,-10,0)])
    fold = face([(0,0,0),(10,0,0),(10,0,10),(0,0,10)])
    gap = face([(0,0,1),(10,0,1),(10,-10,1),(0,-10,1)])
    ea, eb, ef, eg = [edge(x,(5,0,z)) for x,z in [(a,0),(b,0),(fold,0),(gap,1)]]
    seam = lambda target, e: sample_seam(a,ea,0,target,e,0,0.01,0.1)
    test('coplanar sampled seam', lambda: seam(b,eb)['sampled_tangent_planes_within_tolerance'])
    test('same edge ninety degree fold rejected', lambda:
         seam(fold,ef)['sampled_g0_within_tolerance'] and
         not seam(fold,ef)['sampled_tangent_planes_within_tolerance'])
    test('one unit seam gap rejected', lambda: not seam(gap,eg)['sampled_g0_within_tolerance'])
    test('nonfinite seam tolerance rejected', lambda: rejects(lambda:
         sample_seam(a,ea,0,b,eb,0,float('nan'),0.1)))
    test('negative edge index rejected', lambda: rejects(lambda:
         sample_seam(a,-1,0,b,eb,0,0.01,0.1)))
    test('fractional sample count rejected', lambda: rejects(lambda:
         sample_seam(a,ea,0,b,eb,0,0.01,0.1,3.5)))
    facts = audit_geometry(a)
    test('open valid face has four naked edges', lambda:
         facts['valid'] and not facts['solid'] and facts['naked_edges']==4)
    test('single span per surface direction', lambda: facts['faces'][0]['spans']==[1,1])
    c = N.make_curve(doc, [(0,0,0),(1,0,0),(2,1,0),(3,1,0)], 3)
    test('make control curve', lambda: c.IsValid and c.SpanCount==1 and c.Points.Count==4)
    c.Knots.InsertKnot(c.Domain.Mid,2)
    test('repeated knot span counterexample', lambda:
         c.SpanCount==2 and c.Points.Count-c.Degree!=c.SpanCount and
         audit_geometry(c)['spans']==2)
    test('explicit doc ID audit missing object', lambda:
         audit_ids(doc,[System.Guid.Empty])['objects'][0]['error']=='not found')
    line = G.LineCurve(G.Point3d.Origin,G.Point3d(10,0,0))
    next_line = G.LineCurve(G.Point3d(10,0,0),G.Point3d(20,0,0))
    ninety = G.LineCurve(G.Point3d(10,0,0),G.Point3d(10,10,0))
    back = G.LineCurve(G.Point3d(10,0,0),G.Point3d(0,0,0))
    apart = G.LineCurve(G.Point3d(11,0,0),G.Point3d(20,0,0))
    test('directed endpoint G1', lambda: N.boundary_continuity(doc,line,next_line)['g1_candidate'])
    test('ninety degree curve correctly rejected', lambda:
         not N.boundary_continuity(doc,line,ninety)['g1_candidate'] and
         abs(N.boundary_continuity(doc,line,ninety)['tangent_angle_deg']-90)<1e-8)
    test('reverse tangent rejected', lambda:
         not N.boundary_continuity(doc,line,back)['g1_candidate'])
    test('parallel disconnected curves rejected', lambda:
         not N.boundary_continuity(doc,line,apart)['g1_candidate'])
    test('alternate endpoint pairing', lambda:
         N.boundary_continuity(doc,next_line,line,at='start_to_end')['g1_candidate'])
    test('unknown endpoint pairing rejected', lambda: rejects(lambda:
         N.boundary_continuity(doc,line,next_line,at='other')))
    test('single span rebuild with budget', lambda:
         N.rebuild_to_single_span(line,3,doc,0.001).SpanCount==1)
    test('missing rebuild budget rejected', lambda: rejects(lambda:
         N.rebuild_to_single_span(line,3,doc)))
    zig = G.PolylineCurve([G.Point3d(i,10*(i%2),0) for i in range(9)])
    test('underfit rebuild rejected', lambda: rejects(lambda:
         N.rebuild_to_single_span(zig,1,doc,0.001)))
    circle = G.Circle(G.Point3d.Origin,10).ToNurbsCurve()
    test('closed rebuild rejected', lambda: rejects(lambda:
         N.rebuild_to_single_span(circle,3,doc,0.1)))
    test('closed curve endpoint shortcut rejected', lambda: rejects(lambda:
         N.boundary_continuity(doc,circle,circle)))
    test('exact circle internal knots geometrically tangent', lambda:
         all(circle.IsContinuous(G.Continuity.G1_continuous,circle.Domain.ParameterAt(f))
             for f in [0.25,0.5,0.75]))
    original = circle.DuplicateCurve()
    ok = circle.IncreaseDegree(5)
    test('exact degree elevation preserves geometry', lambda:
         ok and circle.Degree==5 and max(original.PointAt(original.Domain.ParameterAt(i/100.)).
         DistanceTo(circle.PointAt(circle.Domain.ParameterAt(i/100.))) for i in range(101))<1e-10)
    test('curve quality real properties', lambda:
         N.curve_quality(circle)['spans']==4 and N.curve_quality(circle)['rational'])
    pts = [(0,0,0),(1,1,0),(2,1,0),(3,0,0)]
    test('interpolated curve', lambda: N.interpolate_curve(pts).IsValid)
    test('too few control points rejected', lambda: rejects(lambda:N.make_curve(doc,pts[:2],3)))
    other = G.LineCurve(G.Point3d(0,10,0),G.Point3d(10,10,0))
    right = G.LineCurve(line.PointAtEnd,other.PointAtEnd)
    left = G.LineCurve(other.PointAtStart,line.PointAtStart)
    test('four edge surface shuffled directions', lambda:
         N.edge_srf_4(doc,other,left,line,right).IsValid)
    high = line.ToNurbsCurve(); high.IncreaseDegree(3)
    test('different degree boundaries permitted', lambda:
         N.edge_srf_4(doc,high,right,other,left).IsValid)
    triangle = [G.LineCurve(G.Point3d(*p),G.Point3d(*q)) for p,q in
                [((0,0,0),(10,0,0)),((10,0,0),(0,10,0)),((0,10,0),(0,0,0))]]
    test('three edge surface', lambda:N.edge_srf_3(doc,*triangle).IsValid)
    test('disconnected boundary rejected', lambda:rejects(lambda:
         N.edge_srf_4(doc,line,right,other,apart)))
    test('ruled surface', lambda:N.ruled_2(line,other).IsValid)
    test('loft open sections', lambda:all(x.IsValid for x in N.loft_surface([line,other])))
    cc = [G.Circle(G.Point3d(0,0,z),10).ToNurbsCurve() for z in [0,10]]
    test('loft planar cap solid', lambda:
         all(x.IsSolid for x in N.loft_surface(cc,cap=True,tolerance=0.001)))
    test('cap without tolerance rejected', lambda:rejects(lambda:N.loft_surface(cc,cap=True)))
    rotated = [G.LineCurve(G.Point3d(5*math.cos(t),5*math.sin(t),0),
                          G.Point3d(5*math.cos(t),5*math.sin(t),3)) for t in [0,2,4]]
    test('closed loft direction', lambda:all(x.IsValid for x in N.loft_surface(rotated,closed=True)))
    test('single loft section rejected', lambda:rejects(lambda:N.loft_surface([line])))
    plane = G.PlaneSurface(G.Plane.WorldXY,G.Interval(0,10),G.Interval(0,10))
    test('plane curvature zero', lambda:abs(N.surface_curvature(plane,(5,5,0))['mean'])<1e-12)
    sphere = G.Sphere(G.Point3d.Origin,10).ToNurbsSurface()
    test('sphere principal curvature magnitude', lambda:
         abs(abs(N.surface_curvature(sphere,(10,0,0))['k1'])-0.1)<1e-8)
    test('surface spans helper', lambda:N.surface_spans(a)['u_spans']==1)
    test('reference plane explicit width height', lambda:
         N.pictureframe_points(G.Plane.WorldXY,20,10)[2].DistanceTo(G.Point3d(20,10,0))<1e-10)
    test('reference size rejected', lambda:rejects(lambda:N.pictureframe_points(G.Plane.WorldXY,-1,2)))
    periodic = N.make_curve(doc,[(0,0,0),(10,0,0),(10,10,0),(0,10,0)],3,periodic=True)
    test('periodic construction real properties', lambda:periodic.IsPeriodic and periodic.IsClosed)
    cylinder = G.Cylinder(G.Circle(G.Plane.WorldXY,10),10).ToBrep(False,False)
    closed_edge = next(i for i,e in enumerate(cylinder.Edges) if e.IsClosed)
    test('closed edge pairing explicitly rejected', lambda:
         rejects(lambda:sample_seam(cylinder,closed_edge,0,cylinder,closed_edge,0,0.01,0.1)))
    test('no document geometry or settings changed', lambda:state()==before)
    result = {'rhino_version':str(Rhino.RhinoApp.Version),'total':len(rows),
              'passed':sum(r['passed'] for r in rows),'cases':rows,
              'document_mutations':0 if state()==before else 'unexpected',
              'g2':'NOT EVALUATED'}
    if result['passed'] != result['total']:
        raise AssertionError(json.dumps(result,ensure_ascii=False))
    return result


if __name__ == '__main__':
    if '__rhino_doc__' not in globals():
        raise RuntimeError('Run inside Rhino with explicit injected document')
    print(json.dumps(run_tests(__rhino_doc__),ensure_ascii=False))
