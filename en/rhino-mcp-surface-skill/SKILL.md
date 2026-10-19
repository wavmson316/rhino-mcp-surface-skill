---
name: rhino-mcp-surface-skill
description: Use Rhino MCP to turn photos, sketches, multi-view drawings, dimensions, or scan data into editable NURBS surfaces. Applies to industrial products, freeform surfaces, automotive exteriors, complex transitions, surface repair, and reverse reconstruction; guides shape reading, patch and UV flow, curve fairness, construction command choice, continuity verification, and reliable execution. Use when the user asks for Rhino surface modeling, reference-image reconstruction, patch layout, MatchSrf, or complex surfaces.
---

# Rhino MCP Surface Skill

Turn user intent into geometry that is correctly shaped, structurally controlled, and evidence-backed. A command that returned successfully is only a construction result; it does not substitute for shape or quality acceptance.

Targets McNeel's [Rhino MCP Platform / RhinoAI](https://github.com/mcneel/RhinoAI), plugin `Rhino-MCP-Platform`; tested on Windows + Rhino 8.29 + Rhino Python 3. The official platform does not support Rhino 6/7; Rhino 8.x is the minimum. See the [install guide](INSTALL-CHECK.md) for connection method.

## Reading and execution

Read this page first, then read only the row of the table below that matches the task — loading every reference each time wastes context. Ordinary reversible operations are performed directly; do not ask the user to approve each stage. Ask questions only when a core dimension, assembly relationship, or design intent is genuinely ambiguous, and keep working on the parts that do not depend on the answer.

| Current question | Reference |
|---|---|
| **Immutable ordering rules and high-cost constraints before starting** | ⭐ [13 Construction Discipline](references/13-construction-discipline.md) |
| How to interpret images, text, and scans | [01 Intent and Reference](references/01-intent-and-reference.md) |
| How to lay out patches, run UV, handle adjacency | [02 Patch Layout](references/02-patch-layout.md) |
| How to choose curve and surface construction commands | [03 Construction](references/03-construction.md) |
| Continuity, fairness, and delivery verification | [04 Continuity and Validation](references/04-continuity-and-validation.md) |
| Connecting MCP, invoking scripts, recovering from timeouts | [05 Execution Protocol](references/05-mcp-execution.md) |
| Splits, tapers, multi-edge corner regions, reverse engineering | [06 Complex Regions](references/06-complex-regions.md) |
| Diagnosis after a bad result | [07 Diagnosis](references/07-diagnosis.md) |
| Sources and retracted rules | [08 Source Audit](references/08-source-audit.md) |
| Cross-category reasoning examples | [09 Worked Examples](references/09-worked-examples.md) |
| **Numeric values, command recipes, and applicability conditions** | ⭐ [10 Parameters and Recipes](references/10-parameters-and-recipes.md) |
| Shells, buttons, assembly, and repeated features | [11 Consumer Electronics](references/11-consumer-electronics.md) |

On first connection read [Install Self-Check](INSTALL-CHECK.md). Log the whole process into the [project template](templates/modeling-plan.md).

Before starting a complex object you must also read [From an object to buildable patches: construction playbooks](references/12-object-construction-playbooks.md) and produce curve IDs, patch/boundary/adjacency tables, concrete inputs, and exit criteria per stage. A list of command names is not a construction plan.

### Triage before reading parameters

**Choose the route by geometric character, not by product name.**
Automotive skins, appliance enclosures, and 3C products have different primary construction strategies and continuity targets,
so first classify the input, then decide whether [11 Consumer Electronics](references/11-consumer-electronics.md) is needed.

## Hard boundaries

