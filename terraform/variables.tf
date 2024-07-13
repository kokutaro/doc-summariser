variable "project_id" {
  description = "The ID of the project to deploy to"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
}

variable "cloud_run_service_name" {
  description = "The name of the service account running this service"
  type        = string
}

variable "github_repo_owner_name" {
  description = "Github Repository owner name"
  type        = string
}

variable "github_repo_name" {
  description = "Github Repository name"
  type        = string
}

variable "upload_bucket_name" {
  description = "Bucket name to upload file"
  type        = string
}
