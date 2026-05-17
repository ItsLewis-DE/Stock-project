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

CREATE OR REPLACE STAGE s3_sto
URL = 's3://stock-bucket-phong-2026'
CREDENTIALS = (aws_key_id ='aws_key_id' aws_secret_key = 'aws_secret_key')
FILE_FORMAT = (TYPE = PARQUET)
SELECT * FROM @s3_sto/parquet/company/2026_05_14
CREATE TABLE IF NOT EXISTS stock_schema.fama_classification(
	fama_id	INT,
	fama_industry VARCHAR(100) UNIQUE,
	fama_sector VARCHAR(50),
    inserted_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS stock_schema.industry (
	industry_id INT,
	industry_name VARCHAR(100) UNIQUE,
	sector_name VARCHAR(100),
    inserted_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS stock_schema.region (
     region_id INT,
	 region_name VARCHAR(100) UNIQUE,
	 market_type VARCHAR(100),
	 local_open BIGINT,
	 local_close BIGINT,
     inserted_at TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS stock_schema.sic_classification (
	sic_code VARCHAR(100) UNIQUE,
	fama_id INT,
	sic_industry VARCHAR(100),
	sic_sector VARCHAR(100),
    inserted_at TIMESTAMP_NTZ
);
CREATE TABLE IF NOT EXISTS stock_schema.exchange(
	exchange_id INT,
	exchange_name VARCHAR(50) UNIQUE,
    region_id INT,
    inserted_at TIMESTAMP_NTZ
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
	sic_code VARCHAR(200),
    inserted_at TIMESTAMP_NTZ
);
CREATE TABLE IF NOT EXISTS news(
    title VARCHAR(1000),
    url VARCHAR(1000),
    time_published VARCHAR(1000),
    authors VARIANT,
    summary VARCHAR(1000),
    banner_image VARCHAR(1000),
    source VARCHAR(1000),
    category_within_source VARCHAR(1000),
    source_domain VARCHAR(1000),
    topics VARIANT,
    overall_sentiment_score FLOAT,
    overall_sentiment_label VARCHAR(1000),
    ticker_sentiment VARIANT,
    inserted_at TIMESTAMP_NTZ
);
CREATE TABLE IF NOT EXISTS ohlc(
    T VARCHAR(20),
    v FLOAT,
    vw FLOAT,
    o FLOAT,
    c FLOAT,
    h FLOAT,
    l FLOAT,
    t_time BIGINT,
    n INT,
    inserted_at TIMESTAMP_NTZ
);
CREATE TABLE dim_date (
    date_key DATE,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_of_month INT NOT NULL,
    day_of_week INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);
INSERT INTO dim_date(
date_key,year,quarter,month,month_name,day_of_month,day_of_week,day_name,is_weekend
)
WITH date_range AS(
    SELECT 
        DATEADD(day,ROW_NUMBER() OVER(ORDER BY NULL) -1, '2025-01-01') as day_gene
    FROM TABLE(GENERATOR(ROWCOUNT => 10000))
)
SELECT 
    day_gene AS date_key,
    EXTRACT(year FROM day_gene) AS year,
    EXTRACT(quarter FROM day_gene) AS quarter,
    EXTRACT(month FROM day_gene) AS month,
    TO_VARCHAR(day_gene,'MMMM') as month_name,
    EXTRACT(day FROM day_gene) AS day_of_month,
    DAYOFWEEKISO(day_gene) AS day_of_week,
    DECODE(DAYOFWEEKISO(day_gene),
        1, 'Monday',2,'Tuesday',3,'Wednesday',
        4,'Thursday',5,'Friday',6,'Saturday',7,'Sunday'
    ) AS day_name,
    CASE WHEN DAYOFWEEKISO(day_gene) IN (6,7) THEN TRUE ELSE FALSE END AS is_weekend
FROM date_range
WHERE day_gene <= '2035-12-31'::DATE;