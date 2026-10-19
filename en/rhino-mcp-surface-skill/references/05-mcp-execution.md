# MCP execution and scripts

## Discover live capabilities

Use McNeel [Rhino MCP Platform](https://github.com/mcneel/RhinoAI), plugin `Rhino-MCP-Platform`, via its router/connector. Read the current tool descriptions and identify the target document. Use list_slots/get_context when present; adapt when absent. Do not assume undo/create_layer/get_object_info exists or does not exist. Keep working connections; paths, ports, and launch commands come from current configuration.

Use the injected document and explicit doc arguments. Never fall back to ActiveDoc or implicit scriptcontext. A remote Rhino process may not share the client filesystem.

```python
import Rhino, math
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
angle = math.radians(30)
layer = Rhino.DocObjects.Layer()
layer.Name = 'P01_Main'
# Add only in an authorized editing step:
# layer_index = doc.Layers.Add(layer)
```

Changing ModelUnitSystem metadata is not a complete coordinate conversion. Decide scaling and tolerance conversion explicitly. Inspect overload docstrings and validate APIs with in-memory examples. Find GUID objects through doc.Objects.FindId before using geometry.

## Helpers

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
import nbs_geometry as N
candidate = N.edge_srf_4(doc, c1, c2, c3, c4)
facts = N.surface_spans(candidate)
```

Rebuild requires an explicit deviation budget and raises instead of silently accepting an excessive result. Endpoint continuity is a directed open-curve diagnostic, not surface continuity. outline_metrics imports in ordinary Python without Rhino.

## Controlled edits

Record original IDs, geometry, and attributes. Compute and inspect candidates in memory, then add them to task layers and record new IDs. Re-identify edges after topology changes. Retire originals only after replacements pass stage checks; preserve parent versions.

Use BeginUndoRecord/EndUndoRecord for groups, not database-style transactions. Track partial additions for explicit cleanup/restoration. Do not use global Undo to disturb unrelated work. Order dependent edits; batch independent reads where appropriate.

After timeouts inspect command/object state before retrying. Large repeated details belong late in the workflow and isolated layers; avoid huge dumps.

## Commands, views, and files

Discover command names and verify options. English underscore prefixes help localization; discovery proves registration, not option signatures. Avoid unattended interactive picks. Check IDs, counts, types, and validity after execution rather than trusting success text.

Use fixed cameras/crops for comparison; claim visual inspection only after actually receiving and examining images. Respect requests not to read images and report numerical-only limits.

Save new versions and separate test outputs. Check exchange units, dimensions, and integrity when required. Do not clear/close/replace an unsaved user document. GH component/data-tree discovery precedes solving/baking. SubD conversion needs face-count and pole inspection and is not automatic Class-A.
