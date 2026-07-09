## データ出典

[調達ポータル（政府電子調達 GEPS）](https://www.p-portal.go.jp/)が公開する落札実績オープンデータです。
中央省庁等の調達案件ごとの落札決定日・落札価格・入札方式・落札事業者（商号又は名称・法人番号）を収録します。
年度別に提供される「全件データファイル（CSV形式）」を結合しています。

## テーブル: procurement_award

1レコード＝1件の落札実績です。平成29年度（2017年度）以降を収録します。

- procurement_item_no: 調達案件番号（VARCHAR、19桁固定）
- procurement_item_name: 調達案件名称（VARCHAR）
- award_date: 落札決定日（DATE）
- fiscal_year: 会計年度（INTEGER、落札決定日を基準に4月始まりで算出）
- award_price: 落札価格（DECIMAL(19,2)、円）
- ministry_code: 府省コード（VARCHAR、2桁固定）
- ministry_name: 府省名称（VARCHAR）
- bidding_method_code: 入札方式コード（VARCHAR、7桁固定）
- bidding_method_name: 入札方式名称（VARCHAR、一般競争入札・指名競争入札・随意契約等）
- trade_name: 商号又は名称（VARCHAR、落札事業者）
- corporate_number: 法人番号（VARCHAR、13桁固定。個人事業主等では欠落）

法人番号（corporate_number）で法人番号公表サイトや gBizINFO のデータと結合でき、企業別の受注分析に利用できます。
府省コード・入札方式コードは仕様の「コード一覧」に基づいて名称列を併記しています。

同一の調達案件で複数事業者が落札する方式（複数落札）があるため、調達案件番号（procurement_item_no）は
一意になりません。オープンカウンタ（少額）案件のうち個人事業主は含まれません。

### データ更新手順

main.py が調達ポータルの年度別「全件データファイル（CSV形式）」を取得して1つの CSV へ結合し、
dbt build で落札実績テーブルを再生成する。各年度ファイルは前月末日時点で公表されている落札実績を
全件収録するため、毎月のビルドで最新化される。
ビルドは `bash scripts/build.sh local` で実行する。

## ライセンス

調達ポータルの[利用条件](https://www.p-portal.go.jp/pps-web-biz/resources/app/html/sitepolicy.html)
（政府標準利用規約に準拠。商用利用可・出典明記が条件）に従う。

出典: 調達ポータル（https://www.p-portal.go.jp/）を加工して作成。

年度別に提供される複数の CSV を結合し、府省コード・入札方式コードに名称列を付与する加工を行っている。
落札価格・落札決定日等の値そのものは改変していない。
