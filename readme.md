# PDF Summarization and Structuring with Google Cloud

This project leverages Google Cloud services to summarize and structure PDF documents, extracting key information and organizing it into a JSON format. The application is triggered by file uploads to a Google Cloud Storage bucket and utilizes a Cloud Run service for processing.

## Functionality

The project performs the following steps:

1. **File Upload Trigger:** The application is triggered when a new file is uploaded to the Google Cloud Storage bucket defined by the `google_storage_bucket.uploads` resource in the Terraform configuration.
2. **Download and Image Extraction:** The PDF is downloaded from the uploads bucket and any embedded images are extracted and stored in a designated output bucket (defined by `google_storage_bucket.outputs`).
3. **PDF Summarization:** The `doc_summariser` module uses a Gemini 1.5 Flash model to summarize the PDF content, including extracted images.
4. **Structure the Summary:** The summarized text is processed to ensure it adheres to a valid JSON format.
5. **Generate Structured JSON Document:** The extracted information is organized into a JSON document, including the file hash, content URI, and structured data.
6. **Store the JSON Document:** The generated JSON document is appended to a `documents.jsonl` file in the output bucket.

## Dependencies

- google-cloud-storage
- google-cloud-logging
- vertexai
- flask
- hashlib
- dotenv (for local development)

## Environment Variables

- `OUTPUT_BUCKET_NAME`: The name of the Google Cloud Storage bucket where the output JSON documents will be stored. This should be set to the value of `var.output_bucket_name` from the Terraform configuration.

## Deployment

The application is deployed as a Cloud Run service defined by the `google_cloud_run_v2_service.default` resource in the Terraform configuration.

## Usage

The application is automatically triggered when a file is uploaded to the Google Cloud Storage bucket defined by `google_storage_bucket.uploads`. The trigger is configured using the `google_eventarc_trigger.trigger` resource in the Terraform configuration.

**Example:**

1. **Upload a PDF file:** Upload a PDF file to the bucket specified by `var.upload_bucket_name` in the Terraform configuration.
2. **Trigger the application:** The `google_eventarc_trigger.trigger` resource will automatically trigger the Cloud Run service to process the uploaded PDF.
3. **Output JSON document:** The processed JSON document will be appended to the `documents.jsonl` file in the bucket specified by `var.output_bucket_name`.

## Notes

- The `doc_summariser` module uses a pre-trained language model from Vertex AI.
- The `image_util` module downloads and extracts images from the PDF.
- The `json_util` module checks the JSON format of the summarized text.
- This project provides a robust solution for summarizing and structuring PDF documents using Google Cloud services. It can be easily integrated into various workflows for data extraction, analysis, and knowledge management.
