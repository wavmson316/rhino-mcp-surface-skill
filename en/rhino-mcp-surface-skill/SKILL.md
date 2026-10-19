---
name: rhino-mcp-surface-skill
description: Use McNeel Rhino MCP in Rhino 8 for editable NURBS reference reconstruction, complex product surfacing, patch/UV planning, transitions, repair and reverse modeling. Guides camera/volume fitting, per-patch construction, defect triage, retained source curves and validation.
---

# Rhino MCP Surface Skill

Deliver reference-consistent shape, valid structure and editable construction evidence. Version v1.8.0; code tests and real image-reconstruction acceptance are separate. Targets [McNeel RhinoAI](https://github.com/mcneel/RhinoAI), tested Windows/Rhino8.29/Python3. See [setup](INSTALL-CHECK.md).

## Start

1. Establish intent, critical features, references, units, dimensions, delivery and budgets. Normalize unknown size; label hidden depth/backside assumptions.
2. Discover live tools and the target document/slot. Use the injected document and protect existing objects/settings. Batch read-only discovery/minimal API probes; do not guess overloads.
3. For reference reconstruction read [17 Fitting loop](references/17-reference-to-model-loop.md), and for complex surfaces [15 Surface strategy](references/15-surface-led-construction.md). Maintain a concise actual build plan, revised after trials.
4. Preserve ALL actual construction/trim/cutting curves in lines or sublayers with the delivered .3dm; map faces to input GUIDs, parameters and versions. See [16 Source curves](references/16-preserve-construction-curves.md). Retained curves do not imply associative History.

## Execute with stage gates

| Stage | Action | Exit evidence |
|---|---|---|
| Reference/blockout | Landmarks/features, camera and coarse volume; lock comparison conditions | Proportions, extrema and main negative spaces within task budgets |
| Parents | Assign highlight/flank/recess/transition roles and UV; trial decisive regions | Actual silhouettes plus longitudinal/transverse/oblique checks, including between stations |
| Adjacency/local regions | Use parent derivative semantics for transitions, closures and opening walls | Validity, intended seams and local volume independently checked |
| Detail | Derive small features after parent acceptance; test one repeating unit | Main features preserved; engineering checked separately |
| Save | Retain curves/parents/parameters, save a new version and independently read back as needed | Inputs and mappings resolve; verification state explicit |

Each iteration records discrepancy, hypothesis, changed parameters and rechecked constraints. After two ineffective similar edits revisit camera/depth/constraints/layout. Defer details while the main-shape gate fails.

## Method and quality boundaries

- Double curvature does not mandate Network; more curves do not establish accuracy. Network needs two justified, consistent intersecting families; face count is not cell count.
- Use Loft for genuinely section-driven regions, explaining longitudinal control and between-station validation. Do not default to whole-body transverse profiles or grade a surface by section count.
- Choose analytic/control-net/boundary/two-rail/network/transition methods from actual constraints. Shading is not automatically a patch boundary. Preserve real creases. Join, elevation and trimming do not establish fairness or G2.
- Apply [19 Defect triage](references/19-defect-triage.md) per batch. Empty/invalid/nonmanifold/unintended duplicate/missing output blocks the step. Open-edge/solid requirements follow delivery, not a universal exterior-solid rule.
- IsValid, watertightness, normals or IoU alone do not prove correct shape, no self-intersection or G2. Seam sampling only supports finite position/tangent-plane diagnostics. Mark unverified checks explicitly.

## Efficient execution

Build small dependent batches in memory with native APIs; return concise checks and timings. publish_patch explicitly writes accepted outputs. Recompute only affected dependencies and delay dense details/fine meshing. Inspect necessary fixed views at stage gates. After timeout inspect completion. Verify module path and reload changed code; do not rediscover every API each step. Use [project record](templates/modeling-plan.md) and [reference record](templates/reference-fit.json).

## Read as needed

Intent [01](references/01-intent-and-reference.md), layout [02](references/02-patch-layout.md), construction [03](references/03-construction.md), continuity [04](references/04-continuity-and-validation.md), MCP [05](references/05-mcp-execution.md), complex regions [06](references/06-complex-regions.md), recovery [07](references/07-diagnosis.md), sources [08](references/08-source-audit.md), examples [09](references/09-worked-examples.md), budgets [10](references/10-parameters-and-recipes.md), products [11](references/11-consumer-electronics.md), playbooks [12](references/12-object-construction-playbooks.md), dependencies [13](references/13-construction-discipline.md), APIs [14](references/14-rhino-python-binding-traps.md), repeating units [18](references/18-repeating-units.md).

Report reconstructed features, layout rationale, retained inputs, evidence, unverified items and file paths. See [validation](VALIDATION.md) for test scope.
