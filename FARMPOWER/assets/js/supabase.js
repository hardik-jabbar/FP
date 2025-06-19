// assets/js/supabase.js
// Lightweight browser-side Supabase client wrapper.
// IMPORTANT: expose ONLY the public (anon) key to the browser.
// Never embed the service role key client-side.

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

// Supabase project details – taken from the anon JWT provided.
// The "ref" claim of the JWT is the project reference (fmqxdoocmapllbuecblc).
// Supabase URL pattern: https://<project_ref>.supabase.co
const SUPABASE_URL = 'https://fmqxdoocmapllbuecblc.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtcXhkb29jbWFwbGxidWVjYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY2NzYsImV4cCI6MjA2NTgxMjY3Nn0.iRtB8eYHC9LSqeBw1HCHXEWh-_mp9i3VWYUrnJYKk_w';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Helper: returns current auth user (if logged in via Supabase auth UI or GoTrue)
export function getCurrentUser() {
  return supabase.auth.getUser().then(({ data }) => data.user).catch(() => null);
}
