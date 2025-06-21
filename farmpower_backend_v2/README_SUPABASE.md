# Supabase Integration

This document outlines how the Supabase integration is set up in the FarmPower backend.

## Environment Variables

Create a `.env` file in the `farmpower_backend_v2` directory with the following variables:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Usage

### Client-Side (Browser)

Use the Supabase client from `assets/js/supabase.js`:

```javascript
import { supabase } from './supabase.js';

// Example: Sign in
auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password',
});
```

### Server-Side (Backend)

Use the Supabase client utility for server-side operations:

```python
from utils.supabase_client import get_supabase

# Initialize client
supabase = get_supabase()

# Example: Create a user
response = supabase.auth.admin.create_user({
    "email": "user@example.com",
    "password": "password",
    "email_confirm": True
})
```

## Security Considerations

1. **Never expose the service role key** in client-side code.
2. Use Row Level Security (RLS) in Supabase to control data access.
3. Validate all user inputs on both client and server sides.
4. Regularly rotate your API keys.

## RLS Policies

Set up Row Level Security policies in your Supabase dashboard to control data access. Example:

```sql
-- Enable RLS on a table
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows users to read their own data
CREATE POLICY "Users can view their own data"
  ON your_table FOR SELECT
  USING (auth.uid() = user_id);
```

## Testing

Test your Supabase integration with:

```bash
pytest tests/test_supabase.py -v
```

## Troubleshooting

- **Connection Issues**: Check your network and Supabase project settings.
- **Authentication Errors**: Verify your API keys and JWT configuration.
- **Permission Denied**: Check your RLS policies and user roles.

For more information, refer to the [Supabase Documentation](https://supabase.com/docs).
