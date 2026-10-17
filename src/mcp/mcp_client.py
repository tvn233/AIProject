"""Official MCP ClientSession; each call opens and closes one stdio session."""
from __future__ import annotations
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def _request(name=None, args=None, specs=False):
    server = StdioServerParameters(command=sys.executable, args=['-m', 'src.mcp.mcp_server'])
    async with stdio_client(server) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            if name is None:
                result = await session.list_tools()
                if specs:
                    return [{"name":t.name,"description":t.description or "",
                             "inputSchema":t.inputSchema} for t in result.tools]
                return [t.name for t in result.tools]
            result = await session.call_tool(name, arguments=args or {})
            if result.isError:
                raise RuntimeError(str(result.content))
            texts = [part.text for part in result.content if getattr(part, 'type', '') == 'text']
            if not texts:
                raise RuntimeError('MCP trả về nội dung rỗng')
            return json.loads(texts[0])

def list_tools():
    return asyncio.run(_request())

def list_tool_specs():
    return asyncio.run(_request(specs=True))

def call_tool(name, **kwargs):
    return asyncio.run(_request(name, kwargs))

def register_and_verify(student_id: str, activity_code: str, confirmed: bool = False):
    written = call_tool('register_ctxh_activity_tool', student_id=student_id,
                        activity_code=activity_code, confirmed=confirmed)
    if not written.get('ok'):
        return {'ok': False, 'write': written}
    read = call_tool('get_ctxh_registration_status_tool', student_id=student_id,
                     activity_code=activity_code)
    ok = (read.get('found') and read.get('record') == written.get('record'))
    return {'ok': bool(ok), 'write': written, 'verify': read}

if __name__ == '__main__':
    print(list_tools())
