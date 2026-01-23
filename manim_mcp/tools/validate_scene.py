"""
Validate Scene Tool
验证已保存的 Animation DSL 场景
"""

import json
from pathlib import Path
from typing import Dict, Any
from ..dsl.validator import validate_dsl_file


# Tool Schema Definition
TOOL_SCHEMA = {
    "name": "validate_scene",
    "description": "验证场景 DSL 是否符合 schema 并可渲染。检查资源文件、动画参数等。",
    "inputSchema": {
        "type": "object",
        "required": ["scene_id"],
        "properties": {
            "scene_id": {
                "type": "string",
                "description": "场景 ID（例如: problem_1_solution）"
            },
            "scenes_dir": {
                "type": "string",
                "default": "scenes",
                "description": "场景文件所在目录（默认: scenes）"
            }
        }
    }
}


def validate_scene(scene_id: str, scenes_dir: str = "scenes") -> Dict[str, Any]:
    """
    验证场景

    Args:
        scene_id: 场景 ID
        scenes_dir: 场景目录

    Returns:
        验证结果字典
    """
    result = {
        "success": False,
        "scene_id": scene_id,
        "file_path": None,
        "validation": None,
        "error": None
    }

    try:
        # 1. 查找场景文件
        scene_file = Path(scenes_dir) / f"{scene_id}.json"

        if not scene_file.exists():
            result["error"] = f"Scene file not found: {scene_file}"
            return result

        result["file_path"] = str(scene_file)

        # 2. 验证 DSL
        validation_result = validate_dsl_file(str(scene_file))

        result["validation"] = {
            "valid": validation_result.valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "estimated_duration": validation_result.estimated_duration,
            "animation_count": validation_result.animation_count,
            "phase_count": validation_result.phase_count
        }

        result["success"] = True
        return result

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        return result


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化结果为人类可读的字符串

    Args:
        result: validate_scene 返回的结果

    Returns:
        格式化的字符串
    """
    lines = []

    if not result["success"]:
        lines.append(f"✗ Validation failed: {result['scene_id']}")
        lines.append(f"  Error: {result['error']}")
        return "\n".join(lines)

    lines.append(f"Scene: {result['scene_id']}")
    lines.append(f"File: {result['file_path']}")

    validation = result["validation"]
    lines.append(f"\n[Validation Result]")

    if validation["valid"]:
        lines.append(f"  ✓ Valid: Yes")
    else:
        lines.append(f"  ✗ Valid: No")

    lines.append(f"  Errors: {len(validation['errors'])}")
    lines.append(f"  Warnings: {len(validation['warnings'])}")
    lines.append(f"  Estimated Duration: {validation['estimated_duration']}s")
    lines.append(f"  Animation Count: {validation['animation_count']}")
    lines.append(f"  Phase Count: {validation['phase_count']}")

    if validation["errors"]:
        lines.append(f"\n[Errors]")
        for i, error in enumerate(validation["errors"], 1):
            lines.append(f"  {i}. {error}")

    if validation["warnings"]:
        lines.append(f"\n[Warnings]")
        for i, warning in enumerate(validation["warnings"], 1):
            lines.append(f"  {i}. {warning}")

    return "\n".join(lines)
