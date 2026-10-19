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

### ⭐⭐ Geometry API binding traps live in their own reference

The four patterns above are **attribute-level**. The geometry API carries
13 more that only fail **at runtime** — `BrepFaceList` has no `__len__`,
`Brep` has no `Volume`, `Extrusion.Create` takes four arguments,
`CreateFilletEdges` wants positional indices and `BlendType.Fillet`
(there is no `Normal`), and `rs.Command` blocks the MCP call.

⛔ **Read [14 RhinoCommon Python binding traps](14-rhino-python-binding-traps.md)
before writing geometry code.** That file was produced by running the code on
this machine, not by paraphrasing documentation.

### ⭐ The port is not a constant

The port, path and start-up command change with the plugin version, the launch arguments and what is currently occupied.
⛔ **Any hard-coded port is wrong** — including values measured on this package's development machine.

The correct approach: run `MCPStart` / `MCPConnect` and **read the banner it prints**,
or try first and fall back to the address in the banner if the connection fails. When the connection fails, check the port first;
⛔ do not suspect the geometry or the command.

### ⭐ The port is not a constant, but the probe is

The port, path and start-up command change with the plugin version, the launch arguments and what is currently occupied.
⛔ **Any hard-coded port is wrong** — including values measured on this package's development machine.

The correct approach: run `MCPStart` / `MCPConnect` and **read the banner it prints**,
or try first and fall back to the address in the banner if the connection fails. When the connection fails, check the port first;
⛔ do not suspect the geometry or the command.

### ⭐ Probing the official RhinoAI 0.3.0 server (measured)

⚠️ **Bypass the HTTP proxy first.** This machine has `http_proxy` set, so
curl goes through the proxy by default; the proxy returns 502 or a connection
error, which **looks like a closed port when the port is actually open**.

```bash
# ⛔ Without --noproxy '*' you get a false negative
curl -s -m 8 --noproxy '*' -X POST "http://127.0.0.1:<PORT>/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2024-11-05","capabilities":{},
        "clientInfo":{"name":"probe","version":"1.0"}}}'
```

**The confirmation response from the official server**:

```json
{"jsonrpc":"2.0","id":1,"result":{
  "protocolVersion":"2024-11-05",
  "serverInfo":{"name":"rhino-mcp","version":"0.3.0.0"},
  "capabilities":{"tools":{"listChanged":false},...}}}
```

**Response header `Server: Microsoft-HTTPAPI/2.0`** means it runs on HTTP.sys — the
signature of the official in-Rhino HTTP service.

### ⭐ Three moves to find the port

```bash
# 1. List local listeners. HTTP.sys ports are owned by PID 4 and are easy to miss.
netstat -ano | grep LISTENING | grep 127.0.0.1

# 2. PID 4 = HTTP.sys = the in-Rhino service; community builds are separate processes
# 3. Try initialize on each candidate; look for serverInfo.name == "rhino-mcp"
```

⚠️ **Measured on this machine**: the official 0.3.0 listens on **10502**;
community builds commonly use 25105. The two speak **different protocols** —
⛔ do not carry assumptions from one over to the other.

### ⭐ End-to-end proof: live data, not just a handshake

A successful `initialize` only proves the port is right. Real verification is a
`tools/call` that returns **live Rhino data**:

```bash
curl -s -m 15 --noproxy '*' -X POST "http://127.0.0.1:<PORT>/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call",
       "params":{"name":"get_context","arguments":{}}}'
```

It returns `activeViewport` (camera location, display mode), `document`
(`objectCount`, `layerCount`) and the `grasshopper` array.

⛔ **`objectCount: 0` still counts as connected** — that is a normal empty
document, not a fault.

### ⭐ The official 0.3.0 tool list (31 tools)

Verified against `tools/list`. **Note there is no `list_slots`** — the mention
of `list_slots` elsewhere in this package is generic wording; this version has none.

| Category | Tools |
|---|---|
| Read | `get_context` `get_selection` `list_objects` `get_viewport_image` `get_commands` |
| Modify | `run_command` `run_python` `run_csharp` `set_selection` `set_camera` |
| Files | `open_doc` `save_doc` `close_doc` |
| View | `zoom_to_object` `zoom_to_layer` `set_layer_material` |
| Grasshopper | `g1_start` `g1_place_component` `g1_place_slider` `g1_connect` `g1_connect_many` `g1_delete_component` `g1_search_components` `g1_describe_component` `g1_get_canvas_graph` `g1_solve_graph` `g1_apply_graph` `g1_clear_canvas` |
| router internals | `_router_spawn_listener` `_router_close_listener` `_router_quit_app` |

⛔ **Do not run interactive commands through `run_command`** (they wait for Enter).
⛔ **Prefer `run_python` over `run_command`** — Rhino command-line options shift
between versions and locales, while the Python API stays stable.

⚠️ `run_csharp` executes C# directly (Roslyn) and can do things RhinoCommon
cannot, but ⛔ do not use it unless the user explicitly asks.

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