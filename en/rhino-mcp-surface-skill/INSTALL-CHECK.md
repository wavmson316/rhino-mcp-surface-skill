# Installation, MCP connection, and self-check

## Tested integration

This package targets McNeel [Rhino MCP Platform / RhinoAI](https://github.com/mcneel/RhinoAI), plugin `Rhino-MCP-Platform`. Tested on Windows, Rhino8.29.26063.11001, and Rhino Python3. Other platforms, Rhino6/7, Rhino9 WIP/Beta, and unrelated third-party MCP servers remain untested. The skill and plugin are separate installations.

## 1. Install and connect the official MCP

Start with [official Getting Started](https://mcneel.github.io/RhinoAI/docs/getting-started/). For Codex:

1. Run Rhino8 `PackageManager`, install `Rhino-MCP-Platform`, and restart Rhino as required.
2. Run `MCPConnect` in Rhino and read its router command and arguments.
3. Configure the MCP server in Codex, commonly in `~/.codex/config.toml`, using that actual output. The official example has this structure; use it literally only when the command exists on your machine:

```toml
[mcp_servers.rhino]
command = "rhino-mcp-router"
args = ["--default-version", "8"]
```

4. Restart Codex and verify the server/tools are visible. Do not guess executable paths or hard-code a developer-machine port.

[Official Codex guide](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/) · [Claude Desktop connector](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/)

The router/connector provides the MCP connection. `run_python`/`run_csharp`/`run_command` execute inside Rhino; Python helpers use RhinoCommon. Live server descriptions define actual tool names and options. Keep an already working connection.

## 2. Install one language

Download Chinese or English ZIP from [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest). Copy the extracted `rhino-mcp-surface-skill` folder to your client's supported Skills directory, with `SKILL.md` directly inside. Both languages share one internal ID; install one.

Common Codex locations are `~/.agents/skills/` and project `.agents/skills/`; verify current configuration. Other clients load skills differently. MCP support alone does not guarantee skill discovery. Start a new session and confirm the skill is visible.

## 3. Inspect connection and document without modifying them

Read `get_context`; use `list_slots` when available to identify the target. Adapt to the actual interface when absent. Ask only if multiple documents cannot be distinguished; never clear or close the user's current document.

```python
import Rhino
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
```

The document handle above is supplied by this MCP integration. Other hosts require explicit adaptation. Do not fall back to ActiveDoc or overwrite settings.

## 4. Run in-memory regression checks

Execute inside Rhino Python3, replacing the placeholder with the real skill path accessible to the Rhino process:

```python
import sys
from pathlib import Path
skill_root = Path(r'<actual skill installation directory>')
sys.path.insert(0, str(skill_root / 'scripts'))
from smoke_test_rhino import run_tests
result = run_tests(__rhino_doc__)
print(result)
```

Expected: 45 cases pass, without adding/deleting/editing document objects. Preserve failures and inspect specific APIs; do not delete assertions. Ordinary Python can run:

```text
python scripts/test_outline_metrics.py
python scripts/check_release.py
```

Expected: 17 outline cases and static checks pass. Geometry code is shared with the 1.0.0 tested implementation; see [VALIDATION.md](VALIDATION.md).

## Troubleshooting

| Symptom | Check |
|---|---|
| No connection or tools | Plugin installation/loading, MCPConnect output, client configuration and restart |
| MCP works, skill missing | Directory nesting, client Skills support, fresh session |
| import Rhino fails | Geometry scripts need Rhino Python; outline_metrics is standalone |
| Script missing | Use a path accessible to the Rhino process; client and remote paths may differ |
| Imported module has no doc | Pass the injected document explicitly; imports do not inherit caller globals |
| Assertions fail | Check Rhino/API version and preserve failure evidence |

Installation checks do not certify a real model's shape, G2, or manufacturability.
