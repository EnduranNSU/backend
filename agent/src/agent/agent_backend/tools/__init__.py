from .mock_tool import mock_tool
from .exercise_rag import exercise_rag_get_tool
from .users_rag_download_tool import user_rag_download_tool
from .users_rag_upload_tool import user_rag_upload_tool
from .cv_analyze import cv_analyze_tool


tools_list = [mock_tool, cv_analyze_tool]

tools = {
    tool.name: tool for tool in tools_list
}
