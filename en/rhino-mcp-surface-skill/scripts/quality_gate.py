"""Small-batch structural gate. Not a shape, fairness or self-intersection proof."""
import math
import Rhino
G=Rhino.Geometry

def check_candidates(breps,require_solid=False,expected_count=None,area_floor=None):
    values=list(breps) if breps is not None else []
    errors=[]; rows=[]
    if not values: errors.append('No output Breps')
    if expected_count is not None and len(values)!=expected_count: errors.append('Unexpected output count')
    if area_floor is not None and (not math.isfinite(area_floor) or area_floor<0):
        raise ValueError('area_floor is an explicit squared-model-unit budget')
    for i,b in enumerate(values):
        if not isinstance(b,G.Brep) or not b.IsValid:
            errors.append('Invalid Brep at index %s'%i); continue
        mass=G.AreaMassProperties.Compute(b)
        area=None if mass is None else mass.Area
        if mass is not None: mass.Dispose()
        if area is None or not math.isfinite(area) or area<=0 or (area_floor is not None and area<area_floor):
            errors.append('Invalid or below-budget area at index %s'%i)
        nonmanifold=sum(e.Valence==G.EdgeAdjacency.NonManifold for e in b.Edges)
        if nonmanifold: errors.append('Nonmanifold edges at index %s'%i)
        if require_solid and not b.IsSolid: errors.append('Expected solid at index %s'%i)
        if any(isinstance(other,G.Brep) and G.GeometryBase.GeometryEquals(b,other) for other in values[:i]):
            errors.append('Duplicate output Brep at index %s'%i)
        rows.append(dict(index=i,faces=b.Faces.Count,area=area,solid=b.IsSolid,
             naked_edges=sum(e.Valence==G.EdgeAdjacency.Naked for e in b.Edges),
             nonmanifold_edges=nonmanifold,orientation=str(b.SolidOrientation)))
    return dict(passed=not errors,errors=errors,objects=rows,
                unverified=['reference similarity','self-intersection/overlap','fairness','G1/G2','thickness/manufacturing'])
