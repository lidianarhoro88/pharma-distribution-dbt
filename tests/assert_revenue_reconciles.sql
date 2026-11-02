-- Total net sales in the monthly mart must equal the fact table (excluding cancelled orders).
with mart as (select round(sum(net_sales_try), 0) as v from {{ ref('mart_monthly_sales') }}),
fact as (select round(sum(net_amount_try), 0) as v from {{ ref('fct_order_lines') }} where not is_cancelled)
select mart.v as mart_total, fact.v as fact_total
from mart, fact
where abs(mart.v - fact.v) > 1
