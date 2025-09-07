# How to Fix the Render Database Connection Issue

## The Problem
Your Supabase connection string contains a placeholder `<IPv4>` that needs to be removed, and there are DNS resolution issues.

## Quick Fix

### Step 1: Get the Correct Connection String
1. Go to your Supabase dashboard
2. Navigate to Settings → Database
3. Copy the "Connection string" under "Connection parameters"
4. Make sure to use the "URI" format

### Step 2: Set the Environment Variable in Render
1. Go to your Render dashboard
2. Navigate to your web service
3. Go to "Environment" tab
4. Find the `DATABASE_URL` environment variable
5. Update it to:

```
postgresql://postgres:Farmpower%40123@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres
```

**Important Notes:**
- Remove the `?hostaddr=<IPv4>` part completely
- Make sure the password is URL encoded (`@` becomes `%40`)
- No spaces or extra characters

### Step 3: Alternative Connection String (if DNS issues persist)
If you still have DNS resolution issues, try using the direct IPv4 address:

```
postgresql://postgres:Farmpower%40123@[IP_ADDRESS]:5432/postgres
```

To find the IPv4 address:
1. Run: `nslookup db.fmqxdoocmapllbuecblc.supabase.co`
2. Use the IPv4 address in the connection string

### Step 4: Redeploy
After setting the environment variable:
1. Save the changes in Render
2. The service should automatically redeploy
3. Check the logs for connection success

## Expected Results
After the fix, you should see in the logs:
```
✅ Fixed Supabase URL by removing placeholder
✅ Database connection successful
```

## Troubleshooting
If you still see errors:
1. Verify the connection string format
2. Check that the password is URL encoded
3. Ensure there are no extra characters
4. Try using the direct IPv4 address instead of hostname

## Manual Test
You can test the connection string locally:
```bash
psql "postgresql://postgres:Farmpower%40123@db.fmqxdoocmapllbuecblc.supabase.co:5432/postgres"
```
