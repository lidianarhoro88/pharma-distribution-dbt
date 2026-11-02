-- Products losing the most value to expired returns: a direct input for
-- stock rotation (FEFO) and purchasing decisions.
select
    p.sku,
    p.product_name,
    p.atc_group_name,
    p.is_cold_chain,
    sum(f.quantity)                                                  as units_sold,
    sum(f.expired_quantity)                                          as units_expired,
    round(sum(f.expired_quantity) / nullif(sum(f.quantity), 0) * 100, 2) as expiry_rate_pct,
    round(sum(f.expired_quantity * f.unit_price_try * (1 - f.discount_pct / 100)), 2) as expired_value_try
from {{ ref('fct_order_lines') }} f
join {{ ref('dim_product') }} p using (sku)
where not f.is_cancelled
group by all
having sum(f.expired_quantity) > 0
order by expired_value_try desc
