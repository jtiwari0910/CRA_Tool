from contextlib import closing
from typing import Any, Iterable

import pandas as pd

from cra_studio.core.db import get_conn


def query_df(sql: str, params: Iterable[Any] = ()) -> pd.DataFrame:
    with closing(get_conn()) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def execute(sql: str, params: Iterable[Any] = ()) -> None:
    with closing(get_conn()) as conn:
        conn.execute(sql, tuple(params))
        conn.commit()
