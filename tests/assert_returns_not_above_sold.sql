-- Returned quantity on a line can never exceed the quantity sold on that line.
select line_id, quantity, returned_quantity
from {{ ref('fct_order_lines') }}
where returned_quantity > quantity
