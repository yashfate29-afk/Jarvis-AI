import asyncio
import json
import functools
from typing import Any, Dict, List


from mcp.types import Tool as MCPTool, CallToolResult
from .server import MCPServer


class FunctionTool:
    def __init__(self, name: str, description: str, params_json_schema: Dict[str, Any], on_invoke_tool, strict_json_schema: bool = False):
        self.name = name
        self.description = description
        self.params_json_schema = params_json_schema
        self.on_invoke_tool = on_invoke_tool  
        self.strict_json_schema = strict_json_schema

    def __repr__(self):
        return f"FunctionTool(name={self.name})"

class MCPUtil:
    @classmethod
    async def get_function_tools(cls, server, convert_schemas_to_strict: bool) -> List[FunctionTool]:
        tools = await server.list_tools()
        function_tools = []
        for tool in tools:
            ft = cls.to_function_tool(tool, server, convert_schemas_to_strict)
            function_tools.append(ft)
        return function_tools

    @classmethod
    def to_function_tool(cls, tool, server, convert_schemas_to_strict: bool) -> FunctionTool:
        
        schema = tool.inputSchema

       
        async def invoke_tool(context: Any, input_json: str, current_tool_name=tool.name) -> str:
            try:
                arguments = json.loads(input_json) if input_json else {}
            except Exception as e:
               
                return f"Error parsing input JSON for tool '{current_tool_name}': {e}"
            try:
                result = await server.call_tool(current_tool_name, arguments)
              
                if "content" in result and isinstance(result["content"], list) and len(result["content"]) >= 1:
                   
                     if len(result["content"]) == 1:
                         content_item = result["content"][0]
                        
                         if isinstance(content_item, (str, int, float, bool)):
                             return str(content_item)
                         
                         else:
                             try:
                                 return json.dumps(content_item)
                             except TypeError:
                                 return str(content_item) 
                     else:
                         
                          try:
                              return json.dumps(result["content"])
                          except TypeError:
                              return str(result["content"]) # Fallback
                else:
                   
                    try:
                        return json.dumps(result)
                    except TypeError:
                        return str(result) # Fallback
            except Exception as e:
                
                 return f"Error calling tool '{current_tool_name}': {e}"

        return FunctionTool(
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=invoke_tool,
            strict_json_schema=convert_schemas_to_strict,
        )