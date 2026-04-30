from openai import BadRequestError, OpenAI


def call_llm(
    model_id: str,
    messages_to_llm: list[dict],
    response_format: dict | None = None,
):
    client = OpenAI()
    kwargs: dict = {"model": model_id, "messages": messages_to_llm}
    if response_format is not None:
        kwargs["response_format"] = response_format
    try:
        response = client.chat.completions.create(**kwargs)
    except BadRequestError:
        if response_format is None:
            raise
        response = client.chat.completions.create(model=model_id, messages=messages_to_llm)
    return response.choices[0].message.content