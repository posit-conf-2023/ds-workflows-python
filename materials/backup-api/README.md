# Backup API

This API will act as a backup in the event that students get rate-limited/blocked from <https://data.cityofchicago.org>.

## Usage

### API

The API can be accessed here: <>.

```bash
# Get the business license data.

# Get the food inspection data.
```

### Update the database

The API queries a database managed by Posit. To update the database run the [scripts/updated-db.ipynb](scripts/updated-db.ipynb) notebook.

```bash
jupyter nbconvert --execute --stdout --to markdown scripts/updated-db.ipynb
```