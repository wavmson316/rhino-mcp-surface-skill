# Rhino MCP Surface Skill

[简体中文](README.md) | [English](README.en.md)

**让 AI Agent 通过 McNeel Rhino MCP，在 Rhino 8 中依据照片、草图、多视图、尺寸或扫描资料，规划并构建可编辑的 NURBS 曲面。**

这是一套给 AI 阅读的建模技能：指导它理解形体、选择分面与 UV 流向、调用 Rhino 工具、检验结果并处理失败。它不包含 Rhino 软件，也不是 MCP 服务器或一键照片转 CAD 程序。

**[下载中文 / English 安装包](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest)** · **[中文技能入口](SKILL.md)** · **[English skill](en/rhino-mcp-surface-skill/SKILL.md)** · **[安装与连接指南](INSTALL-CHECK.md)**

## 使用什么 Rhino、什么 MCP？

| 组件 | 本项目采用的技术与状态 |
|---|---|
| 建模软件 | McNeel **Rhinoceros 3D / Rhino 8**；实际测试为 **Windows + Rhino 8.29.26063.11001** |
| MCP 项目 | McNeel 维护的 **Rhino MCP Platform**，官方仓库 **[mcneel/RhinoAI](https://github.com/mcneel/RhinoAI)** |
| Rhino 插件 | 在 Rhino `PackageManager` 中安装 **`Rhino-MCP-Platform`**；按当前官方指南选择 Rhino 8 对应包 |
| 客户端连接 | 使用官方 MCP router / 客户端 connector。Codex 路线为 `MCPConnect` 输出配置 → 配置 router → 重启客户端；详见下文 |
| 几何执行 | MCP 的 `run_python` / `run_csharp` / `run_command`，以及 RhinoCommon；Python 助手使用 **Rhino 内的 Python 3** |
| 状态与验收接口 | 按当前工具清单使用 `list_slots`、`get_context`、`list_objects`、`get_commands`、`get_viewport_image` 等 |
| 参数化工具 | 当前接口提供相应 `g1_*` 工具时，可使用 Grasshopper 1；本包未完成 GH 端到端验证 |
| 其他版本 | **Rhino 6/7、Rhino 9 WIP/Beta、macOS 和其他第三方 Rhino MCP 尚未经本包实测**；不承诺直接兼容 |

本项目独立于 McNeel，并非 McNeel 官方 Skill。采用的是上面链接的 MCP 项目，不是任意同名的第三方 “Rhino MCP”。工具名和配置会随插件/客户端版本变化，Agent 会先发现实际能力。

```text
用户的参考与建模要求
        ↓
支持 Skills 与 MCP 的 AI Agent
        ├── 读取本 Skill：建模决策、分面、质量与执行纪律
        ↓
McNeel Rhino MCP router / connector
        ↓
Rhino-MCP-Platform 插件 → Rhino 8 / RhinoCommon
        ↓
曲线、NURBS 面、Brep、3dm 与检查报告
```

## 具体能帮助 AI 做什么？

| 任务 | Skill 指导的工作 | 典型例子 |
|---|---|---|
| 参考图还原 | 区分轮廓/阴影/材质，处理定标与透视，识别未知深度和背面假设 | 产品照片、手绘草图、正交视图 |
| 分面与 UV 规划 | 规划主母面、侧面、过渡带、角区；记录邻接、可动边与连续性目标 | 高光鼠标壳、汽车侧围、非对称外壳 |
| 曲线骨架与公平性 | 构造主截面和边界，检查方向、接缝、真实跨度、曲率梳及拟合偏差 | 腰线、轮拱、握柄截面、微鼓盖 |
| 构面方法选择 | 按约束选择解析面、Revolve、Loft、Sweep1/2、EdgeSrf、NetworkSrf、BlendSrf 或 MatchSrf | 旋转音箱、镜筒、双曲率壳、边带过渡 |
| 复杂区域处理 | 比较分叉中心、多边角区、渐消、变宽过渡、凹坑与把手窝的布局 | 三通管柄、拇指凹区、渐消圆角 |
| 产品细节与装配 | 从母面派生分缝、孔、内壁、按钮、格栅；区分运动件、厚度与装配间隙 | 路由器、相机、手机、空调面板 |
| 逆向与修复 | 从扫描截面/设计意图重建；检查噪声、偏差与布局；区分拟合和网格转换 | 扫描握柄、缺面修复 |
| 检查与交付 | 分开报告形状、结构、公平/接缝和工程检查；保存母面、版本和未验证项 | 3dm、按任务需要的交换格式与报告 |

**泛化原则：按实际几何和交付要求决策。** 不规定“汽车只能怎样做”或“家电只能平面加圆角”；也不把单跨、G2 或封闭实体当成所有任务的统一目标。

### 包内实际提供的脚本

| 文件 | 功能 | 边界 |
|---|---|---|
| `audit_geometry.py` | 读取 Degree、真实 SpanCount、控制点、裸边、非流形与实体状态 | 结构审计，不认证造型或 G2 |
| `nbs_geometry.py` | 曲线、受偏差预算约束的单跨重建、三/四边面、直纹面、Loft、曲率查询、曲线端点诊断 | 内存几何助手；添加用户文档由 Agent 受控执行 |
| `sample_seam_g1.py` | 双向采样边界距离与面切平面夹角 | **不判 G2**，不证明全域无反折 |
| `outline_metrics.py` | 独立二维剪影 IoU 与轮廓距离 | 单个简单多边形外环；不是深度或尺寸认证 |
| 测试与发布检查 | Rhino 回归、二维解析样例、语法和文件链接检查 | 不替代真实建模任务验收 |

## 安装：软件、MCP、Skill 是三部分

### 1. 安装并运行 Rhino 8

准备已安装并可正常运行的 [Rhino 8](https://www.rhino3d.com/download/)。当前验证平台为 Windows；Skill 不提供 Rhino 安装包或许可证。

### 2. 连接 McNeel Rhino MCP

先看官方 [Getting Started](https://mcneel.github.io/RhinoAI/docs/getting-started/)。

- **Codex**：在 Rhino 8 的 `PackageManager` 安装 `Rhino-MCP-Platform`，重启 Rhino 后运行 `MCPConnect`。按它输出的实际 command/args 配置 Codex MCP；见 [官方 Codex 指南](https://mcneel.github.io/RhinoAI/docs/getting-started/codex/)。
- **Claude Desktop**：按 [官方 connector 指南](https://mcneel.github.io/RhinoAI/docs/getting-started/connector/) 安装 connector 与 Rhino 插件。
- **其他 Agent**：官方还有 Claude Code、GitHub Copilot、Gemini CLI 等路线；能连接 MCP 不代表客户端自动支持 Skills，技能安装方式仍按各客户端说明。

**不需要把本机某个固定端口抄给所有人。** 使用自己机器上 `MCPConnect` 的输出与官方当前文档；已有有效连接就不重启服务。

### 3. 安装中文或英文 Skill，二选一

在 [Releases](https://github.com/wavmson316/rhino-mcp-surface-skill/releases/latest) 选择：

- `rhino-mcp-surface-skill-1.1.0-zh-CN.zip`：中文技能正文、12篇参考、安装指南、模板与脚本。
- `rhino-mcp-surface-skill-1.1.0-en.zip`：英文技能正文、12篇参考、安装指南、模板与同一套脚本。

两者解压后都得到 `rhino-mcp-surface-skill` 文件夹，放入客户端支持的 Skills 目录，保证里面直接有 `SKILL.md`。两包使用相同内部 ID，**选择一种语言安装，不要同时注册两个同名 Skill**。

Codex 常见用户级目录为 `~/.agents/skills/`，项目级目录为 `.agents/skills/`；以当前 Codex 文档和实际配置为准。其他客户端路径不同。仅支持 MCP 而不支持自动发现 Skills 时，可让 Agent 显式读取入口及相对引用，但不保证获得相同的自动触发行为。

克隆仓库供开发时，不要把包含 `en/` 的整个仓库直接注册为一个Skill；按上面的单语言ZIP安装，避免同名入口重复发现。

重启客户端或新建会话，再按 [INSTALL-CHECK.md](INSTALL-CHECK.md) 做连接与内存几何自检。

## 怎样把一个物品真正做出来？

新增 [详细分面与施工剧本](references/12-object-construction-playbooks.md)，给出：

- 曲线ID、每块面的边界/UV/方法、邻接连续性与可动范围。
- 鼠标式外壳从体块、横截面、顶面、侧面、拇指凹区到过渡、细节的十步施工。
- 旋转音箱/瓶体、三向管柄的具体分面与失败回退。
- 一个可执行的120×70、实际最高40的双曲率封闭壳母形：6块母面→一个有效实体，新增 **12/12** 检查通过。入口为 `scripts/example_closed_shell.py`。

程序化例子明确保留G0硬边，只验证母面施工链，不能冒称鼠标成品、照片还原或G2过渡。关键形体是否符合参考，必须在任务内用固定相机、主截面和特征清单逐项核对。

## 装好后怎么提问？

```text
使用 rhino-mcp-surface-skill。
先确认 Rhino MCP 连接、目标文档、单位和现有对象。
根据我附的鼠标参考图，先分析比例、顶部拱高和拇指凹区；
比较两个分面方案，再构建可编辑的 NURBS 母面与过渡。
没有可靠尺寸时先用归一化尺度，标明假设。
完成后保存新版本 3dm，分别报告形体、结构与连续性检查结果。
```

也可以要求“修复这两张面之间的折痕”“按尺寸重建旋转音箱”“分析三通中心如何分面”。参考、尺寸和验收目标越明确，结果越容易评估。

## 语言、内容与验证

| 内容 | 中文 | English |
|---|---|---|
| 首页 | 本页 | [English README](README.en.md) |
| 技能入口 | [SKILL.md](SKILL.md) | [English SKILL](en/rhino-mcp-surface-skill/SKILL.md) |
| 安装与连接 | [INSTALL-CHECK.md](INSTALL-CHECK.md) | [English setup](en/rhino-mcp-surface-skill/INSTALL-CHECK.md) |
| 参考与模板 | [references](references/01-intent-and-reference.md)、[模板](templates/modeling-plan.md) | [English references](en/rhino-mcp-surface-skill/references/01-intent-and-reference.md)、[template](en/rhino-mcp-surface-skill/templates/modeling-plan.md) |
| 验证记录 | [VALIDATION.md](VALIDATION.md) | [English validation](en/rhino-mcp-surface-skill/VALIDATION.md) |

几何运行代码与机器测试数据中英文共用相同实现。1.0.0 的 Rhino 内存回归 **45/45**、二维指标 **17/17** 已通过；1.1.0 补充双语文档、详细施工剧本与新增12项程序化构造检查，验证范围见各语言记录。

**未承诺：**自动全域 G2/G3 认证、一张照片唯一还原真实尺寸、完整车辆一键生成、真实照片到模型端到端质量、制造可行性、任何车厂 Class-A 标准，以及未经实测的平台/API兼容。未验证项目必须在任务交付中明确写出。

## 来源与项目状态

本 Skill 是独立整理的流程与工具；官方 MCP 本身请到 [mcneel/RhinoAI](https://github.com/mcneel/RhinoAI) 查询。接口说明于 2026-10-19 根据官方安装指南及本机已发现工具核对，插件后续变化以官方文档为准。

本仓库不包含书籍 PDF、扫描页、整本 OCR 或旧工作区笔记。来源与已撤销的规则见 [来源审计](references/08-source-audit.md)。当前没有单独指定开源许可证，不暗示 MIT 等授权。更新见 [CHANGELOG.md](CHANGELOG.md)。
