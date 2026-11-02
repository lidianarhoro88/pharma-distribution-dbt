{% snapshot pharmacies_snapshot %}
{{
    config(
        unique_key='pharmacy_code',
        strategy='check',
        check_cols=['district', 'segment', 'credit_limit_try'],
    )
}}
-- Slowly changing dimension (Type 2): every change to district, segment or
-- credit limit closes the old row (dbt_valid_to) and opens a new one.
select * from {{ ref('stg_erp__pharmacies') }}
{% endsnapshot %}
