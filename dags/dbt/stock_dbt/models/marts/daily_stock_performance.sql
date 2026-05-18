/*
==========================================================================================
BẢNG: daily_stock_performance (Tên Model: daily_stock_performance)
MÔ TẢ:
  Bảng này dùng để tổng hợp và tính toán hiệu suất giao dịch hằng ngày của từng mã cổ phiếu.
  Kết hợp thông tin từ dim_company và dim_ohlc để tạo ra các chỉ số về biến động giá và lợi nhuận trong ngày.

CÁC CỘT QUAN TRỌNG:
  - company_name: Tên của công ty.
  - ticker: Mã cổ phiếu đại diện.
  - open_price / close_price: Giá mở cửa và giá đóng cửa của phiên giao dịch.
  - volume: Khối lượng giao dịch trong ngày.
  - daily_price_change: Mức thay đổi giá đóng cửa so với giá mở cửa (Close - Open).
  - daily_return_percentage: Tỷ lệ lợi nhuận hằng ngày tính theo phần trăm (%).
  - daily_spread: Độ lệch giữa giá cao nhất và thấp nhất trong ngày (Highest - Lowest).
  - date_key: Ngày giao dịch.
==========================================================================================
*/

{{ config(
    materialized='table'
) }}

WITH company AS (
    SELECT * FROM {{ ref('dim_company') }}
),
ohlc AS (
    SELECT * FROM {{ ref('dim_ohlc') }}
),
daily_performance AS (
    SELECT
        c.company_name,
        c.ticker,
        c.exchange_id,
        c.industry_id,
        o.open_price,
        o.close_price,
        o.highest_price,
        o.lowest_price,
        o.volume,
        o.volumn_weight_average_price,
        o.ex_dividend_date,
        -- Calculate daily metrics
        (o.close_price - o.open_price) AS daily_price_change,
        CASE 
            WHEN o.open_price > 0 THEN ((o.close_price - o.open_price) / o.open_price) * 100 
            ELSE 0 
        END AS daily_return_percentage,
        (o.highest_price - o.lowest_price) AS daily_spread,
        o.inserted_at AS date_key
    FROM ohlc o
    JOIN company c ON o.ticker = c.ticker
)

SELECT * FROM daily_performance
