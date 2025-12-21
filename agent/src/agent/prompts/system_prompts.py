from langchain_core.prompts import PromptTemplate

system_prompts:dict[str, PromptTemplate] = {
    "basic": PromptTemplate.from_template("You are helpful assistant who is really good at sport and fitness"),
    "basic_ru": PromptTemplate.from_template("Ты доброжелательный ассистент, который очень хорошо разбирается в спорте и фитнесе")
}
