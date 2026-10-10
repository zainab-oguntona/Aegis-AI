# Aegis financial security API

Phase 1 provides the Django foundation, PostgreSQL/Redis development services, fintech client records, and hashed API-key authentication.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///db.sqlite3"
python manage.py migrate
python manage.py runserver
```

Check `GET /api/v1/health/`. Protected endpoints use the `Api-Key` header. API keys are issued through the Django shell/admin and only the raw value returned at issuance should be given to the client.

The authenticated client smoke-test endpoint is `GET /api/v1/client/`.

Open `http://localhost:8000/` for the demo dashboard. To create a local API key, run:

```powershell
python manage.py shell -c "from apps.clients.models import Client, APIKey; c=Client.objects.create(name='Demo fintech'); print(APIKey.issue(c)[1])"
```

Paste the printed key into the dashboard before running a scenario.

Phase 2 adds `POST /api/v1/risk-assessment/`. Supply `transaction_id`, tokenized user data, amount/currency, selected `enabled_modules`, and optional normalized `module_scores`. The endpoint persists the transaction and assessment and applies weighted score fusion.

Phase 3 adds `POST /api/v1/transaction-risk/`, which evaluates amount deviation against the sender's supplied baseline and recipient novelty/verification signals.

Phase 4 adds independently callable `POST /api/v1/recipient-risk/` for recipient-only checks.

Phase 5 adds `POST /api/v1/environment-risk/`. Device, network, location, telecom, and account-security values are supplied by the fintech or authorized providers; the API does not claim to discover these values itself.

Phase 6 adds `POST /api/v1/facial-risk/`. It accepts derived emotion probabilities from an ML service or mock implementation and never stores raw facial images. Facial emotion is treated as one risk signal, not proof of fraud or coercion.

## Docker

Copy `.env.example` to `.env`, set real local values, then run `docker compose up --build`.
