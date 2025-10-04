# server.py
from mcp.server.lowlevel import Server
import mcp.types as types
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
import json

app = Server("maqueen")

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    """ツール呼び出しハンドラ"""
    print(f"call_tool called: name={name}, arguments={arguments}")
    if name == "move_forward":
        duration = float(arguments.get("duration", 1.0))
        result_text = f"Moving forward for {duration} seconds"
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
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
    print(f"SSE Request received: {request.url}")
    print(f"Method: {request.method}")
    print(f"Headers: {request.headers}")

    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
    except Exception as e:
        print(f"Error in handle_sse: {e}")
        import traceback
        traceback.print_exc()
    return Response()

async def handle_post(request: Request):
    """POSTリクエストハンドラ"""
    print(f"POST Request: {request.url}")
    print(f"Path: {request.url.path}")
    print(f"Headers: {request.headers}")

    try:
        body = await request.body()
        print(f"Body: {body}")

        # JSON-RPCリクエストをパース
        rpc_request = json.loads(body)
        print(f"Parsed RPC Request: {rpc_request}")

        # ツール呼び出し
        if rpc_request.get("method") == "tools/call":
            params = rpc_request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            print(f"Calling tool: {tool_name} with args: {arguments}")

            # call_toolを直接呼び出し
            result = await call_tool(tool_name, arguments)

            # JSON-RPCレスポンスを作成
            response_data = {
                "jsonrpc": "2.0",
                "id": rpc_request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": item.type,
                            "text": item.text
                        } for item in result
                    ]
                }
            }

            print(f"Response: {response_data}")
            return JSONResponse(content=response_data)
        else:
            return JSONResponse(
                content={"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": rpc_request.get("id")},
                status_code=400
            )

    except Exception as e:
        print(f"Error in handle_post: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None},
            status_code=500
        )

starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET", "POST"]),
        Route("/messages/{tool_name:path}", endpoint=handle_post, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=1885)

