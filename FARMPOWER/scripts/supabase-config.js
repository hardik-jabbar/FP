import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'

// Initialize Supabase client
const supabaseUrl = 'https://fmqxdoocmapllbuecblc.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtcXhkb29jbWFwbGxidWVjYmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyMzY2NzYsImV4cCI6MjA2NTgxMjY3Nn0.iRtB8eYHC9LSqeBw1HCHXEWh-_mp9i3VWYUrnJYKk_w';

export const supabase = createClient(supabaseUrl, supabaseKey);