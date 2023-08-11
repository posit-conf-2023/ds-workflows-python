# Backup API

This API will act as a backup in the event that students get rate-limited/blocked from <https://data.cityofchicago.org>.

## Usage

### API

The API can be accessed here: <https://colorado.posit.co/rsc/connect/#/apps/68dcd8d7-8524-4d7a-8d04-4a9c5ca96541>.

```bash
# Get the business license data.
curl -X 'GET' 'https://colorado.posit.co/rsc/content/68dcd8d7-8524-4d7a-8d04-4a9c5ca96541/resource/r5kz-chrr.csv?limit=3'

# Get the food inspection data.
curl -X 'GET' 'https://colorado.posit.co/rsc/content/68dcd8d7-8524-4d7a-8d04-4a9c5ca96541/resource/4ijn-s7e5.csv?limit=3'
```

### Update the database

The API queries a database managed by Posit. To update the database run the [scripts/updated-db.ipynb](scripts/updated-db.ipynb) notebook.

```bash
jupyter nbconvert --execute --stdout --to markdown scripts/updated-db.ipynb
```