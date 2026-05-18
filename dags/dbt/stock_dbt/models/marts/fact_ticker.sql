
-- depends_on: {{ ref('dim_company') }}
-- depends_on: {{ ref('dim_ohlc') }}

{% set configs = [
    {
        "table": ref('dim_company'),
        "columns": "com.company_name, com.ticker, ohlc.open_price AS price_open, ohlc.highest_price, ohlc.lowest_price, ohlc.close_price, ohlc.volume, ohlc.volumn_weight_average_price, ohlc.ex_dividend_date, dim_date.*",
        "alias": "com"
    },
    {
        "table": ref('dim_ohlc'),
        "columns": "",
        "alias": "ohlc",
        "join_condition": "com.ticker = ohlc.ticker"
    },
    {
        "table": source('stock_data', 'dim_date'),
        "columns": "",
        "alias": "dim_date",
        "join_condition": "com.date_key = dim_date.date_key"
    }
] %}

SELECT {{ configs[0]['columns'] }}
FROM
    {% for config in configs %}
    {% if loop.first %}
        {{ config['table'] }} AS {{ config['alias'] }}
    {% else %}
        INNER JOIN {{ config['table'] }} AS {{ config['alias'] }}
        ON {{ config['join_condition'] }}
    {% endif %}
    {% endfor %}