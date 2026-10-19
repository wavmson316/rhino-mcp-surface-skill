# Parameter budgets and transferable recipes

This chapter gives numbers you can put to work immediately, and labels every one of them with its **source, its applicability conditions, and its failure signal**.
No value here is a universal standard; each one states the conditions under which it stops holding.

## Start by sorting the value categories

| Category | Examples | How to adopt it |
|---|---|---|
| Input fact | Drawing dimensions, material specification | Check units and revision, then treat as a constraint |
| Project budget | Seam, fit, angular error | Define the intent and target first, then set the tool |
| Exploration starting point | Concept transition width, display mesh | Adjust after trial surfaces and metric verification |
| Textbook case | Patch stiffness, Pipe gauge radius | Keep the context attached; it does not transfer by itself |
| Engineering standard | Vendor seam, draft angle, shrinkage rate | Needs a specification source and version; without one it is undetermined |

⭐ **What this edition adds back over the purely principled version**: categories three through five used to say only "not transferable". Each now supplies **a usable starting value, where it came from, and when it must be replaced**. The goal is to let you begin work, not to force a choice between "no value" and "copy this blindly".

---

## Unit conversion and exploration settings

### Conversion table (one physical quantity, several representations)

| Quantity | mm document | cm document | m document | inch document |
|---|---|---|---|---|
| 0.01 mm | `0.01` | `0.001` | `0.00001` | `0.0003937` |

⚠️ When you change units, state explicitly whether coordinates, reference geometry, and length tolerances are also scaled; **angles do not scale with length, while curvature converts as the reciprocal of length**.

### Exploration budget (metric, ordinary appearance work at 100–1000 mm)

| Item | Starting point | Applicability conditions | When it must change |
|---|---|---|---|
| Document absolute tolerance | `0.01 mm` | Routine appearance concept work | ⛔ Does not override an existing user setting; products with physical features under 1 mm need a different figure |
| Seam distance tolerance | `0.01 mm` | Within one document | Switch to the actual clearance value when the part carries an assembly gap requirement |
| Tangent-plane angle tolerance | `0.1°` | Glossy appearance surfaces | Structural faces may be looser; ⛔ do not treat it as a manufacturing tolerance |
| Shape fit tolerance | Define separately | Blurred photographs | Fit error on a blurred image is often **far larger** than the seam tolerance — the two do not conflict |

⚠️ **A document tolerance is not a manufacturing tolerance.** It is the resolution floor for geometric operations, not the acceptance standard for the part.

### Where scale conversion stops

**It applies only to similar concept forms.**

| Convertible ✅ | Not convertible ❌ |
|---|---|
| Concept transition width, fillet radius, groove depth (they scale with the overall form) | True wall thickness (set by structure and process) |
| Visible seam width, flange depth | Assembly clearance (set by the supply chain) |
| Display mesh density | Material shrinkage rate (set by material grade plus direction) |

⛔ **Do not derive wall thickness from the ratio of car length to speaker length.** The formula:

```
your radius = reference value × (your model's average dimension ÷ the original case's average dimension)
```

⚠️ Always re-verify after scaling: Rhino starts to misbehave when a fillet radius falls below absolute tolerance × 10.

---

## MatchSrf recipes

Inputs: the adjustable source surface, the target surface's real edges, master/slave assignment, target continuity, and each tolerance.

1. Record the original surface and its adjacent edges; check natural and trimmed edges, correspondence, and corner points.
2. If the starting discrepancy is too large, fix the volume first. Do not use the match to drag the shape into place.
3. Choose Position/Tangency/Curvature per the target; choose the preservation requirement for the other end.
4. Preserve iso can be used as an experiment. Compare Automatic, target-iso, and perpendicular-edge strategies against the form. Do not require identical UV on all edges.
5. Use Average only when both sides are allowed to move; for partially unequal long and short edges, try closest points and check coverage.
6. Trial Refine and manual InsertKnot separately, keep added degrees of freedom under control, then re-check all old edges and fairness inside the surface.

### Measured tolerance anchors

| Item | Textbook dialog screenshot value | Source | Note |
|---|---|---|---|
| Distance | `0.001 units` | Qinghua edition, p.46, fig. 3.44 + p.220, fig. 9.219 (identical in both) | The dialog state during the textbook's worked session |
| Tangency | `1.0°` | same | |
| Curvature | `0.05 %` | same | ⛔ **Not a dimensionless OEM standard** |
| Preserve other end | `Position` | same | |
| Match edges by | `closest points` | same | Enabled when the two edges differ in length |

