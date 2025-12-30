-- 1. Create the 'issue-images' bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public) 
VALUES ('issue-images', 'issue-images', true)
ON CONFLICT (id) DO NOTHING;

-- 2. Enable RLS on objects if not already enabled (Standard Supabase setup)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 3. DROP existing policies to avoid conflicts if you re-run this
DROP POLICY IF EXISTS "Allow Public Uploads 1" ON storage.objects;
DROP POLICY IF EXISTS "Allow Public Viewing 1" ON storage.objects;

-- 4. Create Policy: Allow Public Uploads (INSERT)
-- This allows ANYONE (Anonymous & Logged in) to upload to 'issue-images'
CREATE POLICY "Allow Public Uploads 1"
ON storage.objects FOR INSERT
TO public
WITH CHECK (bucket_id = 'issue-images');

-- 5. Create Policy: Allow Public Viewing (SELECT)
-- This allows ANYONE to view/download images from 'issue-images'
CREATE POLICY "Allow Public Viewing 1"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'issue-images');

-- 6. (Optional) Allow Update/Delete if needed later
-- CREATE POLICY "Allow Public Update" ...
