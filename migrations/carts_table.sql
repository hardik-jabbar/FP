-- Create carts table
CREATE TABLE public.carts (
    id uuid DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    items jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT NOW(),
    updated_at timestamptz DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE public.carts ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to view their own cart
CREATE POLICY "Users can view their own cart" ON public.carts
    FOR SELECT USING (auth.uid() = user_id);

-- Create policy to allow users to update their own cart
CREATE POLICY "Users can update their own cart" ON public.carts
    FOR UPDATE USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own cart
CREATE POLICY "Users can insert their own cart" ON public.carts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own cart
CREATE POLICY "Users can delete their own cart" ON public.carts
    FOR DELETE USING (auth.uid() = user_id);
