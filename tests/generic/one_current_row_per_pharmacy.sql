{% test one_current_row_per_pharmacy(model) %}
-- An SCD2 dimension must have exactly one current version per business key.
select pharmacy_code, count(*) as current_rows
from {{ model }}
where is_current
group by pharmacy_code
having count(*) <> 1
{% endtest %}
