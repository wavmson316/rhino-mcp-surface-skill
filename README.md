# Rhino MCP Surface Skill 1.0.0

从参考图、草图、尺寸或扫描资料建立可编辑 NURBS 曲面，覆盖工业产品、汽车、自由曲面和复杂过渡。

入口是 [SKILL.md](SKILL.md)，首次接入看 [INSTALL-CHECK.md](INSTALL-CHECK.md)。把整个 `rhino-mcp-surface-skill` 文件夹复制到你的 Agent 支持的 skills 目录；不限定 WorkBuddy、Codex 或某个安装路径。内部 ID 与目录名保持一致。

本包包含入口、11篇按需参考、项目模板、结构审计、曲线/曲面几何助手、接缝G1采样、独立二维轮廓指标及验证脚本。脚本默认只处理内存几何或读取显式文档；将结果添加到用户模型由调用方受控完成。

## 适用与边界

按几何类型与交付需求决策，不按“汽车/家电”强制选择曲面或G级。概念可用归一化尺度；制造需要真实尺寸与工艺约束。纯网格/SubD任务可借用形体分析，选择下游真正需要的表示。

这是可分发的技能包，不是车厂Class-A认证或自动制造系统。自动测试不包含照片端到端重建与全域G2认证。详见 [验证记录](VALIDATION.md) 与 [来源审计](references/08-source-audit.md)。

## 最小调用

在Rhino Python中，将本包实际安装目录设为 `skill_root`：

```python
import sys, json
sys.path.insert(0, str(skill_root / 'scripts'))
from audit_geometry import audit_ids
print(json.dumps(audit_ids(__rhino_doc__, object_ids), ensure_ascii=False))
```

`skill_root` 是调用方解析的路径对象，`object_ids` 是任务对象GUID列表；不扫描和修改不相关对象。没有相应MCP工具时按当前连接能力适配。

## 发布维护

规则以本包文档为准；外部旧笔记/知识图谱只作待核对资料，不自动导入。新规则应附适用条件、出处、验证方法与反例，修改后运行 [发布检查](scripts/check_release.py)。

本包不附书籍扫描、OCR或第三方完整教程。没有替来源资料授予许可；作者未提供独立开源许可时，不暗示已有MIT等许可。版本变化见 [CHANGELOG.md](CHANGELOG.md)。
