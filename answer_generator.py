import json
import vertexai
import vertexai.generative_models


def generate_answer(question: str, context: list[dict]) -> str:
    """Generates an answer to a question based on a given context.

    Args:
        question (str): The question to be answered.
        context (list[dict]): A list of dictionaries containing context information.

    Returns:
        str: The generated answer.
    """
    context_json = json.dumps(context, ensure_ascii=False, indent=2)
    vertexai.init()
    model = vertexai.generative_models.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=vertexai.generative_models.GenerationConfig(
            temperature=0.5, max_output_tokens=8192
        ),
    )

    parts = []

    parts.append(
        """以下のコンテキスト情報をもとに、ユーザーからの質問に回答してください。
画像の情報は![<img_description>](<img_path>)の形式で出力してください。画像の情報を出力する行はそれ以外の情報は出力しないでください。"""
    )

    parts.append(f"contenxt: {context_json}")
    parts.append("input: " + question)
    parts.append("output:")

    response = model.generate_content(contents=parts, stream=False)

    return response.text
