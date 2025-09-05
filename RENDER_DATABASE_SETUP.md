# Render Database Setup Guide

## Issue: `<IPv4>` Placeholder in DATABASE_URL

The error `could not parse network address "<IPv4>": Name or service not known` indicates that the Render database connection string is not properly configured.

## Steps to Fix:

### 1. Create the Database in Render

1. Go to your Render dashboard
2. Click "New +" → "PostgreSQL"
3. Name it: `farmpower-db`
4. Choose the same region as your web service
5. Select the free plan
6. Click "Create Database"

### 2. Link Database to Your Service

1. Go to your web service in Render
2. Go to "Environment" tab
3. You should see the database automatically linked
4. If not, click "Link Database" and select `farmpower-db`

### 3. Verify Environment Variables

In your service's Environment tab, you should see:

```
DATABASE_URL = postgresql://user:password@host:port/database
DB_HOST = actual-host-name
DB_PORT = 5432
DB_NAME = farmpower
DB_USER = actual-username
DB_PASSWORD = actual-password
```

### 4. Check render.yaml Configuration

Your `render.yaml` should have:

```yaml
databases:
  - name: farmpower-db
    databaseName: farmpower
    user: farmpower_user
    plan: free

services:
  - type: web
    name: farmpower-backend
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: farmpower-db
          property: connectionString
      - key: DB_HOST
        fromDatabase:
          name: farmpower-db
          property: host
      # ... other DB_* variables
```

### 5. Manual Database Creation (if needed)

If the database doesn't exist, you can create it manually:

1. In Render dashboard, go to "Databases"
2. Click "New PostgreSQL Database"
3. Name: `farmpower-db`
4. Database: `farmpower`
5. User: `farmpower_user`
6. Region: Same as your service
7. Plan: Free

### 6. Troubleshooting

If you still see `<IPv4>`:

1. **Check Database Status**: Ensure the database is "Available" (not "Creating" or "Failed")
2. **Check Service Link**: Go to your service → Environment → verify database is linked
3. **Redeploy**: After linking, trigger a new deployment
4. **Check Logs**: Look for the startup check messages in deployment logs

### 7. Alternative: Use External Database

If Render's managed database continues to have issues, you can use an external PostgreSQL database:

1. Get connection details from your database provider
2. Set environment variables manually in Render:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

### 8. Verify Fix

After setup, check the health endpoint:
```
https://your-app.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Common Issues:

1. **Database not created**: The `farmpower-db` database doesn't exist
2. **Not linked**: Database exists but not linked to the service
3. **Wrong region**: Database and service in different regions
4. **Database still creating**: Wait for database to be "Available"
5. **Cached environment**: Old environment variables cached

## Next Steps:

1. Create the database in Render
2. Link it to your service
3. Redeploy your application
4. Check the logs for the startup check messages
5. Verify the health endpoint works
