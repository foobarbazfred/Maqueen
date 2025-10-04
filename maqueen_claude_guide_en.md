# Maqueen MCP Server - Claude Operation Guide

## Initial Instructions for Claude

When starting a new Claude session, use one of these prompts:

### Simple Approach
```
Show me the Maqueen command list
```
or
```
Make Maqueen move forward for 3 seconds
```

### Detailed Approach (if the simple approach doesn't work)
```
I want to operate Maqueen via MCP Server.
Please use maqueen:run_tool to execute the following:
1. Get command list (tool_name: "list_tools")
2. Execute forward command (tool_name: "move_forward", duration: 3.0)
```

## Available Commands

- `move_forward` - Move Maqueen forward
- `move_backward` - Move Maqueen backward
- `turn_left` - Turn Maqueen left
- `turn_right` - Turn Maqueen right
- `stop` - Stop Maqueen
- `list_tools` - Display available tool list

## Important Parameter Settings

### Duration Settings
- `duration: 0` - Continuous operation (until stopped)
- `duration: n` - Operate for n seconds

### Rotation Calibration
- **duration 3 seconds = 10 degrees rotation**

#### Angle Conversion Examples
- 90 degrees = duration 27 seconds
- 180 degrees = duration 54 seconds
- 45 degrees = duration 13.5 seconds

## Server Setup

### Starting the Server
```bash
python server.py
```

### Server Configuration
- Host: `0.0.0.0`
- Port: `1885`

## Usage Examples

### Get Command List
```
Show Maqueen command list
```

### Movement Commands
```
Move forward
Move forward continuously
Turn right 180 degrees
Stop
```

## Context Information to Preserve

When starting a new Claude session, the following information should be provided:

1. **Basic Setup**: MCP Server operation via `maqueen:run_tool`
2. **Available Commands**: List of 5 movement commands + list_tools
3. **Parameter Rules**: duration 0 = continuous, duration 3s = 10° rotation
4. **Calibration Data**: Rotation angle conversion formula

## Notes

- **Session Data Loss**: Conversation history and learned information are not retained when starting a new chat
- **Tool Availability**: The `maqueen:run_tool` connection remains available across sessions
- **Code Preservation**: Save Artifacts (server code) separately if needed

## Server Implementation

Two versions are available:

1. **Full Version**: Uses MCP library with complete protocol support
2. **Minimal Version**: Pure JSON-RPC implementation with minimal dependencies

Both versions support the same command set and functionality.
