# Construction Discipline and Ordering Rules

This chapter collects the rules that are **order-sensitive, expensive, and hard to repair after the fact**.
Each entry gives: fact → why → failure signal → source.

⛔ These are not "best practice suggestions". They are operational constraints where failure costs something irreversible.

---

## 0. Three things before you start (order cannot be reversed)

| # | Action | Cost of skipping it |
|---|---|---|
| 1 | **Confirm the unit system** (mm / inch / abstract units) | The same "2" on two cars in the same book differs by **30×** |
| 2 | **If real dimensions exist, set the scale; if not, ask the user** | Proportions are wrong, **all the work is wasted** |
| 3 | **Finish the patch layout sketch before opening the software** | NURBS layout errors are **extremely hard** to fix later, and splitting patches tears the seams you already built |

⚠️ The root of rule 3: NURBS layout errors cannot be fixed by adding points.
⛔ **This is the only genuinely irreversible step in the whole process**, which is why it is worth spending ten minutes on a sketch first.

⚠️ When dimensions are missing, **ask — but do not stop working**:
state explicitly that scale is undetermined → build a normalized or assumed-scale model that is easy to revise → list the open items in the report.
⛔ Neither invent millimeter precision nor refuse to start just because dimensions are missing.

---

## 1. ⭐ Three ordering rules

Breaking the order **produces no error message**, only a model that cannot be repaired.

### Rule 1: base surface → recess → operate the recess → chamfer → gap blend

```
base surface → recess/notch → operate the recess → chamfer → gap blend
```

| Order reversed | Consequence |
|---|---|
| Chamfer first, then cut the slot | The slot opening can no longer participate in the fillet |
| Blend first, then build the recess | The blended surface seals the **entrance to the recess**, ⛔ irreversible |

### Rule 2: large fillets first, small fillets second

⛔ Small fillets get swallowed by the large ones.

### Rule 3: asymmetric products must be modeled "in parallel"

⛔ **You cannot finish the parts separately and then assemble them** — that way the proportions and structural relationships between the parts can no longer be adjusted during the process.

Companion rule: **establish the primary-axis skeleton first**, then build the surrounding base surfaces progressively around that axis,
and **do the small button parts last**.

---

## 2. Surface creation discipline

| Rule | Why | Failure signal |
|---|---|---|
| **Matching degrees on opposite edges** are required before `EdgeSrf` | When they differ the software compensates with **interior knots** | ⛔ The result is **distortion, not an error message**, and it is extremely hard to locate |
| **All CPs on a straight run must be collinear** | Otherwise curvature on that run is non-zero | ⛔ The straight run bulges, and Zebra shows it immediately |
| **The last 3 rows of CPs at an intersection ⛔ must not be moved** | They determine curvature at that location | Incorrect edit → continuity breaks outright |
| **The remaining rows are free to edit** | No effect on continuity at that edge | — |
| **Do not cover a curvature problem with a hard-surface crease** | A genuine sharp edge is a design decision | Unexpected crease appears in the highlight |

⚠️ A planar patch net should be **coplanar**; ⛔ never collapse the whole net into a straight line.

⚠️ `SetPt` applies only to the selected design region and the chosen axis — **aligning row by row can destroy the original double curvature**.

### ⭐ Boundary conditions of the three-row method

| Approach | When it holds | ⛔ When it does not |
|---|---|---|
| Aligning the last 3 rows | Same degree, consistent weights, comparable parameter scales | Periodic structures, large differences in parameter domain |
| Using the three-row method for a local bulge | Transverse structure of a single-span Degree2 | When G2 is needed at both ends, extra degrees of freedom must be added |

---

## 3. Curve discipline

| Rule | Why |
|---|---|
| **Cross-check every 3D curve in at least two orthographic views** | It looks correct in one view and **is visibly off after a 90° turn** |
| **Try CP counts degree by degree until Max dev < 0.1 mm** | ⛔ Applying "degree 5, 6 points" everywhere over-fits straight lines into **waves** and under-fits complex curves |
| **`Rebuild`/`Fit`/`Fair` keep the original curve and verify the difference** | All three change the shape |
| **If the error is concentrated on a genuine crease, segment the curve** | Do not raise the degree indefinitely across the whole curve |

⚠️ Alignment in `Top` view ≠ correctness in 3D. `Front`/`Right` view verification is mandatory.

---

## 4. Discipline specific to 3C / consumer electronics

Source: flip phone and digital camera cases (Tsinghua edition, chapters 8 and 9).

### 4.1 ⭐ Meeting between the planar face and the side wall

**The correct approach is "offset the heights, then Trim" — not forcing one surface to bridge them.**

```
1. Build the side wall deliberately taller than the base face
2. Trim away the excess with the base face's boundary curve
3. The two parts meet naturally
```

⚠️ The edge where directly adjacent planar and side faces meet is **sharp**, and still needs blending (see §4.3).

### 4.2 ⭐ Adding degrees of freedom to `Extrude`

A surface extruded with `Extrude` has **only 2 CPs in the V direction** (degree 1).

To hold G2 against a neighboring `Extrude` surface:

```
ChangeDegree: U degree unchanged, V 1 → 3
→ result: V CPs go from 2 to 4
    3 keep curvature (preserving G2), 1 is available to reshape
```

⚠️ `ChangeDegree` **requires pressing `D` to enable Deformable**, otherwise it changes the degree without changing the shape.

⚠️ This is a **specific local solution**; it does not mean every seam can reach G2 this way.

### 4.3 ⭐ The edge blending chain

```
Intersect → Join → Pipe(Cap off) → ExtendSrf(T,S) → SplitSrf → Blend → Sweep2
```

