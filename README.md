# claude-demo

数学解题系统 - 基于Claude API的MCP服务器项目

## Overview

这个项目是一个基于Claude API和MCP (Model Context Protocol)的数学解题系统。它能够自动处理数学题目图片，生成详细的中文解题步骤、Python代码和Manim动画代码。

## Prerequisites

在运行此项目之前，请确保已安装：

- Python 3.9+
- Anthropic API密钥（从 https://console.anthropic.com/ 获取）
- pip（Python包管理器）

## Installation

```bash
# 克隆仓库
git clone https://github.com/airplanecraft/claude-demo.git
cd claude-demo

# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑 .env 文件，添加你的 Anthropic API 密钥
```

## Running the Project

### 准备资源文件

1. **准备题目图片**：将数学题目图片放入 `input/images/` 目录

```bash
input/images/
├── image-1.png
├── image-2.png
└── image-n.png
```

2. **准备视频资源**（用于 Manim 动画）：将 logo 和封面图片放入 `assets/` 目录

```bash
assets/
├── logo.png      # 视频左上角的 Logo
└── cover.png     # 封面背景图
```

详细说明请查看 `assets/README.md`

### 运行解题程序

```bash
cd claude-demo
python run.py
```

程序会自动：
1. 读取 `input/images/` 目录下的所有图片
2. 逐张调用Claude API分析题目
3. 生成解题步骤和代码
4. 保存到 `output/` 目录

### 运行MCP服务器（可选）

```bash
python server.py
```

## Usage

### 输出结果

每道题目的解答会保存在独立的目录中：

```
output/
├── image-1/
│   ├── image-1.md    # 中文解题步骤
│   └── image-1.py    # Python代码（包含解题代码和Manim动画）
├── image-2/
│   ├── image-2.md
│   └── image-2.py
└── ...
```

### 输出内容包括

1. **Markdown文件（.md）**：
   - 题目分析
   - 解题思路
   - 完整的解题步骤
   - Python代码和Manim代码

2. **Python文件（.py）**：
   - 可运行的解题代码
   - Manim动画生成代码

## Configuration

### 环境变量配置

在项目根目录创建 `.env` 文件：

```bash
# Anthropic API Key
ANTHROPIC_API_KEY=your_api_key_here
```

### 提示词配置

编辑 `input/prompt.txt` 来自定义解题提示词。默认提示词要求：
- 详细的中文解题步骤
- Python解题代码
- Manim动画代码

## Project Structure

```
claude-demo/
├── assets/                 # 视频资源目录
│   ├── README.md          # 资源说明文档
│   ├── logo.png           # Logo 图片（需要您提供）
│   └── cover.png          # 封面背景图（需要您提供）
├── input/                  # 输入目录
│   ├── images/            # 题目图片
│   │   ├── image-1.png
│   │   └── image-n.png
│   └── prompt.txt         # 解题提示词
├── output/                # 输出目录（自动生成）
│   ├── image-1/
│   │   ├── image-1.md    # 解题步骤
│   │   └── image-1.py    # Python代码
│   └── ...
├── prompts/               # 模块化提示词系统
│   ├── README.md
│   ├── stage0_master.txt
│   ├── stage1_visual_strategy.txt
│   ├── stage2_math_solution.txt
│   └── stage3_manim.txt
├── templates/             # 代码模板
│   ├── manim_template.py  # Manim 动画模板
│   └── jsxgraph_template.html
├── tools.py               # 工具函数（创建目录、写文件等）
├── server.py              # MCP服务器（工具注册）
├── run.py                 # 主程序（调用Claude API）
├── mcp.json              # MCP配置
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
└── .gitignore            # Git忽略文件配置
```

## Features

- ✅ 自动处理多张题目图片
- ✅ 调用Claude 4 Sonnet生成高质量解答
- ✅ 生成详细的中文解题步骤（Markdown格式）
- ✅ 生成可运行的Python代码
- ✅ 支持Manim动画代码生成
- ✅ MCP服务器架构，可集成到其他工具
- ✅ 结果按题目独立保存，便于管理

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Contact

For questions or support, please [contact information or link to issues page].
