# Deploying a Cloud Run Environment with Terraform

This README outlines the steps for deploying a Cloud Run environment using Terraform. This deployment includes:

- Cloud Run Service: A Cloud Run service running a container image.
- Service Accounts: Dedicated service accounts for Cloud Run, Builder, and EventArc.
- IAM Roles: Granting necessary permissions to service accounts.
- Workload Identity: Enabling secure authentication from GitHub Actions.
- Storage Buckets: Dedicated buckets for uploads and outputs.
- EventArc Trigger: Triggering the Cloud Run service on new uploads to the uploads bucket.
- Artifact Registry: Storing the container image.

## Prerequisites:

- Google Cloud Project: A Google Cloud project with necessary permissions.
- Terraform: Installed and configured with Google Cloud credentials.
- GitHub Repository: A GitHub repository containing the container image.
- GitHub Actions: Enabled for the repository.

## Configuration:

### Variables:

- `project_id`: Your Google Cloud project ID.
- `cloud_run_service_name`: The name of your Cloud Run service.
- `region`: The region where your Cloud Run service will be deployed.
- `upload_bucket_name`: The name of the bucket for uploads.
- `output_bucket_name`: The name of the bucket for outputs.
- `github_repo_owner_name`: The owner of the GitHub repository.
- `github_repo_name`: The name of the GitHub repository.

### Terraform Code:

The provided `main.tf` file contains the Terraform code for deploying the environment.

## Deployment:

### Initialize Terraform:

```shell
terraform init
```

### Apply Terraform:

```shell
terraform apply -auto-approve
```

### Verification:

- Cloud Run Service: Verify the Cloud Run service is running in the Google Cloud Console.
- Service Accounts: Verify the service accounts are created and have the correct IAM roles.
- Workload Identity: Verify the workload identity pool and provider are configured.
- Storage Buckets: Verify the storage buckets are created.
- EventArc Trigger: Verify the EventArc trigger is configured and listening for events.
- Artifact Registry: Verify the Artifact Registry repository is created.

## GitHub Actions Integration:

### Configure GitHub Actions:

- Create a workflow file in your GitHub repository to build and push the container image to Artifact Registry.
- Use the `google-github-actions/auth` action to authenticate with Google Cloud.
- Use the `google-github-actions/buildpacks` action to build the container image.
- Use the `google-github-actions/artifact-registry` action to push the image to Artifact Registry.

### Trigger Workflow:

- Trigger the workflow on push events to the repository.

## Notes:

- This deployment uses the `google_cloud_run_v2_service` resource, which is the latest version of the Cloud Run service resource.
- The `google_iam_workload_identity_pool` and `google_iam_workload_identity_pool_provider` resources are used to enable secure authentication from GitHub Actions.
- The `google_eventarc_trigger` resource is used to trigger the Cloud Run service on new uploads to the uploads bucket.
- The `google_artifact_registry_repository` resource is used to store the container image.

## Troubleshooting:

- Permissions: Ensure that your Google Cloud project has the necessary permissions for all the resources being deployed.
- GitHub Actions: Verify that your GitHub Actions workflow is configured correctly and has the necessary permissions to access Google Cloud.
- Terraform: Check the Terraform logs for any errors.

## Further Development:

- Custom Domains: Configure custom domains for your Cloud Run service.
- Traffic Management: Implement traffic management rules to control traffic flow to your service.
- Monitoring and Logging: Set up monitoring and logging for your Cloud Run service.
- Security: Implement security best practices for your Cloud Run environment.
