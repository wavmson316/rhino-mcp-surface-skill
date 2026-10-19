# Rhino MCP Surface Skill — v1.8.0

Guides AI agents using **McNeel Rhino MCP Platform / RhinoAI** to build editable **Rhino8 NURBS** models from references, plan parents/patches, construct transitions and diagnose defects. Rhino and the MCP plugin are separate installations.

[Skill](SKILL.md) · [Setup](INSTALL-CHECK.md) · [Validation](VALIDATION.md)

This revision removes mandatory-Network/curve-count rules, replaces broken command dispatch with tested native two-rail/network APIs, adds a camera/blockout/parent/local/detail fitting loop and defect triage, and preserves actual inputs in lines with output mappings. No automatic History is claimed.

Targets [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI), plugin Rhino-MCP-Platform; tested Windows/Rhino8.29/Python3. Follow current upstream plugin build requirements and live router/slot/tool descriptions. No fixed port/tool count is prescribed.

Install one language only: both use the same skill ID. Copy this standalone English folder into the client's skills path with SKILL.md directly inside; do not register multiple versions. Common Codex user path is ~/.agents/skills/. Start a new chat and verify the loaded path. Download v1.8.0 from the GitHub release linked below.

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
import patch_with_lines as PWL
from quality_gate import check_candidates
result = PWL.sweep2_with_lines(doc, rails, sections, register=False)
facts = check_candidates(result['breps'], require_solid=False)
if not facts['passed']:
    raise ValueError(facts['errors'])
# Complete shape/adjacency checks, then explicitly persist:
PWL.publish_patch(doc, result, patch_id='P01_v01')
```

network_with_lines and loft_with_lines follow actual constraints, not a universal preferred command. register=True retains inputs only; publish_patch adds outputs/mappings. See [reference fitting](references/17-reference-to-model-loop.md), [surface strategy](references/15-surface-led-construction.md), [input retention](references/16-preserve-construction-curves.md) and [defect triage](references/19-defect-triage.md).

Executed checks:45 Rhino regressions,12 procedural-shell checks,32 native/delivery cases,21 single-ring and27 multi-ring cases. These validate specific code/data paths, not end-to-end real-reference similarity. No books/scans/full OCR distributed; no separate open-source license designated.


## 下载与更新 / Downloads

- [简体中文 ZIP](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/rhino-mcp-surface-skill-1.8.0-zh-CN.zip)
- [English ZIP](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/rhino-mcp-surface-skill-1.8.0-en.zip)
- [SHA256 校验 / checksums](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/SHA256SUMS.txt)

Extract the archive and install the entire `rhino-mcp-surface-skill` folder. Back up and replace the old folder when updating. Choose one language (same skill ID), start a new chat and verify that the agent loads v1.8.0.
