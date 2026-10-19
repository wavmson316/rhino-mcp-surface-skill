# Surface-led construction and the section-stacking trap

Required before complex surfacing. Plan volume and surface roles, identify constraints, then choose commands. Being able to draw ordered sections does not justify Loft. Apply geometric reasoning across object categories.

## Curve roles

Separate observation curves (view-dependent silhouettes, shading, part lines), generative curves (independently justified boundaries, rails and design profiles), and diagnostic curves (sections extracted to inspect a trial). Record sources and assumptions. Do not invent profiles merely to enable Loft and then use those same profiles as the sole proof of correctness. Lighting boundaries are not automatically geometric boundaries.

## Per-patch contract

Record role; extent; authoritative constraints; dominant curvature changes and U/V; untrimmed parent versus trim domain; natural/trimmed/degenerate edges; adjacency and continuity targets; movable region; alternatives and selection reason; independent checks and fallback. Locate high points, maximum width, shoulders, recesses, inflections and feature fade-outs separately. These often require independent controls. Part lines need not be parent-surface boundaries. Four-sided regular patches are useful, but neither four-sided topology nor a particular command guarantees quality.

## Loft eligibility

Loft is appropriate for a region genuinely governed by profiles progressing along one direction with stable correspondence, such as an explicitly section-defined transition duct or a local elongated cover. Before a production Loft, answer:

1. Why is one progression adequate? Which recesses, branches, shoulders or multidirectional fade-outs need separate controls?
2. What independently establishes the profiles? Identify assumptions, orientation, closed-curve seam, segmentation and parameter correspondence.
3. How are longitudinal boundaries, adjacent derivatives and interior volume controlled? If rails or boundary derivatives are authoritative, why not use a construction that explicitly consumes them?
4. How will longitudinal, oblique and BETWEEN-STATION sections, feature positions and silhouettes be checked independently of input profiles?
5. What triggers replanning? Persistent pinching, shoulder drift or bulges require reviewing constraints and partitioning, rather than endlessly adding sections.

If unresolved, label the Loft as temporary blockout, not an accepted production parent. Switching the same unjustified constraints to NetworkSrf does not resolve them.

## Candidate methods

Use low-complexity editable control-net parents for smooth volume-driven highlights; boundary-controlled trials when four boundaries are authoritative; Sweep2 when two rails genuinely control the region; NetworkSrf when two independently justified intersecting curve families exist; Blend or constrained transitions between established parents; and local Loft when the eligibility conditions hold. Inspect interior shape, corner compatibility, parameter correspondence and transverse derivatives as applicable. No default replacement command is prescribed. Compare two plausible approaches for a complex highlight region, not every command for every object.

## Worked route: asymmetric mouse shell with a deep side recess

This is an adaptable construction route, not a fixed mouse recipe. All dimensions, profile shapes and tolerances must come from the task.

1. Establish axes, bottom and assembly datums. Match camera, proportions, top high point and maximum-width location using a simple blockout. Record asymmetric volumes and assumptions.
2. P01 is the top highlight parent, extending across future button cuts and into the shoulder transition allowance. A front-to-rear U and transverse V control net is one candidate. Control longitudinal arch/high-point position and transverse roundness/width together, alternating edits and checks. Compare a boundary trial if those boundaries have independent authority. Do not default to five transverse profiles and Loft.
3. Extract diagnostic longitudinal, transverse and oblique sections, including positions not used for construction. Check both sides of extrema, shoulder position, unintended inflections and nose pinching. Preserve untrimmed parent V01.
4. P02 right side and P03/P05 left-front/left-rear parents control their own flank volumes and bottom relationships. Use a shoulder as an explicit rail/boundary if it must be held. Do not stretch the entire top straight down to the base.
5. P04 recess floor controls depth, lowest-point position, opening and front/rear fade. Establish its parent separately rather than embedding the recess in whole-body transverse profiles.
6. Reserve finite-width P06 top-to-flank transitions and P07/P08 recess fade bands. Establish master/slave and movable widths before Blend or constrained bridging. Avoid forcing the recess into a singular point; enlarge/repartition incompatible corners.
7. Check position, tangent plane and required curvature across every join and between transition bands. Recheck prior edges and main features after Match; do not sacrifice recess depth or the top high point to improve a seam.
8. Derive buttons, wheel opening, part cuts and lower-shell trims only after parent acceptance. Validate moving parts and engineering solids separately.

Acceptance requires independent evidence for feature positions and local volume, fixed-camera silhouettes, longitudinal/transverse/oblique checks, measured target seams and editable parents. Unsupported back geometry remains a design assumption. This written example is not an executed reconstruction or G2 certification.

## Stop blind iteration

After two rounds of the same section adjustment reproduce the same failure, pause and document uncontrolled constraints; revise method, parent extent or partitioning. Two rounds is a workflow stop rule, not a mathematical theorem. Revalidate the replacement. IoU measures one projection; watertightness does not establish surface fairness or shape accuracy.
