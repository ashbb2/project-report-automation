# Railway Deployment Checklist

## Pre-Deployment Checklist

### ✅ Code Preparation
- [x] All dependencies listed in `requirements.txt` with pinned versions
- [x] `Procfile` configured with correct start command
- [x] `railway.toml` and `railway.json` configuration files created
- [x] `runtime.txt` specifies Python version
- [x] Health check endpoint `/health` implemented
- [x] `.gitignore` includes `.env` and sensitive files

### ⬜ Environment Variables (Set in Railway Dashboard)
- [ ] `LLM_PROVIDER` - Set to `openai` or `stub`
- [ ] `OPENAI_API_KEY` - Your OpenAI API key (required if using openai provider)
- [ ] `PORT` - Automatically set by Railway, no action needed
- [ ] `DATABASE_URL` - (Optional) For PostgreSQL, set after adding database

### ⬜ Railway Account Setup
- [ ] Sign up at https://railway.app
- [ ] Verify email address
- [ ] (Optional) Add payment method for usage beyond free tier

### ⬜ Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository is public or Railway has access
- [ ] Default branch is `main` or configured correctly

## Deployment Steps

### Method 1: Via Railway Dashboard (Easiest)

1. **Create Project**
   - [ ] Go to https://railway.app
   - [ ] Click "New Project"
   - [ ] Select "Deploy from GitHub repo"
   - [ ] Choose `project-report-automation` repository

2. **Configure Build**
   - [ ] Railway auto-detects configuration (railway.toml)
   - [ ] Verify build settings in project settings
   - [ ] Confirm Python version from runtime.txt

3. **Set Environment Variables**
   - [ ] Go to "Variables" tab
   - [ ] Add `LLM_PROVIDER=openai`
   - [ ] Add `OPENAI_API_KEY=sk-...`
   - [ ] Save changes

4. **Deploy**
   - [ ] Click "Deploy" or push to main branch
   - [ ] Wait for build to complete (2-3 minutes)
   - [ ] Check deployment logs for errors

5. **Generate Domain**
   - [ ] Go to "Settings" → "Domains"
   - [ ] Click "Generate Domain"
   - [ ] Copy your application URL: `https://xxxxx.up.railway.app`

### Method 2: Via Railway CLI

1. **Install CLI**
   ```bash
   # macOS
   brew install railway
   
   # Or via npm
   npm i -g @railway/cli
   ```

2. **Deploy**
   ```bash
   cd /path/to/project-automation
   railway login
   railway init
   railway variables set LLM_PROVIDER=openai
   railway variables set OPENAI_API_KEY=your-key
   railway up
   railway open
   ```

## Post-Deployment Verification

### ⬜ Functional Testing
- [ ] Visit application URL
- [ ] Health check responds: `https://your-app.railway.app/health`
- [ ] Web form loads correctly
- [ ] Fill and submit form with test data
- [ ] Verify submission returns ID
- [ ] Generate and download test report
- [ ] Confirm report contains expected sections

### ⬜ Performance Checks
- [ ] Check response times (<2s for form load)
- [ ] Verify report generation completes without timeout
- [ ] Monitor memory usage in Railway metrics
- [ ] Check for any error logs

### ⬜ Security Verification
- [ ] HTTPS enabled automatically (Railway default)
- [ ] Environment variables not exposed in logs
- [ ] `.env` file not committed to git
- [ ] API keys secured in Railway variables

## Monitoring Setup

### ⬜ Railway Dashboard
- [ ] Enable notifications for deployment failures
- [ ] Set up usage alerts (optional)
- [ ] Bookmark deployment logs page
- [ ] Note project ID for support requests

### ⬜ Application Monitoring
- [ ] Test error scenarios
- [ ] Verify error logging works
- [ ] Check database persistence (SQLite limitations noted)
- [ ] Monitor LLM API usage/costs

## Troubleshooting Common Issues

### Build Failures
- [ ] Check build logs in Railway dashboard
- [ ] Verify all dependencies in requirements.txt
- [ ] Confirm Python version compatibility
- [ ] Check for syntax errors in code

### Runtime Errors
- [ ] Review application logs: `railway logs`
- [ ] Verify environment variables are set
- [ ] Check health endpoint accessibility
- [ ] Confirm port binding ($PORT variable)

### Database Issues
- [ ] SQLite is ephemeral on Railway (resets on redeploy)
- [ ] For persistence, add PostgreSQL:
  ```bash
  railway add postgresql
  ```
- [ ] Update DATABASE_URL to Postgres connection string

## Optional Enhancements

### ⬜ Custom Domain
- [ ] Purchase domain
- [ ] Add domain in Railway settings
- [ ] Update DNS records as instructed
- [ ] Wait for SSL certificate provisioning

### ⬜ Database Upgrade (Recommended for Production)
- [ ] Add PostgreSQL service in Railway
- [ ] Update `requirements.txt`: add `psycopg2-binary`
- [ ] Modify `app/db.py` to support PostgreSQL
- [ ] Update `DATABASE_URL` environment variable
- [ ] Test database connection
- [ ] Migrate existing data (if any)

### ⬜ CI/CD Pipeline
- [ ] Enable automatic deployments from GitHub
- [ ] Set up deployment notifications (Slack/Discord)
- [ ] Configure staging environment (optional)
- [ ] Add automated tests before deploy

### ⬜ Monitoring & Alerts
- [ ] Set up external uptime monitoring (e.g., UptimeRobot)
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up log aggregation
- [ ] Create runbook for common issues

## Cost Management

### ⬜ Optimize Resource Usage
- [ ] Monitor usage in Railway dashboard
- [ ] Review billing estimates
- [ ] Optimize resource allocation if needed
- [ ] Consider usage-based pricing vs fixed plan

### Current Costs (Estimate)
- Free tier: $5 credit/month
- Small app: ~$5-10/month
- With PostgreSQL: +$5/month
- Total estimated: $10-15/month

## Rollback Plan

### ⬜ Prepare Rollback
- [ ] Note current deployment version
- [ ] Keep previous version accessible
- [ ] Document rollback procedure:
  ```bash
  # Via CLI
  railway rollback
  
  # Or via Dashboard
  # Deployments → Select previous → Rollback
  ```

## Documentation Updates

### ⬜ Update Project Docs
- [ ] Add production URL to README
- [ ] Document deployment process
- [ ] Update API endpoint URLs
- [ ] Add monitoring/support contacts

## Success Criteria

✅ Deployment is successful when:
- [ ] Application accessible via Railway URL
- [ ] All form fields render correctly
- [ ] Submissions save successfully
- [ ] Reports generate without errors
- [ ] Health check returns 200 OK
- [ ] No critical errors in logs
- [ ] Response times acceptable (<5s for report)

## Next Steps After Successful Deployment

1. [ ] Share production URL with stakeholders
2. [ ] Set up regular backups (for future PostgreSQL)
3. [ ] Plan Sprint 2 implementation (Baseline Lock)
4. [ ] Monitor usage and optimize as needed
5. [ ] Gather user feedback
6. [ ] Plan queue implementation (Sprint 4) when needed

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Status**: https://status.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Project Issues**: Check GitHub Issues
- **Deployment Guide**: `docs/RAILWAY_DEPLOYMENT.md`

## Notes

- SQLite is ephemeral on Railway - data resets on redeploy
- For production persistence, use PostgreSQL (add in Sprint 2)
- Free tier includes $5 credit/month
- Automatic HTTPS and SSL certificates
- Zero-downtime deployments enabled
