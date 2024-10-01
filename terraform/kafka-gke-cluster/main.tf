terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 3.5"
    }
  }
}

provider "google" {
  credentials = file(var.auth_key)
  project     = var.project_id
  region      = var.region
}

resource "google_container_cluster" "gke_cluster" {
  name               = "kafka-cluster"
  location           = var.region
  initial_node_count = 2

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 50
    oauth_scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

data "google_client_config" "default" {}

output "gke_cluster_endpoint" {
  value = google_container_cluster.gke_cluster.endpoint
}

output "gke_cluster_token" {
  value     = data.google_client_config.default.access_token
  sensitive = true
}

output "gke_cluster_ca_certificate" {
  value     = base64decode(google_container_cluster.gke_cluster.master_auth[0].cluster_ca_certificate)
  sensitive = true
}
