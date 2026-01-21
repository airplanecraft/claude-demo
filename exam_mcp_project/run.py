#!/usr/bin/env python3
"""
数学解题主程序
逐张处理题目图片，调用Claude API生成解题方案
"""

import os
import sys
import base64
import re
from pathlib import Path
from typing import Dict, Any
import anthropic
from dotenv import load_dotenv

# 导入工具函数
from tools import (
    get_image_list,
    read_prompt,
    create_output_directory,
    write_solution_file
)

# 加载环境变量
load_dotenv()


def encode_image(image_path: str) -> str:
    """
    将图片编码为base64格式

    Args:
        image_path: 图片文件路径

    Returns:
        base64编码的图片数据
    """
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


def get_image_media_type(image_path: str) -> str:
    """
    根据文件扩展名获取媒体类型

    Args:
        image_path: 图片文件路径

    Returns:
        媒体类型字符串
    """
    ext = Path(image_path).suffix.lower()
    media_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    return media_types.get(ext, 'image/png')


def get_question_number(image_name: str) -> str:
    """
    从图片文件名提取题号

    Args:
        image_name: 图片文件名（如 image-1.png）

    Returns:
        题号字符串（如 "1"）
    """
    # 尝试从文件名中提取数字
    match = re.search(r'(\d+)', Path(image_name).stem)
    if match:
        return match.group(1)
    return "1"  # 默认题号


def load_templates() -> Dict[str, str]:
    """
    加载 Manim 和 JSXGraph 模板文件

    Returns:
        包含模板内容的字典
    """
    templates_dir = Path(__file__).parent / "templates"

    templates = {}

    # 读取 Manim 模板
    manim_template_path = templates_dir / "manim_template.py"
    if manim_template_path.exists():
        with open(manim_template_path, 'r', encoding='utf-8') as f:
            templates['manim'] = f.read()
    else:
        templates['manim'] = ""

    # 读取 JSXGraph 模板
    jsx_template_path = templates_dir / "jsxgraph_template.html"
    if jsx_template_path.exists():
        with open(jsx_template_path, 'r', encoding='utf-8') as f:
            templates['jsxgraph'] = f.read()
    else:
        templates['jsxgraph'] = ""

    return templates


def build_full_prompt(base_prompt: str, image_name: str, templates: Dict[str, str]) -> str:
    """
    构建包含模板内容的完整 prompt

    Args:
        base_prompt: 基础 prompt
        image_name: 图片文件名
        templates: 模板字典

    Returns:
        完整的 prompt
    """
    question_number = get_question_number(image_name)

    full_prompt = f"""{base_prompt}

# 题号信息
**当前题号**: {question_number}
**图片文件名**: image_{question_number}.png

---

# Manim 模板代码（完整）
请严格基于以下模板生成 Manim 代码。模板中已经包含了所有必要的配置、颜色、布局、封面、Logo、原题显示、动画讲解、声音、位置、答案和解题步骤的展示功能。

**您只需要**：
1. 将类名 `SolutionVideoTEMPLATE` 改为 `SolutionVideo{question_number}`
2. 将 `image_REPLACE_WITH_NUMBER.png` 改为 `image_{question_number}.png`
3. 填充 `problem_data` 和 `steps_data` 数据
4. 实现 `play_visual_reasoning(self, steps)` 方法中的动画逻辑

**完整模板**：
```python
{templates.get('manim', '# Manim 模板未找到')}
```

---

# JSXGraph 模板代码（完整）
请严格基于以下 HTML 模板生成交互代码。

**您只需要**：
1. 将 `REPLACE_WITH_CORRECT_FILENAME.png` 改为 `image_{question_number}.png`
2. 在 `<script>` 标签中实现交互逻辑
3. 保持所有中文文本不变

**完整模板**：
```html
{templates.get('jsxgraph', '<!-- JSXGraph 模板未找到 -->')}
```

---

# 重要提醒
1. **必须使用上述模板**：不要从头编写代码，而是基于模板修改
2. **保留所有模板功能**：颜色、布局、TTS、封面等所有功能都已在模板中定义
3. **只修改必要部分**：类名、文件名、数据定义、动画逻辑
4. **严格遵循布局规范**：动画必须在 POS_ANIM_CENTER 位置，不得遮挡文字区域
"""

    return full_prompt


def parse_response(response: str) -> tuple[str, str, str]:
    """
    解析Claude响应，分离Markdown解题步骤、Python代码和HTML代码

    Args:
        response: Claude的完整响应

    Returns:
        (markdown_content, python_code, html_code) 元组
    """
    # 查找Python代码块
    python_code = ""
    html_code = ""

    # 提取 Python 代码块（优先提取最长的）
    python_pattern = r'```python\n(.*?)```'
    python_matches = re.findall(python_pattern, response, re.DOTALL)

    if python_matches:
        # 选择最长的 Python 代码块（通常是完整的 Manim 代码）
        python_code = max(python_matches, key=len)

    # 如果没有找到 Python 代码块，尝试查找包含 "SolutionVideo" 的代码
    if not python_code:
        # 尝试查找任何包含 class SolutionVideo 的代码块
        solution_pattern = r'(import.*?class SolutionVideo.*?if __name__.*?main\(\))'
        solution_match = re.search(solution_pattern, response, re.DOTALL)
        if solution_match:
            python_code = solution_match.group(1)

    # 提取 HTML 代码块（JSXGraph）
    html_pattern = r'```html\n(.*?)```'
    html_matches = re.findall(html_pattern, response, re.DOTALL)

    if html_matches:
        # 选择最长的 HTML 代码块（通常是完整的 JSXGraph 代码）
        html_code = max(html_matches, key=len)

    # 如果没有找到标准的 HTML 代码块，尝试查找包含 DOCTYPE 的 HTML
    if not html_code:
        doctype_pattern = r'(<!DOCTYPE html>.*?</html>)'
        doctype_match = re.search(doctype_pattern, response, re.DOTALL | re.IGNORECASE)
        if doctype_match:
            html_code = doctype_match.group(1)

    # Markdown内容就是完整响应
    # （包含代码块，便于查看完整解题过程）
    markdown_content = response

    return markdown_content, python_code, html_code


