# 版本记录

## 1.4.0 — 2026-10-19

**真机实测版本。** 内容来自在官方 Rhino MCP Platform 0.3.0.0 + Rhino 8.29.26063.11001
上的实际运行，不是文档转述。

- ⭐ **新增 [14 RhinoCommon Python 绑定坑](references/14-rhino-python-binding-traps.md)**：
  13 类真机才暴露的运行时陷阱，全部附实测代码。
  包括 `BrepFaceList` 无 `__len__`、`Brep` 无 `Volume`/`BrepFace` 无 `Edges`/
  `BrepEdge` 无 `Index`、`Rhino.Geometry` 无 `Polygon`、`Extrusion.Create` 的 4 参签名、
  `CreateFilletEdges` 要位置索引 + `BlendType.Fillet`（无 `Normal`）、
  `CreateBooleanDifference` 要公差、`Guid` 无 `.Id`、**`rs.Command` 会阻塞 MCP 调用**。
- **05 执行协议补官方探测姿势**：`--noproxy '*'` 绕过代理、
  `initialize` 确证响应、`Server: Microsoft-HTTPAPI/2.0` 特征、
  官方 0.3.0 的 31 个工具清单、端口查找三动作。
- 实测确认：官方 0.3.0 监听 **10502**（HTTP.sys，PID 4），
  `serverInfo.name == "rhino-mcp"`。

⚠️ 本机环境有 `http_proxy`，curl 默认走代理会得到**假阴性**
（看起来像端口没开，其实是代理在挡）。

## 1.3.0 — 2026-10-19

**功能版本。几何实现与 1.2.0 一致；新增多环二维指标并修正版本声明。**

- ⭐ **`outline_metrics.region_iou`** —— 支持多组件与带孔轮廓。
  原 `silhouette_iou` 只接受单个简单环，散热槽、按钮开口、多轮廓外形
  无法直接比较。现在按 even-odd 规则填充，并**按有向面积自动定向环**
  （最大环为外环，其余反向）。
- ⛔ 修正一个会静默出错的陷阱：**多个环同向时孔洞被当成实心**，面积偏大。
  这正是"看起来有洞、算出来没洞"的根因。
- 新增 `scripts/test_region_metrics.py`，**13 项解析验证全部通过**
  （圆环、单孔、双孔、多组件、不相交、自交拒绝等）。
- **版本声明修正**：先前写"Rhino 6/7 未实测"，这是把不在支持范围的东西
  写成待办。实际官方 RhinoAI **不支持 Rhino 6/7**，最低为 Rhino 8.x
  （官方 Release note：PR #109"Moved down from 8.29 to version 8.19"）。
  现在改为明确的版本下界声明。
- 自交轮廓**直接报错**而非求解布尔运算——避免静默错误面积。

测试：45/45（Rhino 内存）、17/17（单环二维）、13/13（多环二维）。
几何代码未改动。

## 1.2.0 — 2026-10-19

**文档版本。代码与几何行为与 1.1.0 完全一致，测试结果不变。**

- 新增 [13 施工纪律](references/13-construction-discipline.md)：开工三件事、三条顺序铁律、
  以及成面/曲线/3C/连续性/验收环节的不可逆约束（每条附失效信号与出处）。
- 扩充 [10 参数](references/10-parameters-and-recipes.md)：
  在五类数值分类框架下增加单位换算表、探索预算、MatchSrf 实测容差锚点、边缘圆滑链、按键配方、
  圆角实测表、Class-A 适用范围警告、IoU 三个实现陷阱。
  **每个数值标注来源、适用条件与失效信号**，不作为制造标准或恒定默认。
- `03` 增补三排法适用边界、`EdgeSrf` 对边阶数检查、`ChangeDegree` 两种模式的用途区分、
  `ExtrudeCrv`/`Extrude` 选项。
- `04` 增补判 G2 的三个错误做法、明暗交界不强求 G2 的理由、匹配失败先查输入、
  镜像时机、CurvatureAnalysis 时机。
- `05` 增补四个在Rhino 8 实测被证伪的 API 写法（`doc.Units.SetUnits` 等）
  与端口纪律。
- `07` 增补17 条实测症状与卡死时的上游回退路径。
- `11` 增补高低错位分面、`Extrude` 提阶补G2、边缘圆滑链、`Same height shapes`
  扭曲正解、`Setpt` 中段对齐、按键 7 步配方。
- `SKILL.md` 增读参数分流、顺序三件事与三条铁律、Stage 3–6 检查项。

**未新增任何平台或建模验证声明**；测试结果仍为 45/45、17/17、12/12。

## 1.1.0 — 2026-10-19

- 新增物品分面/逐步施工剧本、曲线与面块合同、任务验收门，以及12项实测的封闭壳母形构造脚本。
- 补充中文/英文完整首页，明确 Rhino8、McNeel Rhino MCP Platform、router/connector 与安装步骤。
- 新增完整英文技能正文、12篇参考、安装、自检、项目模板、验证和更新说明。
- 分别提供中文/英文安装包，共用同一技能ID与几何实现；二选一安装。
- 本次为文档/分发更新，不新增几何或平台验证声明。

## 1.0.0 — 2026-10-19

- 统一入口与12篇参考：按几何约束、用途和证据分流；移除品类硬限定与互相矛盾的规则。
- 修正Degree/跨度/周期/圆/升阶/Refine/Offset/投影/网格Weld等表述；案例配方补适用条件。
- 修复重建、EdgeSrf、Loft、曲率与曲线G1助手；删除未验证的放图命令拼接入口，以明确几何输入替代。
- 二维轮廓指标独立为普通Python模块，补边界条件；扩展Rhino内存验证与发布检查。
- 分开实测、案例与未验证项目；发布包不依赖工作区、图片或外部旧知识图谱。
