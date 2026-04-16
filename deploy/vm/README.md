# VM Deployment

Runtime target: the current VM host.

- Hadoop/Hive build offline ODS/DWD/ADS tables.
- `bigdata/scripts/sync_hive_ads_to_mysql.py` copies Hive ADS into local MySQL `heart_disease`.
- Django reads MySQL ADS tables with `ANALYTICS_QUERY_ENGINE=mysql`.
- Django serves the API on port `8000`.
- The Vue3 production build is served directly by `python3 -m http.server` on port `4173`.
- The frontend resolves the API at runtime as `http://<current-host>:8000/api`, so no nginx proxy or fixed VM IP is required.