| Step | Key point | ⛔ Consequence if wrong |
|---|---|---|
| `Pipe` | **Press `C` to turn Cap off** (Yes by default) | The tube gets capped and cannot pass through for trimming |
| `Pipe` radius | Textbook case ≈ blend width × 2/3 | ⚠️ A local case; equal width is not guaranteed |
| `ExtendSrf` | **Press `T` to select the method → `S` to set Smooth** | The tube does not pass through and the trim fails |
| `BlendSrf` | Produce the surface with the default Bulge first | ⛔ Do not rush to drag the slider |

⚠️ **Once `BlendSrf`'s boundary curves are selected they cannot be deselected** → when choosing multiple edges, pick the first one and then **press `A`**.

### 4.4 ⭐ The real fix for a twisting `BlendSrf`

**Symptom**: the surface bulges and twists noticeably in the middle, and the highlight behaves abnormally. Press `F10` to see that the control points bulge in the middle.

**Root cause**: the default preserves the blend ratio — **where the surface is narrow the control points shrink with it, and where it is wide the spacing is large too**.

**Fix**: in the `Blend Bulge` dialog, **check `Same height shapes`** and **do not touch the sliders**.

⛔ **Do not treat twisting with "add points" or "move the sliders"** — the slider controls bulge strength and cannot correct distortion at the root.

### 4.5 ⭐ Correct use of `Setpt`

⛔ **Wrong**: aligning only the bottom row of CPs — the outer silhouette looks right, but **the interior surface is still twisted**.

✅ **Correct**: **start from the middle and align every row**.

(The textbook's own wording: aligning only the bottom row makes the surface's outer silhouette correct, but some twisting remains in the interior surface, so you must start from the middle and align all the control points.)

### 4.6 Mirroring and symmetry

| Rule | Explanation |
|---|---|
| ⭐ **Check the centerline before mirroring** | `Mirror` is only a geometric copy; **it does not change continuity at the seam** |
| To get G2 on the centerline | That side must be matched **before** mirroring |
| Method | Mirror a copy → use it to `MatchSrf` the original surface to G2 → delete the mirrored copy → `Mirror` again |
| Draw-only-one-half principle | Draw half the outline along the reference and mirror the other half → **perfectly exact symmetry** |
| `ArcDir` + `Shift` | Hold `Shift` to lock direction while drawing multi-segment symmetric arcs, so all segments stay at equal height |
| `Untrim` | Restores the untrimmed state after mirroring |

⚠️ Surfaces used for assistance or matching should be **deleted as soon as they are no longer needed**; always keep the original surface (it has better quality).

### 4.7 Other 3C operating points

| Item | Rule |
|---|---|
| `Selu` | Selects a whole row/column of control points, replacing manual box selection |
| Moving a kink point | The **kink point and the 4 points on either side must move together**, or continuity breaks |
| Adjusting CPs vs `Offset` | For an inward offset, **adjust control points first**: it does not inflate with offset precision and does not create hard connections |
| Snap-fit rectangle | **All four corners must be blended** — this is not optional |
| `ExtrudeCrv` | The classic approach for hard-surface openings (passes through the surface, not a solid) |
| `Extrude` press `B` | Bothside, bidirectional — the surface must pass through both sides |
| `Extrude` press `C` | Cap, add caps, build a solid |

---

## 5. Continuity discipline

| Rule | Why |
|---|---|
| ⭐ **Do not demand G2 on both sides of the shade boundary** ⛔ | That location is **a break in design intent**; forcing G2 there destroys the design |
| ⭐ **A genuine sharp edge should not be flattened to G2 either** | A sharp edge is a design decision |
| **When G2 does not match, check the input curves first** | ⛔ It is not about piling on CVs — insufficient degrees of freedom cannot be fixed by adding points |
| **`Untrim` is a recovery mechanism** | ⛔ It is not a "failure"; it is a legitimate parametric recovery step |
| `MergeSrf` at a seam | Achieving a true single-surface blend requires **turning Smooth off**; `Smooth=Yes` only sews the surfaces |
| `MirrorSrf` at a seam | **Press `S` to turn Smooth off** where required |

⚠️ **"The shade boundary cannot be used as a patch boundary" and "do not demand G2 at the shade boundary" are two different things**:
the first says it is a product of lighting and cannot be used to lay out patches; the second says a break belongs at that location.

---

## 6. Acceptance discipline

| Rule | Why |
|---|---|
| ⭐ **Run `CurvatureAnalysis` immediately after each base surface is built** | Changing after the surface is settled is extremely expensive; **the base-surface stage is the only cheap quality window** |
| ⭐ **Zebra/EMap are useless on products with many small faces** | Many small faces mean per-face curvature analysis is mandatory |
| **Set watertightness by delivery goal** | Appearance parts must be closed (otherwise rendering and slicing break visibly); open surfaces are legitimate for concept forms |
| ⭐ **Put complex parts on their own layer and hide it in time** | ⛔ Not just for tidiness: a screen full of control points makes screenshots time out and **crashes the MCP session** |
| Set mesh chord height / angle budgets first | ⛔ An oversized minimum edge length can cut off refinement you need |

---

## 7. ⭐ Common misconception: not all rules are equally important

> This chapter lists **high-cost, irreversible** operational constraints.
> Reversible decisions — styling taste, gap width preference, how many surfaces to spend — are **not** listed here.
>
> Do not treat this list as a checklist to apply mechanically — first judge which rules apply to your geometric constraints.

---

## Sources

Tsinghua University Press, *Rhino3D Industrial Design and Modeling*, 3rd edition, chapter 8 (Samsung phone) and chapter 9 (SONY camera),
plus the English automotive book, 624 pages; page numbers distinguish print pages from PDF pages. For the full source audit see [08 Source Audit](08-source-audit.md).