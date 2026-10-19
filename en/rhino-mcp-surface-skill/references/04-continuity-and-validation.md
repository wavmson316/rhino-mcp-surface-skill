# Continuity and acceptance

## Targets and evidence

G0 is positional matching; G1 is tangent or tangent-plane matching with a sensible neighbourhood on both sides; G2 is second-order geometric matching under a suitable parameter correspondence. G3 involves higher-order variation. Set the target per seam according to what that seam is for — planar surfaces, structural parts and gloss surfaces can each need different levels.

Two surfaces can share an identical boundary curve and still meet at 90°; agreeing normals only support a tangent-plane check; zebra lines that run smoothly do not prove numerical G2. A plane meeting a tangent cylinder is a counterexample: that is G1, not G2. Zero curvature can genuinely satisfy G2 — that is not a "fake G2" — but you still have to check whether the design has been flattened.

### ⭐ Three wrong ways to judge G2

| Wrong | Why it is wrong |
|---|---|
| Judging G2 from the curvature of the shared boundary curve | The curve only describes the edge; the cross-curvature on either side was never measured |
| Reporting G2 because the normals agree on both sides | Agreeing normals only support G1 |
| Passing a curvature-vector test by taking `abs(dot)` | ⛔ Opposite curvature directions must not be cancelled by taking the absolute value |

⚠️ For contrast: `abs(dot)` is **correct** for comparing **undirected tangent planes** (`sample_seam_g1.py` does exactly that). It is only wrong on **curvature vectors**. The two must not be mixed.

### ⭐ Do not demand G2 at the shade boundary

**There is a break in design intent at that location, and forcing continuity there destroys the design.**

⚠️ This and "the shade boundary cannot be used as a patch boundary" are **two different things**: the first says it is a product of lighting and you cannot derive patches from it; the second says that location is genuinely supposed to turn, and you should not smooth it away.

## Numerical checks on surface seams

Select the actual surfaces and adjacent edges, and check the endpoints against the whole-edge correspondence. A bidirectional closest-point result is only a diagnostic; you must still check coverage, monotonicity, closing seams, reversals and the neighbourhoods on both sides. Uniform parameter sampling misses local knot and corner defects.

`sample_seam_g1.py` reports only a finite set of sampled positions and the undirected tangent-plane angle. It does not judge G2 and does not prove the absence of an inflection reversal. Opposed normals may only mean the surfaces are oriented in opposite directions; for engineering solids, direction must be checked separately. A failing sample must not be skipped and then reported as a pass.

Reliable G2 requires an edge continuity analysis verified on the current version, or a comparison of second-order / shape operators in a common tangent-plane basis, handling normal direction, weights, parameter scale and singularities. Comparing only the two principal curvature values still leaves out the principal directions. Without a reliable method, write "G2 target, not numerically verified".

### ⭐ When a curvature check is mandatory

```
Run CurvatureAnalysis immediately after each base surface is built
```

| Colour map pattern | Judgement | Action |
|---|---|---|
| Regular and even | Reflection acceptable | Move to the next stage |
| Local bands / irregular | ⛔ Reflection will have problems | **Fix it now** — do not defer until the details are well advanced |

⚠️ Changes after a surface is signed off are extremely expensive. **The base-surface stage is the only cheap quality window.**
⚠️ **Zebra/EMap lacks resolution on small products**, so per-surface curvature analysis is mandatory. See the parameter reference for the colour map settings.

## Matching strategy

Fix the master surface and adjust the slave. When both are allowed to move, use Average. Decide whether to hold the far end, the iso-direction strategy, closest points and Refine; there is no permanently correct combination of toggles. Refine can improve the fit but can also inflate the point count, so compare the result, the structure and the deformation; manual knot insertion is also a candidate. When edges conflict, consider overall constraints or a new patch layout rather than matching edge after edge indefinitely.

### ⭐ When matching fails, check the input — do not pile on CPs

```
1. Are the degree, CP count and deviation of the input curves acceptable?
2. Are the degrees at the two matched ends compatible?
3. Is the CP count sufficient?
4. If all of the above are fine and it still fails → change the matching direction, or split it into two matches
```

⛔ Adding CPs only crowds the control points and makes the reflection worse — **insufficient degrees of freedom cannot be solved by adding points.**
`Refine` can add degrees of freedom but **cannot solve a fundamental shortage of them**.

### ⭐ Common preparation for edge-to-edge matching

| Item | Rule |
|---|---|
| Trimmed edges are hard to match | Use the untrimmed parent surface, extend the parent surface, rearrange the natural edges, or add a transition band |
| `ShrinkTrimmedSrf` | Can affect the recoverable range; it is not a general-purpose preprocessing step |
| `RebuildEdges` | Mainly repairs edge representation and **will not fair the underlying surfaces**; neither is general-purpose preprocessing |
| `BlendSrf` cannot be deselected once picked | When selecting multiple edges, pick the first one and then **press `A`** |
| Dialog preset values | A textbook photo shows `0.001 units / 1.0° / 0.05%`, ⛔ but those are **software defaults, not correct tolerances** |

For mirroring, first verify that the edge lies on the symmetry plane and that the tangent planes are compatible, and check curvature where the target requires it; a temporary mirror copy can be used for the matching.

### ⭐ When to mirror

`Mirror` **only copies the geometry; it does not change the continuity at the seam**.
To get G2 on the centreline, you must achieve the match on that side **before mirroring**:

```
Mirror a copy → use it to MatchSrf the original surface up to G2 → delete the mirror → Mirror again
```

⚠️ Mirroring does not smooth anything automatically, and you do not have to force G3 on every centreline — the target comes from the user and the project.

## Tolerance budget

Define units, document absolute/angular tolerances, reference fit, seam distance, normal angle, curvature error and manufacturing constraints separately. Curvature has units of 1/length; a relative difference near zero is unstable, so an absolute threshold and its definition are required. Where tolerances already exist, read and keep them; for starting points on a new project see the [parameter reference](10-parameters-and-recipes.md).

A CAD seam error is not the same as a physical manufacturing dimensional tolerance. Class-A is a combined requirement covering shape, reflection, control structure and project specifications; without a traceable standard, do not certify a supplier's Class-A surface.

## Four parallel acceptance tracks

| Track | Content |
|---|---|
| Shape | Fixed-camera silhouettes, anchor points, primary sections, negative space, key details; data conditions and the error method |
| Structure | Validity, face count, true span/Degree/CP, singular edges, naked edges, non-manifold edges, solid orientation |
| Fairness and seams | Zebra/EMap from multiple directions, section curvature, curvature colour maps, per-edge G-level evidence |
| Engineering | Thickness, offset self-intersection, clearances, assembly/motion, draft, export round-trip |

Reflection analysis needs a display/analysis mesh fine enough for the job; the colour map range and units must be fixed. An even mean-curvature colouring does not prove the absence of problems, and averaging also hides saddle information. Small parts can be magnified for the Zebra check; no valid diagnostic is forbidden. Whether an open surface is acceptable is a contract question; adjacent Breps that have not been joined still have naked edges. Solids require a check for valid watertightness and orientation; an appearance shell is legitimately allowed to stay open. For mesh export, check chord height, angles, normals, cracks and sharp edges; Rhino Weld is used by its angle semantics, and an absolute distance tolerance must not be substituted for it.