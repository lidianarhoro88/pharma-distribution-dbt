-- A parcel cannot arrive before it leaves the warehouse.
select order_id, dispatched_at, delivered_at
from {{ ref('fct_deliveries') }}
where delivered_at < dispatched_at