1. Record observation, inference, and design completion separately. A single image cannot uniquely recover depth, the back side, or true scale. Without dimensions you may build a normalized model; you may not claim millimeter-accurate reconstruction.
2. Proportion, silhouette, main sections, and volume come first; transitions and details follow. Choose the method from geometric constraints — the product name is only a search key for prior cases.
3. Shade lines, material lines, and part lines are not automatically surface boundaries; and genuine sharp edges should not be forced flat to G2 either. **A shade boundary is a design break by definition — do not demand G2 there.**
4. Single-span is a control strategy. Keep rational arcs and legitimate multi-span structures; never distort the shape to make point counts tidy. Never infer span count from the visual density of isocurves. **Read spans from `SpanCount`.**
5. Join is a topological connection; Trim cuts the visible domain; degree elevation and knot insertion add representational degrees of freedom. None of them automatically improves fairness or achieves G2.
6. After any edit, re-check all adjacent edges and key silhouettes. Record evidence for G0, G1, and G2 separately; a shared edge curve, surface normals, or zebra stripes cannot by themselves prove G2 between faces.
7. Address documents and objects explicitly; do not guess tools or APIs, and do not clear the user's scene. On timeout, verify whether the operation actually completed before retrying.
8. Shape, structure, reflection, and manufacturability are independent acceptance items. Write "unverified" for anything not measured; do not automatically fail an open surface, and do not treat watertight as automatically manufacturable.

### Three things whose order cannot be reversed

| # | Action | Cost of skipping it |
|---|---|---|
| 1 | Confirm the unit system (mm/inch/abstract units) | The same "2" in one model can be off by 30× |
| 2 | If dimensions exist, set the scale; if not, ask the user | Proportions are wrong and all the work is wasted |
| 3 | Finish the patch layout sketch before opening the software | NURBS layout errors are extremely hard to fix later; splitting patches destroys seams you already built |

### Three order-sensitive rules

1. **Base surface → recess → operate the recess → chamfer → gap blend** (reversing the order lets the blended surface seal the recess entrance — irreversible)
2. **Large fillets first, small fillets second** (small fillets get swallowed)
3. Model asymmetric products **in parallel**, not part-by-part then assembled (companion rule: establish the primary-axis skeleton first, buttons and small parts last)

⭐ For the complete discipline — including the irreversible constraints on surface creation, curves, 3C, continuity, and acceptance — see
[13 Construction Discipline](references/13-construction-discipline.md).

## Workflow and exit criteria

### 0. Define the deliverable and identify the environment

Record whether the target is a concept form, appearance surface, manufacturing solid, or reverse fit; the key features; units and the origin of dimensions; symmetry; allowable tolerance; and output format. Read the currently available MCP tools; if the interface has multiple instance slots, name the slot explicitly and use the injected document. Read the existing tolerances and do not change settings on your own.

**Exit:** goal, working document, error budget, and unknowns are recorded. With no network or no Rhino available, continue with the analysis and plan that can be done, state what was not executed, and do not report modeling as complete.

### 1. Read the shape, camera, and scale

Scale orthographic views and cross-check them against shared anchor points; for photos, first match the camera with a low-complexity block, then verify silhouette and volume. Establish the primary axis, bounding dimensions, principal sections, and occlusion assumptions. Compare with a fixed camera — moving the camera to hide error is not allowed.

**Exit:** proportions hold across the main views; unknown depth carries an explicit assumption; conflicting data has a stated resolution.

### 2. Choose layout and construction route

Pick candidates by geometry: revolved body → Revolve; constant cross-section → Extrude; ordered sections → Loft; path plus sections → Sweep; closed boundary → EdgeSrf; two curve families → NetworkSrf; open band → BlendSrf; adjusting an existing surface → MatchSrf. For complex organic concepts, SubD is worth comparing, but the converted result must be re-verified.

For patches like P01, record extent, U/V, natural/trimmed/closed/degenerate edges, parent-child direction, continuity, available blend width, and singularity risk. For seams like E01, record both sides and the check method. Compare at least two layouts for complex highlight regions; build simple analytic objects directly. Update the plan with trial surfaces — you are not expected to foresee every patch in advance.

**Exit:** key constraints have a buildable adjacency and dependency structure, and local failure has a recovery path.

### 3. Build the curve skeleton and test surfaces

Start with analytic geometry and a few principal sections; check direction, closed seams, endpoints, curvature combs, and deviation from the reference. Rebuild/Fit/Fair alter the original curve — keep it and verify the difference. Test a few base surfaces first to judge volume, UV, and reflection, then extend to dependent surfaces. Keep untrimmed parents and keep versions.

