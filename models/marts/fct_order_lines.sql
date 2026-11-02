-- Fact table at order-line grain. Cancelled orders are kept and flagged so
-- revenue measures can exclude them while cancellation rates stay measurable.
select
    l.line_id,
    l.order_id,
    l.order_date,
    p.pharmacy_key,
    l.pharmacy_code,
    l.sku,
    l.warehouse,
    l.order_status,
    l.order_status = 'CANCELLED'      as is_cancelled,
    l.quantity,
    l.unit_price_try,
    l.discount_pct,
    l.gross_amount_try,
    l.net_amount_try,
    l.returned_quantity,
    l.expired_quantity,
    l.returned_amount_try,
    l.net_amount_try - l.returned_amount_try as net_after_returns_try
from {{ ref('int_order_lines_enriched') }} l
left join {{ ref('dim_pharmacy') }} p
    on p.pharmacy_code = l.pharmacy_code
   and p.is_current
