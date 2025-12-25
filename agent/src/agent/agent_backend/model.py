from openai import OpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage

client = OpenAI(

        base_url="https://llm.api.cloud.yandex.net/v1",
        project="b1g1q1f6qkc2rbf6anvo"
    )




def call_llm(messages):
    resp = client.chat.completions.create(
        model="gpt://b1g1q1f6qkc2rbf6anvo/qwen3-235b-a22b-fp8/latest",
        messages=[
            {"role": "user", "content": m}
            for m in messages
        ],
        tools=[],
    )
    return AIMessage(content=resp.choices[0].message.content)

llm = RunnableLambda(call_llm)
