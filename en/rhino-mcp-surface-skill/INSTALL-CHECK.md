# Installation, MCP connection, and self-checks

[简体中文](../../INSTALL-CHECK.md) | English

## Supported environment

This package targets McNeel's [Rhino MCP Platform / mcneel/RhinoAI](https://github.com/mcneel/RhinoAI), with Rhino plugin package `Rhino-MCP-Platform`. Tested on Windows + Rhino 8.29.26063.11001 + Rhino Python 3. **Version floor: the official RhinoAI platform does not support Rhino 6/7**; Rhino 8.x is the minimum. Rhino 9, macOS, and other third-party MCP servers are untested. The skill and the plugin are installed separately.

## 1. Install and connect the official MCP

Start with the official [Getting Started](https://mcneel.github.io/RhinoAI/docs/getting-started/). Below is the official Codex route; the actual commands are whatever the current `MCPConnect` prints.

1. Run `PackageManager` in Rhino 8, search for and install `Rhino-MCP-Platform`, and restart Rhino when prompted.
2. Run `MCPConnect` in Rhino and read the router command and arguments it prints.
3. Configure that output in the Codex MCP settings. The usual configuration file is `~/.codex/config.toml`. The official example has the following structure; use it only if your machine really has that command:

```toml
[mcp_servers.rhino]
command = "rhino-mcp-router"
args = ["--default-version", "8"]
```

4. Restart Codex and confirm the MCP service and its tools are visible. The command, executable path, and arguments should all come from step 2; do not guess a fixed port.

[Official Codex guide](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/) · [Official Claude Desktop connector](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/)

The MCP router/connector handles the protocol and the Rhino connection; `run_python` / `run_csharp` / `run_command` perform the actual execution, and the Python geometry runs through RhinoCommon. Tool names and options are determined by the current service description.

## 2. Install a language package

Download the Chinese or English ZIP from [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest), extract it, and place the whole `rhino-mcp-surface-skill` folder on a skills path supported by your agent. The entry point is the `SKILL.md` sitting directly inside that folder. Both packages share one ID; install one of them.

Common Codex user-level path is `~/.agents/skills/` and the project-level path is `.agents/skills/`; defer to the client's current configuration. Other clients load skills per their own instructions; MCP availability does not imply automatic skills discovery. Open a new session to confirm the skill is visible.

## 3. Read-only checks on the document and connection

Have the agent read `get_context`; where `list_slots` exists, use it to locate the target instance first. Where these interfaces are unavailable, use whatever the current client provides instead. Only ask the user when multi-document state cannot be disambiguated; never clear or close the original document automatically.

```python
import Rhino
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
```

This is the document handle injected by this MCP; other hosts need an explicit adapter. It does not fall back to ActiveDoc and does not modify the user's original settings.

## 4. Run the in-memory tests

Set the actual installation path before running these in Rhino Python 3; this is not ordinary CPython. The path must be reachable by the Rhino process.

```python
import sys
from pathlib import Path
skill_root = Path(r'<replace with the actual installation directory>')
sys.path.insert(0, str(skill_root / 'scripts'))
from smoke_test_rhino import run_tests
result = run_tests(__rhino_doc__)
print(result)
```

Expect all 45 cases to pass, with no document objects added, removed, or edited. On failure, report the specific entry point; do not delete assertions to manufacture a pass. These also run under ordinary Python:

```text
python scripts/test_outline_metrics.py
python scripts/test_region_metrics.py
python scripts/check_release.py
```

Expect21 single-ring and27 multi-ring cases to pass and the static checks to succeed. Native builders and metrics were revised in v1.8.0; for the validation scope see [VALIDATION.md](VALIDATION.md).

## Troubleshooting

| Problem | What to check |
|---|---|
| Cannot connect, or no tools appear | Whether the plugin is installed and loaded, the `MCPConnect` output, the client configuration, and the restart state |
| MCP appears but the skill cannot be found | The skill directory level, whether the client supports Skills, and whether a new session was started |
| `import Rhino` fails | Geometry scripts need Rhino's internal Python; the 2D metrics work under ordinary Python |
| Scripts not found | Use the real path reachable from the Rhino side; do not assume the client and remote paths are identical |
| No `doc` after import | Pass the injected document explicitly; the module does not inherit the caller's globals |
| Tests fail | Check the Rhino/API versions and keep the failure record; do not reuse another machine's passing result |

Installing and passing the self-checks does not mean an actual model has passed shape, G2, or manufacturing acceptance.


Install the v1.8.0 language package per README. Current tests do not establish real-image reconstruction quality.
