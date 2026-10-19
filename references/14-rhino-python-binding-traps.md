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

## 11. 通用原则

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

## 12. 实测通过的片段（可直接抄）

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

## 13. 来源

本机 Rhino **8.29.26063.11001**、Windows、Rhino 内 Python 3、
官方 McNeel Rhino MCP Platform **0.3.0.0**（`serverInfo.name == "rhino-mcp"`）。
所有结论均为真机运行所得，脚本在会话中实测通过。