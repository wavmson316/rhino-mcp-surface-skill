# Reference-to-3D fitting, acceptance, and speed

Required for complex reference reconstruction. Reduce shape error while preserving editability.

## Observe before constructing

Actually inspect the task reference when permitted. Distinguish silhouette, occlusion, materials, reflection, part lines and real creases. A restriction on reading scanned books does not automatically prohibit inspecting the task reference. If the actual reference cannot be inspected, state that image acceptance is unavailable.

Record each image, crop, frame, projection and camera hypotheses. Select identity-defining landmarks: endpoints, crown/maximum-width positions, shoulder turns, recess location, opening centers/widths as visible. Fill [reference-fit.json](../templates/reference-fit.json). Pixels constrain projection, not unique 3D coordinates. Do not invent measurements of hidden geometry. With unknown size normalize length and label depth/backside/engineering assumptions.

## Camera and blockout gate

Use simple analytic geometry or low-complexity control nets to establish proportions, extrema, taper and major negative spaces. Defer fillets, dense holes and tiny details. Calibrate projection, pose, focal length/distance and crop, then lock comparison cameras. Compare plausible depth hypotheses when needed. If camera calibration changes, reevaluate old/new geometry under the same new camera.

Do not refine while coarse previews still show major errors. Require evidence for axes, proportions, high-point/maximum-width location and major openings/recesses. Budgets follow source uncertainty and the task; no universal IoU threshold certifies acceptance.

## Build parents by shape role

Give highlights, flanks, recess floors, transitions and closures independent roles where needed. Parent domains can cross future part trims. See [surface-led decisions](15-surface-led-construction.md). Begin with a decisive parent/trial, not the full detailed object.

Network requires two independently justified, consistently intersecting curve families. More invented curves do not add evidence. Network fits curves; interiors between them still need checks, and output face count is not network cell count. Loft, Sweep2 and control-net methods also need explicit constraint reasoning. Changing a command does not correct wrong shape inference.

Inspect actual surfaces using fixed-view silhouettes and independent longitudinal, transverse and oblique sections, especially between input stations and around extrema/fade-outs. Over-rounded volume can arise from transverse roundness or shoulder width even when input outlines match.

## One hypothesis per iteration

Example: a shoulder is too high and the flank too round. Test shoulder position/transition width while holding camera, total width and crown. Rebuild only affected patches and downstream dependencies. Retain the candidate only if relevant residuals improve without exceeding previously accepted budgets; otherwise revert.

Keep local critical-feature metrics alongside global overlap. IoU cannot hide missing holes or wrong recess depth. Independently recentering/rescaling each candidate conceals size/position errors: lock registration, frame and units. Report scale-free metrics separately when needed. After two ineffective rounds, revisit camera/depth assumptions, uncontrolled constraints or partitioning rather than adding endless curves.

## Details and delivery

After main-shape acceptance, build local transitions, closures, opening walls and part division; dense details come later. Map each critical feature to an object ID, target, actual evidence and status. Shape, topology, continuity and engineering are separate gates. Single-image hidden geometry remains an editable design assumption.

## Efficient execution

- Discover tools/overloads once per environment and revisit after version changes/errors. Verify module.__file__; reload changed loaded modules, not every call. Deleting bytecode alone does not reload a module.
- Prefer native in-memory APIs; patch_with_lines defaults to register=False. Batch a few dependent parents rather than one MCP call per point or the entire detailed product at once. Return IDs, bounds, validity, timings and concise checks.
- Recompute only changed patches and downstream dependencies. publish_patch explicitly writes accepted outputs and actual input curves to lines; do not stack every trial in the scene.
- Use coarse previews for large errors and localized refinement for defects. Inspect fixed cameras at meaningful stage gates. Reference fidelity needs actual visual comparisons.
- Accept one repeated unit before arrays. Delay dense holes, fine meshing and expensive booleans. After timeout inspect completion before replay.
- Measure construction, validation, images and round-trip time separately. No fixed speedup is claimed.

This workflow has not been accepted against the user's failed reference/model. API tests do not establish reconstruction quality. Report feature residuals, method choices, structure/seam checks and unknown regions; label a failed main-shape gate as an intermediate model.
