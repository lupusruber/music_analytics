provider "google" {
  credentials = file(var.auth_key)
  project     = var.project_id
  region      = var.region
  zone        = var.zone

}

# Airflow VM Instance
resource "google_compute_instance" "airflow_vm" {
  name         = "airflow-vm-instance"
  machine_type = "e2-standard-4" # Upgraded machine type
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
    access_config {} # Required to assign an external IP
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

# Output the external IP of the Airflow VM
output "airflow_vm_external_ip" {
  value = google_compute_instance.airflow_vm.network_interface[0].access_config[0].nat_ip
}

# Dataproc Cluster for Spark
resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = "dataproc-cluster"
  region = var.region


  cluster_config {

    # gce_cluster_config {
    #   internal_ip_only = false

    # }

    master_config {
      num_instances = 1
      machine_type  = "n1-standard-4" # Master node machine type
    }

    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-2" # Worker node machine type
    }

  }
}

# Output the Dataproc cluster details (Cluster name and master node)
output "dataproc_cluster_name" {
  value = google_dataproc_cluster.dataproc_cluster.name
}

output "dataproc_cluster_master_type" {
  value = google_dataproc_cluster.dataproc_cluster.cluster_config[0].master_config[0].machine_type
}


resource "google_cloud_run_v2_job" "default" {
  name     = "data-generate-job"
  location = var.region

  template {
    template {
      containers {
        image = "gcr.io/music-analytics-project/events:latest"

        resources {
          limits = {
            "memory" = "4Gi"
          }
        }

        command = []  # This can be left empty or omitted if you're using the default command in the container

        args = [
          "-c", "examples/example-config.json",
          "--start-time", "2021-01-01T00:00:00",
          "--end-time", "2021-12-01T00:00:00",
          "--nusers", "100",
          "--kafkaBrokerList", "35.189.249.169:9094"
        ]
      }

      # Set the maximum duration for the job execution
      timeout = "600s"  # Adjust the timeout as needed
    }
  }
}
