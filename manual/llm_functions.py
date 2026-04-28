from openai import OpenAI


def call_llm(model_id: str, messages_to_llm: list[dict]):
    
    client = OpenAI()
    response = client.chat.completions.create(
        model=model_id,
        messages=messages_to_llm
    )
    return response.choices[0].message.content