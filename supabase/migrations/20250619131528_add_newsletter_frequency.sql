-- Add new frequency column
ALTER TABLE profiles 
ADD COLUMN newsletter_frequency TEXT NOT NULL DEFAULT 'none';

-- Migrate existing subscribers to daily frequency
UPDATE profiles
SET newsletter_frequency = 'daily'
WHERE subscribed_newsletter = true;

-- Remove old boolean column
ALTER TABLE profiles 
DROP COLUMN subscribed_newsletter;
