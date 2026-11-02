select
    upper(trim(sku))                                as sku,
    trim(product_name)                              as product_name,
    upper(trim(atc_group))                          as atc_group,
    case upper(trim(atc_group))
        when 'A' then 'Alimentary tract & metabolism'
        when 'C' then 'Cardiovascular system'
        when 'J' then 'Anti-infectives'
        when 'N' then 'Nervous system'
        when 'R' then 'Respiratory system'
        when 'L' then 'Antineoplastic & immunomodulating'
    end                                             as atc_group_name,
    upper(trim(cold_chain)) = 'Y'                   as is_cold_chain,
    cast(list_price_try as decimal(12, 2))          as list_price_try
from {{ source('erp', 'products') }}
