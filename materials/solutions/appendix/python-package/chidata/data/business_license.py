import pandas as pd
import pandera as pa
from rich import inspect

from ..client import api_client

schema = pa.DataFrameSchema({"id": pa.Column(str), "license_id": pa.Column(str)})


def get(n: int = 100) -> pd.DataFrame:
    # Set up pagination
    step = min(1000, n)
    data = []

    # Fetch the data.
    with api_client() as client:
        # Paginate through the data.
        for offset in range(0, n, step):
            limit = min(step, n - len(data))
            r = client.get(
                "r5kz-chrr.json",
                headers={"Accept": "application/json"},
                params={"$order": "id", "$limit": limit, "$offset": offset},
            )
            r.raise_for_status()
            data += r.json()

    # Validate the data
    df = schema.validate(pd.DataFrame.from_records(data))

    return df
