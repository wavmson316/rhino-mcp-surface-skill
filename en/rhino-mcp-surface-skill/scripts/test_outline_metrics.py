"""Analytical and invalid-input tests, runnable in ordinary CPython."""
import json
import math
from outline_metrics import silhouette_iou, distance_to_polyline


def run_tests():
    square = [(0,0),(10,0),(10,10),(0,10)]
    tests = []
    def check(name, predicate):
        if not predicate():
            raise AssertionError(name)
        tests.append(name)
    def rejects(action):
        try: action()
        except ValueError: return True
        return False
    check('identical', lambda:silhouette_iou(square,square)['iou']==1)
    shift = lambda x:[(a+x,b) for a,b in square]
    check('half overlap', lambda:abs(silhouette_iou(square,shift(5),600)['iou']-1/3)<0.003)
    check('quarter shift', lambda:abs(silhouette_iou(square,shift(2.5),600)['iou']-0.6)<0.003)
    check('disjoint', lambda:silhouette_iou(square,shift(20))['iou']==0)
    check('closed duplicate endpoint', lambda:silhouette_iou(square+[square[0]],square)['iou']==1)
    check('reversed ring', lambda:silhouette_iou(square,list(reversed(square)))['iou']==1)
    circle = lambda r:[(r*math.cos(i*2*math.pi/720),r*math.sin(i*2*math.pi/720)) for i in range(720)]
    for r in [5,9,10.5,11]:
        expected = (min(r,10)/max(r,10))**2
        check('circle radius '+str(r),lambda r=r,expected=expected:
              abs(silhouette_iou(circle(r),circle(10),600)['iou']-expected)<0.003)
    check('boundary distance',lambda:abs(distance_to_polyline(square,(5,5))-5)<1e-12)
    for name,action in [
        ('empty',lambda:silhouette_iou([],square)),
        ('collinear',lambda:silhouette_iou([(0,0),(1,0),(2,0)],square)),
        ('nonfinite',lambda:silhouette_iou([(0,0),(1,0),(float('nan'),1)],square)),
        ('bad samples',lambda:silhouette_iou(square,square,3)),
        ('fractional samples',lambda:silhouette_iou(square,square,20.5)),
        ('buffer rejected',lambda:silhouette_iou(square,square,tolerance=1))]:
        check(name,lambda action=action:rejects(action))
    for name,ring in [('nonzero crossing',[(0,0),(4,4),(0,4),(3,0)]),
       ('self touch',[(0,0),(4,0),(4,4),(2,0),(0,4)]),
       ('adjacent retracing',[(0,0),(4,0),(2,0),(4,4),(0,4)]),
       ('repeated vertex',[(0,0),(4,0),(4,4),(0,0),(0,4)])]:
        check(name,lambda ring=ring:rejects(lambda:silhouette_iou(ring,square)))
    return {'passed':len(tests),'total':len(tests),'cases':tests,
            'scope':'Specific simple polygon analytical cases, not arbitrary resolution guarantee'}


if __name__ == '__main__':
    print(json.dumps(run_tests()))
