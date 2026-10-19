"""Native construction and persistence regressions in a separate headless doc."""
from pathlib import Path
import json
import Rhino
import System
import native_surface_builders as B
from quality_gate import check_candidates
G=Rhino.Geometry

def run_tests(live_doc,output_path):
    output=Path(output_path)
    if output.exists(): raise ValueError('Use a new test artifact path')
    def state(doc):
        return (sorted(str(o.Id) for o in doc.Objects),doc.Layers.Count,str(doc.ModelUnitSystem),
                doc.ModelAbsoluteTolerance,doc.ModelAngleToleranceDegrees,doc.Modified)
    before=state(live_doc)
    doc=Rhino.RhinoDoc.CreateHeadless(None)
    if doc is None: raise RuntimeError('Headless document unavailable')
    checks={}
    def check(name,value):
        checks[name]=bool(value)
        if not checks[name]: raise AssertionError(name)
    def rejects(fn):
        try: fn()
        except ValueError: return True
        return False
    try:
        doc.ModelUnitSystem=Rhino.UnitSystem.Millimeters
        doc.ModelAbsoluteTolerance=0.001
        pt=lambda x,y,z=0:G.Point3d(x,y,z)
        rails=[G.LineCurve(pt(0,0),pt(10,0)),G.LineCurve(pt(0,5),pt(10,5))]
        sections=[G.LineCurve(pt(0,0),pt(0,5)),G.LineCurve(pt(10,0),pt(10,5))]
        snapshot=state(doc)
        originals=[c.DuplicateCurve() for c in rails+sections]
        sweep=B.sweep2_with_lines(doc,rails,sections,register=False)
        check('sweep2_native_valid',len(sweep['breps'])==1 and sweep['brep'].IsValid)
        check('sweep2_expected_area',abs(G.AreaMassProperties.Compute(sweep['brep']).Area-50)<1e-8)
        net=B.network_with_lines(doc,rails,sections,register=False)
        check('network_native_one_surface',net['brep'].Faces.Count==1)
        check('network_expected_area',abs(G.AreaMassProperties.Compute(net['brep']).Area-50)<1e-8)
        # A consistent 3x3 network for z=0.02*x*y: one saddle, not four cells.
        u=[G.LineCurve(pt(x,0),pt(x,10,0.2*x)) for x in [0,5,10]]
        v=[G.LineCurve(pt(0,y),pt(10,y,0.2*y)) for y in [0,5,10]]
        saddle=B.network_with_lines(doc,u,v,register=False)['brep']
        check('three_by_three_network_one_face',saddle.Faces.Count==1)
        s=saddle.Faces[0]
        ok,uu,vv=s.ClosestPoint(pt(5,5,0.5))
        check('saddle_matches_independent_center',ok and s.PointAt(uu,vv).DistanceTo(pt(5,5,0.5))<0.001)
        check('saddle_negative_gaussian',s.CurvatureAt(uu,vv).Gaussian<0)
        check('memory_calls_unchanged_document',state(doc)==snapshot)
        check('inputs_not_mutated',all(G.GeometryBase.GeometryEquals(a,b) for a,b in zip(originals,rails+sections)))
        check('invalid_input_not_dropped',rejects(lambda:B.sweep2_with_lines(doc,rails,sections+[None])))
        check('extra_rail_rejected',rejects(lambda:B.sweep2_with_lines(doc,rails+rails[:1],sections)))
        check('bad_tolerance_rejected',rejects(lambda:B.network_with_lines(doc,rails,sections,tolerance=float('nan'))))
        check('unused_option_not_ignored',rejects(lambda:B.sweep2_with_lines(doc,rails,sections,closed_section=True)))
        check('open_geometry_not_claimed_capped',rejects(lambda:B.loft_with_lines(doc,rails,cap=True,tolerance=0.001)))
        check('no_output_rejected',not check_candidates([])['passed'])
        check('open_surface_accepted_by_contract',check_candidates(net['breps'])['passed'])
        check('open_surface_rejected_if_solid_required',not check_candidates(net['breps'],require_solid=True)['passed'])
        check('duplicate_outputs_rejected',not check_candidates([net['brep'],net['brep'].DuplicateBrep()])['passed'])
        # A pre-existing unrelated solid must never be returned as a new network.
        sentinel=G.Box(G.Plane.WorldXY,G.Interval(100,110),G.Interval(0,10),G.Interval(0,10)).ToBrep()
        sentinel_id=doc.Objects.AddBrep(sentinel)
        local=B.network_with_lines(doc,rails,sections)
        check('existing_solid_not_mistaken_for_output',not local['brep'].IsSolid and local['brep'].GetBoundingBox(True).Max.X<11)
        registered=B.publish_patch(doc,net,'P_TEST')
        ids=registered['line_ids']; out_id=registered['surface_ids'][0]
        records=json.loads(doc.Objects.FindId(out_id).Attributes.GetUserString('construction_inputs'))
        check('both_families_preserved',len(ids)==4 and [r['role'] for r in records]==['u','u','v','v'])
        check('lines_layer_and_mapping',B.audit_curve_retention(doc,records=records)['ok'])
        check('count_alone_not_complete',not B.audit_curve_retention(doc)['ok'])
        check('all_actual_input_geometry_retained',all(G.GeometryBase.GeometryEquals(c,doc.Objects.FindId(g).Geometry) for c,g in zip(rails+sections,ids)))
        check('no_associative_history_claim',registered['history'] is False)
        file=Rhino.FileIO.File3dm()
        try:
            file.Settings.ModelUnitSystem=doc.ModelUnitSystem
            for layer in doc.Layers: file.AllLayers.Add(layer)
            for obj in doc.Objects: file.Objects.Add(obj.Geometry,obj.Attributes)
            check('write_3dm',file.Write(str(output),8))
        finally: file.Dispose()
        reopened=Rhino.FileIO.File3dm.Read(str(output))
        if reopened is None: raise AssertionError('3dm read failed')
        try:
            objects={str(o.Id):o for o in reopened.Objects}
            check('save_read_input_ids',all(str(g) in objects and isinstance(objects[str(g)].Geometry,G.Curve) for g in ids))
            check('save_read_surface_mapping',json.loads(objects[str(out_id)].Attributes.GetUserString('construction_inputs'))==records)
            check('save_read_lines_layer',all(reopened.AllLayers.FindIndex(objects[str(g)].Attributes.LayerIndex).FullPath=='lines' for g in ids))
        finally: reopened.Dispose()
        doc.Objects.Delete(ids[0],True)
        check('missing_input_detected',not B.audit_curve_retention(doc,records=records)['ok'])
        check('unrelated_object_retained',doc.Objects.FindId(sentinel_id) is not None)
        # Verify nested planar boundary rather than inheriting v1.7's false claim.
        ring=lambda s:G.PolylineCurve([pt(-s,-s),pt(s,-s),pt(s,s),pt(-s,s),pt(-s,-s)])
        planar=G.Brep.CreatePlanarBreps([ring(20),ring(5)],0.001)
        check('planar_inner_hole_retained',len(planar)==1 and planar[0].Faces[0].Loops.Count==2 and abs(G.AreaMassProperties.Compute(planar[0]).Area-1500)<1e-8)
    finally:
        doc.Dispose()
    check('live_document_unchanged',state(live_doc)==before)
    return dict(passed=sum(checks.values()),total=len(checks),cases=checks,
                rhino_version=str(Rhino.RhinoApp.Version),live_document_mutations=0,
                scope='Native API, registration, output isolation and 3dm persistence. No reference-image or G2 test')
