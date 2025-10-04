# server.py

#
# MCP Server for control Maqueen 
# this program is executed in docket container in Raspberry Pi
# start with uv run server.py
#

import paho.mqtt.client as mqtt
from mcp.server.lowlevel import Server
import mcp.types as types
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response, JSONResponse
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
import json


#
# setup for MQTT
#

# define of MQTT

MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883
MQTT_TOPIC = "req/maqueen01/control"

# global variable
mqtt_client = None

GO = json.dumps({'control' : {'device':'car', 'set' : 'go'}})
BACK = json.dumps({'control' : {'device':'car', 'set' : 'back'}})
SPIN_L = json.dumps({'control' : {'device':'car', 'set' : 'spin_left'}})
SPIN_R = json.dumps({'control' : {'device':'car', 'set' : 'spin_right'}})
STOP = json.dumps({'control' : {'device':'car', 'set' : 'stop'}})

def init_mqtt():

    global mqtt_client
    mqtt_client = mqtt.Client()
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print(f"MQTT connected to {MQTT_BROKER}:{MQTT_PORT}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_message(client, userdata, msg):
    print(f"Received: {msg.topic} {msg.payload}")

app = Server("maqueen")

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
    """ツール呼び出しハンドラ"""
    print(f"call_tool called: name={name}, arguments={arguments}")
    
    if name == "list_tools":
        # ツールリストを返す特殊処理
        tools = await list_tools()
        tools_info = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in tools
        ])
        result_text = f"Available tools:\n{tools_info}"
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "move_forward":
        duration = float(arguments.get("duration", 1.0))
        if duration <= 0:
            result_text = "Moving forward continuously (until stopped)"
        else:
            result_text = f"Moving forward for {duration} seconds"
        msg = GO
        result = client.publish(MQTT_TOPIC, msg , qos=0)
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "move_backward":
        duration = float(arguments.get("duration", 1.0))
        if duration <= 0:
            result_text = "Moving backward continuously (until stopped)"
        else:
            result_text = f"Moving backward for {duration} seconds"
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "turn_left":
        duration = float(arguments.get("duration", 1.0))
        if duration <= 0:
            result_text = "Turning left continuously (until stopped)"
        else:
            result_text = f"Turning left for {duration} seconds"
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "turn_right":
        duration = float(arguments.get("duration", 1.0))
        if duration <= 0:
            result_text = "Turning right continuously (until stopped)"
        else:
            result_text = f"Turning right for {duration} seconds"
        print(f"Returning: {result_text}")
        return [types.TextContent(type="text", text=result_text)]
    
    elif name == "stop":
        msg = STOP
        result = client.publish(MQTT_TOPIC, msg , qos=0)
        result_text = "Stopping Maqueen"
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
        ),
        types.Tool(
            name="move_backward",
            title="Move Backward",
            description="Moves Maqueen backward",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "description": "Duration in seconds"}
                },
                "required": ["duration"]
            }
        ),
        types.Tool(
            name="turn_left",
            title="Turn Left",
            description="Turns Maqueen left",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "description": "Duration in seconds"}
                },
                "required": ["duration"]
            }
        ),
        types.Tool(
            name="turn_right",
            title="Turn Right",
            description="Turns Maqueen right",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration": {"type": "number", "description": "Duration in seconds"}
                },
                "required": ["duration"]
            }
        ),
        types.Tool(
            name="stop",
            title="Stop",
            description="Stops Maqueen",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
        
        # メソッドに応じて処理を分岐
        method = rpc_request.get("method")
        
        if method == "tools/call":
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
            
        elif method == "tools/list":
            print("Listing tools")
            
            # list_toolsを呼び出し
            tools = await list_tools()
            
            # JSON-RPCレスポンスを作成
            response_data = {
                "jsonrpc": "2.0",
                "id": rpc_request.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        } for tool in tools
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

