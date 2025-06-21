// assets/js/supabase.js
// Lightweight browser-side Supabase client wrapper.
// IMPORTANT: expose ONLY the public (anon) key to the browser.
// Never embed the service role key client-side.

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

// Get Supabase URL and Anon Key from environment variables
// These are injected at build time in your deployment pipeline
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://fmqxdoocmapllbuecblc.supabase.co';
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtcXhkb29jbWFwbGxidWVjYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY2NzYsImV4cCI6MjA2NTgxMjY3Nn0.iRtB8eYHC9LSqeBw1HCHXEWh-_mp9i3VWYUrnJYKk_w';

// Initialize the Supabase client
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
});

// Helper: returns current auth user (if logged in via Supabase auth UI or GoTrue)
export async function getCurrentUser() {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    return user;
  } catch (error) {
    console.error('Error getting user:', error);
    return null;
  }
}

// Helper: Get the current session
export async function getSession() {
  const { data: { session } } = await supabase.auth.getSession();
  return session;
}

// Helper: Sign out
export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}