⚠️ These are **the preset values present when the dialog opens**. They shift with the software version, user preferences, and the `Remember` setting.
Read your own dialog before you run anything, and ⛔ do not treat this value as "the correct tolerance" —
**it only records what the dialog looked like**. The real tolerance has to come from your project's tolerance budget.

### ⭐ The correct fix when you run out of CPs

`Refine match` is not a disabled option, but it **cannot solve insufficient degrees of freedom**:

```
too few CPs → Refine match adds many points and still misses the target continuity
            → correct fix: Setpt to align corresponding control points + InsertKnot (press S) to add points span by span
```

⚠️ Whether you have enough CPs is decided by `SpanCount` compatibility with the degree in the matching direction, ⛔ not by counting points.

### ⭐ The first thing to check when a match fails

⛔ **Do not start piling on CPs.** Check in this order:

```
1. Input curve degree, CP count, deviation — are they all in spec?
2. Are the degrees at the two matching ends compatible?
3. Are there enough CPs? (too few → Setpt + InsertKnot)
4. All of the above are fine and it still fails → change the matching direction, or match in two segments
```

Adding CPs only crowds the control net and makes the reflection worse. **Insufficient degrees of freedom is not solved by adding points.**

---

## Pipe-cut bands and bridging

Applies when: two parent surfaces meet, you are allowed to cut out enough transition domain, and the final transition is not required to be a strict fixed radius.

```text
Intersect to find the intersection curve → Join related curve segments if needed
→ Pipe to build the cutting gauge → extend the gauge past the target boundary
→ Split/Trim the parent surfaces, keeping the sides you need
→ A: BlendSrf; or B: design sections + Sweep2 with real face-edge continuity set
→ check seam, band width, interior curvature, and corner regions
```

Joining the intersection curve is not joining the parent surfaces, and neither one raises continuity automatically.

### ⭐ Two operating facts you must remember

| Item | Fact | Consequence |
|---|---|---|
| **`Pipe` Cap defaults to Yes** | **press `C` to turn Cap off** when building a gauge | Left on, the pipe is capped at both ends and cannot pass through to trim |
| **Radius value** | One textbook case used roughly `2/3` of the intended blend width | ⚠️ A local case, **not a guarantee of constant width**; work from the transition domain you actually need |

⚠️ A capped cutting solid can still trim a surface, so ⛔ it is not correct to assert "Cap=Yes means it can never cut".
That said, **turning Cap off while building a gauge makes extending and trimming easier** — that is an operating convenience, not a geometric requirement.

### ⭐ BlendSrf selections cannot be undone

Once a boundary curve is selected in `BlendSrf`, **it cannot be deselected**. Picking one wrong edge means starting over.

```
The correct way to select multiple edges: select one → press A to select all connected boundary curves
```

⚠️ This is an efficiency problem, not a geometry principle, but it will visibly slow you down on the job.

---

## Low-dome button candidates

Inputs: outline, crown height, side wall, and the target softness of the edges.

### ⭐ Two ways to get the outline continuity (the textbook states both)

| Approach | Continuity | Where to use it |
|---|---|---|
| Two parallel lines plus a semicircle at each end | **G1** (exact) | ⛔ **Enough for the overwhelming majority of buttons**, and easy to resize later |
| `Blend` command to round both ends | **G2** | Glossy surfaces, highly visible buttons |

⚠️ **Do not start at G2.** Button dimensions change frequently, and G2 constraints slow every revision down.

### ⭐ The three-row method for a low dome

Build the cover surface across its width as a single-span Degree 2 → you get 3 rows of control points → **drag only the middle row**.

⚠️ The three-row method changes the end derivatives, so ⛔ it cannot guarantee G2 at both ends. Use more degrees of freedom when you need curvature control at the ends.

### Full button recipe (the textbook's 7 steps)

```
1. Draw the button outline (straight lines + semicircles = G1)
2. Extrude into a side wall (press C to cap it, making a solid)
3. Split the outline into two symmetric halves with a straight line
4. Loft the two split curves → flat surface
5. ChangeDegree to drop the U direction to degree 2 (press D as needed) → 3 rows of CPs
6. Move only the middle row (⛔ the first and last cannot be selected) → domed surface
7. Pipe → Split/Trim → BlendSrf → smooth the seam
```

⚠️ When using `Patch` for a button face, **do not select `Adjust tangency`** (the textbook flags this explicitly).

---

## Patch / Network

