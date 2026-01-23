# 下一步工作 (Next Steps)

## ✅ 已完成 (Completed)

### Phase 1: 架构设计和基础设施 (Architecture Design & Infrastructure)

1. **Animation DSL Schema** ✓
   - 完整的 JSON Schema 定义
   - 支持所有核心动画类型
   - 完善的验证规则

2. **DSL Validator** ✓
   - Schema 验证（使用 jsonschema）
   - 业务逻辑验证（资源检查、ID唯一性、时长估算）
   - 详细的错误和警告报告

3. **DSL Parser** ✓
   - 结构化解析（SceneSpec, PhaseSpec, AnimationSpec）
   - 便捷的访问接口
   - 模板加载支持

4. **示例和模板** ✓
   - 完整示例：simple_solution.json
   - DSL 模板：scene_template.json
   - 测试覆盖率 100%

5. **文档** ✓
   - REFACTORING_PLAN.md（完整架构蓝图）
   - 包含风险分析和迁移策略

6. **测试** ✓
   - test_dsl_validator.py
   - 所有测试通过 ✓

---

## 📋 下一阶段任务 (Next Phase Tasks)

### Phase 2: 核心渲染器 (Priority: P0 - 必须完成)

#### 2.1 DSL → Manim 转换器 (DSL to Manim Converter)

**文件**: `manim_mcp/renderer/dsl_to_manim.py`

**功能**:
- 将 Animation DSL 转换为 Manim Python 代码
- 支持所有动画类型的代码生成
- 处理并行动画
- 生成完整的可运行 Scene 类

**关键方法**:
```python
class DSLToManimConverter:
    def __init__(self, scene_spec: SceneSpec)
    def generate_scene_code() -> str
    def _generate_timeline_code() -> str
    def _generate_animation_code(anim: AnimationSpec) -> str
```

**动画类型映射**:
- `show_text` → Text() + Write()
- `show_math` → MathTex() + Write()
- `show_image` → ImageMobject() + FadeIn()
- `fade_in` → FadeIn()
- `fade_out` → FadeOut()
- `move_to` → animate.move_to()
- `highlight` → SurroundingRectangle() + Create()
- ... 更多

#### 2.2 固定 Scene 模板 (Fixed Scene Template)

**文件**: `manim_mcp/renderer/base_scene.py`

**功能**:
- 固定的 Scene 基类
- 统一的配置（分辨率、帧率、颜色）
- 布局常量（POS_ANIM_CENTER, POS_TEXT_BASE 等）
- 音频处理集成

**示例**:
```python
class DSLScene(Scene):
    def __init__(self, scene_spec: SceneSpec):
        super().__init__()
        self.spec = scene_spec

    def construct(self):
        self.setup_config()
        for phase in self.spec.timeline:
            self.render_phase(phase)
```

#### 2.3 渲染执行器 (Render Executor)

**文件**: `manim_mcp/renderer/render_executor.py`

**功能**:
- 执行 manim 命令
- 处理渲染输出
- 超时控制（300s）
- 错误处理和日志

**示例**:
```python
class RenderExecutor:
    def render(self, scene_id: str, quality: str) -> RenderResult
    def _save_python_code(code: str) -> Path
    def _execute_manim_command() -> subprocess.CompletedProcess
```

---

### Phase 3: MCP Tools 实现 (Priority: P0 - 必须完成)

#### 3.1 create_scene Tool

**文件**: `manim_mcp/tools/create_scene.py`

**功能**:
- 接收 DSL JSON
- 验证 DSL
- 保存到 scenes/ 目录
- 返回验证结果和场景信息

#### 3.2 validate_scene Tool

**文件**: `manim_mcp/tools/validate_scene.py`

**功能**:
- 读取已保存的场景
- 执行完整验证
- 返回详细的验证报告

#### 3.3 render_scene Tool

**文件**: `manim_mcp/tools/render_scene.py`

**功能**:
- 读取场景 DSL
- 转换为 Manim 代码
- 执行渲染
- 返回视频路径和渲染统计

#### 3.4 batch_render Tool

**文件**: `manim_mcp/tools/batch_render.py`

**功能**:
- 批量渲染多个场景
- 进度报告
- 失败处理和重试

#### 3.5 更新 server.py

**功能**:
- 注册新的 MCP tools
- 更新 call_tool() 处理器
- 集成 DSL 工作流

---

### Phase 4: Prompt 更新 (Priority: P1 - 重要)