- **Read spans from `SpanCount`**; do not compute `CP count − degree` (repeated knots and periodic structures break that relation).
- Try CP counts degree by degree until Max deviation meets the budget. **Do not apply a fixed degree/point count everywhere** (a straight line becomes a wavy over-fit).
- **Cross-check every curve in at least two orthographic views** — it can look correct in one view and be visibly off after a 90° turn.
- Before `EdgeSrf`, **confirm all four edges have the same degree** (when they differ, the software compensates with interior knots, so the result is distortion rather than an error).
- **Control points on a straight run must be collinear**, otherwise that run bulges.

**Exit:** main silhouette and interior sections are correct, complexity is justified, there is no unintended oscillation, and the real span count has been read.

### 4. Handle continuity and complex regions

Decide which faces are fixed parents and which are adjustable children; place transitions, tangency, and second-order structure according to the target. When blending, inspect the cross-sections, bulge, correspondence, and corner regions — checking only Curvature is not enough. Re-verify earlier edges after the sequence of matches; when edge-region constraints conflict, change the width, the layout, or use a multi-edge constraint scheme.

- **When a match fails, check the input curves first** (degree/CP count/deviation). ⛔ It is not about piling on CVs.
- When `BlendSrf` twists, **check `Same height shapes`**. ⛔ Do not try to fix it by dragging the slider or adding points.
- **The last 3 rows of control points at an intersection ⛔ must not be moved** (they determine curvature there); the remaining rows are free to edit.
- **Run `CurvatureAnalysis` immediately after every base surface is built** — changing after the surface is settled is extremely expensive.
- On products with many small faces, `Zebra`/`EMap` show nothing useful; per-face curvature analysis is mandatory.

For symmetric surfaces, build and check a mirrored test piece first to validate the seam. Constrain the centerline tangent plane and curvature to the target, mirror, then re-verify. Mirroring does not automatically remove a crease, nor does it require matching to G2 everywhere first — if you want G2 on the centerline, that side must be matched **before** mirroring.

**Exit:** the state of every critical seam is verified; failures are not masked by adding points without limit.

### 5. Details and engineering

Derive holes, panels, and parting lines from the base surface; keep moving parts independent. Schedule slots and fillets by actual dependency — large before small is a candidate, not an ironclad irreversible rule. Constant wall thickness uses real offsets or engineering construction; do not treat translate/scale as equal thickness. Check offset self-intersection, thin regions, flash, draft, and assembly needs.

- ⛔ **Order cannot be reversed**: base surface → recess → operate the recess → chamfer → gap blend.
- When using `Pipe` as a gauge, **press `C` to turn Cap off** (the Yes default seals the tube).
- Put complex parts on **their own layer and hide it in time** — a screen full of control points makes screenshots time out and crashes the MCP session.
- Generate arrays of holes or grilles with an array/parametric operation first and bake them. ⛔ Drawing them one by one accumulates error and leaves missing corners.

**Exit:** design details are complete; manufacturing parameters have a stated source, and any appearance approximation is labeled.

### 6. Re-verify, save, and deliver

Save a new 3dm version and the required exchange files; record the object mapping, the fixed camera, check results, assumptions, and open items. Check solids for watertightness and orientation against the contract; check meshes by chord height, angle, and seam, and do not copy a distance tolerance into Weld's angle setting. When needed, re-import the exchange file into a clean environment to verify units, dimensions, and face count.

**Set watertightness by delivery goal**: appearance parts and skins must be closed (otherwise rendering, slicing, and export break visibly); a concept form may legitimately be delivered as open surfaces.

**Quantify silhouette reconstruction with IoU** (`outline_metrics.silhouette_iou`, 17 items parsed and verified).
⚠️ IoU is valid for one projection only, and **it is not dimensional accuracy** (scaling concentric circles by r gives IoU = r²).

**The delivery note must answer:** what was reconstructed; why the patches were laid out this way; what was actually measured and passed; what is unverified; and where the files are. For the full script boundaries and the tested range see [VALIDATION.md](VALIDATION.md).