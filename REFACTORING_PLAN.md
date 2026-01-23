# Manim MCP Server 架构重构方案

## 一、可行性评估 ✅

### 当前架构问题
❌ **不稳定性**
- LLM 直接生成 Manim Python 代码
- 微小的 prompt 变化导致代码差异大
- 难以保证代码质量和一致性

❌ **不可控性**
- 无法提前验证动画是否可渲染
- 错误只能在渲染时发现（浪费时间）
- 难以批量处理和自动化

❌ **维护困难**
- 每次生成完整的 Python 文件
- 模板修改需要重新生成所有代码
- VGroup/ImageMobject 等问题需要事后修复

### 新架构优势
✅ **确定性**
- LLM 只生成结构化 JSON (Animation DSL)
- DSL → Manim 代码的转换是固定的
- 同样的 DSL 永远产生同样的视频

✅ **可验证性**
- 渲染前可以验证 DSL 合法性
- 可以预估视频时长
- 错误在生成阶段就能发现

✅ **可扩展性**
- 支持批量渲染
- 支持 DSL 版本管理
- 容易添加新的动画类型

### 可行性结论
**非常可行！** 这是一个标准的声明式架构，经过验证的最佳实践。

---

## 二、Animation DSL 设计

### 2.1 核心 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Manim Animation DSL",
  "type": "object",
  "required": ["scene_id", "metadata", "timeline"],
  "properties": {
    "scene_id": {
      "type": "string",
      "description": "场景唯一标识符",
      "pattern": "^[a-zA-Z0-9_-]+$"
    },
    "metadata": {
      "type": "object",
      "required": ["title", "problem_image"],
      "properties": {
        "title": {
          "type": "string",
          "description": "场景标题"
        },
        "problem_image": {
          "type": "string",
          "description": "题目图片文件名"
        },
        "resolution": {
          "type": "string",
          "enum": ["1080p", "720p", "4k"],
          "default": "1080p"
        },
        "frame_rate": {
          "type": "integer",
          "enum": [30, 60],
          "default": 60
        },
        "theme": {
          "type": "string",
          "enum": ["light", "dark"],
          "default": "dark"
        }
      }
    },
    "timeline": {
      "type": "array",
      "description": "时间轴上的所有阶段",
      "items": {
        "$ref": "#/definitions/Phase"
      }
    }
  },
  "definitions": {
    "Phase": {
      "type": "object",
      "required": ["phase_id", "type", "animations"],
      "properties": {
        "phase_id": {
          "type": "string",
          "description": "阶段标识符"
        },
        "type": {
          "type": "string",
          "enum": ["cover", "problem_reading", "solution_steps", "final_answer"],
          "description": "阶段类型"
        },
        "audio": {
          "$ref": "#/definitions/Audio"
        },
        "animations": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Animation"
          }
        }
      }
    },
    "Audio": {
      "type": "object",
      "required": ["text"],
      "properties": {
        "text": {
          "type": "string",
          "description": "语音文本"
        },
        "voice": {
          "type": "string",
          "enum": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
          "default": "zh-CN-XiaoxiaoNeural"
        },
        "rate": {
          "type": "string",
          "default": "+10%"
        }
      }
    },
    "Animation": {
      "type": "object",
      "required": ["anim_id", "type", "target"],
      "properties": {
        "anim_id": {
          "type": "string"
        },
        "type": {
          "type": "string",
          "enum": [
            "create", "write", "fade_in", "fade_out",
            "transform", "move_to", "scale", "rotate",
            "highlight", "indicate"
          ]
        },
        "target": {
          "type": "string",
          "description": "动画目标（对象ID或新建对象定义）"
        },
        "params": {
          "type": "object",
          "description": "动画参数（根据type不同而不同）"
        },
        "duration": {
          "type": "number",
          "default": 1.0,
          "minimum": 0.1
        },
        "parallel": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "与此动画并行执行的其他动画ID"
        }
      }
    }
  }
}
```

### 2.2 实际 DSL 示例

```json
{
  "scene_id": "problem_1_solution",
  "metadata": {
    "title": "Q1: 高斯求和问题",
    "problem_image": "image_1.png",
    "resolution": "1080p",
    "frame_rate": 60,
    "theme": "dark"
  },
  "timeline": [
    {
      "phase_id": "cover",
      "type": "cover",
      "animations": [
        {
          "anim_id": "show_cover_bg",
          "type": "fade_in",
          "target": "cover_background",
          "params": {
            "image": "assets/cover.png"
          },
          "duration": 0.5
        },
        {
          "anim_id": "show_problem_image",
          "type": "fade_in",
          "target": "problem_center",
          "params": {
            "image": "input/images/image_1.png",
            "width": 4.0,
            "height": 3.0,
            "position": [0, -0.8, 0]
          },
          "duration": 1.0
        }
      ]
    },
    {
      "phase_id": "problem_reading",
      "type": "problem_reading",
      "audio": {
        "text": "题目要求：求1到100的和",
        "voice": "zh-CN-XiaoxiaoNeural",
        "rate": "+10%"
      },
      "animations": [
        {
          "anim_id": "highlight_problem",
          "type": "highlight",
          "target": "problem_left",
          "params": {
            "color": "#FFD700",
            "stroke_width": 4
          },
          "duration": 0.5
        }
      ]
    },
    {
      "phase_id": "step_1",
      "type": "solution_steps",
      "audio": {
        "text": "步骤一：利用高斯求和公式"
      },
      "animations": [
        {
          "anim_id": "show_step_text",
          "type": "write",
          "target": "step_text_1",
          "params": {
            "text": "步骤1：高斯求和公式",
            "position": [3.5, -3.0, 0],
            "font_size": 24,
            "color": "#FFD700"
          },
          "duration": 0.6
        },
        {
          "anim_id": "show_formula",
          "type": "write",
          "target": "formula_1",
          "params": {
            "latex": "S_n = \\frac{n(n+1)}{2}",
            "position": [3.5, 2.0, 0],
            "font_size": 32,
            "color": "#FFFFFF"
          },
          "duration": 1.5
        }
      ]
    },
    {
      "phase_id": "final_answer",
      "type": "final_answer",
      "animations": [
        {
          "anim_id": "show_answer",
          "type": "write",
          "target": "answer_box",
          "params": {
            "text": "答案：5050",
            "position": [-3.5, -3.2, 0],
            "font_size": 40,
            "color": "#FFD700",
            "box": true
          },
          "duration": 1.0
        }
      ]
    }
  ]
}
```

---

## 三、新目录结构

```
claude-demo/
├── run.py                          # 主程序（保留，但简化）
├── server.py                       # MCP Server 主入口（重构）
├── mcp.json                        # MCP 配置
├── requirements.txt
│
├── manim_mcp/                      # 新增：MCP Server 核心模块
│   ├── __init__.py
│   ├── server.py                   # MCP Server 实现
│   │
│   ├── tools/                      # MCP Tools
│   │   ├── __init__.py
│   │   ├── create_scene.py         # Tool: 创建场景
│   │   ├── validate_scene.py       # Tool: 验证场景
│   │   ├── render_scene.py         # Tool: 渲染场景
│   │   ├── batch_render.py         # Tool: 批量渲染
│   │   ├── get_scene_info.py       # Tool: 获取场景信息
│   │   └── list_scenes.py          # Tool: 列出所有场景
│   │
│   ├── dsl/                        # DSL 解析和验证
│   │   ├── __init__.py
│   │   ├── schema.json             # DSL JSON Schema
│   │   ├── validator.py            # DSL 验证器
│   │   ├── parser.py               # DSL 解析器
│   │   └── examples/               # DSL 示例
│   │       ├── simple.json
│   │       ├── full_solution.json
│   │       └── batch_scenes.json
│   │
│   ├── renderer/                   # Manim 渲染引擎
│   │   ├── __init__.py
│   │   ├── base_scene.py           # 固定的 Scene 基类
│   │   ├── dsl_to_manim.py         # DSL → Manim 转换器
│   │   ├── timeline.py             # 时间轴管理
│   │   ├── animation_factory.py    # 动画工厂（根据type创建动画）
│   │   └── render_executor.py      # 渲染执行器
│   │
│   ├── audio/                      # 音频处理
│   │   ├── __init__.py
│   │   ├── tts_engine.py           # TTS 引擎（edge_tts + Mac say）
│   │   └── audio_sync.py           # 音频同步
│   │
│   └── utils/                      # 工具函数
│       ├── __init__.py
│       ├── file_manager.py         # 文件管理
│       └── logger.py               # 日志配置
│
├── scenes/                         # 新增：存储 DSL 文件
│   ├── scene_1.json
│   ├── scene_2.json
│   └── ...
│
├── output/                         # 输出目录（保留）
│   ├── image_1/
│   │   ├── scene.json              # DSL 文件（存档）
│   │   ├── image_1.mp4             # 渲染视频
│   │   ├── image_1.py              # 生成的 Manim 代码（可选）
│   │   └── image_1.md              # 解题步骤（保留）
│   └── ...
│
├── assets/                         # 资源文件（保留）
│   ├── logo.png
│   ├── cover.png
│   └── fonts/
│
├── input/                          # 输入文件（保留）
│   ├── images/
│   └── prompt.txt
│
├── templates/                      # 模板（保留旧模板，添加新模板）
│   ├── manim_template.py           # 旧模板（保留用于参考）
│   └── scene_template.json         # 新增：DSL 模板
│
├── prompts/                        # 提示词（需要更新）
│   ├── stage0_master.txt
│   ├── stage1_visual_strategy.txt
│   ├── stage2_math_solution.txt
│   ├── stage3_dsl_generation.txt   # 新增：生成 DSL 的 prompt
│   └── stage4_jsxgraph.txt
│
└── tests/                          # 测试（新增）
    ├── test_dsl_validator.py
    ├── test_dsl_to_manim.py
    ├── test_tools.py
    └── fixtures/
        └── test_scenes/
