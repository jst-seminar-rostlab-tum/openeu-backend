CREATE TABLE tweets (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    author JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    reply_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    quoted_tweet JSONB NULL,
    retweeted_tweet JSONB NULL,
    embedding_input TEXT NULL,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
