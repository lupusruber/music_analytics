# Music Analytics Data Engineering Project

This project focuses on building a data pipeline for processing music event data in real-time using Apache Kafka, Google Cloud Dataproc, and Apache Spark. The pipeline processes events such as page views and listen events, transforms them into different dimensional tables and facts, and stores them for further analytics.

## Dashboard
![Dashboard](https://github.com/lupusruber/music_analytics/blob/master/images/Dashboard.png)

## Data Modelling with Kimball's Approach
![Model](https://github.com/lupusruber/music_analytics/blob/master/images/Data%20Model.png)



## Technologies Used

- **Apache Kafka**: Event streaming platform for managing real-time data streams.
- **Kubernetes**: Manages Kafka and other services in a containerized environment.
- **Apache Spark (Pyspark)**: Processes large-scale data in real-time using Dataproc clusters.
- **Google Cloud Dataproc**: Managed Spark and Hadoop service in Google Cloud.
- **Google Big Query**: DWH storage for the processed data.
- **Airflow**: Orchestrates the execution of the pipeline.
- **Terraform**: Infrastructure as code for provisioning cloud resources.
- **Python**: The main language used for data transformation scripts.

## Solution Architecture
![Solution Architecture](https://github.com/lupusruber/music_analytics/blob/master/images/Solution%20Architecture-Page-1.jpg)

## Project Structure

- **commands**: Contains scripts related to running and interacting with Kafka and Spark.
- **deprecated**: Contains older versions of scripts, including Kafka consumers and producers.
- **docker-eventsim**: Contains Docker files and scripts to simulate event data.
- **images**: Contains architectural diagrams and visualizations.
- **infrastructure**: Contains Terraform files for setting up infrastructure (Kafka on GKE, Docker containers, etc.).
- **scripts**: Contains Python scripts for transforming the event data into dimensional models and facts.
- **requirements.txt**: Python dependencies required for the project.
- **README.md**: Project documentation.

## Data Pipeline Overview

The project consists of multiple data streams from two main event types generated from a syntetic data generator called Eventsim:

- **Page View Events**: Represents users viewing pages in the music app.
- **Listen Events**: Represents users listening to songs.

THhe eventsim docker containers is run while connected to Kafka and directly puts the generated data into Kafka.

These streams are processed through different **dimensional tables** and **fact tables**:

- **Dimensional Tables**: Includes `song_dim`, `location_dim`, `date_and_date_time_dim`, `user_dim`, `event_dim`, `session_dim_and_bridge`.
- **Fact Tables**: Includes `event_fact`, `session_fact`.

The pipeline operates as follows:

1. **Kafka Consumer**: The `dims.py` file reads messages from Kafka topics (`PAGE_VIEW_EVENTS_TOPIC` and `LISTEN_EVENTS_TOPIC`).
2. **Stream Processing**: Each event stream is processed and transformed into a corresponding dimension or fact table using PySpark.
3. **Storage**: The processed data is directly stored in BigQuery for analytics.
4. **Visualization**: The data is visualized on a Power Bi dashboard that showcases real-time data from Big Query

## Airflow Orchestration

Airflow executes two main scripts for handling the data pipeline:

1. **Generating BigQuery Tables**: To generate scripts for transforming data into BigQuery tables, Airflow triggers the following command:

```bash
gcloud dataproc jobs submit pyspark \
  --cluster=dataproc-cluster \
  --region=us-central1 \
  --py-files=scripts.zip \
  --properties-file=config.yaml \
  generate_big_query_tables.py
```

2. **Continuous Streaming Job:** For a continuous streaming job, Airflow triggers the following command:
```bash
gcloud dataproc jobs submit pyspark \
  --cluster=dataproc-cluster \
  --region=us-central1 \
  --py-files=scripts.zip \
  --properties-file=config.yaml \
  dims.py
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/lupusruber/music_analytics.git
cd music_analytics
```

### 2. Install Requirements

Install the necessary Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Set Up Infrastructure with Terraform

Run Terraform to set up your Google Cloud resources (e.g., GKE cluster, Kafka, Dataproc):

```bash
cd infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 4. Deploy Kafka on Kubernetes

Ensure that your Kubernetes cluster is set up and running. Use Helm or kubectl to deploy the Kafka cluster and other related services.

### 5. Run the Data Pipeline with Airflow

1. Set up Airflow to orchestrate the pipeline. Ensure that your Airflow environment is configured to run Spark jobs on Dataproc.
2. Run the DAG to start the data processing pipeline.

### 6. Run the Python Scripts

To manually start the pipeline, you can run the `dims.py` script on Dataproc or in your local environment:

```bash
python scripts/dims.py
```

### 7. Monitoring and Logs

- Logs are available in the Airflow UI for task execution status.
- Data processing logs are captured by Spark in the Dataproc cluster and can be monitored using GCP’s logging service.

## Data Transformation Logic

The main transformation logic is contained within the Python scripts located in the `scripts` directory. Each script processes a different dimension or fact, such as:

- `*_dim.py`: Processes data into a dim table.
- `*_fact.py`: Processes data into a fact table.

The `dims.py` script acts as the orchestrator, creating data streams from the Kafka topics and calling the appropriate transformation function for each stream.

## Running the Pipeline

- `*configs.py`: Handles the configuration logic to connect to the Kafka clusters, the Dataproc Spark cluster, the BigQuery Warehouse etc.

Once everything is set up, the data processing pipeline will automatically start consuming events from Kafka and applying the necessary transformations to store them in BigQuery. Each transformation is designed to run indefinitely (i.e., `awaitTermination`), processing incoming events in real-time.

You can stop the process by interrupting the script execution with `Ctrl + C` or terminate the Airflow job.

## Notes

- Ensure that you have the correct permissions and credentials to interact with Google Cloud services (GCS, BigQuery, Dataproc).
- Modify the Kafka topics (`PAGE_VIEW_EVENTS_TOPIC`, `LISTEN_EVENTS_TOPIC`) in the `configs.py` file if needed.
- Make sure your Dataproc cluster is properly configured to handle PySpark jobs.
- You may need to adjust the configuration settings for your specific environment, such as GCS buckets, Kafka configurations, and Dataproc settings.
- Each script in the scripts/ folder handles a different table form the DWH model
- fill_session_fact_table.py is the batch processing job for the session fact table
- schemas.py defines the schemas for both the raw and dwh tables
- util_functions.py handles the RW operations from different databases
- configs.py has all the configurations for the raw and dwh models

## Troubleshooting

- **Kafka Issues**: Ensure that your Kafka cluster is running and accessible from your Dataproc cluster.
- **Permission Errors**: Check your service account permissions in Google Cloud, especially for GCS and BigQuery.
- **Spark Issues**: Review the logs in Dataproc for any errors related to the PySpark jobs.

For further assistance, feel free to raise an issue in the repository.