```

---

## 四、MCP Tools 设计

### Tool 1: `create_scene`
**功能**: 从 DSL 创建场景

```json
{
  "name": "create_scene",
  "description": "从结构化的 Animation DSL 创建 Manim 场景",
  "inputSchema": {
    "type": "object",
    "required": ["scene_dsl"],
    "properties": {
      "scene_dsl": {
        "type": "object",
        "description": "完整的 Animation DSL 对象"
      },
      "save_to_file": {
        "type": "boolean",
        "default": true,
        "description": "是否保存 DSL 到文件"
      }
    }
  }
}
```

**返回值**:
```json
{
  "success": true,
  "scene_id": "problem_1_solution",
  "saved_path": "scenes/problem_1_solution.json",
  "validation": {
    "valid": true,
    "warnings": [],
    "estimated_duration": 12.5
  }
}
```

### Tool 2: `validate_scene`
**功能**: 验证场景 DSL

```json
{
  "name": "validate_scene",
  "description": "验证场景 DSL 是否符合 schema 并可渲染",
  "inputSchema": {
    "type": "object",
    "required": ["scene_id"],
    "properties": {
      "scene_id": {
        "type": "string"
      }
    }
  }
}
```

**返回值**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Animation 'anim_5' duration is very short (0.1s)"
  ],
  "estimated_duration": 12.5,
  "animation_count": 15,
  "phase_count": 4
}
```

