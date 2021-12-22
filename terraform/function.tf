locals {
  timestamp = formatdate("YYMMDDhhmmss", timestamp())
  root_dir  = abspath("../")
}

# Compress source code
data "archive_file" "source" {
  type        = "zip"
  source_dir  = "../app/src/"
  output_path = "/tmp/function_${local.timestamp}.zip"
}

resource "google_storage_bucket_object" "zip" {
  # Append file MD5 to force bucket to be recreated
  name   = "source.zip#${data.archive_file.source.output_md5}"
  bucket = google_storage_bucket.bucket.name
  source = data.archive_file.source.output_path
}

# Create Cloud Function
resource "google_cloudfunctions_function" "function" {
  name    = "device_function"
  runtime = "nodejs16"

  available_memory_mb   = 1024
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.zip.name
  entry_point           = "listDevice"

  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.bucket_data.name
  }

  environment_variables = {
    MENDER_USERNAME       = var.MENDER_USERNAME
    MENDER_PASSWORD       = var.MENDER_PASSWORD
    MENDER_RESPONSE_TOPIC = google_pubsub_topic.mender_response_topic.name
  }
}

# Create IAM entry so all users can invoke the function
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role   = "roles/cloudfunctions.invoker"
  member = "allUsers"
}

# output "function_url" {
#     value = google_cloudfunctions_function.function.function_url
# }