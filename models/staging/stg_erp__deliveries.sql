select
    trim(order_id)                                  as order_id,
    trim(carrier)                                   as carrier,
    cast(dispatched_at as timestamp)                as dispatched_at,
    cast(promised_at as timestamp)                  as promised_at,
    cast(nullif(trim(cast(delivered_at as varchar)), '') as timestamp) as delivered_at
from {{ source('erp', 'deliveries') }}
