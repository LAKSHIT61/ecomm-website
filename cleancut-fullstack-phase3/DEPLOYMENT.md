# CleanCut Production Deployment

This project is prepared for deployment on Render as one Docker web service plus managed PostgreSQL.

## 1. Put the project in GitHub

Create a repository and upload the contents of this folder to the repository root. Do not upload `backend/.env` or any real secrets.

## 2. Deploy with Render Blueprint

In Render Dashboard choose **New -> Blueprint**, connect the GitHub repository, and deploy the included `render.yaml`.

The Blueprint creates:
- `cleancut-store` web service
- `cleancut-db` PostgreSQL database

The service exposes `/api/health` as its health check.

## 3. Add secrets

During Blueprint setup, provide values for:

- `CORS_ORIGINS`: after the service exists, use the exact public URL, e.g. `https://cleancut-store.onrender.com`. If you later add a custom domain, include both origins separated by commas.
- `RAZORPAY_KEY_ID`: Razorpay public key ID
- `RAZORPAY_KEY_SECRET`: Razorpay secret

Never commit these values to Git.

## 4. Create the production admin

After the first successful deploy, run the admin creation command from a paid Render shell/one-off job or another secure environment with the same `DATABASE_URL`:

```bash
python -m backend.app.create_admin --email your-admin-email@example.com --password "USE-A-STRONG-PASSWORD" --name "CleanCut Admin"
```

Do not put the admin password in source control.

## 5. Custom domain

In Render, open the web service -> Settings -> Custom Domains and add your domain.

For a root domain, use the DNS record Render provides. If your DNS provider requires an A record, Render documents `216.24.57.1` for root domains. For `www`, use a CNAME to your Render `onrender.com` hostname. Remove conflicting AAAA records while configuring the domain.

Render provisions and renews TLS automatically.

## 6. Production database warning

The Blueprint uses Render's Free plans so the first deployment is inexpensive, but Render documents that Free Postgres expires after 30 days and has no backups. Before accepting real customers or storing valuable order data, upgrade the database to a paid plan and upgrade the web service as needed.

## 7. Local production-like check

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then check:

`http://127.0.0.1:8000/api/health`

## Important

Razorpay must be switched to its live credentials only after the site is running on the final HTTPS domain and you have completed your Razorpay account/business verification requirements.
