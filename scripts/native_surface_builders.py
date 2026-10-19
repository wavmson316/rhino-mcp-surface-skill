"""Rhino 8.29 native APIs; no commands or implicit active document.

Construction defaults to memory only. publish_patch explicitly adds surfaces,
retains actual curves in lines, and maps outputs to inputs. No History created.
"""
import json
import math
import Rhino
import System
G, D = Rhino.Geometry, Rhino.DocObjects
LINES_LAYER = 'lines'

def _positive(v,name):
    if isinstance(v,bool) or not math.isfinite(v) or v<=0: raise ValueError('Invalid '+name)
    return float(v)

def _tol(doc,value):
    if doc is None: raise ValueError('Explicit document required')
    return _positive(doc.ModelAbsoluteTolerance if value is None else value,'tolerance')

def _curves(values,minimum=1):
    values=list(values)
    if len(values)<minimum or any(not isinstance(c,G.Curve) or not c.IsValid or c.GetLength()<=0 for c in values):
        raise ValueError('Valid nonzero curves required; invalid inputs are not silently dropped')
    return values

def _layer(doc,name):
    index=doc.Layers.FindByFullPath(name,System.Int32(-1))
    if index>=0:
        if doc.Layers[index].IsLocked: raise ValueError('Locked layer: '+name)
        return index
    layer=D.Layer(); layer.Name=name
    index=doc.Layers.Add(layer)
    if index<0: raise ValueError('Layer creation failed')
    return index

def ensure_lines_layer(doc):
    if doc is None: raise ValueError('Explicit document required')
    return _layer(doc,LINES_LAYER)

def register_curves(doc,curves,layer_index=None,group=None,roles=None):
    curves=_curves(curves,0)
    roles=['input']*len(curves) if roles is None else list(roles)
    if len(roles)!=len(curves): raise ValueError('One role per curve required')
    if not curves: return []
    index=ensure_lines_layer(doc) if layer_index is None else layer_index
    if not 0<=index<doc.Layers.Count or doc.Layers[index].IsLocked: raise ValueError('Invalid layer')
    added=[]
    try:
        for i,(curve,role) in enumerate(zip(curves,roles)):
            a=D.ObjectAttributes(); a.LayerIndex=index; a.Name='%s_%s_%03d'%(group or 'patch',role,i)
            for k,v in {'PatchID':str(group or ''),'input_role':role,'input_order':str(i)}.items(): a.SetUserString(k,v)
            guid=doc.Objects.AddCurve(curve.DuplicateCurve(),a)
            if guid==System.Guid.Empty: raise ValueError('Curve registration failed')
            added.append(guid)
        return added
    except Exception:
        for guid in added: doc.Objects.Delete(guid,True)
        raise

def _result(doc,breps,curves,roles,method,parameters,register,patch_id):
    breps=list(breps) if breps is not None else []
    if not breps or any(not isinstance(b,G.Brep) or not b.IsValid for b in breps): raise ValueError(method+' failed')
    inputs=[c.DuplicateCurve() for c in curves]
    ids=register_curves(doc,inputs,group=patch_id,roles=roles) if register else []
    return dict(breps=breps,brep=breps[0] if len(breps)==1 else None,line_ids=ids,
                inputs=inputs,roles=roles,method=method,parameters=parameters,
                patch_id=patch_id,history=False,fail=None)

def _caps(breps,tol):
    if not breps: raise ValueError('Construction failed')
    result=[b.CapPlanarHoles(tol) for b in breps]
    if any(b is None or not b.IsValid or not b.IsSolid for b in result): raise ValueError('Cap did not produce valid solids')
    return result

def loft_with_lines(doc,sections,closed=False,cap=False,loft_type=None,tolerance=None,register=False,patch_id=None):
    tol=_tol(doc,tolerance); sections=_curves(sections,3 if closed else 2)
    kind=G.LoftType.Normal if loft_type is None else loft_type
    if cap and tolerance is None: raise ValueError('Explicit cap tolerance required')
    breps=G.Brep.CreateFromLoft([c.DuplicateCurve() for c in sections],G.Point3d.Unset,G.Point3d.Unset,kind,bool(closed))
    if cap: breps=_caps(breps,tol)
    return _result(doc,breps,sections,['section']*len(sections),'Loft',
                   dict(closed=bool(closed),cap=bool(cap),type=str(kind),tolerance=tol),register,patch_id)

def sweep2_with_lines(doc,rails,sections,tolerance=None,closed_sweep=False,closed_section=False,cap=False,blend_type=None,register=False,patch_id=None):
    tol=_tol(doc,tolerance); rails=_curves(rails,2); sections=_curves(sections)
    if len(rails)!=2: raise ValueError('Exactly two rails required')
    if closed_section or blend_type is not None: raise ValueError('Unsupported flags; do not silently ignore options')
    if cap and tolerance is None: raise ValueError('Explicit cap tolerance required')
    r=[c.DuplicateCurve() for c in rails]
    breps=G.Brep.CreateFromSweep(r[0],r[1],[c.DuplicateCurve() for c in sections],bool(closed_sweep),tol)
    if cap: breps=_caps(breps,tol)
    return _result(doc,breps,rails+sections,['rail_0','rail_1']+['section']*len(sections),'Sweep2',
                   dict(closed_sweep=bool(closed_sweep),cap=bool(cap),tolerance=tol),register,patch_id)

