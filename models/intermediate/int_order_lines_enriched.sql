-- Line-level grain with pricing, returns and the order header attached.
with lines as (select * from {{ ref('stg_erp__order_lines') }}),
orders as (select * from {{ ref('stg_erp__orders') }}),
returns as (
    select line_id, sum(returned_quantity) as returned_quantity,
           sum(case when return_reason = 'EXPIRED' then returned_quantity else 0 end) as expired_quantity
    from {{ ref('stg_erp__returns') }}
    group by line_id
)

select
    l.line_id,
    l.order_id,
    o.order_date,
    o.pharmacy_code,
    o.warehouse,
    o.order_status,
    l.sku,
    l.quantity,
    l.unit_price_try,
    l.discount_pct,
    round(l.quantity * l.unit_price_try, 2)                                   as gross_amount_try,
    round(l.quantity * l.unit_price_try * (1 - l.discount_pct / 100), 2)      as net_amount_try,
    coalesce(r.returned_quantity, 0)                                         as returned_quantity,
    coalesce(r.expired_quantity, 0)                                          as expired_quantity,
    round(coalesce(r.returned_quantity, 0) * l.unit_price_try * (1 - l.discount_pct / 100), 2) as returned_amount_try
from lines l
join orders o using (order_id)
left join returns r using (line_id)