### ⭐ Patch's real defect is not "poor quality"

The control point count of a `Patch` surface is **unrelated to the input curves**. That is a **loss of topological degrees of freedom** —
it blocks everything downstream: `MatchSrf`, editing, and knot insertion.

⛔ **Do not use Patch for a primary glossy face.** Its correct use is: initialise the central volume, fill corner regions, and then **re-verify from scratch**.

⚠️ Patch's point distance is a length quantity; trial `spans`/`stiffness` against your data and scale.
The `spans=2`/`stiffness=0.1` in the textbook's older example only records the settings for that one approximated dome.

### NetworkSrf

First check the two families of intersections, their order, and the input semantics for edge continuity. A looser fit tolerance usually yields a simpler output but may increase deviation;
record the actual output and verify the error. ⛔ Do not treat `0.01`/`1`/`10` as fixed rungs that hold across units.

**Must set**: **Edge curve** control — it determines the edge-line accuracy of the output surface.

---

## Meshing and output

### ⭐ Two quantities you must confirm by measurement

| Item | Textbook formula | Note |
|---|---|---|
| **Minimum edge length** | `average model dimension ÷ 1000` | ⛔ This is a rule of thumb, **not a hard standard**; re-derive it against your chord-height, angle, seam, and face-count budget |
| **Maximum angle** | `10.0` (**absolute**) | Does not vary with model size |

⚠️ The **failure signal** for the textbook `÷1000` rule: when the shortest edge comes out too large, the refinement a local region needs gets cut off.
If detail refuses to appear, re-derive the value instead of defending the formula.

### Exploration starting point

For a metric appearance preview, try **chord height 0.05 mm and angle 10°** first, then zoom into the critical regions to verify.
These are **exploration values**; re-derive them for very small features, printing, or engineering exchange.

### Mandatory before export

```
UnifyMeshNormals → Weld → Check → Audit → Audit3dmFile
```

⚠️ Verify `Weld` semantics against your current version — Rhino's mesh Weld and other packages' distance-based point merging **are not necessarily the same operation**.
⛔ Do not copy another package's merge threshold.

⚠️ When emitting formats such as STL that **do not reliably carry units**, you must state the units alongside.

---

## Measured starting points for curves and surface construction

| Item | Starting point | Source / condition |
|---|---|---|
| CP count, open curve | `= degree + 1` (→ single span) | General case; ⛔ does not apply to closed or periodic curves, where CP count = degree |
| **Span count** | ⛔ **Read `SpanCount`** — do not compute `CP count − degree` | Repeated knots and periodic structure break that relationship |
| Rebuild deviation | Step through degrees until **Max deviation < 0.1 mm** | Measured in the English car book; ⛔ do not blanket-apply "degree 5, 6 points" (a straight line overfits into a wave) |
| **Opposite edge degrees** | **Must match** before `EdgeSrf` | ⛔ When they differ the software compensates with interior knots, and the result is **distortion rather than an error message** |
| Straight-run CPs | **Must be collinear** | ⛔ Non-collinear → a bulge in the straight run (the textbook stresses this in two independent places) |

### ⭐ Control point discipline at an intersection

**The last 3 rows of control points at an intersection determine surface curvature; the remaining rows can be edited freely without breaking continuity.**

| Free to move | ⛔ Do not move |
|---|---|
| Row 4 and beyond | **The last 3 rows at the intersection** |

⚠️ This is a **construction rule for a constrained situation** (it holds when degrees match, weights agree, and parameter scales are comparable),
⛔ **not a mathematical proof for arbitrary NURBS**. Be careful about the principle, but operate by the 3-row rule on the job.

### ⭐ Fillet size must match part scale

Across 620 pages, the textbook's measured fillet range is **0.1 ~ 90 mm** — a spread of nearly a thousand to one.
**That distribution is itself the evidence that no single value travels everywhere.**

| Part | Textbook case value | Source |
|---|---|---|
| Lens / glass | `1 mm OffsetSrf` + Fillet `0.5~1` | English car book, p.365 |
| Sheet-metal seam | seam width `3 mm` / depth `6 mm` | English car book, p.382 |
| Mirror root | `90 mm` | English car book |
| Hard-surface edge | `16 mm` | Qinghua edition, p.146 |
| Hard-surface degree elevation | `ChangeDegree` → **degree 4** | Qinghua edition, p.171 |

