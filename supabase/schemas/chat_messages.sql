CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_session SERIAL,
    content TEXT,
    author TEXT

    CONSTRAINT fk_chat_sessions
      FOREIGN KEY(chat_session)
        REFERENCES chat_sessions(id)
        ON DELETE CASCADE
)