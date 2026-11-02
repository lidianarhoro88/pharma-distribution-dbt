select
    trim(order_id)                                  as order_id,
    upper(trim(pharmacy_code))                      as pharmacy_code,
    cast(ordered_at as timestamp)                   as ordered_at,
    cast(ordered_at as date)                        as order_date,
    upper(trim(warehouse))                          as warehouse,
    upper(trim(status))                             as order_status
from {{ source('erp', 'orders') }}
