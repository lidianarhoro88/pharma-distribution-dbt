-- The ERP extract occasionally repeats a line. Keep one row per line_id.
with source as (
    select * from {{ source('erp', 'order_lines') }}
),

deduplicated as (
    select *,
        row_number() over (partition by line_id order by line_id) as row_num
    from source
)

select
    cast(line_id as integer)                        as line_id,
    trim(order_id)                                  as order_id,
    upper(trim(sku))                                as sku,
    cast(quantity as integer)                       as quantity,
    cast(unit_price_try as decimal(12, 2))          as unit_price_try,
    cast(discount_pct as decimal(5, 2))             as discount_pct
from deduplicated
where row_num = 1
