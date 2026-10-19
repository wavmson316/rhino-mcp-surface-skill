# Repeating Units, Symmetry, and Arrayed Parts

> This document distills the method behind "repeating-unit surface products"
> (hubs, spokes, grilles, fan blades, multi-hole shells) into a general
> technique. The hub is one of the hardest cases — it demands a **revolved
> surface**, a **polar array**, **internal openings**, and **readable feature
> lines** all at once.
>
> ⚠️ Every core conclusion here was verified on a live machine running
> Rhino 8.29.26063.11001. Anything labeled "measured" was actually executed;
> anything marked ⛔ was **measured and does not hold**.

---

## 0. ⭐ In one sentence

**A hole is an inner boundary of the surface band, not a cavity carved out by a boolean.**

⛔ The "stack solids + boolean-cut the holes" route for a hub: the hole walls
are straight through-bores with no draft and no feature lines, and on a complex
base body the boolean will most likely fail outright.

✅ The correct route: take the radial direction "bore opening → outer profile" and
**split it into intervals**, one surface band per interval, so **the holes emerge
naturally as the loft's starting points**.

```
Profile control points → spatial sections → surface bands → closed unit → polar copies → verify
```

---

## 1. ⭐ Polar array: build only one master unit

⛔ **Never** hand-rebuild 5 "roughly similar" spokes.

✅ Build **one master unit**, then array it 5 times around the axis.

**Rationale**: 5 hand-built parts inevitably differ slightly, and once assembled
they show small visible gaps and asymmetric highlights. An array guarantees exact
consistency.

⚠️ Before arraying you must confirm the master unit's **phase alignment** —
otherwise the spokes come out skewed.

---

## 2. ⭐⭐ Profiles: use control points, not interpolation through points

This is **the easiest thing to overlook and the one with the largest impact**.

```python
# ✅ Periodic cubic NURBS: the input points are control points; the curve does not pass through them
curve = G.NurbsCurve.Create(True, 3, [G.Point3d(*p) for p in pts])

# ⛔ Interpolation through points: the curve passes through the input points, and near the junction of a long straight edge and a small fillet it locally swings back (reversed curvature)
G.Curve.CreateInterpolatedCurve(pts, 3, G.CurveKnotStyle.ChordPeriodic)
```

### 2.1 Why reversed curvature happens

Interpolation through points **forces the curve through every input point**. When
neighboring points differ greatly in spacing (a long straight edge immediately
followed by a small fillet), the Hermite spline will **overshoot** at the
transition, producing a bulge that runs opposite to the design intent — half the
reason you end up with a "too mushy" model and a "reversed-curvature bore opening".

Control-point interpolation (`NurbsCurve.Create`) makes no promise to pass through
its control points, so you control the shape directly.

### 2.2 ⭐ Four conditions that must all hold (otherwise the Loft twists)

```
Inner/outer profiles: same point count · same meaning at the start point · same winding direction · same seam position
```

⚠️ If any one of them fails, Loft will **mismatch points across the two sets** and
the resulting faces will be twisted.

### 2.3 Dimensional normalization (a measured detail)

A control-point curve **does not pass through its control points**, so its bounding
box will be **smaller** than the range of the input points. If you scale by the
min/max of the input points, the actual model comes out too small.

The correct approach:

```
1. Generate the curve from the target control points → take the exact bounding box from the curve
2. Target range = min/max of the original data range
3. Scale and translate the same control points in X and radially, separately
4. Generate the actual curve from the adjusted control points
```

---

## 3. ⭐ The section sequence: parameterize it, do not freehand it

Sections are not "draw a ring at a few heights and call it done"; they are
**parameterized by a radial interpolation ratio t and a height h**.

Taking a real five-window hub as the example (`t` = interpolation ratio from bore
opening to outer profile, `h` = height):

| i | t | h | Role |
|---:|---:|---:|---|
| 0 | 0 | −26 | Rear edge of the inner bore |
| 1 | 0 | −14 | Straight wall of the inner bore |
| 2 | 0.018 | −10 | Start of the bore-wall transition |
| 3 | 0.52 | 21.5 | End of the bore wall near the face |
| 4 | 0.55 | 23.6 | Narrow transition |
| 5 | 0.57 | 24.2 | Inner boundary of the face |
| 6 | 0.74 | 24.7 | Slight undulation on the face |
| 7 | 0.925 | 24.5 | Outer boundary of the face |
| 8 | 0.945 | 24.0 | Narrow transition on the outer side |
| 9 | 0.955 | 22.6 | Start of the outer wall |
| 10 | 1 | 6.0 | Lower edge of the outer wall |
| 11 | 1 | −18 | Rear edge of the outer side |

