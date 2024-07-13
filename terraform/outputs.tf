output "GHA_WORKLOAD_IDENTITY_POOL" {
  value = google_iam_workload_identity_pool.main.name
}

output "GHA_WORKLOAD_IDENTITY_POOL_PROVIDER" {
  value = google_iam_workload_identity_pool_provider.name
}

output "GHA_SERVICE_ACCOUNT_EMAIL" {
  value = google_service_account.builder.email
}
