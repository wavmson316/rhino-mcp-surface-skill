# Product shells, buttons, and assembly transfer

## Start from the geometric features

Consumer electronics range from flat-sided boxes to high-gloss double-curvature shells, ergonomic recesses, and complex branching. Cars have analytic parts too. Choose the form and G level from the reference and the purpose — do not lock into G1 or "flat face plus small fillet" because of the product category.

This chapter borrows from the flip-phone and camera cases: shared parent surfaces, assembly datums, transition sections, and detail dependencies. The router and air-conditioner cases are transfer templates, not end-to-end validations against real references.

## Main shell strategy

| Feature | Candidates | What to watch |
|---|---|---|
| Flat face with side wall | PlanarSrf / Extrude / fillet | Planarity preservation, corner ordering |
| Low-dome cover | Few-section Loft / controllable parent surface | Crown height, maximum volume, reflection |
| Sloped side wall | Sloped extrude / straight grain / dual rail | Draft direction and the real angle |
| Deep recessed grip zone | Independent recess base plus a wide transition | Local reshaping must not drag the top face |
| Contact / assembly faces | Derived from a shared datum parent surface | Clearance, interference, and range of motion |

Letting the side wall overshoot and then trimming is a boolean-intersection technique — it does not guarantee automatic G1/G2. The extrusion direction is often Degree 1 with two rows of CPs, but read the actual U/V values; if you need to edit, elevate the degree precisely rather than enabling Deformable mode. Elevating to Degree 3 for four rows and protecting three rows at one end is a specific local scheme — it does not stand in for G2 on every seam.

### ⭐ Joining a flat face to a side wall: offset in height, then Trim

**Do not try to force a flat face and a side wall together with one surface.** The textbook approach:

```
1. Build the side wall deliberately taller than the base face
2. Trim away the excess using the flat face's outline curve
3. The two parts then meet naturally
```

⚠️ The boundary between directly adjacent flat and side walls is **sharp**, and still needs blending (see below).

### ⭐ Adding the degrees of freedom for G2 on an Extrude face

`Extrude` produces only 2 CPs in the V direction. The textbook approach for holding G2 against a neighbouring `Extrude` face:

```
ChangeDegree: leave the U degree unchanged, raise V from degree 1 → degree 3
→ V CPs go from 2 to 4 (3 of them preserve curvature to hold G2, 1 reshapes)
```

⚠️ This is a **specific local scheme**. It does not mean every seam can reach G2 this way.

---

## Domed buttons and slider keys

Outline, crown height, and edge softness are controlled separately. Straight lines plus semicircles give an exact G1 outline; where gloss demands it, use a G2 transition and verify the error. The face can come from Loft or from section parent surfaces, with Patch only as an approximate candidate; see [Parameter recipes](10-parameters-and-recipes.md) for the conditions on the three-row low-dome method. Handle the slider boss, outer outline, end stop, and side wall independently — do not erase functional hard edges in the name of "one uniformly smooth line".

### ⭐ Two ways to get the outline continuity

| Approach | Continuity | Recommendation |
|---|---|---|
| Two parallel lines plus a semicircle at each end | **G1** (exact) | ⛔ **Prefer this one** — it stays easy to resize later |
| `Blend` to round both ends | **G2** | Only for glossy surfaces and highly visible cases |

⚠️ Button dimensions change frequently, so ⛔ starting at G2 slows every revision down.

### ⭐ Full button recipe (7 steps)

```
1. Draw the outline (straight lines + semicircles = G1)
2. Extrude into a side wall (press C to cap it, making a solid)
3. Split the outline into two symmetric halves with a straight line
4. Loft the two split curves → flat surface
5. ChangeDegree to drop the U direction to degree 2 (press D as needed) → 3 rows of CPs
6. Move only the middle row (⛔ the first and last cannot be selected) → domed surface
7. Pipe → Split/Trim → BlendSrf → smooth the seam
```

⚠️ When using `Patch` for a button face, **do not select `Adjust tangency`**.

---

## Variable-width transitions and fading

After checking edge pairing and sections, trial bulge / Same height shapes. If it still runs away, extract a suitable section from several trial blends and then Sweep2, setting Curvature conditions on the real face-edge band. Read mean curvature, normal sections, and reflection together — do not let a fixed colour scale certify the whole surface.

### ⭐ The standard chain for a blended edge

```
Intersect → Join → Pipe (Cap off) → ExtendSrf (T, S) → SplitSrf → Blend → Sweep2
```

| Step | Key action | ⛔ Consequence |
|---|---|---|
| `Pipe` | **press `C` to turn Cap off** (default Yes) | The pipe is capped and cannot pass through to trim |
| `ExtendSrf` | press `T` → `S` (Smooth) | The pipe does not reach through and the trim fails |
| `BlendSrf` | Start with the default Bulge, ⛔ do not rush to drag the slider | — |

### ⭐ The correct fix for a twisted BlendSrf

**Symptom**: the middle of the surface bulges and twists, and the highlight goes wrong. **Root cause**: the default preserves the blend proportion, so the CPs shrink in at the narrow section.

**Correct fix**: tick **`Same height shapes`** and ⛔ leave the slider alone.

⛔ Do not treat a twist with "add points" or "drag the slider" — the slider controls bulge strength and cannot correct distortion at the root.

### ⭐ Correct use of Setpt

⛔ Aligning only the outermost row → the outer outline is right but **the interior is still twisted**.
✅ **Start from the middle and align every row.**

### ⭐ Efficient edge selection in BlendSrf

A selected boundary curve **cannot be deselected**. To select multiple edges, pick one first, then **press `A`** to select all connected edges.

## Part division, assembly, and repeated features

Establish the overall volume, axes, and interface positions first; refine the individual parts afterwards. Upper and lower shells and cover plates can share an exterior parent surface and then be split, keeping an untrimmed copy. Moving antennas, louvers, and hinges are expressed as separate parts on their own rotation axes — check for interference at least at the closed and open positions, or at the limit positions.

For repeated holes and grilles, validate one cell first and check the edge margin, minimum wall thickness, and hole direction before patterning or parameterising. Surface UV mapping does not guarantee equal arc length, and Flow needs its scaling checked as well; a varying spacing can be perfectly correct, so do not force every pattern to be equidistant. Generate large arrays last and isolate them for display — not every task needs GH, nor needs every hole built as a solid.

## Manufacturing branches

Manufacturing solids need true wall thickness, parting lines, draft, assembly clearance, and process radii. Shrinkage rate comes from the material grade, direction, and process — there is no universal ABS/PC ratio to apply automatically. An appearance concept may legitimately omit screw bosses and snap-fits, provided you record that these were not designed. Scaling an inner layer is only an appearance approximation; do not call it constant thickness.

## Inspection focus

Primary silhouette and negative space, cover crown height, variable-width band and fade, evidence for each G level, independence and clearance of moving parts, hole-array edges, material thickness and undercuts. Small faces can be magnified for Zebra / EMap, and the curvature map range must suit the scale. There is no "single reliable consumer-electronics inspection tool".
