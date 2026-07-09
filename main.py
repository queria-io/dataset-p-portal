"""調達ポータル 落札実績オープンデータの取得 + dbt ビルド。

1. p_portal: 年度別の全件データ CSV を取得・結合して縦持ち CSV へ整形
2. dbt:      dbt ビルド
"""

import datetime
import logging
from pathlib import Path

from dbt.cli.main import dbtRunner

from pportal import download_and_parse

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("pipelines")

FDL_DIR = Path(".fdl")
CSV_PATH = FDL_DIR / "p_portal_awards.csv"


def dbt_build() -> None:
    dbt = dbtRunner()
    for cmd in (["deps"], ["run"], ["docs", "generate"]):
        result = dbt.invoke(cmd)
        if not result.success:
            raise SystemExit(f"dbt {cmd[0]} failed")


def main() -> None:
    FDL_DIR.mkdir(exist_ok=True)

    # 取得上限は当年度（会計年度・4月始まり）。新年度が始まれば自動的に追随する。
    # 未提供年度は skip されるため、年度初めの空白期間も安全に処理できる。
    today = datetime.date.today()
    latest = today.year if today.month >= 4 else today.year - 1

    logger.info("1/2: p_portal (落札実績 全件データ)")
    rows = download_and_parse(CSV_PATH, latest)
    logger.info(f"  p_portal_awards.csv: {rows} 件")

    logger.info("2/2: dbt build")
    dbt_build()


if __name__ == "__main__":
    main()
