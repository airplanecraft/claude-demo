"""
Create Scene Tool
创建并验证 Animation DSL 场景
"""

import json
from pathlib import Path
from typing import Dict, Any
from ..dsl.validator import DSLValidator


# Tool Schema Definition
TOOL_SCHEMA = {
    "name": "create_scene",
    "description": "从结构化的 Animation DSL 创建 Manim 场景。验证 DSL 并保存到文件系统。",
    "inputSchema": {
        "type": "object",
        "required": ["scene_dsl"],
        "properties": {
            "scene_dsl": {
                "type": "object",
                "description": "完整的 Animation DSL 对象（JSON 格式）"
            },
            "save_to_file": {
                "type": "boolean",
                "default": True,
                "description": "是否保存 DSL 到文件（默认: true）"
            },
            "output_dir": {
                "type": "string",
                "default": "scenes",
                "description": "保存 DSL 文件的目录（默认: scenes）"
            }
        }
    }
}


def create_scene(scene_dsl: Dict[str, Any], save_to_file: bool = True, output_dir: str = "scenes") -> Dict[str, Any]:
    """
    创建场景

    Args:
        scene_dsl: Animation DSL 字典
        save_to_file: 是否保存到文件
        output_dir: 输出目录

    Returns:
        创建结果字典
    """
    result = {
        "success": False,
        "scene_id": scene_dsl.get("scene_id", "unknown"),
        "saved_path": None,
        "validation": None,
        "error": None
    }

    try:
        # 1. 验证 DSL
        validator = DSLValidator()
        validation_result = validator.validate(scene_dsl)

        result["validation"] = {
            "valid": validation_result.valid,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings,
            "estimated_duration": validation_result.estimated_duration,
            "animation_count": validation_result.animation_count,
            "phase_count": validation_result.phase_count
        }

        # 如果验证失败，不保存文件
        if not validation_result.valid:
            result["error"] = "DSL validation failed"
            return result

        # 2. 保存到文件（如果需要）
        if save_to_file:
            scene_id = scene_dsl.get("scene_id", "unknown_scene")

            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 保存 DSL 文件
            file_path = output_path / f"{scene_id}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scene_dsl, f, ensure_ascii=False, indent=2)

            result["saved_path"] = str(file_path)

        result["success"] = True
        return result

    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        return result


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化结果为人类可读的字符串

    Args:
        result: create_scene 返回的结果

    Returns:
        格式化的字符串
    """
    lines = []

    if result["success"]:
        lines.append(f"✓ Scene created successfully: {result['scene_id']}")

        if result["saved_path"]:
            lines.append(f"  Saved to: {result['saved_path']}")

        validation = result["validation"]
        lines.append(f"\n[Validation]")
        lines.append(f"  Valid: {validation['valid']}")
        lines.append(f"  Warnings: {len(validation['warnings'])}")
        lines.append(f"  Estimated Duration: {validation['estimated_duration']}s")
        lines.append(f"  Animations: {validation['animation_count']}")
        lines.append(f"  Phases: {validation['phase_count']}")

        if validation["warnings"]:
            lines.append(f"\n[Warnings]")
            for warning in validation["warnings"]:
                lines.append(f"  - {warning}")
    else:
        lines.append(f"✗ Failed to create scene: {result['scene_id']}")
        lines.append(f"  Error: {result['error']}")

        if result["validation"] and result["validation"]["errors"]:
            lines.append(f"\n[Validation Errors]")
            for error in result["validation"]["errors"]:
                lines.append(f"  - {error}")

    return "\n".join(lines)
