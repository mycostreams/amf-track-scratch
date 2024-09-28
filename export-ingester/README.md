
To manually trigger the ingestion run:

```bash
docker compose up sftp mock-api
docker compose run --rm --no-deps export-ingester python -m export_ingester.main
docker compose down --profile down
```


To trigger the ingestion via cron jobs run:

```bash
docker compose --profile dev up
```

