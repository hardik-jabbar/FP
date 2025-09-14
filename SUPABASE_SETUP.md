# Supabase Database Setup Guide

## Issue: `<IPv4>` Placeholder in Supabase Connection String

The error shows that your Supabase connection string contains a placeholder `<IPv4>` at the end, which needs to be removed.

## Current Connection String:
```
postgresql://postgres:9yFWrNN9wL6adLqA@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

## Fixed Connection String:
```
postgresql://postgres:%5BFarmpower%40123%5D@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

## Steps to Fix:

### 1. Get Your Supabase Connection String

1. Go to your Supabase dashboard
2. Navigate to Settings → Database
3. Copy the "Connection string" under "Connection parameters"
4. Make sure to use the "URI" format

### 2. Set Environment Variable in Render

1. Go to your Render dashboard
2. Navigate to your web service
3. Go to "Environment" tab
4. Add or update the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

**Important:** 
- Replace `[YOUR-PASSWORD]` with your actual Supabase database password
- Make sure there's NO `?hostaddr=<IPv4>` at the end
- URL encode special characters in the password (e.g., `@` becomes `%40`)

### 3. URL Encoding for Special Characters

If your password contains special characters, you need to URL encode them:

- `@` → `%40`
- `#` → `%23`
- `$` → `%24`
- `%` → `%25`
- `&` → `%26`
- `+` → `%2B`
- `=` → `%3D`
- `?` → `%3F`

### 4. Example with Your Password

If your password is `Farmpower@123`, the encoded version is `Farmpower%40123`:

```
DATABASE_URL=postgresql://postgres:Farmpower%40123@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

### 5. Verify the Fix

After setting the environment variable:

1. Redeploy your application
2. Check the logs for:
   ```
   ✅ Fixed Supabase URL by removing placeholder
   ✅ Database connection successful
   ```
3. Test the health endpoint: `https://your-app.onrender.com/health`

### 6. Alternative: Use Supabase Environment Variables

You can also set these individual environment variables in Render:

```
SUPABASE_URL=https://fmqxdoocmapllbuecblc.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:Farmpower%40123@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

## Troubleshooting

### If you still see `<IPv4>`:
1. Check that the environment variable is set correctly in Render
2. Make sure there are no extra characters or spaces
3. Verify the password is URL encoded properly
4. Redeploy the application after making changes

### If connection still fails:
1. Check Supabase dashboard for database status
2. Verify the connection string format
3. Test the connection string locally
4. Check Render logs for detailed error messages

## Security Notes

- Never commit database passwords to your repository
- Use environment variables for all sensitive data
- Consider using Supabase's connection pooling for production
- Enable SSL connections (Supabase requires this by default)

## Next Steps

1. Set the correct `DATABASE_URL` in Render
2. Redeploy your application
3. Verify the health endpoint works
4. Test your application functionality
