resource "google_pubsub_topic" "iot-devicestatus" {
  name = "iot-devicestatus"
}

resource "google_pubsub_topic" "iot-telemetry" {
  name = "iot-telemetry"
}


resource "google_cloudiot_registry" "obd-iot-registry" {
  name = "obd-iot-registry"

  event_notification_configs {
    pubsub_topic_name = google_pubsub_topic.iot-telemetry.id
    subfolder_matches = ""
  }

  state_notification_config = {
    pubsub_topic_name = google_pubsub_topic.iot-devicestatus.id
  }

  mqtt_config = {
    mqtt_enabled_state = "MQTT_ENABLED"
  }

  http_config = {
    http_enabled_state = "HTTP_ENABLED"
  }

  log_level = "INFO"

  #   credentials {
  #     public_key_certificate = {
  #       format      = "X509_CERTIFICATE_PEM"
  #       certificate = file("test-fixtures/rsa_cert.pem")
  #     }
  #   }
}