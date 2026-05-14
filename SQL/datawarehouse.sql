use role accountadmin;
create warehouse dbt_wh with warehouse_size = 'x-small';
create database stock_database;
create role dbt_role;

grant usage on warehouse dbt_wh to role dbt_role;
grant all on database stock_database to role dbt_role;
grant role dbt_role to user phongthanh;

use role dbt_role;
create schema stock_database.stock_schema;


CREATE OR REPLACE STORAGE INTEGRATION s3
TYPE = EXTERNAL_STAGE
STORAGE_PROVIDER = 'S3'
ENABLED = TRUE
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::557864981182:role/snowflake_conn'
STORAGE_ALLOWED_LOCATIONS = ('s3://stock-bucket-phong-2026')

DESC STORAGE INTEGRATION s3

CREATE OR REPLACE STAGE s3_sto
URL = 's3://stock-bucket-phong-2026'
CREDENTIALS = (aws_key_id ='aws_key_id' aws_secret_key = 'aws_secret_key')
FILE_FORMAT = (TYPE = PARQUET)
SELECT * FROM @s3_sto/parquet/company/2026_05_14
CREATE TABLE IF NOT EXISTS stock_schema.fama_classification(
	fama_id	INT,
	fama_industry VARCHAR(100) UNIQUE,
	fama_sector VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stock_schema.industry (
	industry_id INT,
	industry_name VARCHAR(100) UNIQUE,
	sector_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS stock_schema.region (
     region_id INT,
	 region_name VARCHAR(100) UNIQUE,
	 market_type VARCHAR(100),
	 local_open TIME,
	 local_close TIME
);
CREATE TABLE IF NOT EXISTS stock_schema.sic_classification (
	sic_code VARCHAR(100) UNIQUE,
	fama_id INT,
	sic_industry VARCHAR(100),
	sic_sector VARCHAR(100)
);
CREATE TABLE IF NOT EXISTS stock_schema.exchange(
	exchange_id INT,
	region_id INT,
	exchange_name VARCHAR(50) UNIQUE
);
CREATE TABLE IF NOT EXISTS stock_schema.company(
	company_id INT,
	company_name VARCHAR(200),
	ticker VARCHAR(200),
	cik VARCHAR(200),
	cusip VARCHAR(200),
	exchange_id INT,
	isDelisted BOOLEAN,
	industry_id INT,
	location VARCHAR(100),
	currency VARCHAR(10),
	category VARCHAR(200),
	sic_code VARCHAR(200)
);