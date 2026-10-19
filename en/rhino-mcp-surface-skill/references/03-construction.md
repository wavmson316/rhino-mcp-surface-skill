# Curve quality and construction choices

## Mathematical boundaries

Rhino Degree is p, Order p+1. An ordinary nonperiodic clamped single-span curve has p+1 control points. Closed and periodic are different; there is no universal periodic CP=Degree rule. Read actual SpanCount, independently for surface U/V.

At an internal knot of multiplicity m, a regular B-spline generally guarantees parameter continuity C^(p-m); special geometry may be smoother. Polynomial/rational pieces are smooth in nonsingular interiors. This is not a cross-surface G-grade formula. High degree does not guarantee fairness, and cubic geometry can satisfy particular higher geometric continuity constraints.

Repeated knots in a rational quadratic circle are not geometric kinks. Preserve exact analytic/rational circles rather than rebuilding them for tidy CP counts.

Exact degree elevation and knot insertion can preserve geometry while adding freedom. Deformable modes, degree reduction, Rebuild, Fit, and Fair can change shape and require deviation checks. No shape change after exact elevation is expected. Multi-span elevation does not generally leave p+1 CP.

## Curve scaffolds

Start with analytic lines/arcs and principal sections, then guides. Control-point curves aid fair editing; interpolation is appropriate for genuinely constrained points, not every noisy pixel. Check endpoints, direction, closed seams, tiny segments, combs, and cross-view projections. Compare combs at fixed display scale.

Preserve originals and try low-complexity fits within a project budget. Split real creases instead of raising the whole degree. Fit can handle suitable polyline inputs when true corners are protected. Uniform/Chord/SqrtChord parameterization is chosen by spacing and shape; none is always smoothest.

## Method selection

| Constraint | Candidate | Inspect |
|---|---|---|
| Analytic planes/cylinders/cones/spheres/tori | Analytic geometry/Revolve | Dimensions, axis, seam |
| Constant section along a vector | ExtrudeCrv | Direction, caps/thickness semantics |
| Rotation, optionally guided by a rail | Revolve/RailRevolve | Poles, profile, rail, self-intersection |
| Ordered sections | Loft | Order, direction, seams, interior volume |
| Path and sections | Sweep1 | Frame rotation and section orientation; asymmetric sections are allowed |
| Two rails and sections | Sweep2 | Correspondence, intersections, scale/height, boundary constraints |
| Two to four boundary curves | EdgeSrf | Boundary interpolation does not establish interior volume or G2 |
| Two intersecting curve families | NetworkSrf | Intersections/order, approximation error, complexity |
| Gap between parent faces | BlendSrf | End constraints, bulge, width, correspondence, corners |
| Adjust an existing face | MatchSrf | Master/slave, opposite-side protection, freedom, deformation |
| Approximate scattered points/boundaries | Patch | Sampling, stiffness, boundary error, tangency option |
| Organic concepts/branches | SubD, then reconstruction if needed | Poles, face count, editability |

EdgeSrf can have different U/V degrees. Opposite-boundary compatibility may add knots, but exact elevation does not itself deform geometry. Parameterization and corner compatibility affect fairness. Loft is not limited to a fixed section count; add sections only when information requires them.

Sweep2 Maintain height concerns section scaling as rails change; verify actual draft instead of assuming a switch guarantees it. When continuity matters, select real surface edges with adjacent-face semantics: DupEdge standalone curves do not carry transverse surface derivatives.

## Local editing

For regular clamped natural boundaries, the first one/two/three CP rows affect position/first/second derivatives. Protecting relevant rows with degree, knots, and weights unchanged can preserve those derivatives. The shortcut does not protect arbitrary trims or other adjacent boundaries. Three aligned rows are not a G2 proof.

Straight-curve control points may be collinear; a planar surface net is coplanar, not globally collinear. Apply SetPt only to intended regions and axes. Flattening rows indiscriminately destroys intended double curvature.

A transverse single-span degree2 three-row cap can be crowned by moving its middle row, but endpoint derivatives change. Two-sided G2 or a local recess needs suitable freedom and width; the three-row recipe is not universal.

## Trimming and offsets

Build good parents covering the design domain with sensible intersection margins. Curves can legitimately trim Breps when placement/projection is defined. Cutter surfaces must cross the relevant region; avoid near tangency. Intersect may produce open, closed, or multiple branches.

Project uses a defined projection direction and can have multiple targets; Pull maps by proximity. Choose according to intended mapping, not a one-face/many-face distinction. Record direction or plane.

Offsets express distance constraints; check numerical approximation and self-intersection. Offsetting analytic segments then re-blending may simplify control, but the new blend is generally not exactly equidistant. Translation/scaling of an inner shell is only a visual approximation. FilletSrf is face-based, FilletEdge Brep-edge-based; a blend transition is not a fixed-radius fillet guarantee.
