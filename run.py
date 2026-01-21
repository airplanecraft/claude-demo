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
    加载 Manim 模板文件（移除 JSXGraph 以减少请求大小）

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

    # 不再加载 JSXGraph 模板以减少请求大小
    # jsx_template_path = templates_dir / "jsxgraph_template.html"

    return templates


def build_full_prompt(base_prompt: str, image_name: str, templates: Dict[str, str]) -> str:
    """
    构建包含模板指引的完整 prompt（轻量级版本，避免 Connection error）

    Args:
        base_prompt: 基础 prompt
        image_name: 图片文件名
        templates: 模板字典（不再嵌入完整代码）

    Returns:
        完整的 prompt
    """
    question_number = get_question_number(image_name)

    # 轻量级 prompt：不嵌入完整模板，只提供结构要求
    full_prompt = f"""{base_prompt}

# 题号信息
**当前题号**: {question_number}
**图片文件名**: image_{question_number}.png

---

# Manim 代码生成要求（基于模板 templates/manim_template.py）

## 必须遵循的模板结构

### 1. 全局配置（必须包含）
```python
import os
import asyncio
import edge_tts
from manim import *

config.disable_caching = True
config.pixel_height = 1080
config.pixel_width = 1920
config.frame_rate = 60

# LaTeX 中文配置
my_tex_template = TexTemplate()
my_tex_template.tex_compiler = "xelatex"
my_tex_template.output_format = ".xdv"
my_tex_template.add_to_preamble(r"\\usepackage[fontset=mac]{{ctex}}")
config.tex_template = my_tex_template
```

### 2. 颜色和常量定义（必须包含）
```python
COLOR_BG = "#415049"
COLOR_HIGHLIGHT = "#FFD700"
FONT_NAME = "Heiti SC"
POS_ANIM_CENTER = [3.5, 2.0, 0]  # 动画区域中心（右上）
POS_TEXT_BASE = [3.5, -3.0, 0]   # 文字区域（右下）
# ... 其他颜色和布局常量
```

### 3. 辅助函数（必须包含）
- `generate_audio_file()` - TTS 语音生成
- `prepare_all_audio()` - 准备所有音频

### 4. Scene 类结构
```python
class SolutionVideo{question_number}(Scene):
    def construct(self):
        self.problem_image_name = os.path.join(PROBLEM_IMAGE_DIR, "image_{question_number}.png")
        self.question_label_text = "Q"
        self.question_label_color = "#FFD700"
        self.text_lines_group = VGroup()

        # 定义数据
        problem_data = {{"speech": "..."}}
        steps_data = [{{"text": "...", "math": "...", "speech": "..."}}, ...]
        final_answer_text = "答案：..."

        prepare_all_audio(problem_data, steps_data)

        # 执行流程（请勿修改）
        cover_objects = self.show_cover_phase()
        video_img_obj = self.transition_to_solution_phase(cover_objects)
        self.safe_read_problem(problem_data, video_img_obj)
        self.play_visual_reasoning(steps_data)
        self.show_final_answer(final_answer_text)

    def play_visual_reasoning(self, steps):
        # ⭐ 您只需要在这里编写动画逻辑！
        # 所有动画对象必须使用 .move_to(POS_ANIM_CENTER) 定位
        for i, step in enumerate(steps):
            self.play_rolling_step_text(step)
            # 在这里添加您的动画代码
            # 例如：
            # if i == 0:
            #     circle = Circle().move_to(POS_ANIM_CENTER)
            #     self.play(Create(circle))

    # ⚠️ 以下方法必须从模板原样复制，不要修改任何内容：
    # - play_rolling_step_text(self, step)
    # - show_cover_phase(self)
    # - transition_to_solution_phase(self, cover_objects)
    # - safe_read_problem(self, problem_data, video_img_obj)
    # - show_final_answer(self, answer_text)
```

## 关键要求
1. **类名**: `SolutionVideo{question_number}`
2. **图片文件名**: 使用 `os.path.join(PROBLEM_IMAGE_DIR, "image_{question_number}.png")`
3. **布局规范**: 动画在 `POS_ANIM_CENTER`，不遮挡下方文字
4. **包含所有辅助方法**: 从模板原样复制所有辅助方法
5. **TTS 支持**: 使用 edge_tts 和 Mac say 命令

---

# ⚠️ 严重警告 - 请务必遵守！

## 不要修改以下辅助方法：
模板中的以下方法已经完整实现，包含复杂的布局和音频处理逻辑。
如果修改这些方法会导致：
- 视频布局错乱（原题和动画重叠）
- 运行时错误（VGroup 类型错误）
- 音频播放问题（声音重叠或截断）

**必须从模板原样复制的方法：**
1. `show_cover_phase()` - 封面显示
2. `transition_to_solution_phase()` - 过渡到解题界面
3. `safe_read_problem()` - 读题
4. `play_rolling_step_text()` - 显示解题步骤（三行滚动）
5. `show_final_answer()` - 显示最终答案

## 您只需要做的事情：
✅ 在 `play_visual_reasoning()` 方法中编写动画代码
✅ 为每个步骤调用 `self.play_rolling_step_text(step)`
✅ 使用 `.move_to(POS_ANIM_CENTER)` 定位动画对象
✅ 填充 problem_data, steps_data, final_answer_text 数据

## 不要做的事情：
❌ 不要重写 show_cover_phase() 方法
❌ 不要修改 play_rolling_step_text() 的实现
❌ 不要更改辅助方法的返回值类型
❌ 不要在辅助方法中使用 VGroup 包含 ImageMobject

---

# 代码生成要求
- 生成**完整可运行**的 Manim 代码
- 从模板**原样复制**所有辅助方法和辅助函数
- 严格遵循布局和文件名规范
- 输出完整的 Python 代码，包含所有必要的 imports、配置和方法
"""

    return full_prompt


