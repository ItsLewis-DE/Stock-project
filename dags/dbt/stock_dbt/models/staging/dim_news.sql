{{ config(
    materialized='incremental',
    unique_key = 'article_id'
)}}
SELECT 
    {{ dbt_utils.generate_surrogate_key(
        ["title","url","time_published","category_within_source","source_domain","overall_sentiment_score","overall_sentiment_label"]
    )}} AS article_id,
    title,
    url,
    TO_TIMESTAMP(time_published,'YYYYMMDD"T"HH24MISS') AS time_published,
    authors,
    summary,
    source,
    category_within_source,
    source_domain,
    overall_sentiment_score,
    overall_sentiment_label,
    ticker_sentiment,
    inserted_at::DATE AS date_key
FROM {{ source('stock_data', 'news') }} n