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

# 创建MCP服务器实例
server = Server("exam-solver-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    列出所有可用的工具
    """
    tools = []
    for tool_def in MCP_TOOLS:
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
