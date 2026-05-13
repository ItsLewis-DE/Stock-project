CREATE TABLE IF NOT EXISTS stock_schema.fama_classification(
	fama_id	INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	fama_industry VARCHAR(100) UNIQUE,
	fama_sector VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS stock_schema.industry (
	industry_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	industry_name VARCHAR(100) UNIQUE,
	sector_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS stock_schema.region (
     region_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
	exchange_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	region_id INT,
	exchange_name VARCHAR(50) UNIQUE
);
CREATE TABLE IF NOT EXISTS stock_schema.company(
	company_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	company_name VARCHAR(200),
	ticker VARCHAR(200),
	cik VARCHAR(200) UNIQUE,
	cusip VARCHAR(200),
	exchange_id INT,
	isDelisted BOOLEAN,
	industry_id INT,
	location VARCHAR(100),
	currency VARCHAR(10),
	category VARCHAR(200),
	sic_code VARCHAR(200)
);