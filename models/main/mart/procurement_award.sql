select
    procurement_item_no,
    procurement_item_name,
    award_date,
    fiscal_year,
    award_price,
    ministry_code,
    ministry_name,
    bidding_method_code,
    bidding_method_name,
    trade_name,
    corporate_number
from {{ ref('stg_procurement_award') }}
