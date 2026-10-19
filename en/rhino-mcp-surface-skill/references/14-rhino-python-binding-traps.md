# RhinoCommon / Python bindings: verify before use

Inspect the connected tool schema and runtime overload documentation; test with in-memory geometry before document mutation. A failed overload does not establish that the API is absent.

Read-only Rhino 8.29 / Python3 inspection in this review observed:

- Extrusion.Create(Curve, Double, Boolean) and Extrusion.Create(Curve, Plane, Double, Boolean) bindings both exist; the Boolean is cap.
- Brep.CreateFilletEdges exposes 7- and 9-argument overloads. The 7-argument order is brep, edgeIndices, startRadii, endRadii, blendType, railType, tolerance. Do not copy an unverified 8-argument example.
- BrepFace exposes OuterLoop and AdjacentEdges(), not OuterEdge in this environment. A loop can contain multiple edges.
- BrepEdge exposes EdgeIndex rather than Index. Topological indices are not permanent spatial labels.
- isinstance(value, Rhino.Geometry.Brep) works for an ordinary Brep. Diagnose actual proxy/runtime issues before replacing type checks with class-name strings.

These observations establish binding availability, not successful filleting or complex reconstruction. Validate enums, .NET collections, units, geometry validity and outputs per call. GUIDs are not geometry; obtain objects through the injected document, duplicate for in-memory trials, and record IDs/Undo scope for document writes.


## Native two-rail and network APIs, verified 2026-10-20

Brep.CreateFromSweep(rail1, rail2, sections, closed, tolerance) returns Breps; SweepTwoRail.PerformSweep also exists. A missing method named CreateSweep2 does not establish absence of two-rail APIs.

NurbsSurface.CreateNetworkSurface(curves_u, 1, 1, curves_v, 1, 1, edge_tol, interior_tol, angle_tol) returned (surface, error) through Python3; success error was0 and angle tolerance is radians. Installed RhinoCommon XML defines 0=Loose,1=Position,2=Tangency,3=Curvature; the four1 values here are position-only, not transferred parent G1/G2.

CreatePlanarBreps([outer, inner], tol) retained a planar hole: two loops, area1500 for40×40 minus10×10. Inspect actual overloads/types instead of guessing by arity.

Count and default enumeration may have different inclusion/filtering; inspect explicit settings and known GUIDs before alleging object-table corruption. isinstance(geometry, Rhino.Geometry.Curve) works; IsValid alone is not a curve type filter. Command blocking depends on context/input completion; native wrappers avoid unattended command prompts. Check module.__file__ and reload changed loaded modules; deleting bytecode does not refresh sys.modules.
