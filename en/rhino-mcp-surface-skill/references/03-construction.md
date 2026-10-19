# Curves and surfacing principles

## Mathematical boundaries

In Rhino, Degree is the degree p, and Order = p+1. An ordinary non-periodic clamped single-span curve has p+1 control points. Periodic and closed are not the same concept, and there is no formula of the form "CP always equals Degree" for periodic curves. Read the actual span count from SpanCount; for surfaces, read it separately in U and V.

With general interior knot multiplicity m, a B-spline guarantees parametric continuity C^(p-m); special geometry can do better. A knotless polynomial piece, or a non-singular rational piece, is smooth in its interior. This rule does not equal cross-surface G-level. High degree does not guarantee fairness, and a cubic can also satisfy a specific higher geometric continuity.

The repeated knots of a rational quadratic circle are not a geometric kink. Exact circles and arcs should keep their analytic or rational representation wherever possible. Do not rebuild a circle into a tolerance approximation just to normalise the point count.

**Exact degree elevation and knot insertion preserve the shape and add degrees of freedom.** The Deformable mode of ChangeDegree, degree reduction, Rebuild, Fit and Fair can all change the shape — state the intent and measure the difference; do not treat them as shape-preserving. A shape that survives degree elevation unchanged is the normal outcome. After multi-span degree elevation, the CP count is not universally p+1.

## Curve strategy

Build the straight lines, arcs and primary sections first, then the auxiliary lines. Control-point curves suit fairness editing; interpolation suits cases that genuinely must pass through given points, and avoid interpolating noisy pixels one by one. Check endpoints, directions, closing seams, micro-segments, the curvature comb and the projection from multiple views. Compare combs at a fixed display scale.

When rebuilding, keep the original line and try low-complexity candidates against a budget. If the error concentrates on a genuine hard edge, split the curve; do not raise the degree indefinitely across the whole curve. Fit can handle suitable polyline input, but genuine corners must be protected — a blanket ban is wrong. Interpolation knot spacing Uniform/Chord/SqrtChord is decided by point spacing and shape trials; no single setting is always the smoothest.

## Choosing the surfacing method

| Constraint | Candidate | Verify |
|---|---|---|
| Analytic planes, cylinders, cones, spheres, tori | Analytic surfaces / Revolve | True dimensions, axis and seam are preserved |
| Constant cross-section along a vector | ExtrudeCrv | Direction, and the thickness/cap semantics |
| Profile revolved about an axis, with a rail | Revolve/RailRevolve | Poles, rail, profile and self-intersection |
| Ordered sections | Loft | Order, direction, closing seam, interior volume |
| Path plus cross-section | Sweep1 | Frame rotation, section orientation; asymmetric sections allowed |
| Two rails plus cross-section | Sweep2 | Rail correspondence, intersection order, section scaling/height and the side-edge constraint |
| Region enclosed by 2–4 edges | EdgeSrf | Boundary interpolation does not guarantee interior volume or cross-surface G2 |
| Two intersecting families of curves | NetworkSrf | Consistency at intersections, the order of each family, fit error, output complexity |
| Empty band between two parent surfaces | BlendSrf | Continuity on both sides, bulge, width, correspondence, corner regions |
| Adjusting an existing surface | MatchSrf | Which side is the master, whether the other edges hold, degrees of freedom and the deformation range |
| Fitting scattered points or edge approximations | Patch | Sampling, stiffness, boundary error, tangent options; review before committing to a use |
| Organic concept with branching | SubD → rebuild if needed | Pole/face count against delivered editability |

The U and V degrees of EdgeSrf may differ. Compatibility adjustment between opposite edges can add knots, but exact degree elevation by itself does not cause deformation. Interior fairness is still governed by boundary parameterisation and corner compatibility. Loft does not require a fixed 3–5 sections; two work too, and add sections only when information is missing.

Maintain height on Sweep2 controls how the section scales while the two rails vary. Whether draft is preserved must be measured — the toggle alone does not guarantee it. Where continuity is required, select the real surface edge together with the semantics of the adjacent surface; a standalone curve obtained with DupEdge does not retain the surface's cross-derivative conditions at that edge.

