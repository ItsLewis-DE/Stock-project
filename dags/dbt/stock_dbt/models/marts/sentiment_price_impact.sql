/*
==========================================================================================
BẢNG: sentiment_price_impact (Tên Model: sentiment_price_impact)
MÔ TẢ:
  Bảng phân tích mối tương quan giữa tâm lý tin tức (sentiment) và biến động giá cổ phiếu (price performance) hằng ngày.
  Bảng này giúp trả lời câu hỏi: Tin tức tích cực/tiêu cực có thực sự tương quan thuận với hiệu suất tăng/giảm giá của cổ phiếu hay không?

CÁC CỘT QUAN TRỌNG:
  - date_key: Ngày giao dịch / Nhận tin.
  - ticker: Mã cổ phiếu đại diện.
  - company_name: Tên của công ty.
  - total_articles: Tổng số lượng bài báo trong ngày về công ty.
  - avg_sentiment_score: Điểm tâm lý trung bình của cổ phiếu trong ngày (từ -1 đến 1).
  - daily_price_change: Mức thay đổi giá đóng cửa so với giá mở cửa.
  - daily_return_percentage: Tỷ lệ lợi nhuận hằng ngày (%) của cổ phiếu.
  - sentiment_price_alignment: Nhãn thể hiện mức độ tương hợp giữa tâm lý tin tức và biến động giá.
      * 'Aligned: Positive': Tâm lý tích cực (> 0.15) & Giá tăng (> 0).
      * 'Aligned: Negative': Tâm lý tiêu cực (< -0.15) & Giá giảm (< 0).
      * 'Contradictory': Ngược chiều (Tâm lý tốt nhưng giá giảm, hoặc ngược lại).
      * 'Neutral/Mixed': Tâm lý trung lập hoặc biến động giá không đáng kể.
==========================================================================================
*/

{{ config(
    materialized='table'
) }}

WITH daily_performance AS (
    SELECT * FROM {{ ref('daily_stock_performance') }}
),
daily_sentiment AS (
    SELECT * FROM {{ ref('company_sentiment') }}
),
sentiment_impact AS (
    SELECT
        dp.date_key,
        dp.ticker,
        dp.company_name,
        ds.total_articles,
        ds.avg_sentiment_score,
        ds.positive_articles,
        ds.negative_articles,
        ds.neutral_articles,
        dp.daily_price_change,
        dp.daily_return_percentage,
        dp.volume,
        -- Classify if the sentiment aligns with price movement
        CASE 
            WHEN ds.avg_sentiment_score > 0.15 AND dp.daily_return_percentage > 0 THEN 'Aligned: Positive'
            WHEN ds.avg_sentiment_score < -0.15 AND dp.daily_return_percentage < 0 THEN 'Aligned: Negative'
            WHEN (ds.avg_sentiment_score > 0.15 AND dp.daily_return_percentage < 0) OR 
                 (ds.avg_sentiment_score < -0.15 AND dp.daily_return_percentage > 0) THEN 'Contradictory'
            ELSE 'Neutral/Mixed'
        END AS sentiment_price_alignment
    FROM daily_performance dp
    LEFT JOIN daily_sentiment ds 
        ON dp.ticker = ds.ticker AND dp.date_key = ds.date_key
)

SELECT * FROM sentiment_impact
