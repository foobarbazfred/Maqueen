#
# MCP Server for control Maqueen  (Minimum version)
#
#
# server_minimal.py
import uvicorn
import json
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request

# 利用可能なツールの定義
TOOLS = {
    "move_forward": {
        "description": "Moves Maqueen forward",
        "params": ["duration"]
    }
}

async def handle_request(request: Request):
    """すべてのリクエストを処理"""
    try:
        # リクエストボディをパース
        body = await request.body()
        rpc_request = json.loads(body)
        
        method = rpc_request.get("method")
        params = rpc_request.get("params", {})
        request_id = rpc_request.get("id")
        
        # tools/call: ツール実行
        if method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # list_tools: ツール一覧を返す
            if tool_name == "list_tools":
                tools_info = "\n".join([
                    f"- {name}: {info['description']}"
                    for name, info in TOOLS.items()
                ])
                result_text = f"Available tools:\n{tools_info}"
            
            # move_forward: 前進コマンド
            elif tool_name == "move_forward":
                duration = float(arguments.get("duration", 1.0))
                result_text = f"Moving forward for {duration} seconds"
            
            else:
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Unknown tool: {tool_name}"},
                        "id": request_id
                    },
                    status_code=500
                )
            
            # 成功レスポンス
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}]
                    }
                }
            )
        
        # 未知のメソッド
        else:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                },
                status_code=400
            )
    
    except Exception as e:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": str(e)},
                "id": None
            },
            status_code=500
        )

# Starletteアプリケーション
app = Starlette(
    routes=[
        Route("/messages/{path:path}", endpoint=handle_request, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1885)
