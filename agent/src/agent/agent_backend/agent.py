from typing import List, Any, Iterable

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import Tool
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from .model import client

class GraphState(BaseModel):
    messages: Any
    tool_call: Any
    user: str
    user_id: int
    user_token: str


class Agent():
    def __init__(self, tools):
        self.model = client
        self.tools = tools
        

        async def make_plan(state: GraphState) -> GraphState:
            
            planner = self.model

            print([agent_tool.openai_description for agent_tool in self.tools.values()])
            print(state.messages)

            resp = planner.chat.completions.create(
                model="gpt://b1g1q1f6qkc2rbf6anvo/qwen3-235b-a22b-fp8/latest",
                messages=state.messages,
                tools=[agent_tool.openai_description for agent_tool in self.tools.values()],
            )

            print(resp)

            print(resp)

            if resp.choices[0].message.tool_calls == None:
                state.messages.append(
                    {
                        "role": resp.choices[0].message.role,
                        "content": resp.choices[0].message.content
                    }
                )
            else:
                state.messages.append(
                    {
                        "role": resp.choices[0].message.role,
                        "tool_calls": resp.choices[0].message.tool_calls
                    }
                )
                state.tool_call = resp.choices[0].message.tool_calls

            print(state.messages)
            return GraphState.model_validate(state)

        async def execute_plan(state: GraphState) -> GraphState:
            for tool_call in state.tool_call:
                func = tool_call.function
                args = {}
                res = await self.tools[func.name].tool(**args)
                if res == None:
                    res = ""
                state.messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": res})
                state.tool_call.remove(tool_call)
            return GraphState.model_validate(state)

        async def has_steps(state: GraphState) -> bool:
            if len(state.tool_call) > 0:
                return True
            return False

        checkpointer = MemorySaver()

        builder = StateGraph(GraphState)
        builder.add_node("planner", make_plan)
        builder.add_node("executor", execute_plan)

        builder.add_edge(START, "planner")
        builder.add_edge("executor", "planner")

        builder.add_conditional_edges("planner", has_steps, {
            True: "executor",
            False: END
        })

        self.graph = builder.compile(checkpointer=checkpointer)


    async def ainvoke(self, message: str, chat_id:str, user_id:int,
                       user_token:str, system_prompt: str = "Ты полезный ассистент"):
            user_message = {
                "role": "user",
                "content": message
            }
            
            try:
                restored_state = GraphState(
                    **self.graph.get_state(config={"configurable": {"thread_id": chat_id}}).values)
                state = GraphState(
                    messages=restored_state.messages + [user_message], 
                    **restored_state.model_dump()
                )
            except:
                system_message = {
                    "role": "system",
                    "content": system_prompt
                }
                state = GraphState(
                    messages=[system_message,user_message], 
                    tool_call={},
                    user=chat_id,
                    user_id=user_id,
                    user_token=user_token
                )
            
            state : GraphState = GraphState.model_validate(
                    await self.graph.ainvoke(state, config={"configurable": {"thread_id": chat_id}})
                )

            return state.messages
