from fastapi import FastAPI
from retriever.routers import ExerciseRouter, UserRouter
from llama_cpp import Llama, ChatCompletionRequestMessage

llm = Llama.from_pretrained(
	repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
	filename="qwen2.5-1.5b-instruct-fp16.gguf",
)

app = FastAPI(title="Retriever Service")

app.include_router(ExerciseRouter)
app.include_router(UserRouter)

@app.get("/")
def root():
    return {"status": "ok", "message": "Retriever is alive. Maybe i won't be sson"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
