import os

import ibis
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import Response


load_dotenv()
app = FastAPI()


@app.get("/resource/{id}", response_class=Response)
async def resource(
    id: str,
    order: str | None = None,
    limit: int = 3
):

    # Create connection to database.
    con = ibis.postgres.connect(
        user="rsw_db_admin",
        password=os.environ["CONF23_DB_PASSWORD"],
        host="postgres-database-samedwardes-test7d1ba05.cpbvczwgws3n.us-east-2.rds.amazonaws.com",
        port=5432,
        database="rsw",
    )

    # Query the database.
    if id == "r5kz-chrr.csv":
        table = con.table("business_license_raw")
    elif id == "4ijn-s7e5.csv":
        table = con.table("food_inspection_raw")
    else:
        raise ValueError(f"The provided 'id' {id} is not recognized.")
    
    if order:
        df = table.order_by(order).limit(limit).to_pandas()
    else:
        df = table.limit(limit).to_pandas()

    # Return a CSV file.
    return Response(content=df.to_csv(index=False), media_type="text/csv")
