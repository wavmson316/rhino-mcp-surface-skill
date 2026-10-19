# RhinoCommon Python 绑定怪癖（Rhino 8.29 实测打脸）

> 本篇是**真机实测**记录，不是文档转述。每一条都在
> Rhino **8.29.26063.11001** + Windows + Rhino 内 Python 3 上跑过。
>
> ⛔ 这些都是**编译期不报错、运行时才炸**的坑，静态查文档看不出来。

---

## 0. 一句话

**RhinoCommon 的 Python 绑定不是普通 Python。** 集合类型不总是可迭代，
部分属性名与 C# 不同，枚举成员名也不同。

⛔ **不要照着 C# 示例写 Python** —— 很多写法在 Python 里直接抛 `AttributeError`。

---

## 1. ⭐ 集合类型：`BrepFaceList` 没有 `__len__`

```python
b = some_brep
len(b.Faces)          # ⛔ TypeError: object of type 'BrepFaceList' has no len()
b.Faces.Count         # ✅ 6
len(list(b.Faces))    # ✅ 6
```

⚠️ `hasattr(b.Faces, 'Count')` 为真，但 `hasattr(x,'Faces')` **不能**用来判断
"这是不是一个 Brep"——`BrepFaceList` 也有 `Faces` 属性。

**判定技巧**：`type(x).__name__ == 'Brep'`。不要用 `isinstance` + `hasattr` 组合。

| 集合 | 计数方式 |
|---|---|
| `Brep.Faces` / `Brep.Edges` | `.Count` |
| `BrepFace.OuterEdge` | `.Count` |
| 任何 Rhino 集合 | `len(list(...))` 最保险 |

---

## 2. ⭐ `Brep` 没有 `Volume` 属性

```python
brep.Volume                        # ⛔ AttributeError: 'Brep' object has no attribute 'Volume'
G.VolumeMassProperties.Compute(brep).Volume   # ✅ 48000.0
```

⚠️ `VolumeMassProperties` 也**没有** `.Area`（面积要逐面求或用别的方法）。

⛔ **别用 `brep.Volume` 做体积验收** —— 这是很容易想当然写出来的代码。

---

## 3. ⭐ `BrepFace` 没有 `Edges` 属性

```python
for f in brep.Faces:
    f.Edges        # ⛔ AttributeError: 'BrepFace' object has no attribute 'Edges'
```

要在面上取边，用 `f.OuterEdge`（外环）或从 Brep 层拿 `brep.Edges`。
**推荐从 Brep 层统一取**，这样边索引才有意义（见 §5）。

---

## 4. ⭐ `BrepEdge` 没有 `Index` 属性

```python
for e in brep.Edges:
    e.Index        # ⛔ AttributeError: 'BrepEdge' object has no attribute 'Index'
```

**边索引用枚举位置**：

```python
edges = list(brep.Edges)
idx = [i for i, e in enumerate(edges) if <条件>]
```

⚠️ 面上的 `f.Edges[ei].Index` 同样不可靠——用 `enumerate` 最稳。

---

## 5. ⭐ `Brep.CreateFilletEdges` 要的是**位置索引**，不是边对象

```python
# ⛔ 传边对象：TypeError
G.Brep.CreateFilletEdges(brep, [edge_obj, ...], ...)

# ✅ 传 int 位置索引
idx = [i for i, e in enumerate(list(brep.Edges)) if <是竖直边>]
r = G.Brep.CreateFilletEdges(brep, idx, [3.0]*len(idx), None, None,
                             G.BlendType.Fillet, G.RailType.RollingBall, 1.0)
```

⚠️ **参数个数容易搞错**：7 参与 8 参重载都存在，传错个数会报
"No overload ... takes 'N' arguments"。

⚠️ `BlendType` 的成员是 **`Fillet` / `Blend` / `Chamfer`**——
⛔ **没有 `Normal`**（那是 `LoftType` 的成员名，别混）。

⚠️ `RailType` 成员是 **`RollingBall`** / `DistanceBetweenRails` / `DistanceFromEdge`。

⚠️ Python.NET 3.0 起，**int 不能隐式转枚举**，必须显式 `G.BlendType.Fillet`。

---

## 6. ⭐ `Rhino.Geometry` 里没有 `Polygon`

```python
G.Polygon(pts)     # ⛔ AttributeError: module 'Rhino.Geometry' has no attribute 'Polygon'
```

**正确做法**：

```python
pts = [G.Point3d(0,0,0), G.Point3d(80,0,0), G.Point3d(80,50,0), G.Point3d(0,50,0)]
closed = pts + [pts[0]]              # 显式闭合
curve = G.PolylineCurve(G.Polyline(closed))
```

⚠️ 平面可以用 `G.Curve.CreatePeriodicPolygon`，但那个要**面积**参数，
用 Polyline 更直接。

---

## 7. ⭐ `Extrusion` 的正确用法

```python
# ⛔ Brep 上没有 CreateExtrusion
G.Brep.CreateExtrusion(...)                    # ⛔ 不存在

# ✅ Extrusion 是独立类
ext = G.Extrusion.Create(curve, plane, height, cap=True)
brep = ext.ToBrep()                            # ✅ 返回单个 Brep
```