## Local edits and transitions

Near a clamped, non-degenerate natural edge, the first, second and third rows of control points govern position, first derivative and second derivative respectively. If the knots, degree and weights are unchanged and the relevant rows are protected, the corresponding derivative at that edge is preserved. Trimmed edges and other adjacent edges are not automatically protected by this simplification. Aligning "three rows" is not proof of G2.

### ⭐ Applicability limits of the three-row method

| Situation | Applicable |
|---|---|
| Two surfaces of equal degree with equal weights and comparable parameter scale | ✅ Holds; usable as a construction rule |
| Periodic or closed structures | ⛔ Not applicable |
| Trimmed edges | ⛔ Not protected by this method |
| G2 required but degrees of freedom are insufficient | ⛔ Three rows are not enough; add degrees of freedom |

The relevant control points along a straight run may be collinear; a planar patch net should be coplanar, and you must not collapse the whole net into a straight line. SetPt applies only to the selected design region and the chosen axis, and aligning row by row can destroy the original double curvature.

### ⭐ Local bulge / slight dome

A single-span transverse-degree-2 three-row structure can use the middle row to form a slight dome cap, but this changes the derivatives at the ends. For G2 on both sides or a local dimple, you need sufficient degrees of freedom and support width — the three-row method cannot be applied to all of them.

⛔ **Keep the two apart**:
- The "three-row method" is a **construction rule for a constrained situation** (cautious in principle, usable in practice)
- "The last three rows determine the curvature of that edge" is a **constraint that keeps you from editing beyond your remit**

### ⭐ The Deformable mode of `ChangeDegree`

Exact degree elevation (Deformable mode) preserving the shape is the normal goal. ⛔ But if the intent is **to change the shape** (add degrees of freedom, correct a bulge, raise a local boss), then without Deformable the command **changes only the degree, not the shape** — it reports "success" while the geometry has not moved, which is easily mistaken for having raised the degree.

⛔ Conversely, do not casually enable Deformable in order to "change the shape": it destroys an already confirmed shape.
**State the intent first, then pick the mode.**

### ⭐ Check opposite-edge degrees before using `EdgeSrf`

When the degrees differ, the software compensates with interior knots, so **the result is deformation rather than an error message**.
This class of problem is extremely hard to locate after the fact in Rhino, so check it before building the surface.

---

## Trimming and offsetting

The parent surface must cover the design domain with reasonable margin for intersections. Choose Split/Trim according to the input object and the projection direction; a curve may legitimately cut a Brep, but a cutting surface must pass fully through the target and avoid near-tangency. Intersect can return an open, multi-piece or closed intersection curve — do not judge success by closure alone.

Project projects along a defined direction and can take several targets; Pull maps to the nearest position. The former suits patterns with a definite direction, the latter suits conforming to a target; the distinction is not "single surface versus multiple surfaces". Record the projection plane or vector.

Offset expresses the intent of a constant distance, so numerical approximation and self-intersection need checking. Offsetting analytic segments one at a time and blending them simplifies control, but the new blend is usually not strictly equidistant. A translated or scaled inner layer is a visual approximation and must not be passed off as constant thickness. FilletSrf handles fillets between surfaces, FilletEdge handles Brep edges; a Blend-style smoothing is not equivalent to a fixed-radius fillet.

### ⭐ `ExtrudeCrv` and hard-surface cutouts

`ExtrudeCrv` extrudes a **surface that passes through** (not a solid). This is the classic hard-surface cutout:

```
1. Draw the outline along the reference
2. ExtrudeCrv into a through surface
3. Trim to cut out the faces inside the opening
4. Join
5. FilletEdge to chamfer
```

### ⭐ The two direction options of `Extrude`

| Option | Key | Use |
|---|---|---|
| Cap | `C` | Extrude a **solid** (buttons, clips, screw posts) |
| Bothside | `B` | When the surface must **fully pass through** both sides |

⚠️ Symbols may differ between versions; check the current version with `get_commands` before `run_command`.