# Rhino MCP Surface Skill — v1.8.0

指导 AI Agent 通过 **McNeel Rhino MCP Platform / RhinoAI** 在 **Rhino 8** 构建可编辑的 NURBS 曲面。适合产品参考图还原、主形与分面、局部过渡、修复与逆向；本包是技能和脚本，Rhino 软件及 MCP 插件需另装。

[中文入口](SKILL.md) · [English](README.en.md) · [安装](INSTALL-CHECK.md) · [验证](VALIDATION.md)

## 这版修复什么

- 撤销 V17 的“复杂双曲率必须 Network”“曲线越多越好”“网络格数等于面数”等错误选型规则。
- 用已在 Rhino 8.29 实测的原生双轨/网络 API 替换会等待交互、误取已有面或固定返回空结果的封装。默认内存构造，显式写入结果。
- 加入 [参考→粗体量→主面→局部→细节的拟合循环](references/17-reference-to-model-loop.md)，锁定相机和比较条件，每轮只修改少量有依据的参数。
- 加入 [破面诊断](references/19-defect-triage.md)，区分几何、接缝、自交、重复面与显示问题。
- 全部实际构面/修剪/切割曲线保留在 `lines`，保存输出面与原始线的对应记录。保留曲线不自动建立 History。

## 接入与安装

MCP 项目为 [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI)，Rhino 插件 `Rhino-MCP-Platform`。实测 Windows + Rhino8.29 + Python3；插件具体最低版本以官方当前说明为准，不把任意8.0都当已验证。当前服务可能有 router/slot，按实时工具描述使用，不固定端口或工具数量。

本目录包含中文包及 `en/rhino-mcp-surface-skill` 英文包，二选一安装，技能 ID 相同。中文安装时复制本目录的内容但不复制 `en` 子目录，目标文件夹直接包含 SKILL.md；英文只复制英文包。Codex 常见用户路径为 `~/.agents/skills/`，其他客户端按其配置。新建对话并核对实际读取路径；不要同时注册重复版本。

[下载 v1.8.0](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/tag/v1.8.0)：中文与英文安装包二选一。

## 运行方式

```python
# 在 Rhino Python3 中；skill_root 指向实际安装目录。
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
import patch_with_lines as PWL
from quality_gate import check_candidates
result = PWL.sweep2_with_lines(doc, rails, sections, register=False)
facts = check_candidates(result['breps'], require_solid=False)
if not facts['passed']:
    raise ValueError(facts['errors'])
# 继续核对实际形体和邻接，通过后才显式登记：
PWL.publish_patch(doc, result, patch_id='P01_v01')
```

支持 `network_with_lines`、`loft_with_lines`。所有封装以实际几何约束选择，不默认某一命令。`register=True` 仅登记输入线；`publish_patch` 才将面与线映射一起写入。详见 [曲面决策](references/15-surface-led-construction.md)、[输入线保留](references/16-preserve-construction-curves.md)。

实测：Rhino45项、参数化壳12项、新构面与交付32项、单环21项、多环27项通过。它们验证具体 API 与数据链，不证明真实参考图还原成功；验证边界见上方记录。没有附带书籍扫描或整本 OCR；来源见 [审计](references/08-source-audit.md)。项目尚未指定独立开源许可证。


## 下载与更新 / Downloads

- [简体中文 ZIP](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/rhino-mcp-surface-skill-1.8.0-zh-CN.zip)
- [English ZIP](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/rhino-mcp-surface-skill-1.8.0-en.zip)
- [SHA256 校验 / checksums](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/download/v1.8.0/SHA256SUMS.txt)

解压后将 `rhino-mcp-surface-skill` 整个文件夹放入客户端技能目录。更新时先备份旧版，再替换整个同名文件夹；不要把中英文两个同 ID 入口同时注册。新建对话，确认 Agent 读取的是 v1.8.0。
