#------------------------------
# file: server.py (MCP Server)
#------------------------------
# server.py
from mcp.server.lowlevel import Server
import mcp.types as types
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from starlette.requests import Request

app = Server("maqueen")

@app.call_tool()
async def move_forward(name: str, arguments: dict) -> list[types.ContentBlock]:
    duration = float(arguments.get("duration", 1.0))
    return [types.TextContent(type="text", text=f"Moving forward for {duration} seconds")]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="move_forward",
            title="Move Forward",
            description="Moves Maqueen forward",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "description": "Duration in seconds"}
                },
                "required": ["duration"]
            }
        )
    ]

sse = SseServerTransport("/messages/")

async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())
    return Response()

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=1885)
