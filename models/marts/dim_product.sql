select
    sku,
    product_name,
    atc_group,
    atc_group_name,
    is_cold_chain,
    list_price_try
from {{ ref('stg_erp__products') }}
