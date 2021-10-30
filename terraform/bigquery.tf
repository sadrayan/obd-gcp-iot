resource "google_bigquery_dataset" "dataset" {
  dataset_id    = "${var.project_id}_dataset"
  friendly_name = "cvt_iot"
  location      = "US"
  description   = "CVT IOT dataset"

  default_table_expiration_ms = 3600000

  labels = {
    env = "cvy_iot"
  }
}


resource "google_bigquery_table" "device_data" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "${var.project_id}_device_data"
  # schema = file("${path.module}/schema.json")
  labels = {
    env = "cvy_iot"
  }
}