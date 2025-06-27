-- Create table for IPEX calendar events
CREATE TABLE IF NOT EXISTS ipex_events (
    id TEXT PRIMARY KEY,  
    title TEXT NOT NULL,  
    start_date DATE,      
    end_date DATE,        
    meeting_location TEXT, 
    tags TEXT[],
    embedding_input text NOT NULL,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()   
);
