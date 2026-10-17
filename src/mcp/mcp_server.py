"""Official MCP SDK server over stdio. Run: python -m src.mcp.mcp_server"""
import json
from mcp.server.fastmcp import FastMCP
from .tools import register_ctxh_activity, get_ctxh_registration_status, convert_ctxh_points, convert_ctxh_points_policy

mcp = FastMCP('CTXH Demo')

@mcp.tool()
def register_ctxh_activity_tool(student_id: str, activity_code: str, confirmed: bool = False) -> str:
    """Register CTXH activity in demo DB. Explicit user confirmation is required."""
    return json.dumps(register_ctxh_activity(student_id, activity_code, confirmed), ensure_ascii=False)

@mcp.tool()
def get_ctxh_registration_status_tool(student_id: str, activity_code: str) -> str:
    """Read back the stored registration status for verification."""
    return json.dumps(get_ctxh_registration_status(student_id, activity_code), ensure_ascii=False)

@mcp.tool()
def convert_ctxh_points_tool(points: float, points_per_day: float) -> str:
    """Convert points to days using an explicitly supplied, verified rate; no guessed rate."""
    return json.dumps(convert_ctxh_points(points, points_per_day), ensure_ascii=False)


@mcp.tool()
def convert_ctxh_points_policy_tool(points: int) -> str:
    """Convert CTXH points using the 10-point policy with documented rounding."""
    return json.dumps(convert_ctxh_points_policy(points), ensure_ascii=False)

if __name__ == '__main__':
    mcp.run(transport='stdio')
