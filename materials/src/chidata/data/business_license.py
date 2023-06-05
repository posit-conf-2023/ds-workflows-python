import pandera as pa
import pandas as pd

from ..client import api_client

schema = pa.DataFrameSchema({
    "id": pa.Column(str),
    "license_id": pa.Column(str)
})


def get() -> pd.DataFrame:
    # Fetch the data.
    with api_client() as client:
        r = client.get(
            "r5kz-chrr.json", 
            params={"$limit": 100}, 
            headers={"Accept": "application/json"}
        )
        r.raise_for_status()

    # Validate the data
    df = schema.validate(pd.DataFrame.from_records(r.json()))

    return df
        
    

    