⚠️ **Every value above is an automotive case.** Convert for a different product category using the scale formula above, then re-verify.
⚠️ **Visible seam width, flange depth, and sheet thickness are three different things** — ⛔ you cannot treat a 6 mm visual extrusion as real sheet-metal thickness.

---

## Curvature verification anchors

### ⭐ Curvature map parameters

| Item | Textbook screenshot value |
|---|---|
| Style | `Mean` |
| Curvature range | `0.1` |
| Show isocurves / Adjust Mesh | ✔ |

⚠️ A fixed colour scale cannot certify a pass across the board — mean curvature, normal sections, and reflection all have to be read together.

### ⭐ When you must run it

```
Run CurvatureAnalysis immediately after every base surface is built
```

| Map pattern | Verdict | Action |
|---|---|---|
| Regular and even | Reflection is acceptable | Move to the next stage |
| Local banding / irregularity | ⛔ **Reflection will be wrong** | **Fix it immediately** — do not defer until you are deep into the details |

⚠️ Changing shape after surfaces are locked in is extremely expensive. **The base-surface stage is the only cheap quality window you will get.**

---

## Silhouette IoU (the only digitalisable fidelity check)

```python
import sys; sys.path.insert(0, str(skill_root / 'scripts'))
from outline_metrics import silhouette_iou
r = silhouette_iou(model_outline, photo_outline)
```

### Validated against analytic theoretical values (17 tests)

| Case | Measured | Theoretical |
|---|---|---|
| Self-comparison | 1.0000 | 1.0000 |
| Concentric circles R11/R10 | 0.8262 | 100/121 = 0.8264 |
| Concentric circles R5/R10 | 0.2500 | 0.2500 |
| Two squares, half-overlapping horizontally | 0.3350 | 1/3 = 0.3333 |

### ⭐ Three traps you have to know about

| Trap | Consequence |
|---|---|
| ⛔ Using point-set Jaccard instead of rasterising | Every sampled point of a scaled copy falls inside the other outline, so **a 10% size error looks like a perfect score** |
| ⛔ Leaving boundary-point ambiguity unresolved | Of 40 points on a circle only 20 register as inside and the IoU collapses (a tolerance must be added) |
| ⚠️ **IoU ≠ dimensional accuracy** | Scale concentric circles by r → IoU = r². **At a 10% size difference the IoU is still 0.83** |

⚠️ IoU is only valid for **one projection**; a perspective photograph must have its camera fixed before you compare.

---

## Minimal calls into this package's code

```python
# doc passed explicitly; prepare the data inside the Rhino host, do not modify the document.
from nbs_geometry import rebuild_to_single_span, edge_srf_4
candidate = rebuild_to_single_span(curve, degree=3, doc=doc,
                                   max_deviation=fit_budget)
face = edge_srf_4(doc, c1, c2, c3, c4)
```

A failed candidate rebuild does not mean the input is noisy — a single span may simply be unable to express it. Adjust the CV layout, use multiple spans, or work in segments. Do not force a high Degree and pass it off as accuracy.

---

## Class-A: ⚠️ automotive-specific, not a general standard

The table below comes from an **automotive house-standard system** (1–2 mm class sheet-metal covering panels).

| Metric | General | Strict house standard |
|---|---|---|
| Gap between adjacent surfaces | ≤0.005 mm | ≤0.001 mm |
| Tangent change | ≤0.16° | ≤0.10° |
| Curvature change | ≤0.05 | ≤0.02 (BMW/VW), 0.03 (Toyota) |
| Centre-plane symmetric surface | G3 | G3 |
| Surface CPs | 6~8 in UV, degree ≤6 | same |
| Large-panel deviation | ≤3 mm | same |

⛔ **Scope warning**: applied to appliances, toys, furniture, and consumer electronics, this tolerance set is usually **too strict** —
single-piece injection moulding tolerance commonly sits at the 0.1–0.3 mm level, and 0.5 mm may already be enough for a small toy.
**Confirm which manufacturing system your product belongs to before quoting any of this**, and prefer that system's actual specification.

⚠️ "Curvature difference 0.05" must always state its **unit and definition** — curvature is the reciprocal of a length, not a dimensionless house standard.

---

## Licensing and sources

The values in this chapter come from *Rhino3D Industrial Modeling and Design*, 3rd edition (page-by-page visual close reading of all 365/365 pages),
*3D Car Modeling with Rhinoceros*, 624 pages, plus measurements taken on this machine with Rhino 8.29.
Page citations distinguish printed pages from PDF pages (Qinghua edition PDF page = printed page + 23). No scans are distributed with this package.
