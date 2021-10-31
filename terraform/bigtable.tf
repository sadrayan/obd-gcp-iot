# resource "google_bigtable_instance" "instance" {
#   name = "${var.project_id}_bt_instance"

#   cluster {
#     cluster_id   = "bt_instance_cluster"
#     zone         = "us-central1-b"
#     num_nodes    = 1
#     storage_type = "HDD"
#   }

#   lifecycle {
#     prevent_destroy = true
#   }
# }

# resource "google_bigtable_table" "table" {
#   name          = "${var.project_id}_bt_table"
#   instance_name = google_bigtable_instance.instance.name

#   lifecycle {
#     prevent_destroy = true
#   }
# }