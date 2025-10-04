#!/usr/bin/python3

# proxy.py
import sys
import httpx
from fastmcp import FastMCP

# get connect URL from args（e.g: python proxy.py https://example.com/mcp）
if len(sys.argv) < 2:
    print("Usage: python proxy.py <REMOTE_MCP_URL>")
    sys.exit(1)

REMOTE_MCP_URL = sys.argv[1]
mcp = FastMCP("Generic MCP Proxy")

@mcp.tool()
def run_tool(tool_name: str, payload: dict) -> dict:
    url = f"{REMOTE_MCP_URL}/{tool_name}"
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": payload
        },
        "id": 1
    }
    response = httpx.post(url, json=mcp_request)
    return response.json()

if __name__ == "__main__":
    mcp.run(transport="stdio")
