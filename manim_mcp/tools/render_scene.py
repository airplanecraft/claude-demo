"""
Render Scene Tool
渲染 Animation DSL 场景为视频
"""

import json
from pathlib import Path
from typing import Dict, Any
from ..renderer.render_executor import render_scene_from_file


# Tool Schema Definition
TOOL_SCHEMA = {
    "name": "render_scene",
    "description": "渲染场景为视频。支持多种质量预设，可选保存生成的 Python 代码。",
    "inputSchema": {
        "type": "object",
        "required": ["scene_id"],
        "properties": {
            "scene_id": {
                "type": "string",
                "description": "场景 ID（例如: problem_1_solution）"
            },
            "quality": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "default": "medium",
                "description": "渲染质量: low (480p@30fps), medium (720p@60fps), high (1080p@60fps)"
            },
            "save_python_code": {
                "type": "boolean",
                "default": True,
                "description": "是否保存生成的 Python 代码（默认: true）"
            },
            "scenes_dir": {
                "type": "string",
                "default": "scenes",
                "description": "场景文件所在目录（默认: scenes）"
            }
        }
    }
}


def render_scene(
    scene_id: str,
    quality: str = "medium",
    save_python_code: bool = True,
    scenes_dir: str = "scenes"
) -> Dict[str, Any]:
    """
    渲染场景

    Args:
        scene_id: 场景 ID
        quality: 渲染质量 (low/medium/high)
        save_python_code: 是否保存 Python 代码
        scenes_dir: 场景目录

    Returns:
        渲染结果字典
    """
    result = {
        "success": False,
        "scene_id": scene_id,
        "dsl_file": None,
        "video_path": None,
        "python_code_path": None,
        "render_time": 0.0,
        "file_size_mb": 0.0,
        "error": None
    }

    try:
        # 1. 查找场景文件
        dsl_file = Path(scenes_dir) / f"{scene_id}.json"

        if not dsl_file.exists():
            result["error"] = f"Scene file not found: {dsl_file}"
            return result

        result["dsl_file"] = str(dsl_file)

        # 2. 执行渲染
        render_result = render_scene_from_file(
            str(dsl_file),
            quality=quality,
            save_python_code=save_python_code
        )

        # 3. 处理结果
        if render_result.success:
            result["success"] = True
            result["video_path"] = render_result.video_path
            result["python_code_path"] = render_result.python_code_path
            result["render_time"] = render_result.render_time
            result["file_size_mb"] = render_result.file_size_mb
        else:
            result["error"] = render_result.error
            result["stderr"] = render_result.stderr[:500] if render_result.stderr else None

        return result

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        return result


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化结果为人类可读的字符串

    Args:
        result: render_scene 返回的结果

    Returns:
        格式化的字符串
    """
    lines = []

    if result["success"]:
        lines.append(f"✓ Rendering completed: {result['scene_id']}")
        lines.append(f"\n[Input]")
        lines.append(f"  DSL File: {result['dsl_file']}")

        lines.append(f"\n[Output]")
        lines.append(f"  Video: {result['video_path']}")
        if result["python_code_path"]:
            lines.append(f"  Python Code: {result['python_code_path']}")

        lines.append(f"\n[Statistics]")
        lines.append(f"  Render Time: {result['render_time']:.1f}s")
        lines.append(f"  File Size: {result['file_size_mb']:.2f} MB")

    else:
        lines.append(f"✗ Rendering failed: {result['scene_id']}")
        lines.append(f"  Error: {result['error']}")

        if result.get("stderr"):
            lines.append(f"\n[Error Details]")
            lines.append(f"  {result['stderr']}")

    return "\n".join(lines)
