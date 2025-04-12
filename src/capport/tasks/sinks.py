import polars as pl


def df_to_csv(df: pl.DataFrame, filepath: str, include_header: bool = True, separator: str = ",") -> str:
    return df.write_csv(filepath, include_header=include_header, separator=separator)
