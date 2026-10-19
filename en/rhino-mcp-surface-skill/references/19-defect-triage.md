# Defect triage and blocking checks

Preserve failed candidates and inputs. Distinguish invalid/empty output, unintended gaps, folds/self-intersections, duplicate coincident faces, geometric creases and display-mesh artifacts.

None/empty/invalid/zero-area outputs fail the step. Inspect source constraints, units, correspondence and API status. Naked edges are defects only where closure is required. For folds/pinches inspect seams, rail pairing, corners and parent domains; widen/repartition rather than hiding geometry with Join or loose tolerances. For flicker/checkerboarding first isolate duplicate/coincident geometry before changing hole dimensions. For display cracks compare actual boundary distances and mesh settings. For arrays validate one sector and its rotated neighbor before replication.

Three gates per step:

1. Inputs: all valid, no silent dropping, sources/directions/seams/order recorded; network crossings consistent and cutters actually cross targets.
2. Outputs: only direct API returns or tracked new objects, never the first pre-existing surface in the scene. Check status, validity, area, count, duplicates and nonmanifold edges. Require solids/orientation only by contract.
3. Shape/adjacency: independent silhouettes, between-station volume, local sections and seam correspondence. IsValid, volume and watertightness do not independently prove correct shape or absence of self-intersection.

```python
from quality_gate import check_candidates
report = check_candidates(result['breps'], require_solid=False)
if not report['passed']:
    raise ValueError(report['errors'])
# Complete task-specific shape/seam checks before publish_patch.
```

The structural helper explicitly lists unverified reference similarity, self-intersection/overlap, fairness and G levels. A valid open parent does not certify a solid delivery. Use verified geometry tools for self-intersection; sampling can miss localized defects. Do not conceal failures with JoinEdge, global tolerance changes or deletion followed by a completion claim. Revert to accepted parents with the cause recorded.