```python
x = 0.5 * (xi + (xo - xi) * t)
r = 0.5 * (ri + (ro - ri) * t)
z = h + 12 * (1 - r / 240.0)      # Radial term: higher toward the center, and a height difference all the way around
P = G.Point3d(x, -r, z)
```

⭐ **Why this is worth doing**: the parameter table is **readable, adjustable, and
reproducible**. When you want to change the form you adjust `t` and `h` instead of
redrawing a pile of lines.

⚠️ `t=0` appears twice (i=0 and i=1), and `t=1` also appears twice — that is not
duplication, it is the **straight-wall segments** (extending along height while the
radial coordinate stays fixed).

### 3.1 Loft grouping: Straight ≠ planar

```python
SPANS = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6,7),(7,8),(8,9),(9,10),(10,11),(11,0)]
# (2,3) additionally inserts section(0.28, 12.0) to create a controlled bend
# (5,6,7) uses LoftType.Normal
```

⚠️ **`LoftType.Straight` means straight rails; it does not mean a planar face** —
this naming is the easiest thing to misread.

Finally `Brep.JoinBreps(bands, 0.01)` → you should get **a single closed solid**.

---

## 4. ⭐⭐ Where feature lines come from (this is the root cause of "too mushy")

**Feature lines come from the superposition of three things**:

```
① Adjacent surface bands have different local normals
+ ② The transition band is narrow enough
+ ③ The face itself has only a slight bulge
```

⛔ **Do not** use `FilletSrf` / `BlendSrf` to smooth everything away — **that is
precisely what makes the result "too mushy"**.

⚠️ The converse also holds: when you want a rounded transition, ⛔ do not use a
global Blend, because that will erase the feature lines you already have. Instead,
**loft only the segment that needs a transition**, and keep the transition band
narrow.

---

## 5. ⭐ Acceptance: curvature sign check (prevents reversed curvature at the bore opening)

```python
signed = Vector3d.CrossProduct(c.TangentAt(t), c.CurvatureAt(t)).Z
# Clockwise profile near the XY plane → normally negative
# > 1e-8 counts as a reversed sample
```

⚠️ **The sign depends on convention**:
- A counter-clockwise profile gives the opposite sign
- For an inclined plane you must use **that plane's consistent normal**; ⛔ you cannot just take `.Z` every time

**Measured scale**: 21 sections × 1200 samples per revolution = **25200 samples**,
with **0 reversed samples** on this model, and signed values falling between
−0.054385 … −0.002181.

⭐ This check catches the dents you cannot see by eye but that show up when you render.

---

## 6. ⭐ How silhouette IoU is actually done

