# Railway Deployment Guide

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional): Install via `npm i -g @railway/cli` or `brew install railway`
3. **GitHub Account**: For automatic deployments

## Deployment Methods

### Method 1: Deploy via Railway Dashboard (Recommended)

1. **Connect Repository**
   - Go to [railway.app](https://railway.app) and login
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub account
   - Select the `project-report-automation` repository

2. **Configure Environment Variables**
   - After project creation, go to "Variables" tab
   - Add the following variables:
     ```
     LLM_PROVIDER=openai
     OPENAI_API_KEY=your-actual-api-key-here
     PORT=8000
     ```
   - Optional variables:
     ```
     DATABASE_URL=sqlite:///./app.db
     SECRET_KEY=your-secret-key-here
     ```

3. **Deploy**
   - Railway will automatically detect:
     - `requirements.txt` → Install dependencies
     - `Procfile` → Start command
     - `railway.toml` or `railway.json` → Build config
   - Click "Deploy" or push to main branch
   - Wait for build to complete (~2-3 minutes)

4. **Access Your Application**
   - Go to "Settings" tab
   - Click "Generate Domain" under "Domains"
   - Your app will be available at: `https://your-app-name.up.railway.app`

### Method 2: Deploy via Railway CLI

1. **Install Railway CLI**
   ```bash
   # macOS
   brew install railway
   
   # npm
   npm i -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   cd /path/to/project-automation
   railway init
   ```
   - Select "Create new project" or link to existing

4. **Add Environment Variables**
   ```bash
   railway variables set LLM_PROVIDER=openai
   railway variables set OPENAI_API_KEY=your-actual-api-key
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get URL**
   ```bash
   railway open
   ```

### Method 3: Deploy from Local Git

1. **Initialize Git** (if not already done)
   ```bash
   cd /path/to/project-automation
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   ```

2. **Link to Railway**
   ```bash
   railway login
   railway link
   ```

3. **Push to Deploy**
   ```bash
   git push railway main
   ```

## Configuration Files Explained

### `railway.toml`
Main configuration file for Railway deployment:
- Builder: NIXPACKS (automatic detection)
- Start command: Uvicorn server
- Health check: `/health` endpoint
- Restart policy: Automatic restart on failure

### `railway.json`
Alternative JSON configuration (Railway supports both):
- Same configuration as TOML
- Used as fallback if TOML not found

### `Procfile`
Process definition for Railway:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### `runtime.txt`
Specifies Python version:
```
python-3.9.*
```

### `requirements.txt`
Pinned dependency versions for reproducible builds.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_PROVIDER` | AI provider to use | `openai` or `stub` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` (Railway auto-assigns) |
| `DATABASE_URL` | Database connection | `sqlite:///./app.db` |
| `SECRET_KEY` | App secret key | Auto-generated |

## Post-Deployment Verification

1. **Check Health Endpoint**
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```
   Expected response:
   ```json
   {"status": "ok"}
   ```

2. **Access Web Form**
   - Navigate to: `https://your-app-name.up.railway.app/`
   - You should see the project feasibility report form

3. **Test Submission**
   - Fill out the form with sample data
   - Click "Generate Report"
   - Verify submission and download work

## Monitoring & Logs

### View Logs
```bash
# Via CLI
railway logs

# Or via Dashboard
# Go to your project → Deployments → Click on deployment → View logs
```

### Monitor Performance
- Railway Dashboard → Metrics tab
- Shows CPU, memory, network usage
- Request counts and response times

## Updating the Deployment

### Automatic Updates (GitHub integration)
```bash
git add .
git commit -m "Update feature X"
git push origin main
```
Railway will automatically detect the push and redeploy.

### Manual Redeploy via CLI
```bash
railway up
```

### Rollback to Previous Version
```bash
# Via CLI
railway rollback

# Or via Dashboard
# Deployments tab → Select previous deployment → Rollback
```

## Troubleshooting

### Build Fails
1. Check logs: `railway logs --build`
2. Verify `requirements.txt` has correct versions
3. Ensure Python version matches `runtime.txt`

### App Crashes on Startup
1. Check runtime logs: `railway logs`
2. Verify environment variables are set correctly
3. Test health endpoint: `/health`
4. Check PORT binding (Railway auto-assigns via `$PORT`)

### Database Issues
- SQLite file location: `./app.db` (ephemeral on Railway)
- For production: Consider PostgreSQL plugin
  ```bash
  railway add postgresql
  ```
- Update `DATABASE_URL` to use Postgres connection string

### Missing Environment Variables
```bash
# List all variables
railway variables

# Set missing variable
railway variables set VARIABLE_NAME=value
```

## Database Persistence (Production)

Railway's filesystem is ephemeral. For production:

1. **Add PostgreSQL**
   ```bash
   railway add postgresql
   ```

2. **Update Code**
   - Install: `pip install psycopg2-binary`
   - Update `app/db.py` to use PostgreSQL URL from env

3. **Migration**
   - Add migration script if needed
   - Run migrations on deploy

## Cost Estimation

- **Free Tier**: $5 credit/month
- **Usage-based**: ~$0.000463 per GB-hour
- **Typical small app**: $5-10/month
- **With database**: +$5/month for PostgreSQL

## Security Best Practices

1. **Never commit `.env` file**
   - Already in `.gitignore`
   - Use Railway variables for secrets

2. **Rotate API Keys**
   - Update in Railway Variables tab
   - App will auto-restart with new values

3. **Enable HTTPS**
   - Automatic with Railway domains
   - Custom domains: Railway auto-provisions SSL

4. **Access Logs**
   - Monitor for suspicious activity
   - Set up alerts in Railway Dashboard

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Status Page**: https://status.railway.app
- **Pricing**: https://railway.app/pricing

## Next Steps After Deployment

1. ✅ Verify all endpoints work
2. ✅ Test full report generation flow
3. ⬜ Set up custom domain (optional)
4. ⬜ Configure PostgreSQL for persistence (Sprint 2)
5. ⬜ Add monitoring/alerting (Sprint 3)
6. ⬜ Implement queue workers (Sprint 4)

## Quick Commands Reference

```bash
# Login
railway login

# Initialize project
railway init

# Set variables
railway variables set KEY=VALUE

# Deploy
railway up

# View logs
railway logs

# Open app in browser
railway open

# Get deployment status
railway status

# List all variables
railway variables

# Rollback
railway rollback
```