def network_with_lines(doc,curves_u,curves_v,tolerance=None,trim_type=True,register=False,patch_id=None,angle_tolerance=None):
    """Position-fit standalone curves. One fitted surface, not a face per cell.

    Does not transfer transverse derivatives from adjacent parent surfaces.
    angle_tolerance uses radians, per RhinoCommon.
    """
    tol=_tol(doc,tolerance); cu,cv=_curves(curves_u,2),_curves(curves_v,2)
    if trim_type is not True: raise ValueError('Unsupported trim_type; this builds an untrimmed network surface')
    angle=doc.ModelAngleToleranceRadians if angle_tolerance is None else _positive(angle_tolerance,'angle')
    if not 0<angle<math.pi: raise ValueError('Invalid angle tolerance in radians')
    # Installed RhinoCommon XML: 0 loose, 1 position, 2 tangent, 3 curvature.
    surface,error=G.NurbsSurface.CreateNetworkSurface([c.DuplicateCurve() for c in cu],1,1,
                    [c.DuplicateCurve() for c in cv],1,1,tol,tol,angle)
    if error!=0 or surface is None or not surface.IsValid: raise ValueError('Network surface error=%s'%error)
    return _result(doc,[surface.ToBrep()],cu+cv,['u']*len(cu)+['v']*len(cv),'NetworkSrf',
                   dict(tolerance=tol,angle_radians=angle,edge_conditions='position'),register,patch_id)

def publish_patch(doc,result,patch_id=None):
    """Explicit opt-in write. Adds a new version; never replaces user objects.

    Keeps actual input snapshots and maps every output to them. Does not certify
    shape, fairness, G2, watertightness or automatic History.
    """
    patch_id=patch_id or result.get('patch_id') or str(System.Guid.NewGuid())
    if result.get('surface_ids'): raise ValueError('Result already published')
    if not result.get('breps') or any(not b.IsValid for b in result['breps']): raise ValueError('Invalid result')
    existing=list(result.get('line_ids',[]))
    if existing and (len(existing)!=len(result['inputs']) or any(doc.Objects.FindId(g) is None for g in existing)):
        raise ValueError('Missing registered inputs')
    added=[]; undo=doc.BeginUndoRecord('Publish surface and construction curves')
    try:
        ids=existing or register_curves(doc,result['inputs'],group=patch_id,roles=result['roles'])
        if not existing: added.extend(ids)
        layer=_layer(doc,'surfaces')
        records=[dict(id=str(g),role=role,order=i) for i,(g,role) in enumerate(zip(ids,result['roles']))]
        made=[]
        for i,brep in enumerate(result['breps']):
            a=D.ObjectAttributes(); a.LayerIndex=layer; a.Name='%s_surface_%02d'%(patch_id,i)
            fields={'PatchID':str(patch_id),'construction_inputs':json.dumps(records),'construction_method':result['method'],
                    'construction_parameters':json.dumps(result['parameters']),'construction_history':'Not created'}
            for k,v in fields.items(): a.SetUserString(k,v)
            guid=doc.Objects.AddBrep(brep,a)
            if guid==System.Guid.Empty: raise ValueError('Surface addition failed')
            made.append(guid); added.append(guid)
        result.update(line_ids=ids,surface_ids=made,patch_id=patch_id)
        return result
    except Exception:
        for guid in reversed(added): doc.Objects.Delete(guid,True)
        raise
    finally:
        if undo: doc.EndUndoRecord(undo)

def audit_curve_retention(doc,expected_minimum=1,records=None):
    layer=doc.Layers.FindName(LINES_LAYER)
    curves=[] if layer is None else [o for o in doc.Objects if isinstance(o.Geometry,G.Curve) and o.Geometry.IsValid and
        (o.Attributes.LayerIndex==layer.Index or doc.Layers[o.Attributes.LayerIndex].FullPath.startswith(layer.FullPath+'::'))]
    if records is None: return dict(ok=False,count=len(curves),reason='Completeness unverified: input mapping required')
    allowed={str(o.Id) for o in curves}; missing=[str(r['id']) for r in records if str(r['id']) not in allowed]
    return dict(ok=not missing and len(records)>=expected_minimum,count=len(curves),missing=missing,
                layer_visible=False if layer is None else layer.IsVisible)

def patch_record(*args,**kwargs):
    raise ValueError('Extracted output edges are derived geometry, not original inputs; use publish_patch with actual inputs')
