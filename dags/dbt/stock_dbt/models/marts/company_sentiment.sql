/*
==========================================================================================
BẢNG: company_sentiment (Tên Model: company_sentiment)
MÔ TẢ:
  Bảng này dùng để tổng hợp điểm tâm lý tin tức (news sentiment score) hằng ngày của từng mã cổ phiếu/công ty.
  Giúp theo dõi xu hướng tâm lý dư luận tích cực hay tiêu cực đối với doanh nghiệp qua từng ngày.

CÁC CỘT QUAN TRỌNG:
  - company_name: Tên của công ty.
  - ticker: Mã cổ phiếu đại diện.
  - date_key: Ngày xuất bản hoặc nhận tin.
  - total_articles: Tổng số lượng bài viết về công ty trong ngày.
  - avg_sentiment_score: Điểm tâm lý trung bình của mã cổ phiếu trong ngày (từ -1 đến 1).
  - positive_articles: Số lượng bài viết mang xu hướng tích cực (Bullish / Positive).
  - negative_articles: Số lượng bài viết mang xu hướng tiêu cực (Bearish / Negative).
  - neutral_articles: Số lượng bài viết mang xu hướng trung lập (Neutral).
==========================================================================================
*/

{{ config(
    materialized='table'
) }}

WITH news AS (
    SELECT * FROM {{ ref('fact_news') }}
),
company AS (
    SELECT * FROM {{ ref('dim_company') }}
),
daily_sentiment AS (
    SELECT
        c.company_name,
        n.ticker,
        n.date_key,
        COUNT(DISTINCT n.article_id) AS total_articles,
        AVG(n.ticker_sentiment_score) AS avg_sentiment_score,
        MAX(n.ticker_sentiment_score) AS max_sentiment_score,
        MIN(n.ticker_sentiment_score) AS min_sentiment_score,
        SUM(CASE WHEN n.ticker_sentiment_label ILIKE '%Bullish%' OR n.ticker_sentiment_label ILIKE 'Positive' THEN 1 ELSE 0 END) AS positive_articles,
        SUM(CASE WHEN n.ticker_sentiment_label ILIKE '%Bearish%' OR n.ticker_sentiment_label ILIKE 'Negative' THEN 1 ELSE 0 END) AS negative_articles,
        SUM(CASE WHEN n.ticker_sentiment_label ILIKE 'Neutral' THEN 1 ELSE 0 END) AS neutral_articles
    FROM news n
    JOIN company c ON n.ticker = c.ticker
    GROUP BY c.company_name, n.ticker, n.date_key
)

SELECT * FROM daily_sentiment
