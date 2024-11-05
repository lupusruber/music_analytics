# Music Analytics Data Engineering Project

## 1. Solution Architecture
![Solution Architecture](https://github.com/lupusruber/crypto_stats/blob/master/Images/ETL%20Pipeline.png)

## 2. Scripts

Each script in the scripts/ folder handles a different table form the DWH model

fill_session_fact_table.py is the batch processing job for the session fact table

schemas.py defines the schemas for both the raw and dwh tables

util_functions.py handles the RW operations from different databases

configs.py has all the configurations for the raw and dwh models
