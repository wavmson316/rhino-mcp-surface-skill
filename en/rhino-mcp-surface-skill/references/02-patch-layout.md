# Patch layout, UV flow, and adjacency

## Keep representations distinct

A NURBS base surface is a parameter rectangle S(u,v); trim loops limit its visible region, while Brep edges and 2D trims describe topology. Display isocurves are not knots/spans, and mesh/SubD topology is not a NURBS control net. A five-sided hole may simply be a trim in a four-sided parent surface.

## Planning process

1. Identify axes, longitudinal/transverse sections, ridges, saddles, recesses, real creases, and symmetry planes.
2. Let one UV family follow major shape flow and the other control sections. Long strips often follow length, but U is not universally the long direction.
3. Pair compatible opposite boundaries. Check endpoints, tangents, parameter distributions, and corner angles; mismatched parameter speeds can cause crowding/twist.
4. Give parent surfaces, transition bands, corners, and features distinct roles. Reserve enough width in reflection-sensitive areas; avoid unjustified singularities or slivers.
5. Compare trial surfaces and update adjacency. Layout is iterative; untrimmed parents make recovery manageable.

Split for real creases, branching flow, incompatible boundaries, or isolated local complexity. Do not split merely for color, shadows, easily trimmed holes, part seams, or single-span aesthetics.

## Patch and seam contracts

For P01 record role/extent, both UV directions, four side types (natural, trimmed, closed seam, degenerate), input parents, fixed masters, allowable motion/deviation, continuity, and risks. For E01 record both actual faces/edges, G target or intentional gap, corner compatibility, test method, and status.

After topology changes, edge indices may change. Re-identify by geometry and parent mapping instead of reusing stale indices.

## Construction dependencies

Blockout and assembly datums precede parent surfaces, dependent surfaces, transition bands, corners, and related detail. Establish major asymmetric components together before independent refinement; this does not forbid separate-part modeling.

Slot/fillet order depends on feature intersections. Large-before-small and slots-before-rounding are candidate strategies, not irreversible laws. Preserve inputs and versions for local reconstruction.

## Corners and singularities

Boundary tangents and transverse derivatives must be compatible at corners. Sequential Match does not prove simultaneous compatibility. Adjust boundaries, widen the transition, relocate junctions, or change connectivity. Sphere poles and cone tips can be intentional; avoid arbitrary collapsed edges in uniform glossy regions.

For five-sided regions compare restoring a larger parent and trimming, multiple four-sided patches, or changing surrounding layout. Not every edge needs G2. Repeated corner failures call for upstream constraint review.
