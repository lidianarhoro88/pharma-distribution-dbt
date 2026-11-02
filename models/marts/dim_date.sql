select
    d::date                                   as date_day,
    year(d)                                   as year,
    quarter(d)                                as quarter,
    month(d)                                  as month,
    strftime(d, '%Y-%m')                      as year_month,
    strftime(d, '%B')                         as month_name,
    isodow(d)                                 as iso_day_of_week,
    isodow(d) in (6, 7)                       as is_weekend
from range(date '2025-12-01', date '2027-01-01', interval 1 day) t(d)
