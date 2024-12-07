provider "google" {
  credentials = file(var.auth_key)
  project     = var.project_id
  region      = var.region
  zone        = var.zone

}

resource "google_compute_instance" "airflow_vm" {
  name         = "airflow-vm-instance"
  machine_type = "e2-standard-2"
  zone         = var.zone
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-jammy-v20240904"
    }
  }

  lifecycle {
    ignore_changes = [metadata["ssh-keys"]]
  }

  network_interface {
    network = "default"
    access_config {}
  }

  metadata_startup_script = <<-EOT
  #!/bin/bash
  apt-get update
  apt-get install -y apache2
  systemctl start apache2
  systemctl enable apache2

  # Install necessary dependencies for Airflow
  apt-get install -y python3-pip
  pip3 install apache-airflow
  airflow db init
  airflow webserver -p 8080 -D
  EOT

  tags = ["http-server"]

  service_account {
    email  = var.service_account_email
    scopes = ["cloud-platform"]
  }
}

output "airflow_vm_external_ip" {
  value = google_compute_instance.airflow_vm.network_interface[0].access_config[0].nat_ip
}

resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = "dataproc-cluster"
  region = var.region


  cluster_config {

    endpoint_config {
    enable_http_port_access = true
  }

    gce_cluster_config {
      internal_ip_only = false
      service_account = var.service_account_email
      service_account_scopes = [
        "cloud-platform"
      ]
    }

    lifecycle_config {
      idle_delete_ttl = "7200s" # 8 hours in seconds
    }

    master_config {
      num_instances = 1
      machine_type  = "n1-standard-2"
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-2"
    }

  }
}

output "dataproc_cluster_name" {
  value = google_dataproc_cluster.dataproc_cluster.name
}

output "dataproc_cluster_master_type" {
  value = google_dataproc_cluster.dataproc_cluster.cluster_config[0].master_config[0].machine_type
}


resource "google_cloud_run_v2_job" "default" {
  name                = "data-generate-job"
  location            = var.region
  deletion_protection = false

  template {
    template {
      containers {
        image = "gcr.io/music-analytics-project/events:latest"

        resources {
          limits = {
            "memory" = "4Gi"
          }
        }

        command = []

        args = [
          "-c", "examples/example-config.json",
          "--start-time", "2021-01-01T00:00:00",
          "--end-time", "2021-12-01T00:00:00",
          "--nusers", "100",
          "--kafkaBrokerList", "35.189.249.169:9094"
        ]
      }

      timeout = "600s" # Adjust the timeout as needed
    }
  }

   lifecycle {
    ignore_changes = [
      template[0].template[0].containers[0].resources[0].limits
    ]
  }
}


resource "google_bigquery_dataset" "music_analytics" {
  dataset_id = "music_analytics"
  project    = var.project_id
}


resource "google_storage_bucket" "music_analytics_bucket" {
  name                        = "music_analytics_bucket"
  location                    = var.region
  force_destroy               = true
  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }

    condition {
      age = 21
    }
  }
}


output "bucket_name" {
  value = google_storage_bucket.music_analytics_bucket.name
}