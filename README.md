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

Open <http://127.0.0.1:5000>. Admin login now supports Supabase Auth. To verify the production-style flow locally, add these values to `.env.local` and sign in with a Supabase Auth user's email/password:

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_AUTH_KEY=your-supabase-anon-key
ADMIN_AUTH_PROVIDER=supabase
```

Without Supabase variables, local development falls back to:

- Email/username: `admin`
- Password: `admin-pass`

## Frontend layout

All Flask-rendered frontend code now lives under `frontend/`:

- `frontend/templates/` contains page, layout, partial, admin, and error templates.
- `frontend/static/` contains CSS, JavaScript, images, fonts, and the favicon.

Flask is configured to serve these centralized folders through the standard `render_template(...)` and `url_for('static', ...)` APIs, so templates do not need per-blueprint template folders.


## SCSS stylesheets

Project-owned styles are now maintained as SCSS source files with matching compiled CSS files kept in the existing static paths used by Flask templates. Install the Sass toolchain once and rebuild CSS after changing any `.scss` file:

```bash
npm install
npm run build:scss
```

To validate that every CSS file has a matching SCSS source and that all SCSS files compile without overwriting committed CSS, run:

```bash
npm run verify:scss
```

For compile-only validation into the temporary `.scss-build` tree, run:

```bash
npm run check:scss
```

The build keeps compiled files in the same `frontend/static/css`, `frontend/static/assets/css`, and `admin/static/css` locations so existing `url_for('static', filename='...css')` template references continue to work without UI or routing changes.

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
