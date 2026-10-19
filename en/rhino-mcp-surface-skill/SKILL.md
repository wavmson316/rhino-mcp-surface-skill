---
name: rhino-mcp-surface-skill
description: Use McNeel Rhino MCP to build editable NURBS surfaces from photographs, sketches, orthographic views, dimensions, or scan references. Covers industrial products, freeform shapes, vehicle exteriors, complex transitions, repair, and reconstruction. Guides shape interpretation, patch layout and UV flow, fair curves, construction choices, continuity validation, and controlled Rhino execution. Use for Rhino surfacing, reference reconstruction, patch planning, MatchSrf, or complex surface modeling.
---

# Rhino MCP Surface Skill

Turn design intent into accurate, editable geometry with explicit evidence. A command completing successfully is not proof of shape or surface quality.

Target integration: McNeel [Rhino MCP Platform / RhinoAI](https://github.com/mcneel/RhinoAI), plugin `Rhino-MCP-Platform`. Tested on Windows with Rhino8.29 and Rhino Python3. See [setup](INSTALL-CHECK.md) for router/connector configuration and compatibility limits.

## Read selectively and act

Read this entry first, then the references relevant to the task. Complete ordinary reversible modeling without asking for stage-by-stage approval. Ask about ambiguities that materially affect dimensions, assembly, or intent, while continuing independent work.

| Question | Reference |
|---|---|
| Interpret images, text, and scan data | [01 Intent](references/01-intent-and-reference.md) |
| Plan patches, UV flow, adjacency | [02 Layout](references/02-patch-layout.md) |
| Select curve/surface methods | [03 Construction](references/03-construction.md) |
| Validate continuity, fairness, delivery | [04 Validation](references/04-continuity-and-validation.md) |
| MCP, scripts, timeouts, document safety | [05 Execution](references/05-mcp-execution.md) |
| Branches, fading features, corners, reverse engineering | [06 Complex regions](references/06-complex-regions.md) |
| Diagnose and recover | [07 Diagnosis](references/07-diagnosis.md) |
| Sources and retracted rules | [08 Source audit](references/08-source-audit.md) |
| Transfer reasoning across products | [09 Examples](references/09-worked-examples.md) |
| Parameters and conditional recipes | [10 Parameters](references/10-parameters-and-recipes.md) |
| Housings, buttons, assemblies, repetition | [11 Products](references/11-consumer-electronics.md) |

Record the work in the [project template](templates/modeling-plan.md).

Before complex objects, read [construction playbooks](references/12-object-construction-playbooks.md). Produce curve IDs, patch/boundary/adjacency contracts, actual inputs, and stage gates; a command list is not a build plan.

## Non-negotiable boundaries

1. Separate observations, inferences, and design completion. A single photograph does not uniquely determine depth, unseen surfaces, or scale. Normalize unknown dimensions; do not invent millimeter accuracy.
2. Establish proportions, silhouette, primary sections, and volume before transitions and detail. Choose methods from geometry; product categories only index examples.
3. Shading, material boundaries, and part boundaries are not automatically surface boundaries. Preserve intended sharp features rather than forcing G2.
4. Single-span is a control strategy. Preserve rational arcs and useful multi-span structures; do not sacrifice shape for neat point counts. Display isocurves do not reveal true spans by themselves.
5. Join establishes topology; Trim limits the visible domain; degree elevation and knot insertion add representation freedom. None automatically improves fairness or produces G2.
6. After edits, recheck every neighboring seam and important silhouette. Record G0/G1/G2 evidence separately. Shared boundary curves, normals, and zebra stripes cannot independently prove surface G2.
7. Operate on an explicitly identified document and objects. Discover tools and APIs; do not clear the scene. After a timeout inspect state before retrying.
8. Shape, structure, reflection quality, and engineering are independent checks. Mark untested items unverified. Open surfaces are not automatically defective, and watertightness is not manufacturing approval.

## Workflow and exit conditions

### 0. Define delivery and identify the environment

Record concept/exterior surfaces/manufacturing solid/reconstruction, key features, dimensions and units, symmetry, error budgets, editability, and output formats. Discover MCP tools; specify a slot when supported and use the injected document. Read existing tolerances without changing them.

Exit: target, document, budgets, unknowns, and assumptions are recorded. If Rhino or network access is unavailable, complete useful analysis and clearly distinguish unexecuted modeling.

### 1. Interpret shape, camera, and scale

Calibrate orthographic views and cross-check shared anchors. For photographs, match a low-complexity blockout and camera before refining shape. Record principal axes, extents, sections, and occlusion hypotheses. Keep comparison cameras fixed.

Exit: major-view proportions hold; unknown depth is explicit; conflicting evidence has a documented resolution.

### 2. Select layout and construction

Rotational geometry suggests Revolve; constant sections Extrude; ordered sections Loft; paths and sections Sweep; bounded domains EdgeSrf; intersecting curve families NetworkSrf; transition gaps BlendSrf; existing-surface adjustment MatchSrf. Compare SubD for suitable concepts, then validate any conversion.

For each P01 patch record coverage, UV flow, natural/trimmed/closed/singular sides, master/slave roles, continuity, movement budget, and singularity risks. For E01 seams record both sides and validation. Compare two substantive layouts for difficult glossy regions; do not invent alternatives for trivial analytic geometry. Update the plan with trial surfaces.

Exit: important constraints have buildable adjacency/dependency relationships and a recovery route.

### 3. Build scaffolds and trial surfaces

Prefer analytic geometry and a few informative sections. Check direction, seams, endpoints, curvature combs, and reference deviation. Preserve originals when rebuilding/fitting/fairing. Test volume, UV flow, and reflections on a few parent surfaces before extending dependencies. Keep untrimmed versions.

Exit: primary silhouettes and internal sections agree, complexity is justified, unintended oscillations are absent, and actual spans are read.

### 4. Resolve seams and complex regions

Define fixed masters and adjustable slaves. Address position, tangent planes, and second-order structure according to requirements. Blend inspection includes sections, bulge, correspondence, width, and corners. Recheck previous seams after sequential matching. Conflicts call for more transition width, different layout, or multi-boundary constraints, not endless point insertion.

Use a temporary mirrored instance to inspect symmetry seams; constrain the center-plane tangent and curvature as required, then recheck the final mirror. Mirroring does not smooth a crease, but there is no universal prerequisite to Match every seam to G2.

Exit: critical seams have explicit validation status; failures are not hidden by excessive complexity.

### 5. Add details and engineering

Derive openings, panels, and gaps from parent surfaces. Keep moving components independent. Sequence slots and fillets from real dependencies; large-before-small is a candidate, not an irreversible law. Use real offsets or engineering construction for thickness, not translation or scaling. Check offset self-intersections, thin areas, flanges, draft, and assembly requirements.

Exit: required features exist; engineering parameters have sources and visual approximations are labeled.

### 6. Recheck and deliver

Save a new 3dm version and requested exchange formats with object mappings, fixed cameras, evidence, assumptions, and unresolved issues. Require watertightness and orientation only when appropriate. Mesh checks use chord/angle/seam criteria, not distance tolerance as a Weld angle. When required, reimport exchanges independently and check units, dimensions, and geometry counts.

Explain what was reconstructed, why the layout was selected, which checks passed, what remains unverified, and where files were saved. Script limits and tested scope are in [VALIDATION.md](VALIDATION.md).
