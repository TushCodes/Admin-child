# Admin authentication

Admin authentication is split by responsibility:

- `app.middleware.admin_auth` protects the `/admin` and `/flask-admin` URL spaces before protected handlers run.
- `routes/admin/auth_routes.py` renders the login form, authenticates submitted credentials with Supabase Auth, and clears sessions on logout.
- `admin/auth.py` owns Supabase Auth integration, session state, and the development-only local fallback.
- Flask-Admin views in `admin/flask_admin_setup.py` keep their own `is_accessible()` checks as a second layer of protection and call `is_admin_authenticated()` only when they need an explicit access decision.

## Supabase Auth configuration

Production should authenticate admin users with Supabase email/password users. Configure these variables in the deployment environment:

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_AUTH_KEY=your-supabase-anon-key
ADMIN_AUTH_PROVIDER=supabase
```

`SUPABASE_AUTH_KEY` is preferred for authentication. If it is not set, the app falls back to `SUPABASE_ANON_KEY` and then the existing `SUPABASE_KEY` variable used by other Supabase integrations.

Create the admin user in Supabase Auth, then sign in at `/admin/login` with that user's email address and password. The Flask session stores the Supabase access token metadata and treats the admin as signed in until the Supabase session expiry time is reached.

## Local verification

Local development can use the same Supabase flow by adding the Supabase variables above to `.env.local`. This lets you verify the production-style authentication flow without changing code.

If Supabase variables are not configured locally, `ADMIN_AUTH_PROVIDER` defaults to `local` and the development fallback remains available so the rest of the admin UI can still be exercised:

```text
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin-pass
```

When Supabase is configured in development but a sign-in fails, the app falls back to the local credentials unless `SUPABASE_AUTH_DISABLE_LOCAL_FALLBACK=true` is set.
