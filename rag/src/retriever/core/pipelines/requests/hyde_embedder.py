import torch
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama, ChatCompletionRequestMessage

llm = Llama.from_pretrained(
	repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
	filename="qwen2.5-1.5b-instruct-fp16.gguf",
)

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Ты используешься в HyDE для RAG-системы. "
        "Отвечай ТОЛЬКО на русском языке. "
        "Сгенерируй реалистичный, информативный текст, "
        "который мог бы быть ответом на вопрос пользователя. "
        "Не упоминай, что это гипотеза. "
        "Не задавай вопросов. "
        "Без воды и вступлений."
    )
}



class HydeEmbedder:
    def __init__(self, system_prompt_on: bool = True):
        self.llm = llm
        self.system_prompt_on = system_prompt_on

        self.system_prompt = SYSTEM_PROMPT
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def __call__(self, request: str, **kwargs):
        messages = []

        if self.system_prompt_on:
            messages.append(self.system_prompt)

        messages.append({
            "role": "user",
            "content": request
        })

        res = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=256,
            temperature=0.7,
        )

        print(res)

        hyde_text = str(res["choices"][0]["message"]["content"])
        return [self.embedder.encode(hyde_text)]
