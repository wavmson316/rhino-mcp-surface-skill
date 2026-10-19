# Parameter budgets and conditional recipes

## Distinguish numeric roles

Input dimensions/material specifications are constraints after checking units/revisions. Project seam/fitting/angle budgets require definitions. Exploratory widths or display meshes need trial validation. Tutorial settings retain their context. Manufacturing/OEM limits require a source and revision; otherwise they are unknown.

## Units and exploratory budgets

0.01mm is 0.001cm, 0.00001m, or about 0.0003937in. This is conversion, not a universal project tolerance. Decide whether unit changes scale coordinates/references/tolerances; angles do not scale with length and curvature scales inversely.

For roughly100–1000mm ordinary concept exteriors, document/seam tolerance0.01mm and tangent-plane angle0.1 degrees may be an explicitly provisional starting budget. They are not manufacturing standards and do not overwrite existing settings. Blurry reference fitting should reflect larger source uncertainty.

Only geometrically similar concepts justify proportional dimensional scaling. Real thickness, fillets, clearances, and shrinkage come from function/material/process; do not scale a car's wall parameters by a speaker's overall length.

## MatchSrf recipe

Inputs: editable source, actual target face edge, master/slave, continuity, and budgets.

1. Preserve originals/adjacency; inspect natural/trimmed sides and corners.
2. Bring large shape discrepancies closer before matching.
3. Select Position/Tangency/Curvature and opposite-end preservation from requirements.
4. Compare iso direction strategies; no universal common UV orientation.
5. Average only if both may move. For partial unequal boundaries try closest points and inspect coverage.
6. Compare controlled Refine with manual knot insertion; recheck old seams and interior fairness.

Old tutorial dialogs showed distance0.001 units, tangency1 degree, curvature0.05 percent. These are case settings, not eternal software defaults or universal dimensionless standards. Define the current curvature-error metric.

## Pipe-cut band and bridge

Suitable when parent surfaces intersect and a sufficiently wide transition can be removed, without requiring the final band to have a fixed fillet radius.

```text
Inspect Intersect curves → optionally Join related curve fragments
→ Pipe cutter → extend beyond relevant boundaries
→ Split/Trim and retain intended sides
→ A: BlendSrf; or B: designed sections + Sweep2 with real-edge constraints
→ inspect seams, width, interior curvature, and corners
```

Joining intersection curves is not joining parent faces; neither establishes smoothness. An open pipe is convenient for extension, but capped cutters can also cut. Pipe radius depends on required removal; a width-times2/3 example is not universal or a fixed-radius guarantee.

## Crowned button candidate

Define outline, crown, walls, and softness. Lines plus semicircles typically form G1; Blend can provide desired curvature transitions. A transverse single-span degree2 three-row cap can crown by moving its middle row. Arbitrary degree reduction does not guarantee three rows or endpoint G2. Use enough freedom and separate seam acceptance.

## Patch and Network

Patch sample spacing is a length, while spans/stiffness require data/scale experiments. Adjust tangency depends on usable actual face edges and desired constraints; do not disable it universally. A tutorial's spans2/stiffness0.1 only describes one approximate cap.

For Network check two-family intersections/order and boundary semantics. Looser fit tolerances may simplify output but increase deviation; record actual results. Numeric0.01/1/10 settings are not cross-unit presets.

## Mesh and export

Set chord/angle error, minimum feature size, and face-count budget. For a millimeter concept preview, chord0.05mm and angle10 degrees can be provisional, followed by enlarged feature checks. Tiny features, printing, and engineering exchanges need different budgets.

An excessive minimum edge can block necessary refinement; initial quad count does not replace chord control. Check seams, sharp normals, and slender triangles. Rhino Weld angle differs from distance-based vertex merge. Formats without reliable units, such as STL, need accompanying unit metadata.

## Minimal helper call

```python
from nbs_geometry import rebuild_to_single_span, edge_srf_4
candidate = rebuild_to_single_span(curve, degree=3, doc=doc,
                                   max_deviation=fit_budget)
face = edge_srf_4(doc, c1, c2, c3, c4)
```

A rejected rebuild may indicate insufficient single-span representation, not noisy input. Adjust layout, use multiple spans, or split instead of forcing a high-degree approximation.
