"""
Supabase client utility for server-side operations.
This should only be used in server-side contexts as it uses the service role key.
"""
import os
from supabase import create_client, Client

def get_supabase() -> Client:
    """
    Initialize and return a Supabase client with service role key.
    This should only be used in server-side contexts.
    """
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and Service Role Key must be set in environment variables")
    
    return create_client(supabase_url, supabase_key)

def get_anon_client() -> Client:
    """
    Initialize and return a Supabase client with anon key.
    Safe for client-side use.
    """
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and Anon Key must be set in environment variables")
    
    return create_client(supabase_url, supabase_key)
