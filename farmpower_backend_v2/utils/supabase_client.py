"""
Supabase client utility for server-side operations.
This should only be used in server-side contexts as it uses the service role key.
"""
import os
from supabase import create_client, Client
from typing import Optional

def get_supabase() -> Client:
    """
    Initialize and return a Supabase client with service role key.
    This should only be used in server-side contexts.
    
    Returns:
        Client: Authenticated Supabase client with service role privileges
    """
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase URL and Service Role Key must be set in environment variables. "
            "Please check your .env file."
        )
    
    return create_client(supabase_url, supabase_key)

def get_anon_client() -> Client:
    """
    Initialize and return a Supabase client with anon key.
    Safe for client-side use.
    
    Returns:
        Client: Authenticated Supabase client with anon privileges
    """
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Supabase URL and Anon Key must be set in environment variables. "
            "Please check your .env file."
        )
    
    return create_client(supabase_url, supabase_key)

def get_supabase_user(token: Optional[str] = None) -> dict:
    """
    Get the current user from Supabase using the provided JWT token.
    
    Args:
        token: Optional JWT token. If not provided, uses the current session.
        
    Returns:
        dict: User information
    """
    supabase = get_supabase()
    
    if token:
        # Verify the token and get the user
        user = supabase.auth.get_user(token)
    else:
        # Get user from the current session
        user = supabase.auth.get_user()
    
    return user
