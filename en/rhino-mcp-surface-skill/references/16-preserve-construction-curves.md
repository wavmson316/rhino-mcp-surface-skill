# Preserve construction curves in the delivered model

## Default requirement

Deliver the actual editable input curves as well as surfaces. Unless the user explicitly requests deletion, preserve construction curves as document objects in the final Rhino `.3dm`, under a layer named `lines`. Python memory, logs, screenshots and temporary files do not satisfy this requirement. Apply it during construction, revision, cleanup and saving.

Optional sublayers include `lines::P01::rails`, `lines::P01::sections`, `lines::P01::boundaries` and `lines::P01::archive`. Small projects may use `lines` directly. Hide construction layers for presentation if useful, but retain them and explain how to show them. Reuse appropriate existing layers without moving or renaming unrelated user objects.

## Preserve actual inputs

| Operation | Retained inputs |
|---|---|
| Sweep1 | One rail and all participating sections |
| Sweep2 | Two rails and one or more sections, not one rail and two sections |
| Loft | All input sections, their order, direction and closed-curve seams |
| EdgeSrf / NetworkSrf | Actual boundary curves / both curve families and correspondence |
| Revolve / RailRevolve | Actual profile, axis endpoint definition and any rail used |
| Extrude / curve-driven trim or cut | Input profiles and any actual path or cutting curves; record direction/distance separately |
| Blend / Match / surface-edge construction | Parent surfaces, selected edge identities, parameter ranges and constraints; retain any actual independent input curves too |

Direct control-net construction need not invent original curves afterwards: preserve editable parent surfaces and control-net/generation parameters. Label extracted inspection curves as diagnostic or derived. DupEdge preserves boundary position, not the parent surface's transverse derivatives or its G1/G2 constraints; retain parent geometry when needed.

## Execution

1. Assign stable input names and IDs, such as `P01_rail_L_v01` and `P01_section_03_v01`; record source, role, direction and order.
2. Persist the exact final curves supplied to the production construction call as document curves, recording returned GUIDs. Retain existing document inputs without gratuitous duplicates. Memory-only tests may remain temporary; production delivery must persist the inputs.
3. Use keep-input options. If an operation may consume or mutate its inputs, preserve copies first. For API operations, work on duplicates as necessary and retain the actual construction version.
4. Preserve meaningful source/final versions around Rebuild, Fit, Fair, reversal or seam changes and record transformations/parameters. Avoid duplicating objects for every display action.
5. Map output patch IDs to method, input GUIDs/names/roles, order, parameters and parent dependencies using object UserText and/or project records. Do not assume a specific MCP metadata tool.
6. Cleanup must not delete construction curves merely because they have been used, nor delete the `lines` layer. After user edits, update the mapping or mark the version discrepancy.

## Acceptance and future edits

Before saving, verify `lines` exists, actual inputs remain valid document curves, mappings resolve, and roles/order/counts are complete. Include these layers and objects in the `.3dm`; exporting only selected finished surfaces is insufficient. Verify saved persistence in an independent document or reader when needed, protecting the current scene.

Export STEP/IGES/STL or other manufacturing files separately as required; equivalent layers, curves, metadata and history are not guaranteed. Supply the editable `.3dm` alongside them or explicitly identify where editing sources are stored.

**Retained curves do not imply associative History.** Promise automatic surface updates only if the actual command, execution mode and Rhino History relationship have been established and verified. Otherwise explain how to show `lines`, edit the rails/sections and rerun construction plus validation. Downstream trims, Match operations and details may need rebuilding.
