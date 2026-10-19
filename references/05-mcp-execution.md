# MCP执行与脚本协议

## 发现当前能力

读工具描述，定位用户文档。有list_slots/get_context时使用；别的连接按其接口适配。不能假定有undo、create_layer、get_object_info，不能假定没有。已连接不要重启。端口、路径、启动命令来自当前插件配置，非建模常量。

Rhino Python使用注入文档；本包函数显式传doc，不回退ActiveDoc或隐式scriptcontext。远端Rhino未必能访问客户端磁盘路径，先确认文件可达。

```python
import Rhino, math
doc = __rhino_doc__
print(str(Rhino.RhinoApp.Version), str(doc.ModelUnitSystem),
      doc.ModelAbsoluteTolerance, doc.ModelAngleToleranceDegrees)
angle = math.radians(30)
# 受控建层时：先设Name再Add，不在自检中实际添加。
layer = Rhino.DocObjects.Layer()
layer.Name = 'P01_Main'
# layer_index = doc.Layers.Add(layer)
```

单位换算需决定是否缩放坐标；改ModelUnitSystem只设元数据不等同完整换算。不要复制初始化例子覆盖用户项目。API重载读方法文档并先作内存测试，Guid经doc.Objects.FindId查到几何再用。

### ⭐ 四个在本机被实测打脸的写法

这些在教材与网络示例中大量流传，但在 Rhino 8 实测会抛异常或静默失效：

| ⛔ 失败写法 | ✅ 正确写法 | 症状 |
|---|---|---|
| `doc.Units.SetUnits(...)` | `doc.ModelUnitSystem = Rhino.UnitSystem.Millimeters` | `Units` 无该方法 |
| `doc.ModelUnitAbsoluteTolerance` | `doc.ModelAbsoluteTolerance` | 属性不存在 |
| `Rhino.Radians(deg)` | `math.radians(deg)` | 命名空间下无该函数 |
| `doc.Layers.Add('name')` | `layer = Layer(); layer.Name='name'; doc.Layers.Add(layer)` | 需传Layer 对象 |

记忆法：单位/公差三兄弟是 `ModelUnitSystem` / `ModelAbsoluteTolerance` /
`ModelAngleToleranceDegrees`，**全部挂 `doc`、全部 `Model` 前缀、全部直接赋值不调用**。

### ⭐ 端口不是常量

端口、路径、启动命令随插件版本、启动参数和占用情况变化。
⛔ **任何写死的端口都是错的**——包括本包开发机实测过的值。

正确做法：执行 `MCPStart` / `MCPConnect`，**读它打印的横幅**，
或先尝试、连不上就换成横幅里的地址。连不上时先查端口，
⛔ 不要怀疑几何或命令。

## 几何助手

```python
import sys
sys.path.insert(0, str(skill_root / 'scripts'))
import nbs_geometry as N
candidate = N.edge_srf_4(doc, c1, c2, c3, c4)
facts = N.surface_spans(candidate)
# 此处只算内存几何；添加文档前按项目目标复验。
```

`rebuild_to_single_span`输出候选Curve；需显式提供拟合预算，失败抛错，不会默默接受超差。`boundary_continuity`只检查开放曲线端部有向G1条件，不判面连续性。二维指标在outline_metrics，可普通Python导入。

## 受控变更

先记录输入ID、几何与属性，内存算候选并验有效性，再加入任务层；记录新Guid和P/E ID映射。拓扑重建后重新识别边，不复用失效edge索引。新结果通过后才删除/替换旧结果，保留母面版本。

用BeginUndoRecord/EndUndoRecord分组；Undo组不是事务，失败仍需跟踪本批ID显式清理或恢复。不以全局Undo回滚其他用户操作。同一文档相互依赖变更顺序执行。

超时先查对象/命令状态/已完成结果，不能盲重试复制模型。普通读取可批处理。大型重复特征后做、分层隔离，避免一次输出海量数据。

## 命令、视图与保存

核实当前命令及选项，国际化使用英文_前缀；get_commands只证明注册名，不证明选项/重载。避免无人响应的交互拾取。命令后查新ID、数量、类型与有效性，不能只看成功文本。

固定相机与裁切用于比较，截图需真的返回并查看才可称视觉核对。只取必要视角/局部，用户限制读图时以文字/数值检查并写明限制。

保存新版本路径，输出和测试文件与用户原件分开。3dm/STEP等需按合同复验单位、尺寸和完整性，不把文件写出当往返测试。不要关闭/清空/替换未保存用户文档。

GH用于参数族、重复/渐变图案，先发现组件和数据接口，检查树、空值和警告再烘焙；不是所有重复特征必须GH。SubD转NURBS后需查极点和面数，不自动Class-A。
