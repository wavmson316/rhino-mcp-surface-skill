# RhinoCommon Python binding quirks (verified on a live Rhino 8.29)

> This document is a record of **live-machine testing**, not a paraphrase of the
> documentation. Every item was run on Rhino **8.29.26063.11001** + Windows + the
> Python 3 bundled inside Rhino.
>
> ⛔ All of these are traps that **don't fail at compile time and only explode at
> runtime** — reading the docs statically will not surface them.

---

## 0. In one sentence

**RhinoCommon's Python binding is not ordinary Python.** Collection types are not
always iterable, some property names differ from C#, and enum member names differ
too.

⛔ **Don't transliterate C# examples into Python** — many of them raise
`AttributeError` outright.

---

## 1. ⭐ Collection types: `BrepFaceList` has no `__len__`

```python
b = some_brep
len(b.Faces)          # ⛔ TypeError: object of type 'BrepFaceList' has no len()
b.Faces.Count         # ✅ 6
len(list(b.Faces))    # ✅ 6
```

⚠️ `hasattr(b.Faces, 'Count')` is true, but `hasattr(x,'Faces')` **cannot** be used
to decide "whether this is a Brep" — `BrepFaceList` has a `Faces` property too.

**Detection trick**: `type(x).__name__ == 'Brep'`. Do not combine `isinstance`
with `hasattr`.

| Collection | How to count |
|---|---|
| `Brep.Faces` / `Brep.Edges` | `.Count` |
| `BrepFace.OuterEdge` | `.Count` |
| Any Rhino collection | `len(list(...))` is the safest bet |

---

## 2. ⭐ `Brep` has no `Volume` property

```python
brep.Volume                        # ⛔ AttributeError: 'Brep' object has no attribute 'Volume'
G.VolumeMassProperties.Compute(brep).Volume   # ✅ 48000.0
```

⚠️ `VolumeMassProperties` also has **no** `.Area` (sum it face by face, or use a
different approach).

⛔ **Don't use `brep.Volume` as a volume acceptance check** — this is exactly the
kind of code you write on autopilot.

---

## 3. ⭐ `BrepFace` has no `Edges` property

```python
for f in brep.Faces:
    f.Edges        # ⛔ AttributeError: 'BrepFace' object has no attribute 'Edges'
```

To get the edges of a face, use `f.OuterEdge` (the outer loop) or take
`brep.Edges` at the Brep level. **Recommended: take them uniformly at the Brep
level**, so that edge indices actually mean something (see §5).

---

## 4. ⭐ `BrepEdge` has no `Index` property

```python
for e in brep.Edges:
    e.Index        # ⛔ AttributeError: 'BrepEdge' object has no attribute 'Index'
```

**Index edges by their enumeration position**:

```python
edges = list(brep.Edges)
idx = [i for i, e in enumerate(edges) if <condition>]
```

⚠️ `f.Edges[ei].Index` on a face is equally unreliable — `enumerate` is the safest
route.

---

## 5. ⭐ `Brep.CreateFilletEdges` wants **positional indices**, not edge objects

```python
# ⛔ Passing edge objects: TypeError
G.Brep.CreateFilletEdges(brep, [edge_obj, ...], ...)

# ✅ Pass int positional indices
idx = [i for i, e in enumerate(list(brep.Edges)) if <is a vertical edge>]
r = G.Brep.CreateFilletEdges(brep, idx, [3.0]*len(idx), None, None,
                             G.BlendType.Fillet, G.RailType.RollingBall, 1.0)
```

⚠️ **The argument count is easy to get wrong**: both a 7-argument and an 8-argument
overload exist; the wrong count reports "No overload ... takes 'N' arguments".

