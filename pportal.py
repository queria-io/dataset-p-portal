"""調達ポータル（政府電子調達 GEPS）落札実績オープンデータの取得・整形。

調達ポータルが公開する年度別の「全件データファイル（CSV形式）」を取得し、
1つの CSV へ結合する。各年度ファイルは前月末日時点で公表されている落札実績を
全件収録しており、年度をまたいで結合しても案件（落札決定日）ごとに一意である。

ソース CSV はヘッダ行を持たず、UTF-8（BOM付き）・CRLF・全項目がダブルクォート囲みで
出力される（ファイル仕様準拠）。本スクリプトはヘッダ付き UTF-8 CSV へ正規化する。
"""

import csv
import io
import logging
import zipfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

logger = logging.getLogger("pipelines")

# 落札実績オープンデータ（CSV形式）全件データファイルのダウンロード用 URL。
# 実ファイル名は successful_bid_record_info_all_<年度(西暦)>.zip。
BASE_URL = (
    "https://api.p-portal.go.jp/pps-web-biz/UAB03/OAB0301?fileversion=v001&filename="
)

# 全件データファイルが提供される最も古い年度（平成29年度＝2017）。
START_FISCAL_YEAR = 2017

# ソース CSV の物理列（ファイル仕様「2.2 出力項目詳細（CSV形式）」順）。
SOURCE_COLUMNS = [
    "procurement_item_no",   # 調達案件番号
    "procurement_item_name",  # 調達案件名称
    "award_date",            # 落札決定日（YYYY-MM-DD）
    "award_price",           # 落札価格
    "ministry_code",         # 府省コード
    "bidding_method_code",   # 入札方式コード
    "trade_name",            # 商号又は名称
    "corporate_number",      # 法人番号（欠落あり）
]

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)


def _fiscal_year_range(latest: int) -> range:
    """取得対象の年度（西暦）レンジ。新年度ファイルが増えても自動追随する。"""
    return range(START_FISCAL_YEAR, latest + 1)


def _fetch_zip(fiscal_year: int) -> bytes | None:
    """指定年度の全件データ zip を取得する。未提供年度は None を返す。

    未提供の年度に対して API は 404 ではなく 400 を返すことがあるため、
    どちらも「未提供」とみなして None を返す。
    """
    filename = f"successful_bid_record_info_all_{fiscal_year}.zip"
    req = Request(BASE_URL + filename, headers={"User-Agent": _UA})
    try:
        with urlopen(req, timeout=120) as resp:
            return resp.read()
    except HTTPError as e:
        if e.code in (400, 404):
            return None
        raise


def _rows_from_zip(content: bytes) -> list[list[str]]:
    """zip 内の CSV（UTF-8 BOM・ヘッダなし・8列）を行リストへ展開する。"""
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".csv"))
        raw = zf.read(name)
    text = raw.decode("utf-8-sig")
    rows: list[list[str]] = []
    for row in csv.reader(io.StringIO(text)):
        if not row:
            continue
        if len(row) != len(SOURCE_COLUMNS):
            raise ValueError(
                f"unexpected column count {len(row)} (expected {len(SOURCE_COLUMNS)})"
            )
        rows.append(row)
    return rows


def download_and_parse(csv_path: Path, latest_fiscal_year: int) -> int:
    """全年度の全件データを取得・結合してヘッダ付き CSV に書き出し、行数を返す。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[list[str]] = []
    for fiscal_year in _fiscal_year_range(latest_fiscal_year):
        content = _fetch_zip(fiscal_year)
        if content is None:
            logger.info(f"  {fiscal_year}年度: 未提供（skip）")
            continue
        rows = _rows_from_zip(content)
        logger.info(f"  {fiscal_year}年度: {len(rows)} 件")
        all_rows.extend(rows)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(SOURCE_COLUMNS)
        writer.writerows(all_rows)

    return len(all_rows)
