from pathlib import Path
from typing import Optional

import polars as pl


def csv_to_df(filepath: str, casting: Optional[dict] = None) -> pl.DataFrame:
    fp = Path(filepath)
    if not fp.exists():
        raise Exception(f"{filepath} does not exist")
    return pl.read_csv(fp).cast(casting)