⚠️ `BlendType` has **`Fillet` / `Blend` / `Chamfer`** —
⛔ **there is no `Normal`** (that is a `LoftType` member name; don't mix them up).

⚠️ `RailType` has **`RollingBall`** / `DistanceBetweenRails` / `DistanceFromEdge`.

⚠️ Since Python.NET 3.0, **int cannot be converted to an enum implicitly**; you must
write `G.BlendType.Fillet` explicitly.

---

## 6. ⭐ There is no `Polygon` in `Rhino.Geometry`

```python
G.Polygon(pts)     # ⛔ AttributeError: module 'Rhino.Geometry' has no attribute 'Polygon'
```

**Correct approach**:

```python
pts = [G.Point3d(0,0,0), G.Point3d(80,0,0), G.Point3d(80,50,0), G.Point3d(0,50,0)]
closed = pts + [pts[0]]              # explicit closure
curve = G.PolylineCurve(G.Polyline(closed))
```

⚠️ `G.Curve.CreatePeriodicPolygon` can build a planar polygon, but that one takes an
**area** parameter; a Polyline is more direct.

---

## 7. ⭐ Correct use of `Extrusion`

```python
# ⛔ Brep has no CreateExtrusion
G.Brep.CreateExtrusion(...)                    # ⛔ does not exist

# ✅ Extrusion is a separate class
ext = G.Extrusion.Create(curve, plane, height, cap=True)
brep = ext.ToBrep()                            # ✅ returns a single Brep
```

⚠️ **The signature takes 4 arguments** (curve, plane, height, cap):

| Attempt | Outcome |
|---|---|
| `Extrusion.Create(curve, vec, 12.0)` | ⛔ Vector3d cannot be converted to Double |
| `Extrusion.Create(curve, plane, 12.0)` | ⛔ the 3-argument version does not exist |
| `Extrusion.Create(curve, plane, 12.0, True)` | ✅ |

⚠️ The 2nd parameter is a **`Plane`, not a `Vector3d`**, and the 3rd is **height
(double), not bool**.

⚠️ `ext.ToBrep()` returns a **single Brep** (not a FaceList) —
⛔ do not write `for f in ext.ToBrep(): br.Append(f)`; that reports
"'Brep' object is not iterable".

---

## 8. ⭐ `CreateBooleanDifference` requires a tolerance argument

```python
G.Brep.CreateBooleanDifference(a, b)              # ⛔ only 2 args accepted? No overload
G.Brep.CreateBooleanDifference(a, b, tolerance)   # ✅
```

Returns a **`Brep[]`**, not a single Brep.

---

## 9. ⭐ `Guid` has no `.Id`

```python
oid = doc.Objects.AddBrep(brep)
oid.Id            # ⛔ AttributeError: 'Guid' object has no attribute 'Id'
```

`AddBrep` returns a `Guid` directly; use `str(oid)` or pass it straight to
`FindId` / `Delete`.

---

## 10. ⭐ `rs.Command` blocks

```python
rs.Command('_-FilletEdge ...', False)   # ⛔ hangs, waiting for input and Enter
```

⚠️ **In testing this hung the MCP call** (it only recovered after manual
intervention).

⛔ **Do not use `rs.Command` to run commands that need interactive input.**

**Use the MCP `run_command` tool instead** — it has a timeout and reports status.

⚠️ Command-line options changed in Rhino 8: `_SelEdges` **no longer exists** (it
errors with "unknown command: _SelEdges"); edge selection uses `Edge` / `SelEdge`.

---

## 11. General principles

⛔ **Don't write RhinoCommon Python from memory.** The right approach:

```python
# 1. Use reflection to find what actually exists
print([n for n in dir(G.Brep) if 'Fillet' in n])
print(G.Brep.CreateFilletEdges.__doc__)     # prints all overloads

# 2. Make a trial call; the error message pinpoints the type mismatch
# 3. Run a batch of probes, not one at a time
```

**Error messages are the fastest documentation**: `No overload ... takes 'N'
arguments` tells you how many parameters there are; `X value cannot be converted to
Y` tells you what to pass.

⚠️ Multi-line signatures in `__doc__` have to be extracted line by line with a
regex; printing directly gets broken up by the newlines.

---

## 12. A snippet verified on a live machine (copy it directly)

```python
import Rhino.Geometry as G
import rhinoscriptsyntax as rs
doc = __rhino_doc__

# build a closed solid
pts = [G.Point3d(0,0,0), G.Point3d(80,0,0), G.Point3d(80,50,0), G.Point3d(0,50,0)]
curve = G.PolylineCurve(G.Polyline(pts + [pts[0]]))
ext = G.Extrusion.Create(curve, G.Plane(G.Point3d(0,0,0), G.Vector3d(0,0,1)), 12.0, True)
brep = ext.ToBrep()

print(brep.Faces.Count)                                  # 6
print(brep.IsSolid)                                      # True
print(G.VolumeMassProperties.Compute(brep).Volume)       # 48000.0

# find vertical edges (by positional index)
edges = list(brep.Edges)
idx = [i for i, e in enumerate(edges) if abs(e.PointAtStart.Z - e.PointAtEnd.Z) > 11.9]

# fillet
res = G.Brep.CreateFilletEdges(brep, idx, [3.0]*len(idx), None, None,
                               G.BlendType.Fillet, G.RailType.RollingBall, 1.0)
print(res[0].Faces.Count, res[0].IsValid)
```

---

## 13. Source

Tested on Rhino **8.29.26063.11001**, Windows, the Python 3 bundled with Rhino, and
the official McNeel Rhino MCP Platform **0.3.0.0** (`serverInfo.name == "rhino-mcp"`).
Every conclusion comes from running on a live machine, and the script was verified
in-session.