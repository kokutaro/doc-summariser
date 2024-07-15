import logging
import os
import vertexai
import vertexai.generative_models
from vertexai.generative_models import Part

PRICE_PER_INPUT_MTOKEN = os.environ.get("PRICE_PER_INPUT_MTOKEN", 0.35)
PRICE_PER_OUTPUT_MTOKEN = os.environ.get("PRICE_PER_INPUT_MTOKEN", 1.05)


def summarise_doc(pdf_path: str, img_paths: list[str]) -> str:
    vertexai.init()
    model = vertexai.generative_models.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=vertexai.generative_models.GenerationConfig(
            temperature=0.5, max_output_tokens=8192
        ),
    )

    parts = []
    parts.append(
        """### 指示
与えられた文章の内容を以下の手順抽出し、以下のJSONスキーマに従った形式でJSON形式で出力してください。必須項目以外については、抽出した文章にその情報がある場合のみ出力してください。

### 出力手順
1. ### 文章に添付されたPDFを読み込み、その内容をマークダウン形式で抽出する。
2. ### 関連画像に添付された画像に、1. で読み込んだ文章を補足するものがあれば、その画像の説明を1. で抽出した文章内の適切な位置に付与する。
3. ### 関連画像に添付された各画像について、1. で抽出した文章をもとに、簡単な画像の説明を行う。
4. "content"に2. で出力した内容、"images"に3. で出力した各イメージの情報を格納したJSON形式の文字列を出力する。

### 文章
"""
    )
    parts.append(Part.from_uri(uri=pdf_path, mime_type="application/pdf"))
    parts.append("### JSONスキーマ")
    parts.append(open("summarised_doc.schema.json").read())
    parts.append("### 関連画像")
    for i, img_path in enumerate(img_paths):
        parts.append(f"- Image {i+1}: {img_path}")
        parts.append(Part.from_uri(uri=img_path, mime_type="image/png"))

    response = model.generate_content(contents=parts, stream=False)
    input_price = (
        PRICE_PER_INPUT_MTOKEN * response.usage_metadata.prompt_token_count / 1_000_000
    )
    output_price = (
        PRICE_PER_OUTPUT_MTOKEN
        * response.usage_metadata.candidates_token_count
        / 1_000_000
    )
    total_price = input_price + output_price
    logging.info(
        "Input price: %s, Output price: %s, Total price: %s",
        input_price,
        output_price,
        total_price,
    )

    return response.text
