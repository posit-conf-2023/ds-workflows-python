# Example Workflow - City of Chicago Food Inspections

This repo is an example of an opinionated data science workflow for using Python with Posit's professional stack of products.

## Data

### (1) Business Licenses

<https://data.cityofchicago.org/Community-Economic-Development/Business-Licenses/r5kz-chrr>

| Description    | Database Host                                                                | Database Name   | Table                      |
| -------------- | ---------------------------------------------------------------------------- | --------------- | -------------------------- |
| Raw data       | posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com | python_workshop | business_license_raw       |
| Validated data | posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com | python_workshop | business_license_validated |

Usage:

```python
import os
import ibis

# Set up ibis for reading data
con = ibis.postgres.connect(
    user="posit",
    password=os.getenv("DB_PASSWORD"),
    host="posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com",
    port=5432,
    database="python_workshop"
)

df = con.table("business_license_validated").to_pandas()
```

### (2) Food Inspections

<https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5>

| Description    | Database Host                                                                | Database Name   | Table                     |
| -------------- | ---------------------------------------------------------------------------- | --------------- | ------------------------- |
| Raw data       | posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com | python_workshop | food_inspection_raw       |
| Validated data | posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com | python_workshop | food_inspection_validated |

Usage:

```python
import os
import ibis

# Set up ibis for reading data
con = ibis.postgres.connect(
    user="posit",
    password=os.getenv("DB_PASSWORD"),
    host="posit-conf-2023-ds-workflowsf5086c0.cpbvczwgws3n.us-east-2.rds.amazonaws.com",
    port=5432,
    database="python_workshop"
)

df = con.table("food_inspection_validated").to_pandas()
```

### (3) Business Map Data

A subset of the business license data. Saved as a Pin to Connect.

| Description | Pin Name                                 | URL                                                                                        |
| ----------- | ---------------------------------------- | ------------------------------------------------------------------------------------------ |
| Map data    | `sam.edwardes/chicago-business-map-data` | <https://colorado.posit.co/rsc/connect/#/apps/3d9a885b-263a-4b47-bbba-db2da51621be/access> |


Usage:

```python
from pins import board_connect

board = board_connect(server_url='https://colorado.posit.co/rsc/')
df = board.pin_read("sam.edwardes/chicago-business-map-data")
```