{{ config(
    materialized='incremental',
    unique_key = 'article_id'
)}}
SELECT 
    article_id,
    title,
    url,
    time_published,
    summary,
    source,
    category_within_source,
    source_domain,
    overall_sentiment_score,
    overall_sentiment_label
FROM {{  ref('dim_news')  }} n,

