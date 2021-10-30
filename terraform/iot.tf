resource "google_pubsub_topic" "iot_devicestatus" {
  name = "iot_devicestatus"
}

resource "google_pubsub_topic" "iot_telemetry" {
  name = "iot_telemetry"
}


resource "google_cloudiot_registry" "obd-iot-registry" {
  name = "obd_iot_registry"

  event_notification_configs {
    pubsub_topic_name = google_pubsub_topic.iot_telemetry.id
    subfolder_matches = ""
  }

  state_notification_config = {
    pubsub_topic_name = google_pubsub_topic.iot_devicestatus.id
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
  #       certificate = file("test_fixtures/rsa_cert.pem")
  #     }
  #   }
}