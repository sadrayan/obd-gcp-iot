resource "google_dataflow_job" "telemetry_to_bq_job" {
  name              = "telemetry_to_bq_cvt_iot"
  max_workers       = 1
  on_delete         = "cancel"
  template_gcs_path = "gs://dataflow-templates-us-central1/latest/PubSub_to_BigQuery"
  temp_gcs_location = "${google_storage_bucket.bucket_data.url}/tmp"
  parameters = {
    inputTopic      = google_pubsub_topic.iot_telemetry.id
    outputTableSpec = "${var.project_name}:${google_bigquery_table.device_data.dataset_id}.${google_bigquery_table.device_data.table_id}"
  }
}