def save_solution(image_name: str, markdown_content: str, python_code: str, html_code: str) -> Dict[str, Any]:
    """
    保存完整的解题方案（Markdown + Python代码 + HTML代码）

    Args:
        image_name: 图片名称
        markdown_content: Markdown格式的解题步骤
        python_code: Python代码
        html_code: HTML交互代码

    Returns:
        保存结果
    """
    results = {
        "image_name": image_name,
        "files_created": []
    }

    # 创建输出目录
    create_output_directory(image_name)

    # 保存Markdown文件
    md_result = write_solution_file(image_name, markdown_content, 'md')
    if md_result["success"]:
        results["files_created"].append(md_result["file_path"])

    # 保存Python文件
    py_result = write_solution_file(image_name, python_code, 'py')
    if py_result["success"]:
        results["files_created"].append(py_result["file_path"])

    # 保存HTML文件（如果有）
    if html_code:
        html_result = write_solution_file(image_name, html_code, 'html')
        if html_result["success"]:
            results["files_created"].append(html_result["file_path"])

    results["success"] = md_result["success"] and py_result["success"]

    return results


def solve_math_problem(client: anthropic.Anthropic, image_path: str, prompt: str, templates: Dict[str, str]) -> Dict[str, Any]:
    """
    调用Claude API解决数学题目

    Args:
        client: Anthropic客户端
        image_path: 题目图片路径
        prompt: 解题提示词
        templates: 模板字典

    Returns:
        包含解题结果的字典
    """
    image_name = Path(image_path).name
    print(f"\n处理图片: {image_name}")
    print("=" * 60)

    try:
        # 编码图片
        image_data = encode_image(image_path)
        media_type = get_image_media_type(image_path)

        # 构建包含模板的完整 prompt
        full_prompt = build_full_prompt(prompt, image_name, templates)

        print(f"题号: {get_question_number(image_name)}")

        # 调用Claude API
        print("正在调用 Claude 4 Sonnet API（包含完整模板）...")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,  # 增加 token 限制以容纳更长的响应
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": full_prompt
                        }
                    ],
                }
            ],
        )

        # 提取响应内容
        response_text = message.content[0].text

        # 解析响应，分离Markdown、Python代码和HTML代码
        markdown_content, python_code, html_code = parse_response(response_text)

        return {
            "success": True,
            "markdown": markdown_content,
            "python": python_code,
            "html": html_code,
            "full_response": response_text
        }

    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def process_all_images():
    """
    处理所有题目图片
    """
    # 检查API密钥
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 ANTHROPIC_API_KEY 环境变量")
        print("请在项目根目录创建 .env 文件并添加:")
        print("ANTHROPIC_API_KEY=your_api_key_here")
        return

    # 创建Anthropic客户端
    client = anthropic.Anthropic(api_key=api_key)

    # 获取图片列表
    images = get_image_list()

    if not images:
        print("❌ 未找到任何图片文件")
        print(f"请将题目图片放入: {Path(__file__).parent / 'input' / 'images'}")
        return

    print(f"\n找到 {len(images)} 张题目图片")
    print("=" * 60)

    # 读取提示词
    prompt = read_prompt()
    print(f"\n使用提示词:")
    print("-" * 60)
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    print("-" * 60)

    # 加载模板
    print("\n加载模板文件...")
    templates = load_templates()
    if templates.get('manim'):
        print(f"✅ Manim 模板已加载 ({len(templates['manim'])} 字符)")
    else:
        print("⚠️  警告: Manim 模板未找到")

    if templates.get('jsxgraph'):
        print(f"✅ JSXGraph 模板已加载 ({len(templates['jsxgraph'])} 字符)")
    else:
        print("⚠️  警告: JSXGraph 模板未找到")

    # 逐张处理图片
    images_dir = Path(__file__).parent / "input" / "images"
    successful = 0
    failed = 0

    for i, image_name in enumerate(images, 1):
        print(f"\n\n进度: {i}/{len(images)}")
        image_path = images_dir / image_name

        # 调用Claude解题（包含模板）
        result = solve_math_problem(client, str(image_path), prompt, templates)

        if result["success"]:
            # 保存解题结果（包括HTML）
            save_result = save_solution(
                image_name,
                result["markdown"],
                result["python"],
                result.get("html", "")
            )

            if save_result["success"]:
                print(f"✅ 成功保存解题结果:")
                for file_path in save_result["files_created"]:
                    print(f"   - {file_path}")
                successful += 1
            else:
                print(f"❌ 保存失败")
                failed += 1
        else:
            print(f"❌ 解题失败: {result.get('error', '未知错误')}")
            failed += 1

    # 打印总结
    print("\n" + "=" * 60)
    print(f"处理完成!")
    print(f"✅ 成功: {successful}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {len(images)}")
    print("=" * 60)


def main():
    """
    主函数
    """
    print("=" * 60)
    print("数学解题系统 - 基于模板的代码生成")
    print("=" * 60)

    try:
        process_all_images()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
