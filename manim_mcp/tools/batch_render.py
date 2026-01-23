"""
Batch Render Tool
批量渲染多个 Animation DSL 场景
"""

import time
from pathlib import Path
from typing import Dict, Any, List
from ..renderer.render_executor import render_scene_from_file


# Tool Schema Definition
TOOL_SCHEMA = {
    "name": "batch_render",
    "description": "批量渲染多个场景。按顺序渲染所有指定的场景，提供进度报告。",
    "inputSchema": {
        "type": "object",
        "required": ["scene_ids"],
        "properties": {
            "scene_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要渲染的场景 ID 列表"
            },
            "quality": {
                "type": "string",
                "enum": ["low", "medium", "high"],
                "default": "medium",
                "description": "渲染质量: low (480p@30fps), medium (720p@60fps), high (1080p@60fps)"
            },
            "save_python_code": {
                "type": "boolean",
                "default": False,
                "description": "是否保存生成的 Python 代码（默认: false，批量渲染时通常不需要）"
            },
            "scenes_dir": {
                "type": "string",
                "default": "scenes",
                "description": "场景文件所在目录（默认: scenes）"
            },
            "stop_on_error": {
                "type": "boolean",
                "default": False,
                "description": "遇到错误时是否停止（默认: false，继续渲染其他场景）"
            }
        }
    }
}


def batch_render(
    scene_ids: List[str],
    quality: str = "medium",
    save_python_code: bool = False,
    scenes_dir: str = "scenes",
    stop_on_error: bool = False
) -> Dict[str, Any]:
    """
    批量渲染场景

    Args:
        scene_ids: 场景 ID 列表
        quality: 渲染质量
        save_python_code: 是否保存 Python 代码
        scenes_dir: 场景目录
        stop_on_error: 遇到错误时是否停止

    Returns:
        批量渲染结果字典
    """
    result = {
        "success": False,
        "total_scenes": len(scene_ids),
        "completed": 0,
        "failed": 0,
        "total_time": 0.0,
        "results": [],
        "errors": []
    }

    start_time = time.time()

    try:
        for i, scene_id in enumerate(scene_ids, 1):
            print(f"\n[Batch Render] Scene {i}/{len(scene_ids)}: {scene_id}")

            scene_result = {
                "scene_id": scene_id,
                "success": False,
                "video_path": None,
                "render_time": 0.0,
                "file_size_mb": 0.0,
                "error": None
            }

            try:
                # 查找场景文件
                dsl_file = Path(scenes_dir) / f"{scene_id}.json"

                if not dsl_file.exists():
                    scene_result["error"] = f"Scene file not found: {dsl_file}"
                    result["failed"] += 1
                    result["errors"].append(f"{scene_id}: File not found")

                    if stop_on_error:
                        result["results"].append(scene_result)
                        break
                    else:
                        result["results"].append(scene_result)
                        continue

                # 执行渲染
                render_result = render_scene_from_file(
                    str(dsl_file),
                    quality=quality,
                    save_python_code=save_python_code
                )

                if render_result.success:
                    scene_result["success"] = True
                    scene_result["video_path"] = render_result.video_path
                    scene_result["render_time"] = render_result.render_time
                    scene_result["file_size_mb"] = render_result.file_size_mb
                    result["completed"] += 1

                    print(f"  ✓ Completed in {render_result.render_time:.1f}s")
                else:
                    scene_result["error"] = render_result.error
                    result["failed"] += 1
                    result["errors"].append(f"{scene_id}: {render_result.error}")

                    print(f"  ✗ Failed: {render_result.error}")

                    if stop_on_error:
                        result["results"].append(scene_result)
                        break

            except Exception as e:
                scene_result["error"] = str(e)
                result["failed"] += 1
                result["errors"].append(f"{scene_id}: {str(e)}")

                print(f"  ✗ Exception: {str(e)}")

                if stop_on_error:
                    result["results"].append(scene_result)
                    break

            result["results"].append(scene_result)

        result["total_time"] = time.time() - start_time
        result["success"] = result["completed"] > 0

        return result

    except Exception as e:
        result["total_time"] = time.time() - start_time
        result["errors"].append(f"Batch render error: {str(e)}")
        return result


def format_result(result: Dict[str, Any]) -> str:
    """
    格式化结果为人类可读的字符串

    Args:
        result: batch_render 返回的结果

    Returns:
        格式化的字符串
    """
    lines = []

    lines.append(f"Batch Render Summary")
    lines.append(f"=" * 60)

    lines.append(f"\n[Overall]")
    lines.append(f"  Total Scenes: {result['total_scenes']}")
    lines.append(f"  Completed: {result['completed']}")
    lines.append(f"  Failed: {result['failed']}")
    lines.append(f"  Total Time: {result['total_time']:.1f}s")

    if result["completed"] > 0:
        avg_time = result["total_time"] / result["completed"]
        lines.append(f"  Average Time: {avg_time:.1f}s per scene")

    lines.append(f"\n[Results]")
    for i, scene_result in enumerate(result["results"], 1):
        scene_id = scene_result["scene_id"]
        if scene_result["success"]:
            lines.append(f"  {i}. ✓ {scene_id}")
            lines.append(f"     Video: {scene_result['video_path']}")
            lines.append(f"     Time: {scene_result['render_time']:.1f}s")
            lines.append(f"     Size: {scene_result['file_size_mb']:.2f} MB")
        else:
            lines.append(f"  {i}. ✗ {scene_id}")
            lines.append(f"     Error: {scene_result['error']}")

    if result["errors"]:
        lines.append(f"\n[Errors Summary]")
        for error in result["errors"]:
            lines.append(f"  - {error}")

    lines.append(f"\n" + "=" * 60)
    if result["success"]:
        lines.append(f"✓ Batch render completed ({result['completed']}/{result['total_scenes']} successful)")
    else:
        lines.append(f"✗ Batch render failed (all scenes failed)")

    return "\n".join(lines)
