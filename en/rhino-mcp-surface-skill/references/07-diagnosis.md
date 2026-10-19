# Diagnosis and fallback

Propose one testable cause per round and compare the geometry/metrics before and after. If two rounds produce no improvement, re-evaluate upstream. What follows is a set of candidate causes, not a one-to-one mapping from symptom to command.

| Symptom | Check | Next step |
|---|---|---|
| Looks right from one view, skewed when you rotate | Camera, depth, sections and occlusion | Return to the volume; do not add detail to paper over it |
| Loft/Sweep twists | Directions, closing seams, frames, section order | Unify the correspondence and redo |
| Four edges match but the interior bulges | Parameter speed, corners, inner sections | Adjust the boundaries or change the surfacing/layout |
| Blend bulges where it widens | Pairing, sections, bulge, width | Try Same height shapes or restructure the sections |
| ⭐ **BlendSrf visibly bulges and twists in the middle** | Mixing proportions makes the CPs shrink where the band is narrow | ⛔ **Do not add points and do not drag the slider** — tick `Same height shapes` |
| ⭐ **Pipe cannot pass through a trimmed region** | Is Cap set to Yes | **Press `C` to turn Cap off**; then ExtendSrf, press `T` then `S` |
| ⭐ **A surface bulges along a straight run** | Are the CPs on that run collinear | Force them collinear |
| ⭐ **A surface goes skewed when opposite edges differ in degree** | Are the degrees of all four edges consistent | Unify the degrees (the software compensates with interior knots; no error message warns you) |
| ⭐ **An extruded surface only reaches G0** | The V direction of `Extrude` has only 2 CPs | `ChangeDegree` in V from 1→3 to add degrees of freedom |
| ⭐ **Still twisted after Setpt** | Did you only align the outermost row | **Start from the middle** and align every row |
| ⭐ **Fewer than 6 CV rows at the end, and the G2 change landed on the wrong end** | Matching direction and the CP count at the end | Add CPs or **change the matching direction** |
| ⭐ **A surface bulges locally** | Too **many** control points | ⛔ Reduce the CP count (over-fitting causes bulges) |
| ⭐ **Change one place and another place falls apart** | Knot coupling in a multi-span structure | Revert to a single span, or split into independent surface groups |
| ⭐ **A highlight converges and wrinkles at a point** | A singularity in a three-/five-sided patch | Add points to turn it into a four-sided structure, and move the convergence point out of the highlight |
| ⭐ **A recess that was meant to be added after the fillet cannot be made / its entrance is sealed** | The order is reversed | ⛔ All recesses must come before the fillets and gap blends |
| Star-shaped highlight | A pole, an overly narrow corner band, or several surfaces converging | Enlarge the corner region, move the convergence point |
| Match succeeds on one edge and fails on another | Constraint conflicts, degrees of freedom, holding the far end | Fix the master surface; change the width, the multi-edge constraints or the layout |
| Refine inflates the point count | Tolerance, target complexity, initial placement | Compare against manual local knot insertion and rebuilding; do not permanently ban Refine |
| ⭐ **Refine inflates the point count but still misses the target G-level** | Is the CP count fundamentally insufficient | ⛔ Refine does not solve this; use `Setpt` + `InsertKnot`(S) |
| The shape does not change after degree elevation | Is it an exact degree elevation? | If Degree has increased, that is expected; **if the intent was to change the shape, Deformable (D) must be enabled** |
| Join fails | The actual gap, units, short edges, correspondence | Recompute the intersection or rebuild; do not loosen the global tolerance first |
| Join succeeds but edges still show | Tangent plane and curvature are discontinuous | Measure G1 and G2 separately |
| Trim fails | The tool does not pass through, projection direction, tangency | Inspect the independent intersection curve and endpoints; extend locally |
| Offset self-intersects | Radius of curvature, concave corners, thickness | Adjust the design, thickness or corner handling; do not fake it with a translation |
| The numbers pass but the reflection is poor | Sampling misses detail, display mesh, waviness inside the surface | Densify locally and add sections/reflections from multiple directions |
| Curvature colours are even yet something is wrong | The colour scale, cancellation by averaging, the mesh | Check principal curvature, sections and reflection |
| ⭐ **Problems are invisible on a small product** | The faces are too small; Zebra/EMap lacks resolution | Per-surface `CurvatureAnalysis` |
| A fillet breaks up | Radius, short edges, corner compatibility, feature order | Split the corner region, change the build order, or use a Blend |
| MCP timeout | Whether the operation actually completed, the object count | Check the IDs and status; a blind retry is forbidden |
| ⭐ **Screenshots hang / the session crashes** | Too many control points in the scene | Put complex parts on their own layer and hide them promptly |
| An API exception | The true signature, the host, the return type | Read the docstring and reproduce in memory |

Fallback ladder: local parameters → boundaries/sections → transition band → adjacent-surface degrees of freedom → untrimmed parent surface → patch layout. Do not attribute every failure to multi-span structure or too many points; insufficient degrees of freedom also causes failure. Keep genuine sharp edges and reasonable negative curvature — do not use camera moves or hiding objects as a fix.

### ⭐ Upstream fallback path when a patch is stuck

When a surface repeatedly refuses to come out right, the standard move is **upstream**, not to add points further downstream:

```
Current surface fails
  → fall back to the dependent surface one level up (transition band / corner region) and adjust the boundaries
    → still not right → fall back to the untrimmed parent surface and change the UV flow
      → still not right → re-plan the patches (move the seams, enlarge the transition zone)
        → still not right → substitute an analytic surface / Sweep / NetworkSrf
          → still not right → Untrim and redo the Blend
```

⛔ **Adding more points along the same path is the biggest waste of time**: no number of CPs can fix the distortion caused by a layout error.