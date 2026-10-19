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

✅ **2026-10-19 官方 Rhino MCP 0.3.0.0 真机复验**：以上四条全部确认，
`doc.ModelUnitSystem` 读到 `Millimeters`、`doc.ModelAbsoluteTolerance` 读到 `0.001`。

### ⭐⭐ 几何 API 的绑定坑另见专篇

上面四条是**属性级**的。几何 API 还有 13 类**运行时才炸**的陷阱
（`BrepFaceList` 无 `__len__`、`Brep` 无 `Volume`、`Extrusion.Create` 的 4 参签名、
`CreateFilletEdges` 要位置索引 + `BlendType.Fillet`、`rs.Command` 会阻塞 MCP 调用……）。

⛔ **写几何代码前先读 [14 RhinoCommon Python 绑定坑](14-rhino-python-binding-traps.md)**。
那篇是本机真机逐条打出来的，不是文档转述。

### ⭐ 端口不是常量，但探测方法是固定的

端口、路径、启动命令随插件版本、启动参数和占用情况变化。
⛔ **任何写死的端口都是错的**——包括本包开发机实测过的值。

正确做法：执行 `MCPStart` / `MCPConnect`，**读它打印的横幅**，
或先尝试、连不上就换成横幅里的地址。连不上时先查端口，
⛔ 不要怀疑几何或命令。

### ⭐ 官方 RhinoAI 0.3.0 的实测探测姿势

⚠️ **先绕过 HTTP 代理**——本机环境变量里有 `http_proxy`，
curl 默认会走代理，代理返回 502/连接错误，**看起来像端口没开，其实是代理在挡**。

```bash
# ⛔ 少了 --noproxy '*' 就会得到假阴性
curl -s -m 8 --noproxy '*' -X POST "http://127.0.0.1:<PORT>/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2024-11-05","capabilities":{},
        "clientInfo":{"name":"probe","version":"1.0"}}}'
```

**官方服务的确证响应**：

```json
{"jsonrpc":"2.0","id":1,"result":{
  "protocolVersion":"2024-11-05",
  "serverInfo":{"name":"rhino-mcp","version":"0.3.0.0"},
  "capabilities":{"tools":{"listChanged":false},...}}}
```

**响应头 `Server: Microsoft-HTTPAPI/2.0`** = 走 HTTP.sys，这是官方 Rhino 内
HTTP 服务的特征（社区版绑 127.0.0.1 且不一定是这个头）。

### ⭐ 找端口的三个动作

```bash
# 1. 列出所有本地监听（HTTP.sys 的端口归属 PID 4，容易被漏看）
netstat -ano | grep LISTENING | grep 127.0.0.1

# 2. 注意 PID 4 = HTTP.sys = Rhino 内服务；社区版是独立进程
# 3. 用 initialize 逐个试，认 serverInfo.name == "rhino-mcp"
```

⚠️ **本机实测**：官方 0.3.0 实际监听 **10502**，而社区版常用 25105。
两者**协议不同**——社区版是 JSON-RPC 的 `tools/call`，官方也是，
但工具集与 `initialize` 握手不同，⛔ 不要拿社区版的假设套官方。

### ⭐ 端到端真验：拿到活数据才算通

`initialize` 成功只说明端口对。真正的验证是 `tools/call` 返回**活的 Rhino 数据**：

```bash
curl -s -m 15 --noproxy '*' -X POST "http://127.0.0.1:<PORT>/" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call",
       "params":{"name":"get_context","arguments":{}}}'
```

正常会返回 `activeViewport`（相机位置、显示模式）、`document`
（`objectCount`、`layerCount`）、`grasshopper` 数组。

⛔ **返回 `objectCount: 0` 也算通**——那是空文档的正常状态，不是故障。

### ⭐ 官方 0.3.0 的工具清单（31 个）

已按 `tools/list` 实测核对。**注意没有 `list_slots`**，
本 Skill 提到 `list_slots` 是通用说法，实际这个版本没有：

| 分类 | 工具 |
|---|---|
| 读 | `get_context` `get_selection` `list_objects` `get_viewport_image` `get_commands` |
| 改 | `run_command` `run_python` `run_csharp` `set_selection` `set_camera` |
| 文件 | `open_doc` `save_doc` `close_doc` |
| 视图 | `zoom_to_object` `zoom_to_layer` `set_layer_material` |
| Grasshopper | `g1_start` `g1_place_component` `g1_place_slider` `g1_connect` `g1_connect_many` `g1_delete_component` `g1_search_components` `g1_describe_component` `g1_get_canvas_graph` `g1_solve_graph` `g1_apply_graph` `g1_clear_canvas` |
| router 内部 | `_router_spawn_listener` `_router_close_listener` `_router_quit_app` |

⛔ **不要用 `run_command` 跑交互式命令**（会等输入回车）。
⛔ **`run_python` 优先于 `run_command`**——Rhino 命令行的选项在不同版本/语言下
可能变，而 Python API 稳定。

⚠️ `run_csharp` 可直接执行 C#（Roslyn 脚本），能做 RhinoCommon 做不到的事，
但⛔ 未经用户明确要求不要用。

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
