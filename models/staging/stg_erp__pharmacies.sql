with source as (
    select * from {{ source('erp', 'pharmacies') }}
)

select
    upper(trim(pharmacy_code))                      as pharmacy_code,
    trim(pharmacy_name)                             as pharmacy_name,
    {{ normalize_district('district') }}            as district,
    trim(segment)                                   as segment,
    cast(credit_limit_try as decimal(12, 2))        as credit_limit_try,
    cast(opened_on as date)                         as opened_on
from source