def ensure_complete_manim_code(python_code: str, template_code: str) -> str:
    """
    确保生成的 Manim 代码包含所有必要的辅助方法
    如果缺少，从模板中注入

    Args:
        python_code: Claude 生成的代码
        template_code: 完整的模板代码

    Returns:
        完整的代码
    """
    # 检查是否包含关键的辅助方法
    required_methods = [
        'def generate_audio_file(',
        'def prepare_all_audio(',
        'def play_rolling_step_text(',
        'def show_cover_phase(',
        'def transition_to_solution_phase(',
        'def safe_read_problem(',
        'def show_final_answer('
    ]

    missing_methods = [m for m in required_methods if m not in python_code]

    if not missing_methods:
        # 代码已完整
        return python_code

    # 代码不完整，需要从模板中提取并合并
    print(f"  ⚠️  检测到生成的代码缺少 {len(missing_methods)} 个辅助方法，正在从模板补充...")

    # 提取模板中的 SolutionVideoTEMPLATE 类
    template_class_pattern = r'(class SolutionVideoTEMPLATE\(Scene\):.*?)(?=\n\nclass |\Z)'
    template_class_match = re.search(template_class_pattern, template_code, re.DOTALL)

    if not template_class_match:
        print("  ⚠️  警告：无法从模板中提取类定义")
        return python_code

    template_class_code = template_class_match.group(1)

    # 提取生成代码中的 construct 和 play_visual_reasoning 方法
    construct_pattern = r'(    def construct\(self\):.*?)(?=\n    def |\Z)'
    construct_match = re.search(construct_pattern, python_code, re.DOTALL)

    visual_pattern = r'(    def play_visual_reasoning\(self, steps\):.*?)(?=\n    def |\Z)'
    visual_match = re.search(visual_pattern, python_code, re.DOTALL)

    if construct_match and visual_match:
        # 将生成的方法替换到模板中
        result_code = template_class_code
        result_code = re.sub(
            r'    def construct\(self\):.*?(?=\n    def )',
            construct_match.group(1) + '\n',
            result_code,
            flags=re.DOTALL
        )
        result_code = re.sub(
            r'    def play_visual_reasoning\(self, steps\):.*?(?=\n    def )',
            visual_match.group(1) + '\n',
            result_code,
            flags=re.DOTALL
        )

        # 提取模板头部（imports 和全局配置）
        template_header_pattern = r'^(.*?)(?=class SolutionVideoTEMPLATE)'
        template_header_match = re.search(template_header_pattern, template_code, re.DOTALL)
        template_header = template_header_match.group(1) if template_header_match else ""

        # 组合完整代码
        return template_header + result_code
    else:
        print("  ⚠️  警告：无法提取生成代码的方法，返回原始代码")
        return python_code


def parse_response(response: str, template_code: str = "") -> tuple[str, str]:
    """
    解析Claude响应，分离Markdown解题步骤和Python代码（移除HTML以减少复杂度）

    Args:
        response: Claude的完整响应
        template_code: Manim 模板代码（用于补全）

    Returns:
        (markdown_content, python_code) 元组
    """
    # 查找Python代码块
    python_code = ""

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

    # 确保代码完整（包含所有辅助方法）
    if python_code and template_code:
        python_code = ensure_complete_manim_code(python_code, template_code)

    # Markdown内容就是完整响应
    # （包含代码块，便于查看完整解题过程）
    markdown_content = response

    return markdown_content, python_code


def save_solution(image_name: str, markdown_content: str, python_code: str) -> Dict[str, Any]:
    """
    保存完整的解题方案（Markdown + Python代码）

    Args:
        image_name: 图片名称
        markdown_content: Markdown格式的解题步骤
        python_code: Python代码

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
        print("正在调用 Claude 4 Sonnet API（轻量级 prompt，避免 Connection error）...")
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

        # 解析响应，分离Markdown和Python代码（移除HTML以减少复杂度）
        # 传递模板代码以便后处理时补全缺失的辅助方法
        markdown_content, python_code = parse_response(
            response_text,
            templates.get('manim', '')
        )

        return {
            "success": True,
            "markdown": markdown_content,
            "python": python_code,
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

    # 加载模板（仅 Manim，移除 JSXGraph）
    print("\n加载 Manim 模板文件...")
    templates = load_templates()
    if templates.get('manim'):
        print(f"✅ Manim 模板已加载 ({len(templates['manim'])} 字符)")
    else:
        print("⚠️  警告: Manim 模板未找到")

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
            # 保存解题结果（仅 Markdown 和 Python）
            save_result = save_solution(
                image_name,
                result["markdown"],
                result["python"]
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
    print("数学解题系统 - 智能模板代码生成")
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
