SELECT * 
FROM {{ source('stock_data', 'company') }}