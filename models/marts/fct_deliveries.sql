-- One row per dispatched order. OTIF = on time (by promised time) and in full (no returned quantity).
with d as (select * from {{ ref('stg_erp__deliveries') }}),
o as (select * from {{ ref('stg_erp__orders') }}),
lines as (
    select order_id, sum(quantity) as units, sum(returned_quantity) as returned_units,
           bool_or(p.is_cold_chain) as has_cold_chain
    from {{ ref('int_order_lines_enriched') }}
    join {{ ref('dim_product') }} p using (sku)
    group by order_id
)

select
    d.order_id,
    o.order_date,
    o.pharmacy_code,
    o.warehouse,
    d.carrier,
    lines.has_cold_chain,
    d.dispatched_at,
    d.promised_at,
    d.delivered_at,
    d.delivered_at is not null                                         as is_delivered,
    round(date_diff('minute', o.ordered_at, d.delivered_at) / 60.0, 1) as lead_time_hours,
    d.delivered_at <= d.promised_at                                    as is_on_time,
    lines.returned_units = 0                                           as is_in_full,
    (d.delivered_at <= d.promised_at) and lines.returned_units = 0     as is_otif
from d
join o using (order_id)
join lines using (order_id)
