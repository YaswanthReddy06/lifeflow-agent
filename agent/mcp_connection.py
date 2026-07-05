"""
mcp_connection.py — wires the ADK agents up to the LifeFlow MCP Server.

Concept demonstrated: MCP Server (Day 2), consumed here on the *client*
side. ADK's MCPToolset launches our server.py as a subprocess over stdio
and exposes its @mcp.tool()-decorated functions as regular ADK tools —
this is exactly the "no bespoke integration code" benefit MCP is meant
to provide.
"""

import sys
from pathlib import Path

from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_lifeflow_toolset() -> MCPToolset:
    """Returns an MCPToolset connected to our local LifeFlow MCP server."""
    return MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=["-m", "mcp_server.server"],
                cwd=str(PROJECT_ROOT),
            ),
            timeout=30,
        )
    )
