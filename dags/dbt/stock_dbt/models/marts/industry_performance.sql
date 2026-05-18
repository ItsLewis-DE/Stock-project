/*
==========================================================================================
BẢNG: industry_performance (Tên Model: industry_performance)
MÔ TẢ:
  Bảng này dùng để tổng hợp hiệu suất giao dịch theo ngành (industry) và lĩnh vực (sector) hằng ngày.
  Kết hợp dữ liệu hiệu suất cổ phiếu hằng ngày (daily_stock_performance) với danh mục ngành (dim_industry) 
  để cung cấp cái nhìn tổng quan về xu hướng thị trường ở cấp độ vĩ mô.

CÁC CỘT QUAN TRỌNG:
  - date_key: Ngày giao dịch.
  - industry_name: Tên ngành phân loại.
  - sector_name: Tên lĩnh vực lớn.
  - num_companies_traded: Số lượng doanh nghiệp trong ngành có phát sinh giao dịch trong ngày.
  - total_trading_volume: Tổng khối lượng giao dịch của toàn ngành trong ngày.
  - avg_industry_return: Tỷ lệ lợi nhuận trung bình (%) của ngành trong ngày.
  - avg_closing_price: Giá đóng cửa trung bình của các cổ phiếu thuộc ngành trong ngày.
==========================================================================================
*/

{{ config(
    materialized='table'
) }}

WITH daily_performance AS (
    SELECT * FROM {{ ref('daily_stock_performance') }}
),
industry AS (
    SELECT * FROM {{ ref('dim_industry') }}
),
industry_aggregation AS (
    SELECT
        dp.date_key,
        i.industry_name,
        i.sector_name,
        COUNT(DISTINCT dp.ticker) AS num_companies_traded,
        SUM(dp.volume) AS total_trading_volume,
        AVG(dp.daily_return_percentage) AS avg_industry_return,
        AVG(dp.close_price) AS avg_closing_price
    FROM daily_performance dp
    JOIN industry i ON dp.industry_id = i.industry_id
    GROUP BY dp.date_key, i.industry_name, i.sector_name
)

SELECT * FROM industry_aggregation
