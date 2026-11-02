-- Monthly KPIs by ATC group for the sales dashboard.
select
    dd.year_month,
    p.atc_group_name,
    count(distinct f.order_id)                       as orders,
    count(distinct f.pharmacy_code)                  as active_pharmacies,
    sum(f.quantity)                                  as units,
    round(sum(f.net_amount_try), 2)                  as net_sales_try,
    round(sum(f.returned_amount_try), 2)             as returns_try,
    round(sum(f.returned_amount_try) / nullif(sum(f.net_amount_try), 0) * 100, 2) as return_rate_pct
from {{ ref('fct_order_lines') }} f
join {{ ref('dim_date') }} dd on dd.date_day = f.order_date
join {{ ref('dim_product') }} p using (sku)
where not f.is_cancelled
group by 1, 2
