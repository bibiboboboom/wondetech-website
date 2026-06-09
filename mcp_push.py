import json, sys, subprocess, os, re

# Read local files
html = open('risk-intelligence.html', 'r', encoding='utf-8').read()
css  = open('risk-intelligence.css',  'r', encoding='utf-8').read()

# Construct the mcp__github__push_files tool call
# We need to use the WorkBuddy MCP client to make the call
# Since we can't directly call MCP tools from Python,
# we'll output the tool call in a format the agent can use

payload = {
    "owner": "bibiboboboom",
    "repo": "wondetech-website",
    "branch": "main",
    "message": "feat: redesign Risk Intelligence page with scenario-driven visual workflow",
    "files": [
        {"path": "risk-intelligence.html", "content": html},
        {"path": "risk-intelligence.css",  "content": css}
    ]
}

# Write the tool call parameters to a file
# The agent framework will use DeferExecuteTool to call the MCP tool
tool_call = {
    "toolName": "mcp__github__push_files",
    "params": payload
}

with open('C:/Users/lenovo/WorkBuddy/mcp_tool_call.json', 'w', encoding='utf-8') as f:
    json.dump(tool_call, f, ensure_ascii=False, indent=2)

print(f"Tool call payload written. HTML: {len(html)} bytes, CSS: {len(css)} bytes")
print("Ready for MCP tool call via DeferExecuteTool")