⚠️ **签名是 4 参**（curve, plane, height, cap）：

| 尝试 | 结果 |
|---|---|
| `Extrusion.Create(curve, vec, 12.0)` | ⛔ Vector3d 不能转 Double |
| `Extrusion.Create(curve, plane, 12.0)` | ⛔ 3 参版不存在 |
| `Extrusion.Create(curve, plane, 12.0, True)` | ✅ |

⚠️ 第 2 参是 **`Plane` 不是 `Vector3d`**，第 3 参是 **height(double) 不是 bool**。

⚠️ `ext.ToBrep()` 返回**单个 Brep**（不是 FaceList）——
⛔ 不要写 `for f in ext.ToBrep(): br.Append(f)`，那会报
"'Brep' object is not iterable"。

---

## 8. ⭐ `CreateBooleanDifference` 要公差参数

```python
G.Brep.CreateBooleanDifference(a, b)              # ⛔ 只接受 2 参？No overload
G.Brep.CreateBooleanDifference(a, b, tolerance)   # ✅
```

返回 **`Brep[]`**，不是单个 Brep。

---

## 9. ⭐ `Guid` 没有 `.Id`

```python
oid = doc.Objects.AddBrep(brep)
oid.Id            # ⛔ AttributeError: 'Guid' object has no attribute 'Id'
```

`AddBrep` 直接返回 `Guid`，用 `str(oid)` 或直接传给 `FindId` / `Delete`。

---

## 10. ⭐ `rs.Command` 会阻塞

```python
rs.Command('_-FilletEdge ...', False)   # ⛔ 卡住不动，等输入回车
```

⚠️ **实测卡死了 MCP 调用**（直到手动干预才恢复）。

⛔ **不要用 `rs.Command` 跑需要交互输入的命令。**

**改用 MCP 的 `run_command` 工具**，它有超时与状态回报。

⚠️ 命令行选项在 Rhino 8 有变化：`_SelEdges` **已不存在**
（报错"未知的指令: _SelEdges"），边选择要用 `Edge` / `SelEdge`。

---

## 11. ⭐⭐ `Sweep2` 与 `NetworkSrf` 在 RhinoCommon 里根本不存在

**这是最容易白花时间的一条。** 很多人以为"Rhino 命令 = RhinoCommon 方法"，
然后花半小时找一个不存在的方法。

```python
G.Brep.CreateSweep2        # ⛔ AttributeError
G.Brep.CreateNetworkSrf    # ⛔ AttributeError
G.Surface.CreateSweep2     # ⛔ AttributeError
```

**实测（Rhino 8.29）**：`Brep.Create*` 的完整列表里没有这两个。

### 11.1 哪些构面有 API，哪些没有

| 命令 | RhinoCommon 方法 | 说明 |
|---|---|---|
| `Loft` | ✅ `Brep.CreateFromLoft` | 有 |
| `EdgeSrf` | ✅ `Brep.CreateEdgeSurface` | 有 |
| `Patch` | ✅ `Brep.CreatePatch` | 有 |
| `FilletEdge` | ✅ `Brep.CreateFilletEdges` | 有 |
| `Extrusion` | ✅ `Extrusion.Create` + `ToBrep` | 是独立类，不是 Brep 方法 |
| `Revolve` | ✅ `Brep.CreateFromRevSurface` | 有 |
| ⛔ **`Sweep2`** | ❌ **无** | **只能走命令** |
| ⛔ **`NetworkSrf`** | ❌ **无** | **只能走命令** |
| ⛔ `Sweep1` | ⚠️ `Brep.CreateFromSweep*` 存在但语义不同 | 见 §11.3 |

### 11.2 只能走命令时怎么办

⛔ **`rs.Command` 会阻塞 MCP 调用**（见 §10）。可行的做法：

```python
import rhinoscriptsyntax as rs
# 1. 把工作副本加进文档（命令只认文档里的对象）
ids = [doc.Objects.Add(c) for c in working_copies]
# 2. 用下划线前缀的命令名（与语言无关）
rs.Command('_-NetworkSrf _SelCrv ' + ','.join(map(str, ids)) + ' _Enter', False)
# 3. 从文档里捞结果
```

⚠️ 风险与代价：
- ⛔ 命令会**消耗输入对象**，它们从场景消失 → 这也是本包坚持"先复制再构面"的原因
- ⚠️ 异步执行，结果不一定立刻可用 → **必须检查结果**，不能假设成功
- ⚠️ 命令行选项随版本变化 → ⛔ 不要背选项字符串，用前先 `get_commands` 核实

### 11.3 `Sweep1` 的坑

`Brep.CreateFromSweep` / `CreateFromSweepInParts` 存在，
但⛔ **它们不是 `Sweep1` 命令的等价物** —— 参数语义和结果拓扑都对不上。

需要严格的 `Sweep1` 行为（标架、扭转、封盖）时，走命令。

---

