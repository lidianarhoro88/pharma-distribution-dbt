select
    trim(return_id)                                 as return_id,
    cast(line_id as integer)                        as line_id,
    cast(returned_on as date)                       as returned_on,
    cast(quantity as integer)                       as returned_quantity,
    upper(trim(reason))                             as return_reason
from {{ source('erp', 'returns') }}
