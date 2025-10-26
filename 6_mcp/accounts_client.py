"""
MCP Client for Accounts Server

This module provides client functions to interact with the accounts_server.py MCP server.
It includes functions to list tools, call tools, read resources, and convert MCP tools
to OpenAI-compatible format for use with the Agents SDK.
"""

import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from agents import FunctionTool
import json

# Configure connection parameters for the MCP server
# Uses uv to run accounts_server.py as an MCP server via stdio transport
params = StdioServerParameters(command="uv", args=["run", "accounts_server.py"], env=None)


async def list_accounts_tools():
    """
    List all available tools from the accounts MCP server.

    Returns:
        list: List of MCP Tool objects available on the server
    """
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            return tools_result.tools
        
async def call_accounts_tool(tool_name, tool_args):
    """
    Call a specific tool on the accounts MCP server.

    Args:
        tool_name (str): Name of the tool to call
        tool_args (dict): Arguments to pass to the tool

    Returns:
        The result of the tool execution
    """
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return result
            
async def read_accounts_resource(name):
    """
    Read an account resource from the MCP server.

    Args:
        name (str): Name of the account resource to read

    Returns:
        str: The text content of the resource
    """
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.read_resource(f"accounts://accounts_server/{name}")
            return result.contents[0].text
        
async def read_strategy_resource(name):
    """
    Read a strategy resource from the MCP server.

    Args:
        name (str): Name of the strategy resource to read

    Returns:
        str: The text content of the strategy resource
    """
    async with stdio_client(params) as streams:
        async with mcp.ClientSession(*streams) as session:
            await session.initialize()
            result = await session.read_resource(f"accounts://strategy/{name}")
            return result.contents[0].text

async def get_accounts_tools_openai():
    """
    Convert MCP tools to OpenAI-compatible FunctionTool objects.

    This function bridges MCP tools with the OpenAI Agents SDK by:
    1. Getting the list of MCP tools from the server
    2. Converting each MCP tool's schema to OpenAI format
    3. Wrapping each tool in a FunctionTool that calls back to MCP

    Returns:
        list: List of FunctionTool objects compatible with OpenAI Agents SDK
    """
    openai_tools = []
    for tool in await list_accounts_tools():
        # Convert MCP schema to OpenAI format and disable additional properties
        schema = {**tool.inputSchema, "additionalProperties": False}
        openai_tool = FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            # Lambda captures tool name and calls MCP tool when invoked
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_accounts_tool(toolname, json.loads(args))

        )
        openai_tools.append(openai_tool)
    return openai_tools