#!/usr/bin/env python3
"""
数学解题主程序
逐张处理题目图片，调用Claude API生成解题方案
"""

import os
import sys
import base64
from pathlib import Path
from typing import Dict, Any
import anthropic
from dotenv import load_dotenv

# 导入工具函数
from tools import (
    get_image_list,
    read_prompt,
    save_solution,
    create_output_directory
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


def solve_math_problem(client: anthropic.Anthropic, image_path: str, prompt: str) -> Dict[str, Any]:
    """
    调用Claude API解决数学题目

    Args:
        client: Anthropic客户端
        image_path: 题目图片路径
        prompt: 解题提示词

    Returns:
        包含解题结果的字典
    """
    print(f"\n处理图片: {Path(image_path).name}")
    print("=" * 60)

    try:
        # 编码图片
        image_data = encode_image(image_path)
        media_type = get_image_media_type(image_path)

        # 调用Claude API
        print("正在调用 Claude 4 Sonnet API...")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
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
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # 提取响应内容
        response_text = message.content[0].text

        # 解析响应，分离Markdown和Python代码
        markdown_content, python_code = parse_response(response_text)

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


def parse_response(response: str) -> tuple[str, str]:
    """
    解析Claude响应，分离Markdown解题步骤和Python代码

    Args:
        response: Claude的完整响应

    Returns:
        (markdown_content, python_code) 元组
    """
    # 查找Python代码块
    python_code = ""
    markdown_content = response

    # 提取所有Python代码块
    import re
    python_pattern = r'```python\n(.*?)```'
    python_matches = re.findall(python_pattern, response, re.DOTALL)

    if python_matches:
        # 合并所有Python代码
        python_code = "\n\n".join(python_matches)

    # Markdown内容就是完整响应
    # （包含代码块，便于查看完整解题过程）
    markdown_content = response

    return markdown_content, python_code


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
    print(prompt)
    print("-" * 60)

    # 逐张处理图片
    images_dir = Path(__file__).parent / "input" / "images"
    successful = 0
    failed = 0

    for i, image_name in enumerate(images, 1):
        print(f"\n\n进度: {i}/{len(images)}")
        image_path = images_dir / image_name

        # 调用Claude解题
        result = solve_math_problem(client, str(image_path), prompt)

        if result["success"]:
            # 保存解题结果
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
    print("数学解题系统")
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
