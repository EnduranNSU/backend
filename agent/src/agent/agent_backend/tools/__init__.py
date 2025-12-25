from .mock_tool import mock_tool
from .exercise_rag import exercise_rag_get_tool
from .users_rag_download_tool import user_rag_download_tool
from .users_rag_upload_tool import user_rag_upload_tool


tools_list = [mock_tool, user_rag_upload_tool, user_rag_download_tool, exercise_rag_get_tool]
tools_list = [mock_tool]

tools = {
    tool.name: tool for tool in tools_list
}
