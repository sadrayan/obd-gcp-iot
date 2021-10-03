variable "project_id" {
    description = "The project ID where all resources will be launched."
    default     = "obd-iot"
    type        = string
}

variable "region" {
    description = "The location region to deploy the Cloud IOT services. Note: Be sure to pick a region that supports Cloud IOT."
    default     = "us-central1"
    type        = string
}

variable "zone" {
    description = "The location zone to deploy the Cloud IOT services. Note: Be sure to pick a region that supports Cloud IOT."
    default     = "us-central1-a"
    type        = string
}
