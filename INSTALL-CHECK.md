# 安装、MCP连接与自检

[简体中文](INSTALL-CHECK.md) | [English](en/rhino-mcp-surface-skill/INSTALL-CHECK.md)

## 适配环境

本包采用 McNeel [Rhino MCP Platform / mcneel/RhinoAI](https://github.com/mcneel/RhinoAI)，Rhino 插件包名 `Rhino-MCP-Platform`。实测为 Windows + Rhino 8.29.26063.11001 + Rhino Python3。**版本下界：官方 RhinoAI 不支持 Rhino 6/7**，最低为 Rhino 8.x 系列。Rhino 9、macOS 及其他第三方 MCP 未实测。Skill与插件分开安装。

## 1. 安装并连接官方 MCP

先看 [官方 Getting Started](https://mcneel.github.io/RhinoAI/docs/getting-started/)。下面是官方Codex路线的说明，实际命令以当前 `MCPConnect` 输出为准。

1. 在 Rhino 8 运行 `PackageManager`，搜索安装 `Rhino-MCP-Platform`，按提示重启 Rhino。
2. 在 Rhino 运行 `MCPConnect`，读取它打印的 router 命令和参数。
3. 把该输出配置到 Codex 的 MCP 设置。常见配置文件为 `~/.codex/config.toml`。官方示例的结构如下，只有本机确有该命令时才照用：

```toml
[mcp_servers.rhino]
command = "rhino-mcp-router"
args = ["--default-version", "8"]
```

4. 重启 Codex，检查MCP服务和工具可见。运行命令、可执行文件路径与参数应来自第2步，不猜固定端口。

[Codex官方指南](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/) · [Claude Desktop官方connector](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/)

MCP router/connector负责协议和Rhino连接；`run_python`/`run_csharp`/`run_command`负责实际执行，Python几何通过RhinoCommon运行。工具名称/选项由当前服务描述决定。

## 2. 安装语言包

在 [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest) 下载中文或英文ZIP，解压后把整个 `rhino-mcp-surface-skill` 放到Agent支持的skills路径。入口为文件夹内直接的 `SKILL.md`。两包同ID，二选一安装。

Codex常见用户级路径为 `~/.agents/skills/`，项目级为 `.agents/skills/`，以客户端当前配置为准。其他客户端按自身说明加载Skills；MCP可用不等于自动发现Skills。新建会话确认技能可见。

## 3. 文档与连接只读检查

让Agent读取 `get_context`；有 `list_slots` 时先定位目标实例。没有这些接口时用当前客户端对应能力。多文档无法消歧才询问，不自动清空或关闭原文档。

```python
import Rhino
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
```

这是本MCP注入的文档句柄；其他宿主需显式适配。不回退到ActiveDoc，不修改用户原设置。

## 4. 运行内存测试

在Rhino Python3中设置实际安装路径后执行；不是普通CPython。路径必须能被Rhino进程访问。

```python
import sys
from pathlib import Path
skill_root = Path(r'<替换为实际安装目录>')
sys.path.insert(0, str(skill_root / 'scripts'))
from smoke_test_rhino import run_tests
result = run_tests(__rhino_doc__)
print(result)
```

预期45项全部通过，不添加/删除/编辑文档对象。失败报告具体入口，不删除断言制造通过。普通Python可运行：

```text
python scripts/test_outline_metrics.py
python scripts/check_release.py
```

预期二维17项通过，静态检查通过。当前测试代码与1.0.0几何实现相同；验证范围见 [VALIDATION.md](VALIDATION.md)。

## 排错

| 问题 | 检查 |
|---|---|
| 连不上或没有工具 | 插件是否安装/加载、MCPConnect输出、客户端配置和重启状态 |
| 显示MCP但找不到Skill | Skill目录层级、客户端是否支持Skills、是否新建会话 |
| import Rhino失败 | 几何脚本需Rhino内Python；二维指标可普通Python |
| 找不到脚本 | 使用Rhino侧可访问的实际路径，不能假设客户端和远端路径相同 |
| import后没有doc | 显式传入注入文档，模块不继承调用方全局变量 |
| 测试不通过 | 核对Rhino/API版本并保留失败记录，别沿用别台机器的通过声明 |

安装和自检不代表实际模型已经通过形体、G2或制造验收。

## ⭐ ��地存档（发布后必做，2026-10-20 补充）

⛔ **发布到 GitHub 不等于本地有存档。** 2026-10-20 才发现仓库建在
`/tmp/` 里（临时目录，重启即丢）。

**发布完成后必须确认这几处存在：**

```
1. ~/.workbuddy/skills/rhino-mcp-surface-skill/     ← 唯一被加载的路径
2. G://RHINO MCP SKILL\rhino-mcp-surface-skill-repo\  ← git 仓库（带 tag）
3. G://RHINO MCP SKILL\20-最新版-vX.Y.Z\              ← 目录名必须带当前版本号
4. ~/.workbuddy/skill-backups/...\packages\*.zip      ← 离线安装包
5. ~/.workbuddy/skill-backups/...\LOCAL-ARCHIVE.md    ← 存档索引
```

**验证命令：**

```bash
# 版本号是否一致
grep -o '"version": "[^"]*"' ~/.workbuddy/skills/rhino-mcp-surface-skill/release-manifest.json | head -1
cd "G:/RHINO MCP SKILL/rhino-mcp-surface-skill-repo" && git log --oneline -1

# 内容是否一致（必须是 0 差异）
diff -rq --exclude=.git --exclude=.gitignore --exclude=__pycache__ \
  "G:/RHINO MCP SKILL/rhino-mcp-surface-skill-repo" \
  ~/.workbuddy/skills/rhino-mcp-surface-skill/
```

⛔ **不要在 `/tmp/` 或系统临时目录下建 git 仓库** —— 重启即丢。
⛔ **目录名带版本号的，改版本后必须同步改名** —— 否则名实不符，
下次找文件会被误导。

⚠️ 英文包最容易漏同步：`en/rhino-mcp-surface-skill/scripts/` 下的文件
与中文包是两份，改一处必须 `cp` 两处，再 `diff -rq` 验证。