### Tool 3: `render_scene`
**功能**: 渲染场景

```json
{
  "name": "render_scene",
  "description": "渲染场景为视频",
  "inputSchema": {
    "type": "object",
    "required": ["scene_id"],
    "properties": {
      "scene_id": {
        "type": "string"
      },
      "quality": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "default": "medium"
      },
      "format": {
        "type": "string",
        "enum": ["mp4", "webm", "gif"],
        "default": "mp4"
      },
      "save_python_code": {
        "type": "boolean",
        "default": false,
        "description": "是否保存生成的 Python 代码"
      }
    }
  }
}
```

**返回值**:
```json
{
  "success": true,
  "video_path": "output/image_1/image_1.mp4",
  "python_code_path": "output/image_1/image_1.py",
  "render_time": 18.2,
  "video_duration": 12.5,
  "file_size_mb": 3.4
}
```

### Tool 4: `batch_render`
**功能**: 批量渲染多个场景

```json
{
  "name": "batch_render",
  "description": "批量渲染多个场景",
  "inputSchema": {
    "type": "object",
    "required": ["scene_ids"],
    "properties": {
      "scene_ids": {
        "type": "array",
        "items": {"type": "string"}
      },
      "quality": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "default": "medium"
      },
      "parallel": {
        "type": "boolean",
        "default": false,
        "description": "是否并行渲染（实验性）"
      }
    }
  }
}
```

