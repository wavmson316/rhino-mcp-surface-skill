# Validation record — 1.1.0 documentation release

Geometry baseline executed on 2026-10-19: Windows, Rhino8.29.26063.11001, Rhino Python3, and the McNeel Rhino MCP connection. Version1.1.0 adds translated documentation/setup, construction playbooks, and an additional example builder. The original helpers and 45-case regression suite remain unchanged from1.0.0; the new example is tested separately below. Images were not read. No claim of this reviewer visually reading every source scan is inherited.

| Checks | Result | Evidence |
|---|---|---|
| Rhino in-memory regressions | 45/45 | [results](rhino-test-results.json), [suite](scripts/smoke_test_rhino.py) |
| Standalone analytical 2D cases | 17/17 | [results](outline-test-results.json), [suite](scripts/test_outline_metrics.py) |
| Syntax, local file links, entry, package hygiene | Run for release | [checker](scripts/check_release.py), [manifest](release-manifest.json) |

Tests added/deleted/edited no document objects. Object count, units, and tolerances matched before/after. A recorded pass on this version does not guarantee another Rhino/client; rerun [installation checks](INSTALL-CHECK.md).

## Rhino coverage

- Sampled coplanar seam, shared-edge90-degree fold, one-unit gap; invalid indices/sample counts/nonfinite tolerances rejected; closed edges explicitly require seam-aware pairing.
- Valid open face/four naked edges, actual directional spans, repeated-knot counterexample, missing ID with explicit doc.
- Control/interpolated/periodic curves, geometric tangent continuity of exact circle knots, exact elevation and curve properties.
- Correct rebuild overload, explicit deviation budget, missing budget rejection, underfit rejection, closed input rejection.
- Directed endpoint joins: aligned,90-degree,180-degree reversal, disconnected parallel, alternate pairing, invalid mode, closed shortcut rejection.
- Three/four-edge surfaces, shuffled directions, different degrees, disconnected boundaries, ruled surfaces, open/capped/closed-direction lofts, invalid loft inputs.
- Plane/sphere curvature, explicit image-plane dimensions and invalid size.

## 2D coverage

Identical/overlapping/disjoint rings, duplicate endpoint, reverse direction, four analytical concentric-circle area ratios, boundary distance, empty/degenerate/nonfinite inputs, invalid resolution, and rejected old buffering behavior.

These examples do not guarantee arbitrary shapes/resolutions have the same error. Thin features need higher resolution and local metrics. Only single simple outer rings are supported, not holes, components, or self-intersections; callers ensure valid topology.

## Unverified or uncertified

1. Full-domain surface G2/G3, second-order shape operators, and global absence of folds/overlap.
2. End-to-end reconstruction quality from real photographs, unique unknown scale/camera/backside recovery.
3. Thickness, self-intersection, draft, parting, shrinkage, assembly motion, or OEM Class-A compliance for real products.
4. STEP/IGES/STL round trips or material/layer preservation.
5. All native option matrices, GH workflows, other MCP servers, Rhino6/7/9, macOS, or other hosts.
6. Curvature helper evaluates the nearest underlying surface, not trimmed visibility or outward-solid signs. A single sample is not a fairness test.
7. Curve distance uses Rhino's numerical estimator, not an exact Hausdorff bound; localized features need independent checks.

## Previously fixed blockers

Fixed wrong Rebuild/Loft overloads, nonexistent EdgeSrf/curvature methods, and Unitize boolean multiplication that falsely called a90-degree curve join0 degrees. The old six-case suite did not exercise these helpers. New cases cover released helper families and counterexamples. Removed an unverified image-command builder; retained explicit reference-plane geometry. Split outline_metrics from Rhino dependencies and made old source notes non-executable references.

## New procedural construction benchmark — 1.1.0

[example_closed_shell.py](scripts/example_closed_shell.py) constructs a crowned enclosure in memory from explicit parameters: top degree3×4/CP4×5, four derived ruled walls, planar bottom, joined valid solid. The actual surface center reaches height40. **12/12** checks pass on the recorded Rhino8 environment; [results](example-test-results.json). This checks six parents, solid validity/orientation, edge status, degrees/spans, crown, volume, invalid inputs, and unchanged document state. It does not test G2, wall thickness, molding, or reference-photo similarity. See [playbook](references/12-object-construction-playbooks.md).
