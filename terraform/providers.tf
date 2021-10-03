provider "google" {
  project = var.project_id
  region  = var.region
}

terraform {
  backend "gcs" {
    bucket = "obd-iot-tf-state"
    prefix = "terraform/state"
  }
}