// Initialize Supabase client
const supabaseUrl = 'https://your-project-url.supabase.co';
const supabaseKey = 'your-anon-key';

const supabase = supabase.createClient(supabaseUrl, supabaseKey);

window.supabase = supabase; // Make supabase globally available