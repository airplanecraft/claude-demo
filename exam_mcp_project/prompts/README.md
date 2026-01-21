# 模块化 Prompt 系统说明

## 概述

本项目采用模块化的 prompt 设计，将复杂的数学解题任务分解为四个独立阶段，每个阶段都有详细的指导文档。

## 文件结构

```
prompts/
├── README.md                      # 本文件
├── stage0_master.txt              # 主 prompt（概览）
├── stage1_visual_strategy.txt     # 第一阶段：视觉策略决策
├── stage2_math_solution.txt       # 第二阶段：数学求解
├── stage3_manim.txt              # 第三阶段：Manim 视频代码生成
└── stage4_jsxgraph.txt           # 第四阶段：JSXGraph 交互代码生成
```

## 四个阶段说明

### 第一阶段：视觉策略决策
**文件**: `stage1_visual_strategy.txt`

**目的**: 在编写代码前，分析题目类型并选择最合适的视觉呈现策略。

**内容**:
- 题目分类（找规律/几何/逻辑/代数）
- Manim 动画策略
- JSXGraph 交互策略
- 策略选择理由

### 第二阶段：数学求解
**文件**: `stage2_math_solution.txt`

**目的**: 给出详细的、分步骤的解题逻辑。

**内容**:
- 题目分析
- 解题思路
- 详细步骤（每步包含推导、关键点、结果）
- 答案验证
- 答案总结

**重要**: 后续的 Manim 动画和 JSXGraph 交互都基于此步骤。

### 第三阶段：Manim 视频代码生成
**文件**: `stage3_manim.txt`

**目的**: 基于模板生成完整的 Manim 动画代码。

**核心要求**:
- 高清画质 (1080p @ 60fps)
- 布局防重叠（动画在右上，文字在右下）
- 文件名规则 (`image_{题号}.png`)
- 类名规则 (`SolutionVideo{题号}`)

**模板位置**: `../templates/manim_template.py`

### 第四阶段：JSXGraph 交互代码生成
**文件**: `stage4_jsxgraph.txt`

**目的**: 基于模板生成完整的 HTML 交互代码。

**核心要求**:
- 正确的图片文件名
- 独立可运行的 HTML
- 基于模板结构
- 保持中文文本

**模板位置**: `../templates/jsxgraph_template.html`

## 使用方法

### 方式一：使用主 prompt（推荐）

在 `input/prompt.txt` 中已经整合了所有阶段的概要，并引用了详细文档。

运行 `run.py` 时，Claude 会读取主 prompt 并自动处理所有四个阶段。

### 方式二：单独使用某个阶段

如果只需要某个特定阶段，可以单独读取对应的文件：

```python
# 示例：只需要视觉策略分析
with open('prompts/stage1_visual_strategy.txt', 'r') as f:
    strategy_prompt = f.read()
```

### 方式三：自定义组合

可以根据需要组合不同阶段的 prompt：

```python
# 示例：只需要数学求解和 Manim 代码
math_prompt = read_file('prompts/stage2_math_solution.txt')
manim_prompt = read_file('prompts/stage3_manim.txt')
combined_prompt = f"{math_prompt}\n\n{manim_prompt}"
```

## 修改 Prompt

### 修改策略

如果要调整某个阶段的指导方针：

1. 编辑对应的 `stageN_*.txt` 文件
2. 保存修改
3. 下次运行时会自动使用新的 prompt

### 修改模板

模板文件位于 `../templates/` 目录：

- `manim_template.py` - Manim 代码模板
- `jsxgraph_template.html` - JSXGraph HTML 模板

修改模板后，在 prompt 中引用的模板会自动更新。

## 最佳实践

### 1. 保持阶段独立性
每个阶段应该能够独立理解和执行，但最终结果要相互关联。

### 2. 详细的示例
在每个阶段的 prompt 中提供具体示例，帮助 AI 理解期望的输出格式。

### 3. 明确的约束
使用"铁律"、"CRITICAL"等标记强调不可违反的规则。

### 4. 模板引用
通过引用模板文件而不是内联完整代码，保持 prompt 简洁。

## 优势

### ✅ 可维护性
- 每个阶段独立管理
- 修改某个阶段不影响其他部分
- 代码模板与 prompt 分离

### ✅ 可扩展性
- 容易添加新的阶段
- 可以创建不同的 prompt 组合
- 支持多种题目类型的定制

### ✅ 可读性
- 结构清晰，层次分明
- 文档化的指导说明
- 便于团队协作

### ✅ 复用性
- 模板可以在多个项目中复用
- Prompt 可以针对不同题型定制
- 减少重复编写

## 常见问题

### Q: 如何添加新的阶段？

1. 创建新的 `stageN_*.txt` 文件
2. 在 `input/prompt.txt` 中添加引用
3. 必要时创建对应的模板文件

### Q: 如何针对特定题型定制？

可以创建题型专用的 prompt 变体：
- `stage1_visual_strategy_geometry.txt`
- `stage1_visual_strategy_algebra.txt`

然后在主 prompt 中根据题型选择加载。

### Q: 模板文件过大怎么办？

可以将模板进一步模块化：
- 将配置和代码分离
- 创建多个子模板
- 使用代码注释标记可替换部分

## 贡献

如果您改进了 prompt 或模板，欢迎分享您的修改！

## 相关文档

- 项目主 README: `../README.md`
- Manim 模板: `../templates/manim_template.py`
- JSXGraph 模板: `../templates/jsxgraph_template.html`
