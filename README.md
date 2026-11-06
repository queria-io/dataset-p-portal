# 調達ポータル 落札実績

[調達ポータル（政府電子調達システム GEPS）](https://www.p-portal.go.jp/)が公開する、中央省庁等の落札実績を SQL で検索・集計できるテーブルにしたデータセットです。法人番号で houjin_bangou・gbizinfo と結合して、企業ごとの受注を集計できます。

## 出典と利用条件

- 調達ポータルの落札実績オープンデータのうち、年度別の「全件データファイル（CSV形式）」を結合して作成しています
- 府省コード・入札方式コードには、仕様の「コード一覧」に基づいて名称の列を付けています。落札価格・落札決定日などの値は変更していません
- 調達ポータルの[利用条件](https://www.p-portal.go.jp/pps-web-biz/resources/app/html/sitepolicy.html)（政府標準利用規約に準拠）に従います。出典を明記すれば商用利用できます

## テーブル

`main.procurement_award` は 1 行が 1 件の落札実績です。2017 年度以降を収録しています。

| 列 | 内容 |
| --- | --- |
| `procurement_item_no` | 調達案件番号（19 桁） |
| `procurement_item_name` | 調達案件名称 |
| `award_date` | 落札決定日 |
| `fiscal_year` | 会計年度（落札決定日から 4 月始まりで算出） |
| `award_price` | 落札価格（円） |
| `ministry_code` / `ministry_name` | 府省コード（2 桁） / 府省名称 |
| `bidding_method_code` / `bidding_method_name` | 入札方式コード（7 桁） / 入札方式名称（一般競争入札・指名競争入札・随意契約など） |
| `trade_name` | 落札事業者の商号又は名称 |
| `corporate_number` | 落札事業者の法人番号（13 桁）。個人事業主などは NULL |

## 使い方

2024 年度の府省ごとの落札件数と落札額を出す:

```sql
SELECT ministry_name, count(*) AS awards, sum(award_price) AS total_yen
FROM p_portal.main.procurement_award
WHERE fiscal_year = 2024
GROUP BY ALL
ORDER BY total_yen DESC;
```

## 注意

- 複数の事業者が落札する方式（複数落札）があるため、`procurement_item_no` は一意ではありません。案件数を数えるときは重複を除いてください
- オープンカウンタ（少額）の案件のうち、個人事業主の落札は含みません
- 各年度のファイルは前月末時点で公表されている落札実績を収録しています。毎月取り込み直します

## 更新

```bash
bash scripts/build.sh
```
