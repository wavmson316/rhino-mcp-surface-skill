# v1.8.0 validation

Executed2026-10-20 on Windows/Rhino8.29.26063.11001/Rhino Python3 through the current MCP router. No scanned images read.

| Check | Result | Evidence |
|---|---|---|
| Original in-memory geometry |45/45|[results](rhino-test-results.json)|
| Procedural shell chain |12/12|[results](example-test-results.json)|
| Native construction and source delivery |32/32|[results](native-test-results.json), [suite](scripts/test_native_builders.py)|
| Single-ring metrics |21/21|[results](outline-test-results.json)|
| Components/holes metrics |27/27|[results](region-test-results.json)|
| Syntax/links/encoding/bilingual file coverage/shared scripts |Current checks|[checker](scripts/check_release.py), [manifest](release-manifest.json)|

New cases cover native two-rail/network construction, a3×3 network producing one saddle with an independent center/curvature check, no document mutation in memory mode, retained exact inputs, invalid-input rejection, failed caps, empty/duplicate output gates, isolation from pre-existing solids, source mapping, count-only incompleteness, .3dm GUID/layer/mapping persistence, missing-source detection and planar holes.

Persistence tests used a separate headless document and test file. Live object IDs, layer count and modification state matched before/after; the live document was not opened/closed/saved. Failure cleanup targets only newly added objects; empty created layers may remain.

Even-odd filling is winding-independent. Each component has one outer ring with strictly internal disjoint/non-nested holes; islands are separate components and components union. Specified crossing/touching/retracing cases are rejected using floating-point predicates. Normalize/clean extreme or near-degenerate data. Rasterization can miss thin features.

Not established: reconstruction of the user's failed reference (no failed model/log supplied), arbitrary-agent/reference guarantees, unique hidden geometry, full-domain self-intersection/G2/G3, all commands/platforms, manufacturing or STEP/IGES/STL round trips. Only example .3dm source persistence was verified. quality_gate is structural; sampled seams are finite position/tangent-plane diagnostics; the procedural shell is not photo reconstruction. Native network edge conditions here are position, not automatic parent G1/G2.
