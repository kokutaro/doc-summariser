import hashlib
import os
import fitz
import shutil
import logging
from google.cloud import storage
from uuid import uuid4 as uuid


def _calculate_sha256_hash(file):
    """Calculates the SHA-256 hash of a file."""
    hasher = hashlib.sha256()

    hasher.update(file)
    return hasher.hexdigest()


def _extract_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        for img in page.get_images():
            xref = img[0]
            base_image = doc.extract_image(xref)
            images.append(base_image)
    return images


def _export_images(extracted_images: list[dict], image_path: str):
    image_hashes = []
    for image in extracted_images:
        image_data = image["image"]
        file_hash = _calculate_sha256_hash(image_data)
        if file_hash in image_hashes:
            continue

        image_hashes.append(file_hash)
        image_filename = f"image_{uuid()}.jpg"
        image_output_path = os.path.join(image_path, image_filename)
        with open(image_output_path, "wb") as f:
            f.write(image_data)
            yield image_output_path


def download_and_extract_images(bucket_name: str, file: str):
    work_dir = "/tmp/work/"
    image_path = os.path.join(work_dir, file.split(".")[0])
    os.makedirs(image_path, exist_ok=True)

    pdf_file = os.path.join(work_dir, file)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file)
    blob.download_to_filename(pdf_file)

    extracted_images = _extract_images(pdf_file)
    image_paths = _export_images(extracted_images, image_path)

    output_uris = []

    for image_path in image_paths:
        bucket = storage_client.bucket(bucket_name)
        blob_name = image_path.replace(work_dir, "")
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(image_path)
        logging.info(
            "Uploaded %s to: gs://%s/%s",
            image_path,
            bucket_name,
            blob_name,
        )
        output_uris.append(f"gs://{bucket_name}/{blob_name}")

    # Clean up working dir
    shutil.rmtree(work_dir)

    return output_uris
