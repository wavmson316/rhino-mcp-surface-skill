# Patch Route Selection and Curve Retention

> This document solves two problems that keep recurring:
> 1. An AI meets a complex object, "draws a few silhouette lines + `Loft`", and produces a surface with a **distorted interior volume**
> 2. The input curves used to build the patch are not kept in the file, so the user **cannot make a second round of edits**
>
> ⚠️ This document is not optional reading. **Mandatory before starting work on any complex object.**

---

## 1. ⛔ Why "draw a few lines + `Loft`" is wrong

### 1.1 `Loft` creates no control points, it only *connects* them

`Loft` performs **interpolation** between adjacent sections. Few sections → wide interpolation spans → the surface has
**no constraint at all** inside those spans. Everything you see on the sections is correct, but **the part between two
sections is entirely made up**.

```
3 sections + Loft         5×5 grid + NetworkSrf
                                           
 ┃      ┃            ┃ ┃ ┃ ┃ ┃
 ┃      ┃     →      ┃ ┃ ┃ ┃ ┃
 ┃      ┃            ┃ ┃ ┃ ┃ ┃
 ┃      ┃            ┃ ┃ ┃ ┃ ┃
                    
 No constraint          Constrained
 between sections       everywhere between sections
```

### 1.2 ⭐ Measured: one shell, two approaches

Measured on an 80×50×12 mm shrink-wrap shell (25% shrink):

| Approach | Input curves | Trustworthy interior volume |
|---|---|---|
| 3 sections + `Loft` | **3** | ⛔ Completely distorted between sections |
| 5×5 grid + `NetworkSrf` | **50** | ✅ Constrained in every cell |

⚠️ Key conclusion: **surface quality depends on how many input curves you have and where they sit, not on which command you use.**

⛔ `Loft` is not a bad command, and `NetworkSrf` is not a good command ——
**lofting with 3 lines is wrong; lofting with 50 lines is fine** (just unnecessary).

### 1.3 ⛔ Three typical misuses of `Loft`

| Misuse | Consequence |
|---|---|
| Using `Loft` for a **four-sided patch** | 4 closed edges are not an *ordered section family*; you get a twisted tube-like surface |
| Drawing only the outer outline of the sections, with no **interior structure lines** | The interior is unconstrained, so the volume is invented out of nothing |
| Trying to rescue `Loft` by **adding more sections** | Switch to grid lines or `NetworkSrf`; adding sections is not the fix |

⚠️ Exception: `Loft` is genuinely correct for an **equal-section family** — sections of similar shape in progressive
positions, with no interior control needed (tapered rods, beams of constant section). ⛔ **Complex free-form surfaces are
not in this category.**

---

## 2. ⭐ The order of decisions when choosing a patch route

⛔ **This is not "pick a command", it is "first decide how many directions need constraints".**

```
Ask yourself: how many control points does this surface need in the 【U】 direction? And in the 【V】 direction?
```

| Constraints needed | Correct approach | ⛔ Do not use |
|---|---|---|
| Several in U, a single one in V | `Sweep1` (path + section) | Forcing a `Loft` |
| Several in both U and V (**by far the most common**) | `NetworkSrf` (grid lines) | ⛔ **`Loft`** |
| Only 4 boundary edges, interior is free | `EdgeSrf` | `Loft` |
| A transition band between two parent surfaces | `BlendSrf` | `Loft` |
| An existing surface needs a shape change | `MatchSrf` | Rebuilding from scratch |
| Equal sections (similar shape, progressive position) | `Loft` ✅ | — |
| Fully regular (revolution / extrusion) | `Revolve` / `ExtrudeCrv` | — |

### 2.1 ⭐ How to lay out grid lines (the practical side of `NetworkSrf`)

**Key principle: grid density is decided by how the curvature of the surface varies, not by whether it "looks good enough".**

```
1. Draw the 【boundary lines】 first —— the four edges of the surface; they are hard constraints
2. In each direction, divide the edge evenly and lay lines inward
3. Densify where curvature changes fast, keep flat areas sparse
4. ⛔ Do not let grid lines run far past the boundary (just enough intersection margin)
5. ⛔ The two line families must 【intersect cleanly】 —— non-intersecting lines produce garbage surfaces
```

**Verification step**: check immediately after `NetworkSrf` —
- Is the face count ≈ (number of U lines − 1) × (number of V lines − 1)?
- Are there stray fragments?
- Is the colour map from `CurvatureAnalysis` even?

### 2.2 ⭐ When `Loft` is the right answer

⛔ **Do not ban `Loft` outright** —— it is correct in these cases:

- The sections have the **same shape and only translate/rotate along one direction** (tapering, arrayed rods)
- Straight runs of lofted furniture (the section is just one profile translated)
- **Adding sections genuinely expresses the form** —— meaning the form was defined by a section sequence to begin with

⛔ **Getting this call wrong**: if "adding two more sections" makes the shape more accurate, that is a grid-line problem,
not a section problem.

---

## 3. ⭐⭐ Patch curves must stay in the file

### 3.1 Why this is a hard requirement

The input curves used to build the patch **are the user's future edit entry points**. Throwing them away means:

- ⛔ The user cannot change the form —— the entire surface has to be redone
- ⛔ There is no way to answer "why is this edge here?"
- ⛔ There is no way to adjust the form locally —— the surface is baked in
- ⛔ The deliverable is **not editable**, which defeats the point of NURBS

⚠️ This is a **delivery requirement**, not a "best practice".

### 3.2 ⭐ Rule: all patch input curves go into the `Lines` layer

```
Whenever a surface is constructed, put 【all of its input curves】 into the Lines layer.
```

