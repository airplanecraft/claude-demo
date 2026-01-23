"""MCP Tools for Manim Animation DSL"""

from . import create_scene
from . import validate_scene
from . import render_scene
from . import batch_render

# Tool schemas for MCP registration
MANIM_TOOLS = [
    create_scene.TOOL_SCHEMA,
    validate_scene.TOOL_SCHEMA,
    render_scene.TOOL_SCHEMA,
    batch_render.TOOL_SCHEMA,
]

# Tool implementations
MANIM_TOOL_HANDLERS = {
    "create_scene": create_scene.create_scene,
    "validate_scene": validate_scene.validate_scene,
    "render_scene": render_scene.render_scene,
    "batch_render": batch_render.batch_render,
}

# Tool formatters
MANIM_TOOL_FORMATTERS = {
    "create_scene": create_scene.format_result,
    "validate_scene": validate_scene.format_result,
    "render_scene": render_scene.format_result,
    "batch_render": batch_render.format_result,
}

__all__ = [
    "MANIM_TOOLS",
    "MANIM_TOOL_HANDLERS",
    "MANIM_TOOL_FORMATTERS",
    "create_scene",
    "validate_scene",
    "render_scene",
    "batch_render",
]
