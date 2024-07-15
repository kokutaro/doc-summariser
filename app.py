import hashlib
import json
import logging
from os import getenv
import re
import sys
import google.cloud.logging
from flask import Flask, request, jsonify
from google.cloud import storage
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from doc_summariser import summarise_doc
from image_util import download_and_extract_images
from json_util import check_json_format
from uuid import uuid4 as uuid


Log_Format = "%(levelname)s %(asctime)s - %(message)s"

if __name__ == "__main__":
    import dotenv

    dotenv.load_dotenv()
    logging.basicConfig(
        stream=sys.stdout,
        filemode="w",
        format=Log_Format,
        level=logging.INFO,
    )
else:
    client = google.cloud.logging.Client()
    client.setup_logging()

OUTPUT_BUCKET_NAME = getenv("OUTPUT_BUCKET_NAME")

if OUTPUT_BUCKET_NAME is None:
    raise ValueError("OUTPUT_BUCKET_NAME must be set")

app = Flask(__name__)
app.json.ensure_ascii = False

logger = logging.getLogger(__name__)


@app.route("/", methods=["POST"])
def main():
    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 415

    bucket_name = data.get("bucket")
    file_name = data.get("name")

    if not bucket_name or not file_name:
        return jsonify({"error": "Missing bucket or file in request body"}), 400

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    file = bucket.blob(file_name)
    if not file.exists():
        return jsonify({"error": "File not found in bucket"}), 404
    if re.match(r".*?\.pdf$", file.name) is None:
        logging.info(
            "Content type of file of %s is %s.",
            file_name,
            re.sub(r".*?\.(\w+$)", "\\1", file.name),
        )
        return jsonify({"message": "No file processed. File is not a PDF"}), 200

    hasher = hashlib.sha256()

    hasher.update(file.download_as_bytes())
    file_hash = hasher.hexdigest()

    jsonl_file = storage_client.bucket(OUTPUT_BUCKET_NAME).blob("documents.jsonl")
    jsonl_text = ""
    if jsonl_file.exists():
        jsonl_text = jsonl_file.download_as_text()

    if file_hash in jsonl_text:
        logger.info("File %s already processed.", file_name)
        return jsonify({"message": "File already processed"}), 200

    image_paths = download_and_extract_images(
        bucket_name, file_name, OUTPUT_BUCKET_NAME
    )

    summarised = summarise_doc(
        pdf_path=f"gs://{bucket_name}/{file_name}",
        img_paths=image_paths,
    )

    json_data = re.sub("```json", "", summarised)
    json_data = re.sub("```", "", json_data)

    if not check_json_format(json_data):
        logger.warning("LLM generated invalid JSON format.\n%s", json_data)
        return jsonify({"error": "LLM generated invalid JSON format"}), 500

    struct_data = json.loads(json_data)
    struct_data["file_hash"] = file_hash

    doc_data = {
        "id": str(uuid()),
        "content": {
            "mimeType": "application/pdf",
            "uri": f"gs://{bucket_name}/{file_name}",
        },
        "structData": struct_data,
    }

    json_line = json.dumps(doc_data, ensure_ascii=False)

    jsonl_text += json_line + "\n"
    jsonl_file.upload_from_string(jsonl_text, content_type="application/json")

    return jsonify({"documents": doc_data}), 200


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
