# Rhino MCP Surface Skill

[简体中文](https://github.com/wavmson316/rhino-mcp-surface-skill/blob/main/README.md) | English

**A modeling skill for AI agents using McNeel's Rhino MCP Platform to plan and build editable NURBS surfaces in Rhino 8 from photos, sketches, orthographic drawings, dimensions, or scan references.**

The skill teaches shape interpretation, patch layout and UV flow, construction choices, controlled tool execution, and evidence-based validation. It is not Rhino itself, an MCP server, or a one-click photo-to-CAD application.

**[Download Chinese / English packages](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest)** · **[English skill](en/rhino-mcp-surface-skill/SKILL.md)** · **[Setup guide](en/rhino-mcp-surface-skill/INSTALL-CHECK.md)**

## Which Rhino and which MCP?

| Component | Technology and compatibility |
|---|---|
| CAD application | McNeel **Rhinoceros 3D / Rhino 8**. Actually tested on **Windows with Rhino 8.29.26063.11001** |
| MCP project | **Rhino MCP Platform**, maintained by McNeel in **[mcneel/RhinoAI](https://github.com/mcneel/RhinoAI)** |
| Rhino plugin | Install **`Rhino-MCP-Platform`** with Rhino `PackageManager`; follow the current official Rhino 8 instructions |
| Client connection | Official MCP router or client connector. For Codex: run `MCPConnect`, use the emitted router configuration, and restart the client |
| Geometry execution | MCP `run_python`, `run_csharp`, and `run_command`, plus RhinoCommon. Python helpers run inside **Rhino Python 3** |
| Inspection tools | Discover the live tool set: for example `list_slots`, `get_context`, `list_objects`, `get_commands`, and `get_viewport_image` |
| Parametric workflows | Grasshopper 1 when corresponding `g1_*` tools are available; no end-to-end GH validation is claimed |
| Other environments | **Rhino 6/7, Rhino 9 WIP/Beta, macOS, and unrelated third-party Rhino MCP servers have not been tested by this package** |

This is an independent skill, not an official McNeel skill. It targets the MCP project linked above, rather than every third-party server called “Rhino MCP.” Tools and configuration can change between versions; the agent discovers actual capabilities before execution.

```text
Your references and modeling requirements
                  ↓
AI agent with Skills and MCP support
    ├── reads this skill: modeling decisions and validation
                  ↓
McNeel Rhino MCP router / connector
                  ↓
Rhino-MCP-Platform plugin → Rhino 8 / RhinoCommon
                  ↓
Curves, NURBS surfaces, Breps, 3dm files, and inspection reports
```

## What can it help an agent do?

| Task | Guided behavior | Examples |
|---|---|---|
| Interpret references | Separate silhouette, shading, materials, scale, perspective, and unknown depth | Product photographs, concept sketches, orthographic views |
| Plan patches and UV flow | Allocate primary surfaces, side surfaces, transition bands, and corners; record adjacency and continuity targets | Glossy mouse shells, vehicle panels, asymmetric housings |
| Build curve scaffolds | Design sections and boundaries; check direction, seams, true span counts, curvature combs, and fitting deviation | Shoulder lines, wheel arches, handle sections, crowned covers |
| Choose construction methods | Select analytic geometry, Revolve, Loft, Sweep1/2, EdgeSrf, NetworkSrf, BlendSrf, or MatchSrf from constraints | Rotational speakers, lens barrels, double-curved shells |
| Resolve difficult regions | Compare layouts for branches, multi-sided corners, fading features, variable-width blends, and recesses | Y-junction handles, thumb recesses, fading fillets |
| Add product details | Derive panel gaps, openings, walls, buttons, and repeated features; keep moving components separate | Routers, cameras, phones, air-conditioning panels |
| Reconstruct or repair | Rebuild from scan sections and design intent; distinguish fitting from mesh conversion | Scanned grips and missing-surface repair |
| Inspect and deliver | Report shape, structure, fairness/seams, and engineering separately; keep parent surfaces and versions | 3dm, task-specific exchange files, and reports |

**Generalization comes from geometric constraints and delivery requirements.** The skill does not force every appliance to be planar, every surface to be single-span, or every seam to be G2.

### Included working scripts

| Script | Function | Scope |
|---|---|---|
| `audit_geometry.py` | Degree, true SpanCount, control points, naked/non-manifold edges, solid state | Structural facts, not shape or G2 certification |
| `nbs_geometry.py` | Curves, budget-checked rebuilds, three/four-edge surfaces, ruled surfaces, lofts, curvature queries, endpoint diagnostics | In-memory geometry; document additions are controlled by the caller |
| `sample_seam_g1.py` | Bidirectional sampled edge gaps and tangent-plane angles | **Not G2**, not a proof against folds/overlap |
| `outline_metrics.py` | Standalone 2D silhouette IoU and boundary distance | Single simple rings only; not depth or dimensional certification |
| Regression/release checks | Rhino geometry cases, analytical 2D examples, syntax and file links | Not a substitute for real modeling-task acceptance |

## Install the three separate parts

### 1. Rhino 8

Install and license [Rhino 8](https://www.rhino3d.com/download/). Windows is the tested platform. This repository supplies neither Rhino nor a license.

### 2. McNeel Rhino MCP

Follow the official [Getting Started guide](https://mcneel.github.io/RhinoAI/docs/getting-started/).

- **Codex:** install `Rhino-MCP-Platform` from Rhino 8 `PackageManager`, restart Rhino as required, and run `MCPConnect`. Use the actual command/arguments it prints for your Codex MCP configuration. See the [official Codex guide](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/).
- **Claude Desktop:** follow the official [connector guide](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/) for the connector and Rhino plugin.
- **Other agents:** the official documentation also covers Claude Code, GitHub Copilot, Gemini CLI, and other clients. MCP connectivity does not automatically imply Skills support; follow your client's skill-loading instructions.

Do not copy a developer-machine port as a universal setting. Use your own `MCPConnect` output and the current official instructions. Do not restart a working connection merely to discover its address.

### 3. Choose one skill language

Download an asset from [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest):

- `rhino-mcp-surface-skill-1.1.0-zh-CN.zip`: Chinese entry, 12 references, setup guide, template, and scripts.
- `rhino-mcp-surface-skill-1.1.0-en.zip`: English entry, 12 references, setup guide, template, and the same scripts.

Both archives contain a `rhino-mcp-surface-skill` folder. Copy it to a Skills location supported by your client, with `SKILL.md` directly inside that folder. **Install one language: both use the same internal skill ID.**

Common Codex locations are `~/.agents/skills/` for user-level skills and `.agents/skills/` for project-level skills; verify against your current client configuration. Other clients use different locations. If a client only supports MCP, explicitly reading the skill may still be useful, but automatic skill discovery is not guaranteed.

For installation, use one language ZIP rather than registering the entire development repository containing `en/`; this avoids duplicate discovery of the same skill ID.

Restart the client or open a new session, then run the [installation checks](en/rhino-mcp-surface-skill/INSTALL-CHECK.md).

## How does an object actually get built?

The [construction playbooks](en/rhino-mcp-surface-skill/references/12-object-construction-playbooks.md) specify curve IDs, patch boundaries/UV/methods, seam targets, editable constraints, build steps, and recovery gates. They include a ten-step mouse-like shell plan, rotational products, and three-way junctions.

An executable 120×70 crowned parent enclosure builds six parent faces into one valid solid with actual crown height40; **12/12 additional checks pass**. Use `scripts/example_closed_shell.py`. It intentionally retains G0 edges and is a parent-construction benchmark, not photo reconstruction, a finished mouse, or a G2 demonstration. Real shape acceptance still needs task-specific fixed-camera, section, and feature comparisons.

## Example prompt

```text
Use rhino-mcp-surface-skill.
Check the Rhino MCP connection, target document, units, and existing objects.
Use the attached mouse reference to analyze proportions, top crown, and thumb recess.
Compare two patch layouts, then build editable NURBS parent surfaces and transitions.
If dimensions are unknown, start normalized and record assumptions.
Save a new 3dm version and report shape, structure, and continuity evidence separately.
```

Other tasks include repairing a visible crease between surfaces, building a dimensioned rotational speaker, or planning the center of a three-way junction. Clear references, dimensions, and acceptance targets make results easier to assess.

## Bilingual contents and validation

The English package includes the complete skill entry, all 12 reference documents, setup guide, project template, validation notes, and changelog. The geometry implementation and machine-readable test data are shared between language variants.

The 1.0.0 geometry suite passed **45/45 Rhino in-memory cases** and **17/17 standalone 2D cases**. Version 1.1.0 adds bilingual documentation, detailed construction playbooks, and 12 additional procedural-construction checks. Read [VALIDATION](en/rhino-mcp-surface-skill/VALIDATION.md) for the precise scope.

Not claimed: full-domain G2/G3 certification; unique dimensional reconstruction from one photograph; one-click complete vehicles; end-to-end photo reconstruction quality; manufacturing feasibility; any OEM Class-A standard; or compatibility with untested platforms and servers. Report unverified items in each delivery.

## Sources and project status

The modeling workflow and helpers are independently maintained. The official MCP implementation belongs to [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI). Connection guidance was checked on 2026-10-19 against upstream instructions and currently exposed tools; follow upstream documentation if the plugin changes.

No book PDFs, scans, complete OCR, or old workspace notes are distributed. See the source audit in the selected language package. No separate open-source license has been designated; no MIT or similar permission is implied. See [changelog](en/rhino-mcp-surface-skill/CHANGELOG.md).
