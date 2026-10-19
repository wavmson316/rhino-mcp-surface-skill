# MCP execution and scripting protocol

## Discovering the current capabilities

Read the tool descriptions and locate the user documentation. Use list_slots/get_context when they exist; adapt to whichever interface a different connection exposes. Do not assume that undo, create_layer or get_object_info are present, and do not assume they are absent. Do not restart an already connected session. The port, path and start-up command come from the current plugin configuration — they are not modelling constants.

Rhino Python uses the injected document. Functions in this package take doc explicitly and never fall back to ActiveDoc or to an implicit scriptcontext. A remote Rhino may not be able to reach the client disk path, so confirm the file is reachable first.

```python
import Rhino, math
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
angle = math.radians(30)
# For a controlled layer creation: set Name first, then Add; do not actually add it during a self-check.
layer = Rhino.DocObjects.Layer()
layer.Name = 'P01_Main'
# layer_index = doc.Layers.Add(layer)
```

A unit conversion requires a decision on whether to scale the coordinates; changing ModelUnitSystem only sets metadata and is not equivalent to a full conversion. Do not copy the initialisation example over a user project. For API overloads, read the method documentation and test in memory first, and look the geometry up with doc.Objects.FindId before using a Guid.

### ⭐ Four call patterns disproven by testing on this machine

These circulate widely in textbooks and online examples, but they either raise an exception or fail silently when tested in Rhino 8:

| ⛔ Wrong | ✅ Correct | Symptom |
|---|---|---|
| `doc.Units.SetUnits(...)` | `doc.ModelUnitSystem = Rhino.UnitSystem.Millimeters` | `Units` has no such method |
| `doc.ModelUnitAbsoluteTolerance` | `doc.ModelAbsoluteTolerance` | The property does not exist |
| `Rhino.Radians(deg)` | `math.radians(deg)` | No such function under that namespace |
| `doc.Layers.Add('name')` | `layer = Layer(); layer.Name='name'; doc.Layers.Add(layer)` | A Layer object must be passed |

Mnemonic: the unit/tolerance trio is `ModelUnitSystem` / `ModelAbsoluteTolerance` /
`ModelAngleToleranceDegrees` — **all three hang off `doc`, all three carry the `Model` prefix, and all three are assigned directly rather than called.**

### ⭐ The port is not a constant

The port, path and start-up command change with the plugin version, the launch arguments and what is currently occupied.
⛔ **Any hard-coded port is wrong** — including values measured on this package's development machine.

The correct approach: run `MCPStart` / `MCPConnect` and **read the banner it prints**,
or try first and fall back to the address in the banner if the connection fails. When the connection fails, check the port first;
⛔ do not suspect the geometry or the command.

## Geometry helpers

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
import nbs_geometry as N
candidate = N.edge_srf_4(doc, c1, c2, c3, c4)
facts = N.surface_spans(candidate)
# Only in-memory geometry is computed here; re-verify against the project goal before adding to the document.
```

`rebuild_to_single_span` outputs a candidate Curve; it requires an explicit fit budget, raises on failure, and will not silently accept an out-of-tolerance result. `boundary_continuity` only checks directed G1 conditions at the ends of open curves; it does not judge surface continuity. The two-dimensional metrics are in outline_metrics and can be imported as ordinary Python.

## Controlled changes

First record the input IDs, geometry and properties; compute candidates in memory and check validity; then add them to the task layer. Record the new Guids and the P/E ID mapping. After a topological rebuild, re-identify the edges — do not reuse a stale edge index. Delete or replace the old result only after the new one passes, and keep the parent-surface version.

Group changes with BeginUndoRecord/EndUndoRecord. An undo group is not a transaction: on failure you must still track this batch's IDs and clean up or recover explicitly. Do not use a global undo to roll back another user's actions. Interdependent changes in the same document must run in sequence.

On timeout, check the object/command status and the results already produced; do not blindly retry and duplicate the model. Ordinary reads can be batched. After a large repeated feature, split and isolate by layer so that a single call does not emit an enormous amount of data.

## Commands, views and saving

Verify the current command and its options; for internationalised installs use the English_ prefix. get_commands only proves the registered name, not the options or overloads. Avoid interactive point picking that no one can answer. After a command, check the new IDs, the count, the type and validity — the success message alone is not enough.

Fix the camera and the clipping for comparisons; a screenshot can only be called a visual check if it is actually returned and viewed. Request only the views and locals you need; when the user restricts image reading, use text/numerical checks and state the limitation.

Save to a new version path, and keep outputs and test files separate from the user's originals. Formats such as 3dm/STEP must be re-verified for units, dimensions and completeness against the contract; writing a file out is not a round-trip test. Do not close, clear or replace an unsaved user document.

GH is for parametric families and repeated or gradient patterns. Discover the components and data interfaces first, and inspect the tree, null values and warnings before baking; not every repeated feature needs GH. After converting SubD to NURBS, check the poles and face count — it does not become Class-A automatically.