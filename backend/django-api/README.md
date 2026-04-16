# Heart Disease Django API

Minimal Django REST Framework backend for the heart-disease-system.

## Scope

- `/api/health`
- `/api/auth/login`
- `/api/dashboard/overview`
- `/api/analysis/age`
- `/api/analysis/lifestyle`
- `/api/analysis/clinical`
- `/api/model/metrics`
- `/api/predict`

Analytics endpoints read offline MySQL ADS tables generated from Hive. They do not query CSV files or Hive on every page request.

## Run

```bash
cd heart-disease-system/backend/django-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Notes

- Login uses Django's built-in users. Create an account with `python manage.py createsuperuser`.
- Keep `ANALYTICS_QUERY_ENGINE=mysql` for normal API/page reads.
- Run `bigdata/scripts/load_to_hive.sh`, then `bigdata/scripts/sync_hive_ads_to_mysql.py`, before opening the dashboard.
- Configure `ADS_MYSQL_HOST`, `ADS_MYSQL_PORT`, `ADS_MYSQL_DATABASE`, `ADS_MYSQL_USER`, and `ADS_MYSQL_PASSWORD`.
- CORS is configurable through environment variables.
- Database defaults to SQLite, but the settings support MySQL when `DATABASE_ENGINE=mysql`.
