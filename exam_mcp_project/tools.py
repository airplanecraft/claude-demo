"""
MCP工具函数模块
提供创建目录、写入文件等功能
"""

import os
from pathlib import Path
from typing import Dict, Any


def create_output_directory(image_name: str) -> str:
    """
    为指定图片创建输出目录

    Args:
        image_name: 图片名称（如 image-1.png）

    Returns:
        创建的目录路径
    """
    # 获取不带扩展名的文件名
    base_name = Path(image_name).stem

    # 创建输出目录路径
    output_dir = Path(__file__).parent / "output" / base_name

    # 创建目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)

    return str(output_dir)


def write_solution_file(image_name: str, content: str, file_type: str) -> Dict[str, Any]:
    """
    将解题内容写入文件

    Args:
        image_name: 图片名称（如 image-1.png）
        content: 文件内容
        file_type: 文件类型（'md' 或 'py'）

    Returns:
        包含状态和文件路径的字典
    """
    try:
        # 创建输出目录
        output_dir = create_output_directory(image_name)

        # 获取不带扩展名的文件名
        base_name = Path(image_name).stem

        # 构建文件路径
        file_path = Path(output_dir) / f"{base_name}.{file_type}"

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "file_path": str(file_path),
            "message": f"成功写入 {file_type} 文件"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"写入 {file_type} 文件失败"
        }


def get_image_list() -> list:
    """
    获取input/images目录下所有图片文件列表

    Returns:
        图片文件名列表
    """
    images_dir = Path(__file__).parent / "input" / "images"

    if not images_dir.exists():
        return []

    # 获取所有图片文件（支持常见图片格式）
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}
    images = [
        f.name for f in images_dir.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    # 按文件名排序
    images.sort()

    return images


def read_prompt() -> str:
    """
    读取提示词文件

    Returns:
        提示词内容
    """
    prompt_file = Path(__file__).parent / "input" / "prompt.txt"

    if not prompt_file.exists():
        return "请分析这道数学题目并提供详细的解题步骤。"

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


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


# MCP工具定义
MCP_TOOLS = [
    {
        "name": "create_output_directory",
        "description": "为指定的题目图片创建输出目录",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_name": {
                    "type": "string",
                    "description": "图片文件名（如 image-1.png）"
                }
            },
            "required": ["image_name"]
        }
    },
    {
        "name": "write_solution_file",
        "description": "将解题内容写入指定类型的文件",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_name": {
                    "type": "string",
                    "description": "图片文件名"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容"
                },
                "file_type": {
                    "type": "string",
                    "enum": ["md", "py"],
                    "description": "文件类型：md 或 py"
                }
            },
            "required": ["image_name", "content", "file_type"]
        }
    },
    {
        "name": "save_solution",
        "description": "保存完整的解题方案（包括Markdown和Python代码）",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_name": {
                    "type": "string",
                    "description": "图片文件名"
                },
                "markdown_content": {
                    "type": "string",
                    "description": "Markdown格式的解题步骤"
                },
                "python_code": {
                    "type": "string",
                    "description": "Python解题代码"
                }
            },
            "required": ["image_name", "markdown_content", "python_code"]
        }
    },
    {
        "name": "get_image_list",
        "description": "获取所有待处理的题目图片列表",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "read_prompt",
        "description": "读取解题提示词",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]
