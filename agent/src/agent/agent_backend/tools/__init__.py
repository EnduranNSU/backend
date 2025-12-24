from .mock_tool import mock_tool

tools_list = [mock_tool]

tools = {
    tool.name: tool for tool in tools_list
}
