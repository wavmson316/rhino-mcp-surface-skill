# Rhino MCP Surface Skill

[简体中文](../../README.md) | English

**Lets an AI agent plan and build editable NURBS surfaces in Rhino 8 through McNeel Rhino MCP, starting from photographs, sketches, orthographic views, dimensions, or scan data.**

This is a modeling skill written to be read by an AI agent. It guides the agent through interpreting the shape, choosing a patch layout and UV flow, calling Rhino tools, checking results, and recovering from failure. It does not include Rhino itself, and it is neither an MCP server nor a one-click photo-to-CAD application.

**[Download the Chinese / English package](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest)** · **[Chinese skill entry](../../SKILL.md)** · **[English skill](SKILL.md)** · **[Installation and connection guide](INSTALL-CHECK.md)**

## Which Rhino, and which MCP?

| Component | Technology and status adopted by this project |
|---|---|
| Modeling software | McNeel **Rhinoceros 3D / Rhino 8**; actually tested on **Windows + Rhino 8.29.26063.11001** |
| MCP project | **Rhino MCP Platform**, maintained by McNeel in **[mcneel/RhinoAI](https://github.com/mcneel/RhinoAI)** |
| Rhino plugin | Install **`Rhino-MCP-Platform`** from Rhino `PackageManager`; follow the current official guide to pick the package matching Rhino 8 |
| Client connection | Use the official MCP router / client connector. On the Codex route, `MCPConnect` prints the configuration → configure the router → restart the client; see below |
| Geometry execution | MCP `run_python` / `run_csharp` / `run_command`, plus RhinoCommon; the Python helpers run on **Python 3 inside Rhino** |
| State and acceptance interface | Per the current tool list, `list_slots`, `get_context`, `list_objects`, `get_commands`, `get_viewport_image`, and similar calls |
| Parametric tooling | Grasshopper 1 may be used where the current interface exposes the matching `g1_*` tools; this package has not completed end-to-end GH validation |
| Version floor | **Rhino 6/7 are not supported** by the official RhinoAI platform; this package makes no compatibility claim for them |
| Other environments | **Rhino 9, macOS, and unrelated third-party Rhino MCP servers have not been tested by this package** |

This project is independent of McNeel and is not an official McNeel Skill. It uses the MCP project linked above, not any third-party product that happens to share the name "Rhino MCP." Tool names and configuration change with plugin and client versions, so the agent discovers the actual capabilities first.

```text
Client references and modeling requirements
        ↓
AI agent with Skills and MCP support
        ├── reads this skill: modeling decisions, patch layout, quality, execution discipline
        ↓
McNeel Rhino MCP router / connector
        ↓
Rhino-MCP-Platform plugin → Rhino 8 / RhinoCommon
        ↓
Curves, NURBS surfaces, Breps, 3dm files, and inspection reports
```

## What can this actually help an agent do?

| Task | What the skill guides | Typical example |
|---|---|---|
| Reference reconstruction | Separate silhouette, shading, and material; handle calibration and perspective; identify unknown depth and back-side assumptions | Product photos, hand sketches, orthographic views |
| Patch layout and UV planning | Plan the main parent surfaces, side surfaces, transition bands, and corner regions; record adjacency, movable edges, and continuity targets | Glossy mouse shells, vehicle side panels, asymmetric housings |
| Curve scaffold and fairness | Build primary sections and boundaries; check direction, seams, true spans, curvature combs, and fitting deviation | Belt lines, wheel arches, grip sections, gently crowned covers |
| Surface construction method | Choose among analytic surfaces, Revolve, Loft, Sweep1/2, EdgeSrf, NetworkSrf, BlendSrf, and MatchSrf according to the constraints | Rotational speakers, lens barrels, double-curved shells, edge-band transitions |
| Difficult regions | Compare layouts for branching centers, multi-sided corners, fading features, variable-width transitions, recesses, and grip hollows | Three-way tube handles, thumb recesses, fading fillets |
| Product detail and assembly | Derive panel gaps, holes, inner walls, buttons, and grilles from the parent surfaces; separate moving parts, thickness, and assembly clearance | Routers, cameras, phones, air-conditioning panels |
| Reverse engineering and repair | Rebuild from scan sections or design intent; check noise, deviation, and layout; distinguish fitting from mesh conversion | Scanned grips, missing-surface repair |
| Inspection and delivery | Report shape, structure, fairness/seams, and engineering checks separately; keep parent surfaces, versions, and unverified items | 3dm, task-specific exchange formats, and reports |

**Generalization principle: decide from the actual geometry and the delivery requirement.** It does not dictate that a vehicle "must be built one way" or that an appliance "must be a plane plus fillets," and it does not treat single-span, G2, or a closed solid as one universal target for every task.

### Scripts actually included in the package

| File | Function | Boundary |
|---|---|---|
| `audit_geometry.py` | Read Degree, true SpanCount, control points, naked edges, non-manifold edges, and solid state | Structural audit; does not certify shape quality or G2 |
| `nbs_geometry.py` | Curves, deviation-budget-constrained single-span rebuilds, three/four-edge surfaces, ruled surfaces, Loft, curvature queries, curve endpoint diagnostics | In-memory geometry helper; agent-controlled insertion into the user document |
| `sample_seam_g1.py` | Bidirectional sampling of boundary distance and surface tangent-plane angle | **Does not judge G2**; does not prove the absence of folds over the whole domain |
| `outline_metrics.py` | Standalone 2D silhouette IoU and contour distance | Single simple polygon outer ring; not depth or dimensional certification |
| Tests and release checks | Rhino regression, 2D analytical cases, syntax and file-link checks | Does not replace acceptance of real modeling tasks |

## Installation: software, MCP, and skill are three separate parts

### 1. Install and run Rhino 8

Have [Rhino 8](https://www.rhino3d.com/download/) installed and running. The current verified platform is Windows; this skill ships neither a Rhino installer nor a license.

### 2. Connect McNeel Rhino MCP

Start with the official [Getting Started](https://mcneel.github.io/RhinoAI/docs/getting-started/) guide.

- **Codex**: install `Rhino-MCP-Platform` from the Rhino 8 `PackageManager`, restart Rhino, then run `MCPConnect`. Configure the Codex MCP settings with the actual command and args it prints; see the [official Codex guide](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/).
- **Claude Desktop**: install the connector and the Rhino plugin following the [official connector guide](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/).
- **Other agents**: the official documentation also covers Claude Code, GitHub Copilot, Gemini CLI, and similar routes. Being able to connect MCP does not mean the client automatically supports Skills; install skills per each client's own instructions.

**You do not need to copy one fixed port from someone's machine to everyone.** Use the output of `MCPConnect` on your own machine and the current official documentation; if you already have a working connection, do not restart the service.

### 3. Install either the Chinese or the English skill — choose one

From [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest), choose:

- `rhino-mcp-surface-skill-1.2.0-zh-CN.zip`: Chinese skill body, 13 references, installation guide, templates, and scripts.
- `rhino-mcp-surface-skill-1.2.0-en.zip`: English skill body, 13 references, installation guide, templates, and the same set of scripts.

Both archives extract to a `rhino-mcp-surface-skill` folder. Place it in a Skills directory supported by your client, making sure `SKILL.md` sits directly inside. Both packages use the same internal ID, so **install one language only; do not register two Skills with the same name at once**.

Common Codex user-level location is `~/.agents/skills/`, and the project-level location is `.agents/skills/`; defer to the current Codex documentation and your actual configuration. Other clients use different paths. If a client supports MCP but not automatic Skills discovery, you can have the agent read the entry point and its relative references explicitly, but identical automatic triggering is not guaranteed.

When cloning the repository for development, do not register the whole repository including `en/` as a single Skill; install from one of the single-language ZIPs above so the same entry point is not discovered twice.

Restart the client or open a new session, then run the connection and in-memory geometry self-checks in [INSTALL-CHECK.md](INSTALL-CHECK.md).

## How does an object actually get built?

The new [detailed patch layout and construction playbook](references/12-object-construction-playbooks.md) provides:

- Curve IDs, the boundaries/UV/method of each patch, adjacency continuity, and the movable range.
- A ten-step build for a mouse-style shell, from blockout and cross sections through top, sides, thumb recess, transitions, and detail.
- Concrete patch layouts and failure fallbacks for rotational speakers/bodies and three-way tube handles.
- An executable 120×70 double-curved closed shell with an actual maximum height of 40: six parent surfaces → one valid solid, adding **12/12** passing checks. Entry point is `scripts/example_closed_shell.py`.

The programmatic example deliberately keeps G0 hard edges and validates only the parent-surface construction chain; it must not be presented as a finished mouse, a photo reconstruction, or a G2 transition. Whether the key forms match the reference must be checked item by item within the task, using a fixed camera, primary sections, and a feature checklist.

## How do I prompt it after installing?

```text
Use rhino-mcp-surface-skill.
First confirm the Rhino MCP connection, target document, units, and existing objects.
From the mouse reference I attached, analyze proportions, top crown height, and the thumb recess;
compare two patch layouts, then build editable NURBS parent surfaces and transitions.
Without reliable dimensions, start from a normalized scale and state the assumptions.
When finished, save a new 3dm version and report shape, structure, and continuity checks separately.
```

You can also ask it to "fix the crease between these two surfaces," "rebuild a rotational speaker from dimensions," or "analyze how to lay out the patches at the center of a three-way junction." The clearer the references, dimensions, and acceptance targets, the easier the result is to assess.

## Language, contents, and validation

| Content | 中文 | English |
|---|---|---|
| Overview | [README](../../README.md) | This page |
| Skill entry | [SKILL.md](../../SKILL.md) | [SKILL.md](SKILL.md) |
| Installation and connection | [INSTALL-CHECK.md](../../INSTALL-CHECK.md) | [INSTALL-CHECK.md](INSTALL-CHECK.md) |
| References and templates | [references](../../references/01-intent-and-reference.md)、[template](../../templates/modeling-plan.md) | [references](references/01-intent-and-reference.md)、[template](templates/modeling-plan.md) |
| Validation record | [VALIDATION.md](../../VALIDATION.md) | [VALIDATION.md](VALIDATION.md) |

The geometry runtime and machine-readable test data share the same implementation across languages. The Rhino in-memory regression passes **45/45**, the 2D metrics **17/17**, and the programmatic closed shell **12/12**. **1.2.0 is a documentation version**: verified numbers, construction discipline, and API errata were restored to the body text, and 13 construction-discipline rules were added; **the code and geometric behavior are exactly identical to 1.1.0, and no new validation claim is added**. See each language's record for the validation scope.

**Not claimed:** automatic full-domain G2/G3 certification, unique reconstruction of true dimensions from a single photograph, one-click generation of a complete vehicle, end-to-end photo-to-model quality, manufacturability, any OEM Class-A standard, and compatibility with any platform or API that has not been actually tested. Unverified items must be stated explicitly in the task delivery.

## Sources and project status

This skill is an independently compiled workflow and toolset; for the official MCP itself, see [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI). The interface description was checked on 2026-10-19 against the official installation guide and the tools discovered on the local machine; for later plugin changes, the official documentation governs.

This repository contains no book PDFs, scan pages, complete OCR, or old workspace notes. For sources and rescinded rules, see the [source audit](../../references/08-source-audit.md). No separate open-source license has been designated, and nothing here implies an MIT-style grant. For updates, see [CHANGELOG.md](CHANGELOG.md).
