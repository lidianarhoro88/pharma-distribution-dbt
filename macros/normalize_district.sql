{# Map the many spellings found in the ERP extract to one canonical Istanbul district name. #}
{% macro normalize_district(column) -%}
case upper(strip_accents(trim({{ column }})))
    when 'KADIKOY'  then 'Kadıköy'
    when 'BESIKTAS' then 'Beşiktaş'
    when 'USKUDAR'  then 'Üsküdar'
    when 'SISLI'    then 'Şişli'
    when 'BAKIRKOY' then 'Bakırköy'
    when 'ATASEHIR' then 'Ataşehir'
    when 'FATIH'    then 'Fatih'
    when 'PENDIK'   then 'Pendik'
    else trim({{ column }})
end
{%- endmacro %}
