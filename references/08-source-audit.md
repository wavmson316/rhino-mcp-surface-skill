# 来源、可信度与撤销记录

## 本版依据与阅读边界

本版检查当前技能文字与代码，按用户要求未读取扫描图片。此前资料的审读记录属于历史来源，不代表本次逐页阅读全部书籍。API 结论以当前 Rhino 最小试验和随包测试范围为准。

资料包括《Rhino3D工业级造型与设计》第3版、André Kutscherauer《3D Car Modeling with Rhinoceros》及免费样章、Rhino训练资料和当前RhinoCommon API。书籍页码应区分印刷页/PDF页；本包不附扫描/OCR。具体案例可启发构面，不能仅凭出现频率升级为数学定理。原车书以可视化为目标，也不能自动成为量产标准。

## 官方查询入口

- [Rhino帮助](https://docs.mcneel.com/rhino/8/help/en-us/index.htm)：查询当前命令、选项、单位、网格与文件交换。
- [RhinoCommon API](https://developer.rhino3d.com/api/rhinocommon/)：查询真实重载与返回类型。
- [开发者指南](https://developer.rhino3d.com/guides/)：版本和宿主集成。
- [McNeel论坛](https://discourse.mcneel.com/)：具体问题案例，不能代替项目验收标准。

这些是查询入口，不表示本轮已逐页联网核验。当前API事实由Rhino8内存测试支持，具体范围见 [验证记录](../VALIDATION.md)。

## 撤销与替换

| 撤销的绝对规则 | 本版规则 |
|---|---|
| 主面只准EdgeSrf/Loft | 根据几何约束选解析、Sweep、Network等 |
| 玻璃一律平面；家电一律G1 | 形体与反射/用途决定 |
| ChangeDegree不开Deformable不生效 | 精确升阶保形是正常目标 |
| Refine永远不能G2 | 能增加自由度，需监控结构与结果 |
| CP−Degree为通用跨度；周期CP=Degree | 读取真实SpanCount及周期/闭合属性 |
| 圆有四个Kink | 重复结点不等于几何折角 |
| 单跨不能手工G2 | 端部约束与自由度决定 |
| 三通一次Blend唯一解 | 两侧桥接与中心布局分开 |
| 明暗交界不要G2 | 光照线不能决定不连续 |
| Offset含Blend不可能G2 | 检查非奇异偏置及数值误差 |
| 曲线不能修剪Brep | 看实际位置/投影与命令条件 |
| Pipe半径=未来过渡宽×2/3 | 局部案例量规，不是通用公式 |
| 所有可见面必须实体 | 交付要求决定开放/封闭 |
| Weld值=绝对距离公差 | Rhino网格Weld按角度等当前语义核实 |
| 平均尺寸/1000是网格硬标准 | 按弦高/角度/接缝与预算设置 |
| 端口、slot工具永久固定 | 每次发现实际连接能力 |
| 已编译或6项冒烟过即全部可靠 | 每个发布入口及反例分别验证 |

外部09知识图谱和根索引含旧规则，不是本发布包的执行依赖。维护时若改图谱，撤销状态必须真正过滤旧条目，不只是添加免责声明。新知识字段建议：id、statement、scope、preconditions、evidence、validation、counterexample、status、supersedes。
