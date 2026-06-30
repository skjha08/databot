import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import tools

server = Server("databot-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="load_dataset",
            description="Loads a CSV dataset from the specified filepath into memory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "The path to the CSV file to load."}
                },
                "required": ["filepath"]
            }
        ),
        types.Tool(
            name="calculate_stats",
            description="Calculates and returns summary statistics of the loaded dataset.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="check_missing_values",
            description="Checks the loaded dataset for missing values.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_correlation",
            description="Calculates the Pearson correlation coefficient between two specific columns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "col1": {"type": "string", "description": "The name of the first column."},
                    "col2": {"type": "string", "description": "The name of the second column."}
                },
                "required": ["col1", "col2"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if arguments is None:
        arguments = {}
        
    try:
        if name == "load_dataset":
            filepath = arguments.get("filepath")
            if not filepath:
                raise ValueError("Missing 'filepath' argument.")
            result = tools.load_dataset(filepath)
            return [types.TextContent(type="text", text=result)]
            
        elif name == "calculate_stats":
            result = tools.calculate_stats()
            return [types.TextContent(type="text", text=result)]
            
        elif name == "check_missing_values":
            result = tools.check_missing_values()
            return [types.TextContent(type="text", text=result)]
            
        elif name == "get_correlation":
            col1 = arguments.get("col1")
            col2 = arguments.get("col2")
            if not col1 or not col2:
                raise ValueError("Missing 'col1' or 'col2' argument.")
            result = tools.get_correlation(col1, col2)
            return [types.TextContent(type="text", text=result)]
            
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="databot-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
