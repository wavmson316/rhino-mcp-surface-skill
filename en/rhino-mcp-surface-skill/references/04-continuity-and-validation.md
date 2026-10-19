# Continuity and evidence

G0 is positional agreement. G1 matches tangents/tangent planes with a valid two-sided neighborhood. G2 matches second-order geometry under suitable correspondence. G3 concerns higher variation. Define targets per seam from function and appearance.

Two surfaces can share the same straight edge and form a 90-degree fold. Matching normals supports only a tangent-plane check. Zebra appearance alone cannot prove numeric G2. A plane tangent to a cylinder is G1 but not G2. Zero curvature can legitimately satisfy G2; separately inspect whether the design was flattened.

## Numerical seam checks

Select real faces and adjacent edges, validate endpoints and full-edge correspondence. Bidirectional closest points remain diagnostics: inspect coverage, monotonicity, closed seams, folds, and side neighborhoods. Uniform parameter samples can miss knot/corner defects.

`sample_seam_g1.py` reports sampled position and unoriented tangent-plane angles. It does not evaluate G2 or prove no overlap/folding. Opposite normals may reflect face orientation; check engineering solid orientation separately. Do not skip failed samples and report a pass.

Reliable G2 requires a verified native continuity tool or second-order/shape-operator comparison in a common tangent basis, handling orientation, weights, parameter scale, and singularities. Principal-curvature magnitudes alone omit principal directions. Without a reliable method write “G2 intended; numerical validation incomplete.”

## Matching strategy

Fix a master and adjust a slave; use Average only if both may move. Select opposite-end preservation, iso direction, closest-point correspondence, and Refine from geometry. No switch combination always works. Refine can add freedom but also excessive knots; compare shape and complexity with manual insertion. Resolve conflicting sides with wider transitions, joint constraints, or new layout.

At symmetry seams check center-plane position, compatible tangent planes, and curvature when required. A temporary mirror can help. Mirroring neither smooths a seam automatically nor requires every center seam to be G3.

## Budgets and acceptance

Separate document units/tolerances, reference fitting, seam distance, tangent angle, curvature error, and manufacturing constraints. Curvature has inverse-length units; relative errors near zero need absolute safeguards and a defined metric. Existing settings remain unchanged without a task-based reason. CAD seam error and manufactured dimensional tolerance are different. Do not certify OEM Class-A without traceable standards.

| Category | Report |
|---|---|
| Shape | Fixed-camera silhouette, anchors, sections, negative spaces, critical features and reference conditions |
| Structure | Validity, face count, actual spans/degree/CP, singularities, naked/nonmanifold edges, solid orientation |
| Fairness/seams | Multiple reflection directions, section combs, curvature maps, and separate G evidence |
| Engineering | Thickness, offset intersections, clearances, motion, draft, and exchange round trips |

Use adequate display/analysis meshes and known units/color scales. A uniform mean-curvature map is not proof of good reflection; saddle contributions may cancel. Zooming small parts makes zebra useful too. Open-surface acceptance depends on delivery; unjoined adjacent Breps still have naked edges. Mesh export needs chord/angle/seam/normal checks. Rhino Weld angle is not a distance tolerance.
