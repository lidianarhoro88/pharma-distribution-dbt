-- SCD Type 2 pharmacy dimension built from the snapshot.
-- pharmacy_key identifies one version; pharmacy_code identifies the pharmacy.
select
    md5(pharmacy_code || '|' || cast(dbt_valid_from as varchar))   as pharmacy_key,
    pharmacy_code,
    pharmacy_name,
    district,
    segment,
    credit_limit_try,
    opened_on,
    dbt_valid_from                                                 as valid_from,
    coalesce(dbt_valid_to, timestamp '9999-12-31')                 as valid_to,
    dbt_valid_to is null                                           as is_current
from {{ ref('pharmacies_snapshot') }}
