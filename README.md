# Admin Child Local Development

## One-command local setup

```bash
./scripts/bootstrap_local.sh
```

The bootstrap script:

1. Copies `.env.example` to `.env.local` when a local env file does not exist.
2. Starts a local PostgreSQL container from `docker-compose.yml` when Docker Compose is available.
3. Recreates the project virtual environment when it is missing or incompatible.
4. Installs Python dependencies from `requirements.txt`.
5. Imports the Flask app once so tables are created and development seed data is loaded.

## Run the app

```bash
source .venv/bin/activate
python run_local.py
```

Open <http://127.0.0.1:5000>. The development admin login is:

- Username: `admin`
- Password: `admin-pass`

## Local database

The default local database URL is:

```text
postgresql://admin_child:admin_child@127.0.0.1:5432/admin_child
```

In development, the app creates required tables automatically and seeds 100 sample consignments if fewer than 100 exist.

## Run tests

```bash
source .venv/bin/activate
python -m playwright install chromium
python -m pytest -q
```

If the browser cannot start on a Linux workstation, install Playwright system packages once with:

```bash
python -m playwright install-deps chromium
```
