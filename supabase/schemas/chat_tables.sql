CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    title TEXT
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_session SERIAL,
    content TEXT,
    author TEXT,
    date TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_chat_sessions
      FOREIGN KEY (chat_session)
      REFERENCES chat_sessions(id)
      ON DELETE CASCADE
);