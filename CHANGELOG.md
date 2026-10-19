# 版本记录

## 1.7.0 — 2026-10-19

**吸收轮毂 Skill 的精华 + 实机纠错。** 新增第 16 篇，references 增至 16 篇。

### 融合了什么

从 `rhino-wheel-surface-modeling` 提炼出重复单元件的通用方法：

- ⭐ **孔洞是分面的内边界，不是布尔挖出来的洞** —— 径向切区间放样自然成孔
- ⭐ **只做一个母单元 + 极轴阵列**，⛔ 不手工重建 5 个「差不多」的辐条
- ⭐⭐ **轮廓用控制点插值，不要用穿点插值** —— 后者在长直边接小圆角处会过冲反凹，
  这就是「模型太肉 / 孔口反凹」的一半原因
- ⭐ **内外轮廓四点必须一致**（点数 / 起点含义 / 环绕方向 / 闭合缝位置），否则 Loft 扭转
- ⭐⭐ **棱线来自「法向差 + 窄过渡带 + 正面少量鼓起」** —— ⛔ 不用 BlendSrf 抹平，
  那正是「太肉」的来源
- ⭐ **曲率符号检查**（25200 采样 0 反向样本，防孔口反凹）
- ⭐ **剪影 IoU 的取巧做法**：模型后放纯黑平面 + Rendered/Top 正交截图，
  按质心 + 99.7 分位外半径归一化
- ⭐ **判定改动好坏必须用同一把尺子** —— 实测孔口缩小 8% 后 IoU 反而 0.805 → 0.787
- ⭐ **不要被高光骗**：金属件宽明暗渐变 ≠ 几何宽倒角

### ⭐ 同时纠正了 5 处过时说法（实测证伪）

| 旧说法 | 实测结论 |
|---|---|
| `SolidOrientation.Inward` | ⛔ 不存在，真实名 `BrepSolidOrientation` |
| `Brep.CreatePlanarBreps([outer]+holes)` 造带孔平面 | ⛔ 内圈被忽略，造不出孔 |
| `f.Objects[0]` 需先 `list(f.Objects)` | ⛔ `BrepFace` 根本没有 `Objects` 属性 |
| `Extrusion.CreateCap()` | ⛔ 不存在，用 `ToBrep()` |
| 视口类名 `Viewport` | ⛔ 真名是 **`RhinoViewport`** |

内圈正确做法实测精确吻合：外 40×40、内 10×10、高 10 →
`volume=15000.0`，理论 `(1600−100)×10 = 15000`。

### 轮毂 Skill 自身也一并修正

- §4 删除「必须带 slot 参数」的说法 —— ⛔ 官方 RhinoAI 0.3.0.0 的 31 个工具里
  **没有 `list_slots`**，那是社区版的概念
- §4 补直连姿势：`curl --noproxy '*'` + `initialize` 握手
- §5 按实测重写，区分「仍然成立」与「已证伪」
- `rhino_call.py` 同步更新；清掉 `__pycache__`（8 文件 68K → 7 文件 56K）

### 改动位置

- 新增 `references/16-repeating-units-and-polar-array.md`（中英）
- `SKILL.md` 读取路由 + Stage 2 构面表加「重复单元」行
- `13` 篇成面纪律加两条（⛔ 布尔挖孔代替分面、⛔ 穿点插值当轮廓）
- `15` 篇加阵列件的曲线留存提醒（母单元曲线 + 轴线 + 相位角）

## 1.6.0 — 2026-10-19

**双语对齐 + 真机验证修正。** 中英两版各覆盖 15 篇 references 与 10 个脚本。

### 真机抓出的三个 API 事实

| 发现 | 影响 |
|---|---|
| ⛔ **`Sweep2` 与 `NetworkSrf` 在 RhinoCommon 里不存在** | `Brep.CreateSweep2` / `Brep.CreateNetworkSrf` / `Surface.CreateSweep2` 全部 AttributeError。它们是 Rhino 命令，只能命令派发 |
| ⛔ `doc.Layers.FindName` 返回 `None` 而非 `-1` | 写 `if found >= 0` 抛 TypeError |
| ⛔ `doc.Objects.Count` 与枚举不一致 | 两次复现（Count 8/16，枚举均 0）；判定文档干净必须用枚举 |

修掉一个更隐蔽的问题：`_run_sweep2` 收集了结果却 `return []`，永远返回空 ——
⛔ 这种「假装成功」的代码比报错危险。改为比对命令前后的对象 id。

### 双语一致性

⛔ 36/36 · ⚠️ 24/24 · ⭐ 15/15 · 章节 17/17 · 代码块 44/44。

### 端口不是常量 —— 三次印证

10500 → 10502 → **10501**（同一台机器，重开 Rhino 后变了）。

## 1.5.1 — 2026-10-19

**真机验证修正。** 三个 API 事实写入 14 篇，修正 `patch_with_lines.py` 的错误假设。

实测通过：`ensure_lines_layer` → `Lines` 图层建立；
`loft_with_lines` → `breps=1 line_ids=3 valid=True`；
`audit_curve_retention` → `ok=True count=3`；
`register=False` 纯内存不碰文档；3 项非法输入正确拒绝。

⚠️ `Sweep2` / `NetworkSrf` 的命令派发路径仍未验证（`rs.Command` 有阻塞前科）。

## 1.5.0 — 2026-10-19

**构面路线与曲线留存。** 修两个实际问题：AI 遇复杂物体就「画几条线 + Loft」；
构面输入曲线没留在文件里导致交付物不可编辑。

- 新增 [15 构面路线与曲线留存](references/15-patch-route-and-curve-retention.md)
- 新增 `scripts/patch_with_lines.py`
- `SKILL.md` 五处改动，含**Stage 2 构面选择表重写**（Loft 移到末尾并带 ⛔）
- `03` 篇成面表改警告式 · `12` 篇鼠标案例 P01–P04 全改 `NetworkSrf`/`Sweep2` ·
  `09` 篇音箱案例 · `13` 篇新增铁律 4/5

⭐ 根因是措辞：原文「有序截面→Loft」与解析面并列，
且「少量主截面」「先试少量母面」在鼓励走最省事的路 —— 只加禁令无效，必须改推荐路径。

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
