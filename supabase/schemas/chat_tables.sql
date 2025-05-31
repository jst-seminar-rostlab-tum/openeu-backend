CREATE TABLE IF NOT EXISTS chat_sessions (
    id TEXT PRIMARY KEY DEFAULT (gen_random_uuid())::text,
    user_id TEXT,
    title TEXT
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY DEFAULT (gen_random_uuid())::text,
    chat_session TEXT,
    content TEXT,
    author TEXT,
    date TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_chat_sessions
      FOREIGN KEY (chat_session)
      REFERENCES chat_sessions(id)
      ON DELETE CASCADE
);