This adds one **trick** to the [main document's IoU explanation](10-parameters-and-recipes.md):

```
1. Place a pure black plane behind the model (material Diffuse pure black + Shine 0)
2. Rendered + Top orthographic screenshot → a silhouette of "black background / bright subject"
3. If the reference image is also bright-on-black → the same threshold can segment it
4. Align and normalize by "centroid + 99.7-percentile outer radius"
5. Compute IoU, and visualize "reference only" / "model only" separately
```

⚠️ **Material lives in `Rhino.DocObjects`, not `Rhino.Geometry`** (measured).

### 6.1 ⭐ Judging whether a change helped or hurt requires the same ruler

⛔ **Do not judge by eye whether a change improved or damaged the model.**

Measured lesson: after shrinking a hub's bore opening by 8%, IoU actually **dropped
from 0.805 to 0.787** — which shows those differences were **not on the planar
profile at all**, and shrinking the bore only makes everything else worse.

⭐ The correct approach: compute `V_old` and `V_new` with **the same alignment and
normalization**, and only then is the difference meaningful.

### 6.2 ⭐ Do not be fooled by highlights

A **broad light-to-dark gradient on a metal part does not necessarily mean** a wide
chamfer or large fillet in the geometry.

The strong highlight in a reference image only tells you **how the face orientation
changes**; ⛔ it cannot be read directly as an edge line.

---

## 7. ⭐ API facts verified on a live machine (including corrections to older claims)

⚠️ Everything below was run on **Rhino 8.29.26063.11001**.

### 7.1 Still holds

| Item | Measured result |
|---|---|
| `Faces.Count` is not `len()` | ✅ Holds |
| `RhinoView` has no class-level `ZoomExtents` | ✅ Holds; you must use a `RhinoViewport` instance |
| The real viewport class name in `Rhino.Display` | **`RhinoViewport`** (not `Viewport`) |
| `DisplayModeDescription.RenderedDisplayModeId` does not exist | ✅ Holds; use `FindByName("Rendered")` |
| Periodic `CreateInterpolatedCurve` needs the first point appended | ✅ **Measured and confirmed**: 8 points → `IsClosed=False`; 9 points → `IsClosed=True` |
| A non-empty return from `JoinBreps` ≠ usable | ✅ Holds; you must check `IsValid` / `IsSolid` |
| Solid orientation | Compare `Brep.SolidOrientation` against `BrepSolidOrientation.Outward` |
| Overlapping bore walls on adjacent layers → checkerboard pattern | Enlarge the backing-plate holes locally by **1.035×** to leave a gap |

### 7.2 ⛔ Outdated claims (older docs were wrong)

| Old claim | ⛔ Measured conclusion |
|---|---|
| `SolidOrientation.Inward` | **Does not exist**. The real name is `BrepSolidOrientation` |
| `Brep.CreatePlanarBreps([outer]+holes)` to make a plane with holes | **The inner rings are ignored**, so no holes come out. Use `Extrusion.AddInnerProfile()` |
| `f.Objects[0]` requires calling `list(f.Objects)` first | **`BrepFace` has no `Objects` property at all** |
| `Material` is in `Rhino.Geometry` | It is in **`Rhino.DocObjects`** |
| `Extrusion.CreateCap()` | **Does not exist**. Use `Extrusion.ToBrep()` |

### 7.3 ⭐ The measured-correct way to make an inner profile

```python
ext = G.Extrusion.Create(outer_curve, G.Plane(origin, G.Vector3d(0,0,1)), height, True)
ext.AddInnerProfile(inner_curve)     # returns True
brep = ext.ToBrep()                   # ⛔ not CreateCap
```

**Measured**: outer 40×40, inner 10×10, height 10 →
`faces=10 solid=True volume=15000.0`, and the theoretical value
`(1600−100)×10 = 15000` ✅ **matches exactly**.

### 7.4 Another easy mistake

```python
G.NurbsCurve.Create(True, 3, pts)
# ⛔ pts is a list of tuples → TypeError: 'tuple' value cannot be converted to Point3d
# ✅ You must pass [G.Point3d(x, y, z), ...]
```

---

## 8. Delivery order (follow it, do not skip steps)

```
1. Build the geometry in memory
2. Check profile / Brep validity / closure / orientation
3. Only after it passes, add it to the document or replace the designated object
4. Save a standalone .3dm
5. ⭐ Read the saved file back and verify the object count and geometry state
```

⚠️ Step 5 cannot be skipped — the save process may truncate or reorder objects.

---

## 9. Quick self-check

```
□ Did you build only one master unit and rely on an array for the rest?
□ Did the profile use control-point interpolation, not interpolation through points?
□ Are point count / start point / winding direction / seam position consistent across the inner and outer profiles (all four)?
□ Were the dimensions normalized against the curve's bounding box?
□ Do the feature lines come from normal differences plus narrow transition bands, rather than from smoothing with BlendSrf?
□ Did you run the curvature sign sampling, with 0 reversed samples?
□ Were IoU's V_old / V_new computed with the same ruler?
□ Are all the construction input curves left on the Lines layer? (see document 15)
```

---

## 10. Sources

The conclusions in sections 2.3, 5, and 6 come from a measured reconstruction of a
five-window hub (diameter ≈484 mm, 14 valid closed solids, 11 faces per spoke,
0 reversed out of 25200 samples, silhouette IoU 0.8054). All of section 7 was
re-verified on Rhino 8.29.26063.11001, including 5 corrections to older claims.

⚠️ The specific counts, phases, and alignment method for an arrayed part vary from
product to product; this document only provides **reusable criteria and pitfalls**.
