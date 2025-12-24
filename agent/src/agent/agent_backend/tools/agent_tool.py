class AgentTool:
    def __init__(self, name:str, tool, openai_description: dict):
        self.name = name
        self.tool = tool
        self.openai_description = openai_description
