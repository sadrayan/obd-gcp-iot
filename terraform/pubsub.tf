resource "google_pubsub_topic" "iot_devicestatus" {
  name = "iot_devicestatus"
}

resource "google_pubsub_topic" "iot_telemetry" {
  name = "iot_telemetry"
}

resource "google_pubsub_topic" "mender_response_topic" {
  name = "mender_response_topic"
}

resource "google_pubsub_subscription" "mender_response_sub" {
  name  = "mender_response_sub"
  topic = google_pubsub_topic.mender_response_topic.name
  ack_deadline_seconds = 300
}

resource "google_pubsub_subscription" "iot_telemetry_sub" {
  name  = "iot_telemetry_sub"
  topic = google_pubsub_topic.iot_telemetry.name
  ack_deadline_seconds = 300
}