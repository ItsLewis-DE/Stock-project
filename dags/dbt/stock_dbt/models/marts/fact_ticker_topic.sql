{{ config(
    materialized='incremental',
    unique_key = 'ticker_topic_id'
)}}
SELECT 
    {{ dbt_utils.generate_surrogate_key(
        ['article_id',"COALESCE(f.value::STRING,'')",'ts.value:"ticker"::STRING']
    )}} AS ticker_topic_id,
    article_id,
    COALESCE(f.value::STRING,'') AS authors,
    ts.value:"ticker"::STRING AS ticker,
    ts.value:"relevance_score"::FLOAT AS relevance_score_ticker,
    ts.value:"ticker_sentiment_label"::STRING AS ticker_sentiment_label,
    ts.value:"ticker_sentiment_score"::FLOAT As ticker_sentiment_score,
    date_key
FROM {{ ref('dim_news') }} n,
LATERAL FLATTEN(input => PARSE_JSON(n.authors),outer=>true) f,
LATERAL FLATTEN(input=>PARSE_JSON(n.ticker_sentiment),outer=>true) ts