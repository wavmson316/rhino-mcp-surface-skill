# Repeating units, openings and polar arrays

Build one master and array it only when repetition is established. Record axis, count, phase, direction and intentional variation. Validate a master against its transformed neighbor before full replication: boundaries, overlap, gap, orientation and silhouettes. Graded/asymmetric units need appropriate parameters.

Openings may use trims, nested planar boundaries, walls/closures, local patching or suitable booleans. Booleans are not inherently straight-wall-only, and radial bands are not universal. Choose a representation retaining the actual design constraints.

Control-point curves and interpolation each have appropriate uses and possible overshoot; preserve analytic lines/arcs. Measure actual curves, not control hulls. Equal profile CP counts are neither required nor sufficient for a good Loft; correspondence, parameterization, direction and seams matter.

Preserve intended creases. Properly sized Blend/Fillet transitions can be correct; no universal ban or narrow-band requirement. Curvature-sign tests apply only to regions expected to be convex and require a consistent plane normal/direction; legitimate concave outlines may change sign.

Compare fixed-camera silhouettes, openings and critical local features under one registration. Independently rescaling/recentering candidates can hide errors. Flat unlit masks are easier to segment; rendered shadows/highlights can contaminate thresholded silhouettes.

Rhino8.29 verification: Brep.CreatePlanarBreps([outer, inner], tolerance) produced one face with two loops and area1500 for a40×40 outer and10×10 inner boundary. Extrusion.AddInnerProfile is an alternative for holed extrusions, not proof that planar holes are unsupported. Validate input nesting/coplanarity and outputs per call.

Retain master curves, axis and array parameters in lines/project records. Choose instances or copies by editing requirements; recheck transformed joins. A particular wheel's measurements/sampling/IoU do not validate unrelated reconstructions.
