# 安装与接入自检

1. 将整个目录放入当前Agent支持的skills路径，确认入口frontmatter可识别。读取工具列表，确认当前连接协议、Rhino版本和目标文档。已连接就使用现有连接，不为确认端口重启服务。没有连接时按所装MCP插件说明查启动命令与实际端点；不预设端口或工具名。
2. 有 `list_slots` 时定位用户目标实例；没有时用当前连接的上下文接口。无法消歧才询问。读取注入文档的单位、公差、文件和对象，不修改。
3. Rhino Python3中运行下方测试。它仅构造内存几何，不添加用户文档对象。测试失败应报告具体失败入口，不能沿用别台机器的“通过”。

```python
import sys
from pathlib import Path
skill_root = Path(r'<替换为实际安装目录>')
sys.path.insert(0, str(skill_root / 'scripts'))
from smoke_test_rhino import run_tests
result = run_tests(__rhino_doc__)
print(result)
```

4. 普通Python可运行 `python scripts/test_outline_metrics.py` 与 `python scripts/check_release.py`。前者无需Rhino；后者只作语法/引用/发布内容检查，不能代替Rhino测试。
5. 比较 [VALIDATION.md](VALIDATION.md) 的已测版本和当前版本。Rhino6/7或其他Python宿主未验证时记录限制；方法论可用，API须现场核实。

## 排错

| 现象 | 处理 |
|---|---|
| 连不上 | 检查当前插件、服务日志、端点与客户端配置；不猜固定10500/10501 |
| 缺模块 | 传Rhino进程可访问的绝对scripts路径；本地客户端路径未必等于远端Rhino路径 |
| import Rhino失败 | 几何脚本需RhinoCommon宿主；二维指标独立在outline_metrics中 |
| 注入doc在import后不可见 | 调用函数时显式传文档，不能回退ActiveDoc |
| 测试断言失败 | 保留失败结果，核对API与版本；不能删断言制造通过 |