#### 4.1 更新 stage3 Prompt

**文件**: `prompts/stage3_dsl_generation.txt`

**目标**:
- 让 LLM 生成 Animation DSL (JSON) 而不是 Python 代码
- 提供 DSL 示例和模板
- 明确 DSL 规范和最佳实践

**关键内容**:
```
你的任务是生成 Animation DSL (JSON 格式)，而不是 Manim Python 代码。

DSL 示例：
[包含 simple_solution.json 的内容]

DSL 规范：
- 所有动画必须在右上方区域 (position: [3.5, 2.0, 0])
- 文字步骤在右下方 (position: [3.5, -3.0, 0])
- 题目图片在左侧 (position: [-3.5, 0.5, 0])
- ...

要求：
1. 生成完整的 JSON（从 { 到 }）
2. 确保所有必需字段都存在
3. 使用正确的动画类型
4. 合理估算动画时长
```

#### 4.2 更新 stage0_master Prompt

**功能**:
- 说明新的工作流程
- 强调 DSL 优先

---

## 🔧 实现建议 (Implementation Suggestions)

### 1. 优先级

**立即开始** (今天-明天):
- Phase 2.1: DSL → Manim 转换器
- Phase 2.2: 固定 Scene 模板

**本周内完成**:
- Phase 2.3: 渲染执行器
- Phase 3.1-3.3: 核心 MCP tools

**下周完成**:
- Phase 3.4: batch_render
- Phase 4: Prompt 更新

### 2. 测试策略

每个组件都需要：
- 单元测试（测试单个函数）
- 集成测试（测试完整流程）
- 示例测试（使用 simple_solution.json）

### 3. 迭代策略

**MVP (Minimum Viable Product)**:
- 支持 6 种核心动画类型（show_text, show_math, show_image, fade_in, fade_out, move_to）
- 支持单场景渲染
- 基本错误处理

**V1.0**:
- 支持所有 DSL 定义的动画类型
- 支持批量渲染
- 完善的错误处理和日志
- 音频集成

**V2.0**:
- 性能优化
- 并行渲染
- DSL 版本管理
- 更多动画类型

### 4. 兼容性

**向后兼容**:
- 保留旧的 run.py（标记为 deprecated）
- 提供 Python → DSL 转换工具
- 提供迁移文档

---

## 📊 进度追踪 (Progress Tracking)

### 当前状态
- [x] Phase 1: 架构设计 (100%)
- [ ] Phase 2: 核心渲染器 (0%)
- [ ] Phase 3: MCP Tools (0%)
- [ ] Phase 4: Prompt 更新 (0%)

### 估算时间
- Phase 2: 2-3 天
- Phase 3: 2-3 天
- Phase 4: 1 天
- 测试和调试: 1-2 天

**总计**: 约 1 周完成 MVP

---

## 🚀 快速开始下一步 (Quick Start Next Step)

如果你想立即开始实现，建议从这里开始：

```bash
# 1. 创建 DSL → Manim 转换器的骨架
cat > manim_mcp/renderer/dsl_to_manim.py << 'EOF'
from typing import Dict
from ..dsl.parser import SceneSpec, PhaseSpec, AnimationSpec

class DSLToManimConverter:
    def __init__(self, scene_spec: SceneSpec):
        self.spec = scene_spec

    def generate_scene_code(self) -> str:
        """生成完整的 Manim Scene 代码"""
        # TODO: 实现
        pass
EOF

# 2. 测试转换器
python3 -c "
from manim_mcp.dsl.parser import DSLParser
from manim_mcp.renderer.dsl_to_manim import DSLToManimConverter

scene = DSLParser.parse_file('manim_mcp/dsl/examples/simple_solution.json')
converter = DSLToManimConverter(scene)
print('Converter created successfully!')
"
```

---

## 📚 参考资料 (References)

- **架构文档**: `REFACTORING_PLAN.md`
- **DSL Schema**: `manim_mcp/dsl/schema.json`
- **DSL 示例**: `manim_mcp/dsl/examples/simple_solution.json`
- **DSL 模板**: `templates/scene_template.json`
- **测试**: `test_dsl_validator.py`

---

## ❓ 问题和讨论 (Questions & Discussion)

如果你有任何问题或需要讨论实现细节，请参考 REFACTORING_PLAN.md 中的对应章节。

---

**最后更新**: 2026-01-23
**状态**: Phase 1 完成 ✓
**下一步**: 开始 Phase 2 - 实现 DSL → Manim 转换器
