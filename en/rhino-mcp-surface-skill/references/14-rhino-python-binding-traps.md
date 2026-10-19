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

## 11. ⭐⭐ `Sweep2` and `NetworkSrf` do not exist in RhinoCommon at all

**This is the single most reliable way to waste your time.** Plenty of people
assume "Rhino command = RhinoCommon method" and then spend half an hour hunting
for a method that was never there.

```python
G.Brep.CreateSweep2        # ⛔ AttributeError
G.Brep.CreateNetworkSrf    # ⛔ AttributeError
G.Surface.CreateSweep2     # ⛔ AttributeError
```

**Verified (Rhino 8.29)**: neither one appears anywhere in the complete list of
`Brep.Create*` methods.

### 11.1 Which surfacing operations have an API and which do not

| Command | RhinoCommon method | Notes |
|---|---|---|
| `Loft` | ✅ `Brep.CreateFromLoft` | available |
| `EdgeSrf` | ✅ `Brep.CreateEdgeSurface` | available |
| `Patch` | ✅ `Brep.CreatePatch` | available |
| `FilletEdge` | ✅ `Brep.CreateFilletEdges` | available |
| `Extrusion` | ✅ `Extrusion.Create` + `ToBrep` | a separate class, not a Brep method |
| `Revolve` | ✅ `Brep.CreateFromRevSurface` | available |
| ⛔ **`Sweep2`** | ❌ **none** | **command only** |
| ⛔ **`NetworkSrf`** | ❌ **none** | **command only** |
| ⛔ `Sweep1` | ⚠️ `Brep.CreateFromSweep*` exists but means something else | see §11.3 |

### 11.2 When you have to go through a command

⛔ **`rs.Command` blocks the MCP call** (see §10). What does work:

```python
import rhinoscriptsyntax as rs
# 1. Add the working copies to the document (commands only see document objects)
ids = [doc.Objects.Add(c) for c in working_copies]
# 2. Use the underscore-prefixed command name (language independent)
rs.Command('_-NetworkSrf _SelCrv ' + ','.join(map(str, ids)) + ' _Enter', False)
# 3. Fish the result back out of the document
```

⚠️ The risks and costs:
- ⛔ The command **consumes its input objects** — they disappear from the scene →
  this is exactly why this package insists on "copy first, then build"
- ⚠️ It runs asynchronously, so the result may not be usable yet →
  **you must check the result**; you cannot assume it worked
- ⚠️ Command-line options change between versions → ⛔ do not memorise option
  strings; run `get_commands` first to verify them

### 11.3 The trap in `Sweep1`

`Brep.CreateFromSweep` / `CreateFromSweepInParts` do exist, but
⛔ **they are not the equivalent of the `Sweep1` command** — the parameter
semantics and the resulting topology do not line up either way.

When you need strict `Sweep1` behaviour (framing, twist, capping), go through
the command.

---

## 12. ⭐⭐ `doc.Layers.FindName` returns `None`, **not** `-1`

```python
doc.Layers.FindName('Lines')     # returns None when the layer does not exist
if found >= 0:                   # ⛔ TypeError: '>=' not supported between
    return found                     NoneType and int
```

**Correct approach**:

```python
found = doc.Layers.FindName('Lines')
if found is not None:
    return found.Index        # ✅ a Layer object — take .Index
# when it is missing you get None, so Add a Layer object first (see below)
layer = Rhino.DocObjects.Layer()
layer.Name = 'Lines'
doc.Layers.Add(layer)         # returns an int index
```

⚠️ Two things to note:
- ⛔ `doc.Layers.Add('Lines')` **does not accept a string**; you must pass a `Layer`
  object
- When it is found you get a **`Layer` object**, not an int; the index comes from
  `.Index`

---

## 13. ⭐ `doc.Objects.Count` may disagree with enumeration

```python
doc.Objects.Count          # 16
len(list(doc.Objects))     # 0   ← actually empty
```

**Verified (Rhino 8.29, reproduced twice independently)**:

| Scenario | `Count` | Enumeration |
|---|---|---|
| After a Rhino command consumed the inputs | 8 | **0** |
| After deleting every object | 16 | **0** |

⚠️ **`Count` sits at the old value in both cases and never refreshes.** Worse, it
leads you to think "the objects are still there and cannot be deleted", when in
fact enumerating once shows there is nothing left.

⚠️ A related trap: `Rhino.Geometry.NurbsCurve` has **no `IsCurve` property**.
To filter objects by geometry type you are left with `IsValid` plus a check on
the geometry class name.

⚠️ **To determine whether a document is clean, enumerate it instead of reading
`Count`**:

```python
clean = len(list(doc.Objects)) == 0        # ✅ reliable
# ⛔ doc.Objects.Count == 0                 # may fool you
```

⚠️ This matters most in assertions of the form "the object count should match
before and after the test" — `Count` will hand you a false verdict.

### 13.1 `Purge` requires an argument

```python
doc.Objects.Purge()          # ⛔ No overload ... takes '0' arguments
```

⛔ Do not call it on intuition; the signature varies by version.

### 12.2 You must reload after editing script source

Rhino's Python **caches modules it has already imported**. Edit the `.py`, run
it again, and you still get the old code — while the traceback points at a line
that doesn't match your source, which is thoroughly misleading.

```python
import importlib, patch_with_lines
importlib.reload(patch_with_lines)      # ✅ must reload after editing the source
```

⚠️ Or delete `__pycache__` at the file level. ⛔ **Do not use that to discover
whether your code change actually took** — first confirm that `module.__file__`
points at the file you think it does.

---

## 14. General principles

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

## 15. A snippet verified on a live machine (copy it directly)

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

## 16. Source

Tested on Rhino **8.29.26063.11001**, Windows, the Python 3 bundled with Rhino, and
the official McNeel Rhino MCP Platform **0.3.0.0** (`serverInfo.name == "rhino-mcp"`).
Every conclusion comes from running on a live machine, and the script was verified
in-session.