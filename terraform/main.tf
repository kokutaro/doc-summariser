locals {
  name = "roles"
  roles_for_cloud_run_sa = [
    "roles/datastore.user",
    "roles/storage.objectUser",
    "roles/storage.hmacKeyAdmin",
    "roles/discoveryengine.editor",
    "roles/run.invoker",
    "roles/aiplatform.user",
    "roles/iam.serviceAccountTokenCreator",
    "roles/logging.logWriter"
  ]
  roles_for_builder = [
    "roles/run.admin",
    "roles/artifactregistry.admin",
    "roles/iam.serviceAccountUser"
  ]
  roles_for_event_arc_sa = [
    "roles/run.invoker",
    "roles/eventarc.eventReceiver",
    "roles/pubsub.publisher"
  ]
}

resource "google_service_account" "main" {
  account_id   = "sa-${var.cloud_run_service_name}"
  display_name = "Cloud Run Service Account for ${var.cloud_run_service_name}"
}

resource "google_service_account" "builder" {
  account_id   = "sa-${var.cloud_run_service_name}-builder"
  display_name = "Service Account for Builder of ${var.cloud_run_service_name}"
}

resource "google_service_account" "event_arc" {
  account_id   = "sa-${var.cloud_run_service_name}-event-arc"
  display_name = "Service account for EventArc of ${var.cloud_run_service_name}"
}

resource "google_project_iam_member" "cloud_run_sa_roles" {
  project  = var.project_id
  for_each = toset(local.roles_for_cloud_run_sa)
  role     = each.key
  member   = "serviceAccount:${google_service_account.main.email}"
}

resource "google_project_iam_member" "builder_roles" {
  project  = var.project_id
  for_each = toset(local.roles_for_builder)
  role     = each.key
  member   = "serviceAccount:${google_service_account.builder.email}"
}

resource "google_project_iam_member" "event_arc_sa_roles" {
  project  = var.project_id
  for_each = toset(local.roles_for_event_arc_sa)
  role     = each.key
  member   = "serviceAccount:${google_service_account.event_arc.email}"
}

resource "google_iam_workload_identity_pool" "main" {
  workload_identity_pool_id = "gh-${var.cloud_run_service_name}"
  display_name              = "GH Actions for ${var.cloud_run_service_name}"
  description               = "GH Actions for ${var.cloud_run_service_name}"
  disabled                  = false
  project                   = var.project_id
}

resource "google_iam_workload_identity_pool_provider" "name" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.main.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "Github"
  description                        = "Github Provider"
  disabled                           = false
  attribute_condition                = "assertion.repository_owner == \"${var.github_repo_owner_name}\""
  attribute_mapping = {
    "google.subject" = "assertion.repository"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
  project = var.project_id
}

resource "google_service_account_iam_member" "workload_identity_sa_iam" {
  service_account_id = google_service_account.builder.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principal://iam.googleapis.com/${google_iam_workload_identity_pool.main.name}/subject/${var.github_repo_owner_name}/${var.github_repo_name}"
}

resource "google_storage_bucket" "uploads" {
  name                        = var.upload_bucket_name
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "outputs" {
  name                        = var.output_bucket_name
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true
}

resource "google_cloud_run_v2_service" "default" {
  name     = var.cloud_run_service_name
  location = var.region
  template {
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello"

      resources {
        limits = {
          memory = "512Mi"
          cpu    = "1"
        }
      }
    }
    service_account = google_service_account.main.email
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  lifecycle {
    ignore_changes = [
      client,
      client_version,
      template[0].containers[0].image,
      template[0].containers[0].name,
      template[0].containers[0].resources,
      template[0].labels["commit-sha"],
      template[0].labels["managed-by"]
    ]
  }
}

resource "google_eventarc_trigger" "trigger" {
  name = "${var.cloud_run_service_name}-event-arc-trigger"
  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.uploads.name
  }
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }
  project  = var.project_id
  location = var.region

  service_account = google_service_account.event_arc.email

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.default.name
      region  = google_cloud_run_v2_service.default.location
    }
  }
}

resource "google_artifact_registry_repository" "main" {
  location      = var.region
  project       = var.project_id
  repository_id = var.cloud_run_service_name
  format        = "DOCKER"
}
