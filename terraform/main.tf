#-------------------------------------------------------
# Enable APIs
#    - Cloud Function
#    - Pub/Sub
#    - Firestore
#    - Cloud IoT
#    - Dataflow
#-------------------------------------------------------

module "project_services" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "10.1.1"

  project_id    = var.project_id
  activate_apis =  [
    "cloudresourcemanager.googleapis.com",
    "cloudfunctions.googleapis.com",
    "pubsub.googleapis.com",
    "firestore.googleapis.com",
    "dataflow.googleapis.com",
    "cloudiot.googleapis.com"
  ]

  disable_services_on_destroy = false
  disable_dependent_services  = false
}

resource "google_storage_bucket" "bucket" {
  name = "test-bucket-random-1231111"
}