## 12. ⭐⭐ `doc.Layers.FindName` 返回 `None`，不是 `-1`

```python
doc.Layers.FindName('Lines')     # 层不存在时返回 None
if found >= 0:                   # ⛔ TypeError: '>=' not supported between
    return found                     NoneType and int
```

**正确写法**：

```python
found = doc.Layers.FindName('Lines')
if found is not None:
    return found.Index        # ✅ Layer 对象，取 .Index
# 不存在时返回 None，必须先 Add 一个 Layer 对象（见下）
layer = Rhino.DocObjects.Layer()
layer.Name = 'Lines'
doc.Layers.Add(layer)         # 返回 int 索引
```

⚠️ 两个要点：
- ⛔ `doc.Layers.Add('Lines')` **不接受字符串**，必须传 `Layer` 对象
- 找到了返回的是 **`Layer` 对象**不是 int，取索引用 `.Index`

---

## 13. ⭐ `doc.Objects.Count` 可能与枚举不一致

```python
doc.Objects.Count          # 16
len(list(doc.Objects))     # 0   ← 实际是空的
```

**实测（Rhino 8.29，两次独立复现）**：

| 场景 | `Count` | 枚举 |
|---|---|---|
| Rhino 命令消耗对象后 | 8 | **0** |
| 删除全部对象后 | 16 | **0** |

⚠️ **两种情况下 `Count` 都停在旧值不刷新。** 更糟的是它会让人以为
"对象还在，删不掉" —— 而实际枚举一遍就什么都没有了。

⚠️ 另一处相关陷阱：`Rhino.Geometry.NurbsCurve` **没有 `IsCurve` 属性**，
想按类型过滤对象时只能用 `IsValid` 加几何类名判断。

⚠️ **判定文档是否干净，用枚举而不是 `Count`**：

```python
clean = len(list(doc.Objects)) == 0        # ✅ 可靠
# ⛔ doc.Objects.Count == 0                 # 可能骗你
```

⚠️ 这条在「测试前后对象数量应一致」的断言里尤其重要 —— 用 `Count` 会误判。

### 13.1 `Purge` 需要参数

```python
doc.Objects.Purge()          # ⛔ No overload ... takes '0' arguments
```

⛔ 不要凭直觉调用，签名随版本不同。

### 13.2 改过脚本源码后必须 reload

Rhino 的 Python 会**缓存已 import 的模块**。改了 `.py` 重新跑，
拿到的还是旧代码 —— 而报错行号会指向源码里不匹配的行，非常误导。

```python
import importlib, patch_with_lines
importlib.reload(patch_with_lines)      # ✅ 改过源码后必须 reload
```

⚠️ 或者在文件层面删掉 `__pycache__`。⛔ **不要靠这个发现代码改对了没** ——
先确认 `module.__file__` 指向你以为的那个文件。

---

## 14. 通用原则

⛔ **不要靠记忆写 RhinoCommon Python。** 正确姿势：

```python
# 1. 反射查真实存在的东西
print([n for n in dir(G.Brep) if 'Fillet' in n])
print(G.Brep.CreateFilletEdges.__doc__)     # 打印所有重载

# 2. 试调用，错误信息会精确指出类型不匹配
# 3. 一次跑一批探测，别一个一个试
```

**错误信息是最快的文档**：`No overload ... takes 'N' arguments` 直接告诉你
有几个参数；`X value cannot be converted to Y` 直接告诉你该传什么。

⚠️ `__doc__` 里的多行签名要用正则逐行提取，直接 print 会被换行拆散。

---

## 15. 实测通过的片段（可直接抄）

```python
import Rhino.Geometry as G
import rhinoscriptsyntax as rs
doc = __rhino_doc__

# 造一个封闭实体
pts = [G.Point3d(0,0,0), G.Point3d(80,0,0), G.Point3d(80,50,0), G.Point3d(0,50,0)]
curve = G.PolylineCurve(G.Polyline(pts + [pts[0]]))
ext = G.Extrusion.Create(curve, G.Plane(G.Point3d(0,0,0), G.Vector3d(0,0,1)), 12.0, True)
brep = ext.ToBrep()

print(brep.Faces.Count)                                  # 6
print(brep.IsSolid)                                      # True
print(G.VolumeMassProperties.Compute(brep).Volume)       # 48000.0

# 找竖直边（用位置索引）
edges = list(brep.Edges)
idx = [i for i, e in enumerate(edges) if abs(e.PointAtStart.Z - e.PointAtEnd.Z) > 11.9]

# 圆角
res = G.Brep.CreateFilletEdges(brep, idx, [3.0]*len(idx), None, None,
                               G.BlendType.Fillet, G.RailType.RollingBall, 1.0)
print(res[0].Faces.Count, res[0].IsValid)
```

---

## 16. 来源

本机 Rhino **8.29.26063.11001**、Windows、Rhino 内 Python 3、
官方 McNeel Rhino MCP Platform **0.3.0.0**（`serverInfo.name == "rhino-mcp"`）。
所有结论均为真机运行所得，脚本在会话中实测通过。