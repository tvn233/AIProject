"""Discover MCP schemas dynamically and attach guarded Python callbacks."""
from __future__ import annotations
from typing import Callable
from .mcp_client import list_tool_specs, call_tool, register_and_verify

def discover_mcp_tools(confirm: Callable[[str,str],bool] | None = None):
    schemas, handlers = [], {}
    for spec in list_tool_specs():
        name=spec['name']
        # Tool names are discovered from MCP server, not from a hard-coded list.
        params=dict(spec['inputSchema'])
        # Never let LLM supply confirmation flag; only CLI user can approve.
        if name == 'register_ctxh_activity_tool':
            props=dict(params.get('properties',{}));props.pop('confirmed',None)
            params['properties']=props
            params['required']=[x for x in params.get('required',[]) if x!='confirmed']
            def write(student_id: str, activity_code: str):
                if confirm is None or not confirm(student_id,activity_code):
                    return {'ok':False,'error':'Người dùng chưa xác nhận; không ghi dữ liệu'}
                return register_and_verify(student_id,activity_code,confirmed=True)
            handlers[name]=write
        else:
            def dispatch(_name=name,**kwargs):
                return call_tool(_name,**kwargs)
            handlers[name]=dispatch
        schemas.append({'type':'function','function':{'name':name,
                        'description':spec['description'], 'parameters':params}})
    return schemas,handlers
