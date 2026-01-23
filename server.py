"""
MCP服务器主文件
注册并提供解题工具
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

# 导入工具函数
from tools import (
    create_output_directory,
    write_solution_file,
    save_solution,
    get_image_list,
    read_prompt,
    MCP_TOOLS
)

# 导入 Manim MCP Tools
from manim_mcp.tools import (
    MANIM_TOOLS,
    MANIM_TOOL_HANDLERS,
    MANIM_TOOL_FORMATTERS
)

# 创建MCP服务器实例
server = Server("exam-solver-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    列出所有可用的工具
    """
    tools = []

    # 添加原有的解题工具
    for tool_def in MCP_TOOLS:
        tools.append(Tool(
            name=tool_def["name"],
            description=tool_def["description"],
            inputSchema=tool_def["inputSchema"]
        ))

    # 添加 Manim 渲染工具
    for tool_def in MANIM_TOOLS:
        tools.append(Tool(
            name=tool_def["name"],
            description=tool_def["description"],
            inputSchema=tool_def["inputSchema"]
        ))

    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    调用指定的工具
    """
    try:
        if name == "create_output_directory":
            result = create_output_directory(arguments["image_name"])
            return [TextContent(
                type="text",
                text=json.dumps({"directory": result}, ensure_ascii=False, indent=2)
            )]

        elif name == "write_solution_file":
            result = write_solution_file(
                arguments["image_name"],
                arguments["content"],
                arguments["file_type"]
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "save_solution":
            result = save_solution(
                arguments["image_name"],
                arguments["markdown_content"],
                arguments["python_code"]
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]

        elif name == "get_image_list":
            result = get_image_list()
            return [TextContent(
                type="text",
                text=json.dumps({"images": result}, ensure_ascii=False, indent=2)
            )]

        elif name == "read_prompt":
            result = read_prompt()
            return [TextContent(
                type="text",
                text=result
            )]

        # Manim Tools
        elif name in MANIM_TOOL_HANDLERS:
            # 调用对应的 Manim tool handler
            handler = MANIM_TOOL_HANDLERS[name]
            formatter = MANIM_TOOL_FORMATTERS[name]

            result = handler(**arguments)

            # 格式化结果为人类可读的字符串
            formatted_text = formatter(result)

            # 同时返回格式化文本和 JSON 数据
            return [
                TextContent(
                    type="text",
                    text=formatted_text
                ),
                TextContent(
                    type="text",
                    text="\n\n[JSON Data]\n" + json.dumps(result, ensure_ascii=False, indent=2)
                )
            ]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"未知的工具: {name}"}, ensure_ascii=False)
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
        )]


async def main():
    """
    启动MCP服务器
    """
    # 使用stdio传输运行服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
