CREATE TABLE IF NOT EXISTS stock_schema.fama_classification(
	fama_id	INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	fama_industry VARCHAR(100) UNIQUE,
	fama_sector VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stock_schema.industry (
	industry_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	industry_name VARCHAR(100) UNIQUE,
	sector_name VARCHAR(100)
)

CREATE TABLE IF NOT EXISTS stock_schema.region (
     region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	 region_name VARCHAR(100) UNIQUE,
	 market_type VARCHAR(50),
	 local_open TIME,
	 local_close TIME	 
)