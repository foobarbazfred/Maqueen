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
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    """ツール呼び出しハンドラ"""
    if name == "move_forward":
        duration = float(arguments.get("duration", 1.0))
        return [types.TextContent(type="text", text=f"Moving forward for {duration} seconds")]
    else:
        raise ValueError(f"Unknown tool: {name}")

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
    """SSEハンドラ"""
    print(f"Request received: {request.url}")
    print(f"Method: {request.method}")
    print(f"Headers: {request.headers}")
    
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    return Response()

async def handle_post(request: Request):
    """POSTリクエストハンドラ（デバッグ用）"""
    print(f"POST Request: {request.url}")
    print(f"Path: {request.url.path}")
    print(f"Headers: {request.headers}")
    body = await request.body()
    print(f"Body: {body}")
    
    # SseServerTransportのPOSTハンドラに委譲
    return await sse.handle_post_message(request)

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST"]),
        Route("/messages/{tool_name:path}", endpoint=handle_post, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=1885)
