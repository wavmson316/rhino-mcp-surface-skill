---
name: rhino-mcp-surface-skill
description: 通过 McNeel Rhino MCP 在 Rhino 8 构建可编辑 NURBS 模型。用于照片/草图/多视图还原、复杂产品曲面、分面布线、过渡修复与逆向；指导参考分析、相机和体量拟合、逐面构造、破面诊断、原始曲线保留及验证。
---

# Rhino MCP Surface Skill

目标：形体接近参考、结构有效、修改依据完整。当前为 v1.8.0；基础代码测试与真实图片还原验收分开。支持 McNeel [RhinoAI](https://github.com/mcneel/RhinoAI)，实测 Windows/Rhino 8.29/Python3；接入见 [安装说明](INSTALL-CHECK.md)。

## 开始任务

1. 明确用户目标、关键特征、参考、单位、尺寸来源、交付类型与公差。单图无尺寸可做归一化模型，未知深度/背面标为假设。
2. 发现当前工具与目标文档，有多实例时明确 slot；显式使用注入文档。保留用户已有对象和设置。读取/最小 API 试验可批量做，失败不猜重载。
3. 参考还原必读 [17 图片到三维循环](references/17-reference-to-model-loop.md)；复杂构面再读 [15 逐面决策](references/15-surface-led-construction.md)。写一份简短实际施工计划，随试面更新，不只列命令。
4. 所有实际用于构面、修剪和切割的曲线保存在 `lines` 或其子层，随 `.3dm` 交付，记录面与输入 GUID/参数/版本。详见 [16 原始曲线保留](references/16-preserve-construction-curves.md)。保留曲线不等于自动 History。

## 执行循环与出口

| 阶段 | 动作 | 通过条件 |
|---|---|---|
| 参考与体块 | 记录锚点/特征，匹配相机和粗体量，锁定比较条件 | 主比例、高点、最大宽、主要负空间有依据且残差可接受 |
| 主面 | 按高光/侧腹/凹底/过渡职责选择母面与 U/V，先试决定形体的区域 | 实际曲面轮廓及纵横斜截面成立，包括生成站位之间 |
| 邻接与局部 | 用真实父面约束构造过渡、收口和孔壁；修改后回查旧边 | 有效性、目标接缝、局部体量各自有证据 |
| 细节 | 从通过的母面派生小孔、分缝；先验证一个重复单元 | 关键特征未被细节破坏；工程需求另查 |
| 保存 | 保留曲线/母面/参数，保存新版本并按需独立读回 | 输入可找、映射完整、结构与验证状态明确 |

每轮明确“差异→假设→只改哪些参数→复查哪些约束”。连续两轮同类修改无改善就回查相机/深度/约束/布局。主形未通过时暂停细节，不用加线、加点或换命令掩盖推断问题。

## 构面与质量边界

- 双向曲率不意味着必须 Network；曲线越多不意味着越准确。Network 需要两族有依据且一致的曲线，输出不是一格一张面。
- Loft 仅用于有真实单向剖面生成关系的区域，并说明纵向边界和站位间体量怎样受控。不能默认排一串截面做整件复杂主形，也不按截面数量判好坏。
- 解析/控制网/边界面/双轨/网络/过渡各按实际约束选。明暗线不是天然分面边；真实锐边保留。Join、升阶、修剪不自动带来公平性或 G2。
- 每批输出按 [19 破面分类](references/19-defect-triage.md) 检查。空结果、无效面、非流形、意外重复和缺失应有对象阻断本步。裸边/封闭要求按交付合同，不强迫外观面一律实体化。
- `IsValid`、水密、法线或 IoU 单项均不能证明无自交、形体正确或 G2。接缝采样只支持有限 G0/切平面诊断；未测写未验证。

## 执行效率

优先原生 API 在内存批量生成少量相关面，再返回简短指标；通过后 `publish_patch` 显式落文档。只重算受影响依赖，延迟密孔/高精网格。每阶段看必要固定视图，超时先查结果。源码变更核对模块路径并 reload，不每步重新探测全部接口。使用 [项目记录](templates/modeling-plan.md) 与 [参考记录](templates/reference-fit.json)。

## 按需读取

输入/定标 [01](references/01-intent-and-reference.md)；分面/UV [02](references/02-patch-layout.md)；构面数学 [03](references/03-construction.md)；连续性 [04](references/04-continuity-and-validation.md)；MCP [05](references/05-mcp-execution.md)；复杂区 [06](references/06-complex-regions.md)；回退 [07](references/07-diagnosis.md)；来源 [08](references/08-source-audit.md)；示例 [09](references/09-worked-examples.md)；参数 [10](references/10-parameters-and-recipes.md)；产品 [11](references/11-consumer-electronics.md)；逐步剧本 [12](references/12-object-construction-playbooks.md)；依赖纪律 [13](references/13-construction-discipline.md)；API [14](references/14-rhino-python-binding-traps.md)；重复单元 [18](references/18-repeating-units.md)。

交付说明：还原了哪些特征、为何这样分面、原始线在哪里、实测证据、未验证项、文件路径。脚本与测试边界见 [VALIDATION.md](VALIDATION.md)。