### Tool 5: `get_scene_info`
**功能**: 获取场景信息

```json
{
  "name": "get_scene_info",
  "description": "获取场景详细信息",
  "inputSchema": {
    "type": "object",
    "required": ["scene_id"],
    "properties": {
      "scene_id": {"type": "string"}
    }
  }
}
```

### Tool 6: `list_scenes`
**功能**: 列出所有场景

```json
{
  "name": "list_scenes",
  "description": "列出所有已创建的场景",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filter": {
        "type": "string",
        "enum": ["all", "rendered", "not_rendered"],
        "default": "all"
      }
    }
  }
}
```

---

## 五、核心代码实现示例

### 5.1 DSL 验证器

```python
# manim_mcp/dsl/validator.py
import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Tuple

class DSLValidator:
    def __init__(self):
        schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate(self, dsl: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        验证 DSL

        Returns:
            (valid, errors, warnings)
        """
        errors = []
        warnings = []

        # JSON Schema 验证
        try:
            jsonschema.validate(dsl, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation failed: {e.message}")
            return False, errors, warnings

        # 业务逻辑验证
        errors, warnings = self._validate_business_logic(dsl)

        return len(errors) == 0, errors, warnings

    def _validate_business_logic(self, dsl: Dict) -> Tuple[List[str], List[str]]:
        """验证业务逻辑"""
        errors = []
        warnings = []

        # 检查资源文件是否存在
        problem_image = dsl["metadata"]["problem_image"]
        if not Path(f"input/images/{problem_image}").exists():
            errors.append(f"Problem image not found: {problem_image}")

        # 检查动画时长
        for phase in dsl["timeline"]:
            for anim in phase["animations"]:
                if anim["duration"] < 0.1:
                    warnings.append(f"Very short animation: {anim['anim_id']}")

        # 检查并行动画
        all_anim_ids = set()
        for phase in dsl["timeline"]:
            for anim in phase["animations"]:
                all_anim_ids.add(anim["anim_id"])

        for phase in dsl["timeline"]:
            for anim in phase["animations"]:
                if "parallel" in anim:
                    for parallel_id in anim["parallel"]:
                        if parallel_id not in all_anim_ids:
                            errors.append(
                                f"Invalid parallel animation: {parallel_id}"
                            )

        return errors, warnings
```

### 5.2 DSL → Manim 转换器

```python
# manim_mcp/renderer/dsl_to_manim.py
from typing import Dict, Any
from manim import *

class DSLToManimConverter:
    def __init__(self, dsl: Dict):
        self.dsl = dsl
        self.mobjects = {}  # 存储创建的对象

    def generate_scene_code(self) -> str:
        """生成 Manim Scene 代码"""
        scene_id = self.dsl["scene_id"]
        class_name = self._to_class_name(scene_id)

        code = f"""
from manim import *
import os

class {class_name}(Scene):
    def construct(self):
        # 配置
        config.pixel_height = 1080
        config.pixel_width = 1920
        config.frame_rate = 60

        # 执行时间轴
{self._generate_timeline_code()}
"""
        return code

    def _generate_timeline_code(self) -> str:
        """生成时间轴代码"""
        code_lines = []

        for phase in self.dsl["timeline"]:
            code_lines.append(f"        # Phase: {phase['phase_id']}")

            for anim in phase["animations"]:
                anim_code = self._generate_animation_code(anim)
                code_lines.append(f"        {anim_code}")

            code_lines.append("")

        return "\n".join(code_lines)

    def _generate_animation_code(self, anim: Dict) -> str:
        """生成单个动画代码"""
        anim_type = anim["type"]
        target = anim["target"]
        params = anim.get("params", {})
        duration = anim.get("duration", 1.0)

        if anim_type == "write":
            if "latex" in params:
                obj = f"MathTex(r'{params['latex']}')"
            else:
                obj = f"Text('{params['text']}')"

            if "position" in params:
                obj += f".move_to({params['position']})"

            return f"self.play(Write({obj}), run_time={duration})"

        elif anim_type == "fade_in":
            # ... 实现其他动画类型
            pass

        # ... 更多动画类型
```

