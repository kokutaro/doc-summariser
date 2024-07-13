import json
import re
import google.cloud.logging
from flask import Flask, request, jsonify
from google.cloud import storage
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from doc_summariser import summarise_doc
from image_util import download_and_extract_images
from json_util import check_json_format

app = Flask(__name__)
app.json.ensure_ascii = False
client = google.cloud.logging.Client()
client.setup_logging()


@app.route("/", methods=["POST"])
def main():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400

    bucket_name = data.get("bucket")
    file_name = data.get("file")

    if not bucket_name or not file_name:
        return jsonify({"error": "Missing bucket or file in request body"}), 400

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    file = bucket.blob(file_name)
    if not file.exists():
        return jsonify({"error": "File not found in bucket"}), 400

    image_paths = download_and_extract_images(bucket_name, file_name)

    summarised = summarise_doc(
        pdf_path=f"gs://{bucket_name}/{file_name}",
        img_paths=image_paths,
    )

    json_data = re.sub("```json", "", summarised)
    json_data = re.sub("```", "", json_data)

    if not check_json_format(json_data):
        return jsonify({"error": "LLM generated invalid JSON format"}), 500

    return jsonify({"documents": json.loads(json_data)}), 200


def embed_text(
    texts: list[str] = ["banana muffins? ", "banana bread? banana muffins?"],
    task: str = "RETRIEVAL_DOCUMENT",
    model_name: str = "	text-multilingual-embedding-002",
    dimensionality: int | None = 256,
) -> list[list[float]]:
    """Embeds texts with a pre-trained, foundational model."""
    model = TextEmbeddingModel.from_pretrained(model_name)
    inputs = [TextEmbeddingInput(text, task) for text in texts]
    kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
    embeddings = model.get_embeddings(inputs, **kwargs)
    return [embedding.values for embedding in embeddings]


if __name__ == "__main__":
    app.run(debug=True, port=8080)
