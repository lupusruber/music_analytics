variable "project_id" {
  default     = "music-analytics-project"
  description = "GCP Project ID"
}

variable "project_name" {
  default     = "music-analytics-project"
  description = "GCP Project Name"
}


variable "region" {
  default     = "us-central1"
  description = "Project Location"
}

variable "zone" {
  default     = "us-central1-a"
  description = "Location zone"
}


variable "auth_key" {
  default     = "/home/lupusruber/music_analytics/keys/music-analytics-project-87df530f458e.json"
  description = "GCP Serivice Account Authentication Key"
}

variable "service_account_email" {
  default     = "music-analytics-service-accoun@music-analytics-project.iam.gserviceaccount.com"
  description = "GCP Service Account"
}