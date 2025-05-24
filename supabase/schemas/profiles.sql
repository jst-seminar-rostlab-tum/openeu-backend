CREATE TABLE profiles (
    id                      uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    name                    text IS NOT NULL,
    surname                 text IS NOT NULL, 
    company_name            text IS NOT NULL, 
    company_description     text IS NOT NULL, 
    topic_list              text[] IS NOT NULL 
)