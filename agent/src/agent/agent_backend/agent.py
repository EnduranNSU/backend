import json
from typing import Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel

from .model import client, CHAT_MODEL


class GraphState(BaseModel):
    messages: Any
    tool_call: Any
    user: str
    user_id: int
    user_token: str


def _normalize_tool_call(tc: Any) -> dict:
    """OpenAI tool_call → plain dict (works for raw SDK objects and restored dicts)."""
    if isinstance(tc, dict):
        return {
            "id": tc.get("id"),
            "type": tc.get("type", "function"),
            "function": {
                "name": tc.get("function", {}).get("name"),
                "arguments": tc.get("function", {}).get("arguments", "{}"),
            },
        }
    return {
        "id": tc.id,
        "type": "function",
        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
    }


class Agent:
    def __init__(self, tools):
        self.model = client
        self.tools = tools

        async def make_plan(state: GraphState) -> GraphState:
            resp = self.model.chat.completions.create(
                model=CHAT_MODEL,
                messages=state.messages,
                tools=[t.openai_description for t in self.tools.values()],
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                state.messages.append({"role": "assistant", "content": msg.content or ""})
                state.tool_call = []
            else:
                tool_calls = [_normalize_tool_call(tc) for tc in msg.tool_calls]
                state.messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": tool_calls,
                })
                state.tool_call = tool_calls

            return GraphState.model_validate(state)

        async def execute_plan(state: GraphState) -> GraphState:
            pending = list(state.tool_call)
            state.tool_call = []

            for raw in pending:
                tc = _normalize_tool_call(raw)
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"] or "{}")
                except json.JSONDecodeError:
                    args = {}

                if name not in self.tools:
                    res = f"tool '{name}' is not registered"
                else:
                    try:
                        res = await self.tools[name].tool(**args)
                    except Exception as exc:
                        res = f"tool '{name}' raised: {exc}"

                if res is None:
                    res = ""
                if not isinstance(res, str):
                    res = json.dumps(res, ensure_ascii=False, default=str)

                state.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": res,
                })

            return GraphState.model_validate(state)

        async def has_steps(state: GraphState) -> bool:
            return len(state.tool_call) > 0

        builder = StateGraph(GraphState)
        builder.add_node("planner", make_plan)
        builder.add_node("executor", execute_plan)
        builder.add_edge(START, "planner")
        builder.add_edge("executor", "planner")
        builder.add_conditional_edges("planner", has_steps, {True: "executor", False: END})

        self.graph = builder.compile(checkpointer=MemorySaver())

    async def ainvoke(self, message: str, chat_id: str, user_id: int,
                      user_token: str, system_prompt: str = "Ты полезный ассистент"):
        user_message = {"role": "user", "content": message}

        try:
            restored = self.graph.get_state(config={"configurable": {"thread_id": chat_id}}).values
            restored_state = GraphState(**restored)
            state = GraphState(
                messages=restored_state.messages + [user_message],
                tool_call=[],
                user=restored_state.user,
                user_id=restored_state.user_id,
                user_token=user_token,
            )
        except Exception:
            state = GraphState(
                messages=[
                    {"role": "system", "content": system_prompt},
                    user_message,
                ],
                tool_call=[],
                user=chat_id,
                user_id=user_id,
                user_token=user_token,
            )

        result = await self.graph.ainvoke(
            state, config={"configurable": {"thread_id": chat_id}}
        )
        return GraphState.model_validate(result).messages
