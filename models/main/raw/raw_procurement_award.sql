{# 調達ポータル 落札実績オープンデータの生データ。
   main.py が年度別の全件データ CSV を取得・結合して .fdl/p_portal_awards.csv に保存する。 #}

{{ config(materialized='table') }}

select *
from read_csv(
    '.fdl/p_portal_awards.csv',
    header=true,
    all_varchar=true
)
