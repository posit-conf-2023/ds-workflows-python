from pathlib import Path
import pandas as pd
from pins import board_connect
import os
import ibis

from .console import console


def create_db_connection() -> ibis.BaseBackend:
    db_user = "posit"
    db_password = os.environ["CONF23_DB_PASSWORD"]
    db_host = os.environ["CONF23_DB_HOST"]
    db_port = 5432
    db_database = "python_workshop"

    con = ibis.postgres.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_database
    )
    return con


def get_zip_code_options(con: ibis.BaseBackend) -> dict[str, str]:
    """
    A helper function to generate all of the options for the zip code dropdown.
    """
    console.log("Getting zip code options...")

    data = con.table("business_license_validated") \
        [["zip_code"]] \
        .order_by([ibis.desc("zip_code")]) \
        .distinct() \
        .to_pandas()["zip_code"] \
        .tolist()
    options = {'': 'All'} | {i: i for i in data}
    return options


def get_license_code_options(con: ibis.BaseBackend) -> dict[str, str]:
    """
    A helper function to generate all of the options for the license code 
    dropdown.
    """
    console.log("Getting license code options...")   

    df = con.table("business_license_validated") \
        [["license_code", "license_description"]] \
        .distinct() \
        .to_pandas()
    
    options = {'': 'All'}
    
    for _, row in df.iterrows():
        key = row["license_code"]
        value = row["license_code"] + " - " + row["license_description"]
        options[key] = value

    return options
        
