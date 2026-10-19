# Sources, confidence, and retractions

## Reading and evidence boundary

The reviewed Chinese source package's 20 text files were fully read and compared by hash with the previous review. Existing industrial-book OCR review, sample pages, and updated structured notes informed corrections. Images were excluded as requested. This package does not claim this reviewer visually read every scan, and rendered image counts do not prove reading coverage.

Sources include Rhino3D Industrial Modeling and Design, third edition; André Kutscherauer's 3D Car Modeling with Rhinoceros and sample; training material; and current RhinoCommon APIs. Distinguish printed/PDF page numbers. Tutorials inspire methods but frequency does not establish mathematical truth. Visualization-oriented tutorials are not manufacturing standards.

## Official lookup

- [Rhino8 help](https://docs.mcneel.com/rhino/8/help/en-us/index.htm): commands, units, meshes, exchange.
- [RhinoCommon API](https://developer.rhino3d.com/api/rhinocommon/): overloads/return types.
- [Developer guides](https://developer.rhino3d.com/guides/): integration/versions.
- [McNeel forum](https://discourse.mcneel.com/): cases, not acceptance standards.
- [Rhino MCP Platform](https://github.com/mcneel/RhinoAI) and [setup documentation](https://mcneel.github.io/RhinoAI/docs/getting-started/): plugin/router/client instructions.

Lookup links do not imply every page was verified. API evidence is limited to the recorded Rhino8 tests. MCP setup was checked on 2026-10-19 against upstream documentation and discovered tools; subsequent changes require rechecking.

## Retracted universal rules

| Retracted | Replacement |
|---|---|
| Main faces only EdgeSrf/Loft | Choose from actual geometry constraints |
| All glass planar; appliances only G1 | Shape, reflection, and purpose decide |
| Deformable required for degree elevation | Exact elevation preserving shape is valid |
| Refine can never reach G2 | It can add freedom; monitor result and complexity |
| CP−Degree universally gives spans; periodic CP=Degree | Read real properties |
| A circle has four geometric kinks | Repeated knots do not establish kinks |
| Single-span curves cannot meet G2 manually | End constraints and available freedom decide |
| One Blend is the unique three-way solution | Bridges and center layout are separate |
| Terminators should not be G2 | Lighting does not establish discontinuity |
| Blend offsets cannot be smooth | Check offset singularities and numeric error |
| Curves cannot trim Breps | Position/projection and command conditions decide |
| Pipe radius universally equals transition width times 2/3 | Local tutorial gauge only |
| All visible surfaces must be solids | Delivery defines open/closed requirements |
| Weld equals distance tolerance | Check Rhino's angle-based mesh semantics |
| Average dimension/1000 is a meshing standard | Budget chord/angle/seam error |
| Fixed ports/tools apply everywhere | Discover actual environment |
| Compilation or six cases certify all helpers | Test each released entry and counterexamples |

External old notes/knowledge graphs are not execution dependencies. Retractions must disable stale rules, not merely add disclaimers. New knowledge should record id, statement, scope, preconditions, evidence, validation, counterexample, status, and supersedes. No scans, full OCR, or full third-party tutorials are distributed.
