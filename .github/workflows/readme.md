# Build and Deploy to Cloud Run

This GitHub Actions workflow automates the build, tagging, pushing, and deployment of a container image to Google Cloud Run.

## Workflow Overview

1. Trigger: The workflow is triggered on two events:
   - Workflow Dispatch: Manually triggered by a user.
   - Push: Triggered when a push event occurs on the main branch, excluding changes to terraform and .devcontainer directories.
1. Jobs: The workflow contains a single job named deploy.
1. Deploy Job:
   - Environment: Runs on the ubuntu-latest runner.
   - Permissions: Requires write access to ID tokens and read access to repository contents.
   - Steps:
     - Checkout: Checks out the repository code.
     - Set up Buildx: Sets up Docker Buildx for building multi-platform images.
     - Set Metadata: Uses the docker/metadata-action to generate tags based on the image version and commit SHA.
     - Authenticate to Google Cloud: Authenticates to Google Cloud using a service account and workload identity federation.
     - Set up Cloud SDK: Installs the Google Cloud SDK.
     - Docker Auth: Authenticates to the Google Container Registry.
     - Build, Tag, and Push Container: Builds, tags, and pushes the container image to the Google Container Registry.
     - Create Service Declaration: Generates a Cloud Run service YAML file using a template and environment variables.
     - Deploy to Cloud Run: Deploys the container image to Cloud Run using the generated service YAML file.
     - Show Output: Prints the URL of the deployed Cloud Run service.

## Configuration

- Secrets:
  - `WIF_PROVIDER`: The workload identity provider used for authentication.
  - `WIF_SERVICE_ACCOUNT`: The service account used for authentication.
- Variables:
  - `REGION`: The Google Cloud region where the Cloud Run service will be deployed.
  - `PROJECT_ID`: The Google Cloud project ID.
  - `SERVICE`: The name of the Cloud Run service.
  - `OUTPUT_BUCKET_NAME`: The name of the Google Cloud Storage bucket used for storing service logs.

## Usage

1. Configure the required secrets and variables in your repository settings.
1. Trigger the workflow manually using the "Workflow Dispatch" option or by pushing changes to the main branch.
1. The workflow will build, tag, push, and deploy your container image to Cloud Run.
