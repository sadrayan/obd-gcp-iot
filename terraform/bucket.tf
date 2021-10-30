resource "google_storage_bucket" "bucket_data" {
  name = "${var.project_id}_data_deployment"
}