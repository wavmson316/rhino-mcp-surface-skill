# RhinoCommon / Python 绑定：使用前核验

同名重载随 Rhino 版本、运行时和类型而变。先查已连接环境的工具 schema 与 `__doc__`，用内存几何最小试验，再写入文档。不要根据一次重载失败宣布整个 API 不存在。

本次在 Rhino 8.29 / Python3 只读探测观察到：

- `Extrusion.Create(Curve, Double, Boolean)` 和 `Extrusion.Create(Curve, Plane, Double, Boolean)` 均有绑定；第三个布尔参数是 cap，不能误写成 plane 或省略必需参数。
- `Brep.CreateFilletEdges` 有 7 参数及 9 参数重载；7 参数顺序是 brep、edgeIndices、startRadii、endRadii、blendType、railType、tolerance。不套用未经核对的 8 参数样例。
- `BrepFace` 有 `OuterLoop`、`AdjacentEdges()`；本次不存在 `OuterEdge`。一个面的外环可以有多条边，不能把环当单边。
- `BrepEdge` 的拓扑索引是 `EdgeIndex`；不要猜测 `Index`。索引由拓扑决定，不保证固定对应左/右/前/后。
- 正常的 `isinstance(value, Rhino.Geometry.Brep)` 可以成立。跨运行时代理异常应保存实际类型信息再处理；不要普遍以类名字串替代类型检查。

以上是绑定可用性探测，不是倒角、实体或复杂造型的成功认证。枚举、.NET 集合、参数单位和输出有效性仍需逐调用验证。文档对象 GUID 不等于几何对象；通过注入文档查对象并复制几何后再做内存试验，写入结果需记录返回 ID 和 Undo 范围。


## 原生双轨与网络面 API（2026-10-20 实测）

- 双轨：`Brep.CreateFromSweep(rail1, rail2, sections, closed, tolerance)`，返回 Brep 数组；`SweepTwoRail.PerformSweep` 也存在。方法名不叫 CreateSweep2 不等于没有双轨 API。
- 网络面：`NurbsSurface.CreateNetworkSurface(curves_u, 1, 1, curves_v, 1, 1, edge_tol, interior_tol, angle_tol)`。本机 Python3 将 out error 返回为 `(surface, error)`，本次成功状态为 0；角度参数为弧度。安装的 RhinoCommon XML 明确：0=Loose、1=Position、2=Tangency、3=Curvature；这里的 1 为位置约束，不自动提供父面 G1/G2。
- `CreatePlanarBreps([outer, inner], tol)` 可以保留内孔。本次 40×40 外环、10×10 内环得到两环、面积 1500。
- 查看真实签名和实测返回；不解析参数个数后猜类型。不同重载可能语义不同。
- 文档对象计数可能包含与枚举过滤不同的对象；不能仅凭 Count 和默认枚举不同宣布对象表坏了。通过已记录 GUID 与明确枚举设置查询。
- `isinstance(geometry, Rhino.Geometry.Curve)` 可用于过滤曲线；仅 IsValid 会把合法面也算成曲线。
- `rs.Command` 是否阻塞取决于命令、上下文和输入完成情况；不在后台依赖无人响应的拾取。当前封装直接用原生 API，不通过命令临时添加对象。
- 已加载模块改源码后先确认 `module.__file__`，再 reload。删除 __pycache__ 不会刷新 sys.modules 内旧模块。