### 5.3 渲染执行器

```python
# manim_mcp/renderer/render_executor.py
import subprocess
from pathlib import Path
from typing import Dict, Any

class RenderExecutor:
    def __init__(self, scene_id: str, quality: str = "medium"):
        self.scene_id = scene_id
        self.quality = quality
        self.quality_flags = {
            "low": ["-ql", "--fps", "30"],
            "medium": ["-qm", "--fps", "60"],
            "high": ["-qh", "--fps", "60"]
        }

    def render(self, python_code: str) -> Dict[str, Any]:
        """执行渲染"""
        # 保存 Python 代码
        code_path = self._save_python_code(python_code)

        # 执行 manim 命令
        output_dir = Path("output") / self.scene_id
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "manim",
            *self.quality_flags[self.quality],
            "-o", f"{self.scene_id}.mp4",
            str(code_path),
            self._get_class_name()
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                video_path = self._find_video_file()
                return {
                    "success": True,
                    "video_path": str(video_path),
                    "stdout": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Render timeout (300s)"
            }
```

---

## 六、迁移步骤

### Phase 1: 基础设施（第1-2天）
✅ 创建新目录结构
✅ 实现 DSL schema 和 validator
✅ 创建基础 MCP tools 框架
✅ 编写测试用例

### Phase 2: 核心转换（第3-4天）
✅ 实现 DSL → Manim 转换器
✅ 实现固定 Scene 模板
✅ 实现渲染执行器
✅ 集成音频处理

### Phase 3: MCP 集成（第5天）
✅ 更新 server.py
✅ 实现所有 MCP tools
✅ 更新 prompts（让 LLM 生成 DSL）
✅ 端到端测试

### Phase 4: 向后兼容（第6天）
✅ 保留旧的 run.py（可选）
✅ 添加迁移工具（Python → DSL）
✅ 文档更新
✅ 性能优化

---

## 七、风险和缓解

### 风险1：DSL 表达能力不足
**缓解**:
- 先支持 80% 的常见场景
- DSL 支持 "custom_code" 字段用于特殊情况
- 可以逐步扩展 DSL

### 风险2：LLM 生成无效 DSL
**缓解**:
- 强大的 validation 在渲染前捕获错误
- 提供详细的错误信息和修复建议
- 提供 DSL 示例和最佳实践

### 风险3：迁移成本
**缓解**:
- 分阶段迁移，保留旧系统
- 提供自动转换工具
- 详细的迁移文档

---

## 八、预期效果

### 性能提升
- ✅ 验证时间：< 100ms（当前：需要运行才知道错误）
- ✅ 渲染稳定性：99%+（当前：约 80%）
- ✅ 批量处理：支持（当前：需要逐个处理）

### 维护性提升
- ✅ 模板修改：只需修改转换器（当前：需要重新生成所有代码）
- ✅ DSL 版本管理：支持（当前：无）
- ✅ 错误定位：精确到 animation（当前：Python 异常）

### 开发体验
- ✅ LLM 负担：大幅降低（只需生成 JSON）
- ✅ 可调试性：强（DSL 是人类可读的）
- ✅ 可复现性：100%（同样 DSL = 同样视频）

---

## 九、决策建议

### 立即开始重构 ✅

**理由**:
1. 架构设计成熟，风险可控
2. 当前系统已暴露明显问题（VGroup bug 等）
3. 后续需求（批量渲染）在新架构下更容易实现
4. 迁移成本可控（约 1 周）

### 重构优先级
1. **P0**: DSL schema + validator（必须先做）
2. **P0**: DSL → Manim 转换器（核心）
3. **P0**: create_scene, validate_scene, render_scene tools
4. **P1**: batch_render tool
5. **P2**: 迁移旧代码
6. **P3**: 性能优化和扩展功能

---

**总结**: 这不是一个"要不要做"的问题，而是"什么时候做"的问题。建议立即开始。
