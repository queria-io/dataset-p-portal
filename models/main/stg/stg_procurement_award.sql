{# 型付け・コード名称の付与・年度（会計年度）の導出を行う。
   会計年度は落札決定日を基準に 4月始まり（1〜3月は前暦年）で算出する。 #}

with src as (
    select
        procurement_item_no,
        procurement_item_name,
        cast(award_date as date) as award_date,
        cast(award_price as decimal(19, 2)) as award_price,
        ministry_code,
        bidding_method_code,
        trade_name,
        nullif(corporate_number, '') as corporate_number
    from {{ ref('raw_procurement_award') }}
)

select
    procurement_item_no,
    procurement_item_name,
    award_date,
    case
        when month(award_date) >= 4 then year(award_date)
        else year(award_date) - 1
    end as fiscal_year,
    award_price,
    ministry_code,
    {{ ministry_name('ministry_code') }} as ministry_name,
    bidding_method_code,
    {{ bidding_method_name('bidding_method_code') }} as bidding_method_name,
    trade_name,
    corporate_number
from src