| Patch method | Curves that must be retained |
|---|---|
| `Loft` | All section curves |
| `Sweep1` | Path + section |
| `Sweep2` | **Both rails + all sections** |
| `NetworkSrf` | All U-direction lines + all V-direction lines |
| `EdgeSrf` | All boundary edges (3 or 4) |
| `BlendSrf` | The edges on both sides |
| `Patch` | All input curves / sample points |
| `MatchSrf` | The target edge and the edge being matched |

⚠️ `Sweep2` is simply **the one most easily overlooked** —— two rails plus however many sections,
and many people keep only the sections, which makes the path impossible to change.

### 3.3 ⭐ Layer convention (usable as-is)

```
Document
 ├── Lines        ← All patch input curves (the truth of the patch record)
 ├── Surfaces     ← The surfaces (may be split into layers per patch)
 └── Guides       ← Optional: reference lines, axes, construction aids
```

⚠️ If the document already has a layering convention, **stay consistent**, but the "input curves" must be findable.

### 3.4 ⭐ Ready-made helper: `scripts/patch_with_lines.py`

Less work than writing it by hand each time, and much harder to forget a curve:

```python
import sys; sys.path.insert(0, str(skill_root / 'scripts'))
import patch_with_lines as PWL

# NetworkSrf + retain both line families (most common case)
r = PWL.network_with_lines(doc, curves_u, curves_v, tolerance=0.01)
# r['brep'] / r['line_ids']

# Sweep2 + retain the 2 rails and all sections
r = PWL.sweep2_with_lines(doc, rails=[r1, r2], sections=secs, tolerance=0.01)
# ⛔ The rails must be retained too —— they are what everyone forgets

# Loft (only for equal sections) + retain all sections
r = PWL.loft_with_lines(doc, sections, closed=False)

# Self-check before delivery
print(PWL.audit_curve_retention(doc))   # {'ok': True, 'count': 50, ...}
```

⚠️ **This helper has NOT been verified on a live Rhino** (the Rhino process had already exited when it was written). Because of that, it:

- Does **not hardcode the argument count** for `CreateSweep2` / `CreateNetworkSrf`,
  but parses the available overload arity from `__doc__` before calling —— avoiding `No overload` caused by version differences
- Validates input strictly (rails must be exactly 2, sections non-empty, cap requires a tolerance)
- Raises an explicit exception on failure instead of silently returning nothing
- Builds purely in memory when `register=False`, without touching the document

⚠️ **On first use, run it in memory first** (`register=False`) and confirm it is correct before writing to the document.
If one of the wrappers reports an argument error on your Rhino version, paste the contents of `__doc__` and it can be located ——
which is exactly why the reflection layer is there.

### 3.5 Implementation notes (RhinoCommon)

⚠️ **Do not delete curves at runtime.** Rhino's surfacing commands mark the input curves as consumed,
but the curve objects **still exist in the document** (they are only hidden).

```python
import Rhino.Geometry as G
import Rhino.DocObjects as D

# Create the layer (set Name first, then Add —— passing a string will fail)
layer = D.Layer()
layer.Name = 'Lines'
layer_index = doc.Layers.Add(layer)

# Put the patch input curves in it
for curve in construction_curves:          # your list of patch input curves
    attr = D.ObjectAttributes()
    attr.LayerIndex = layer_index
    doc.Objects.AddCurve(curve, attr)

doc.Layers.FindName('Lines').IsVisible = True   # make sure it is visible
```

⚠️ **Duplicate first, then surface.** Let the command consume the duplicate, because managing the original afterwards is awkward:

```python
working = [c.DuplicateCurve() for c in design_curves]   # working copies
brep = G.Brep.CreateFromLoft(working, ...)                # the command consumes working
# design_curves stays intact and goes into the Lines layer
```

### 3.6 ⭐ Self-check before delivery

```
□ Every surface can name its input curves
□ The input curves are all in the Lines layer
□ The layer is visible (do not leave it hidden)
□ Curves can be double-clicked straight into edit mode from the Design panel
□ ⛔ There are no curves that were "only mentioned in the conversation and cannot be found in the file"
```

⛔ **If you cannot trace a finished surface back to its input curves, the delivery fails.**

---

## 4. ⭐ Construction order (including two new iron rules)

After the three iron rules in [13 Construction Discipline](13-construction-discipline.md), add:

### Rule 4: ⛔ `Loft` is forbidden for the main body of a complex object

```
Test: the main body is a free-form surface (curvature varies both ways) → grid lines + NetworkSrf are mandatory
      the main body has equal sections (same shape, progressive position) → Loft is acceptable
```

**Why**: the unconstrained-between-sections behaviour of `Loft` makes it unsuitable for free-form surfaces.

### Rule 5: ⭐ Keep every patch input curve in the file

```
Test: register each surface's input curves at construction time → all of them go into the Lines layer
Why: the curves are the user's only edit entry point
```

⚠️ Neither of these two rules **can be remedied afterwards** —— once a surface is baked in, or the curves are deleted,
the whole block has to be redone.

---

## 5. ⭐ Quick self-check: three questions

Ask yourself before starting:

```
1. How many constraint points does this surface need in each of the U and V directions?
   → both >1 → NetworkSrf, not Loft

2. After it is built, can the user change it?
   → are the input curves in the file? In the Lines layer?

3. Can I explain in one sentence "why is this surface built this way"?
   → if I cannot → the plan itself is wrong, not the execution
```

---

## 6. Source

The comparison in section 1.2 is based on a measurement in Rhino 8: the same shrink-wrap shell was built with a 3-section
`Loft` and with a 5×5 grid `NetworkSrf`, observing how the section perimeter varies with height.
The rules in section 3 come from real delivery scenarios: once the curves are lost, the deliverable is not editable.

⚠️ This document changes no technical property of any surfacing command; it only specifies **which one to use when**
and **what must be retained**.