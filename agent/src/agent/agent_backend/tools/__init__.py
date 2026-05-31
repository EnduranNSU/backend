from .exercise_catalog import exercise_catalog_tool
from .exercise_rag import exercise_rag_get_tool
from .cv_analyze import cv_analyze_tool
from .users_rag_download_tool import user_rag_download_tool
from .users_rag_upload_tool import user_rag_upload_tool


tools_list = [
    exercise_catalog_tool,
    exercise_rag_get_tool,
    cv_analyze_tool,
    user_rag_download_tool,
    user_rag_upload_tool,
]

tools = {
    tool.name: tool for tool in tools_list
}
