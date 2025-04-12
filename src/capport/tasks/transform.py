import polars as pl


async def into_df(data: any, schema: dict = None) -> pl.DataFrame:
    return pl.DataFrame(data, schema=schema)
