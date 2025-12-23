from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.schema import HumanMessage, AIMessage

# -------- State --------
class AgentState(TypedDict):
    messages: List

# -------- LLM --------
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# -------- Tool --------
@tool
def multiply(a: int, b: int) -> int:
    """Умножает два числа"""
    return a * b

tools = [multiply]

# -------- Nodes --------
def agent_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

def tool_node(state: AgentState):
    last = state["messages"][-1]
    tool_call = last.tool_calls[0]

    if tool_call["name"] == "multiply":
        result = multiply.invoke(tool_call["args"])
        return {
            "messages": state["messages"] + [
                AIMessage(content=str(result))
            ]
        }

# -------- Router --------
def router(state: AgentState):
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tool"
    return END

# -------- Graph --------
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tool", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    router,
    {
        "tool": "tool",
        END: END
    }
)

graph.add_edge("tool", "agent")

app = graph.compile()
