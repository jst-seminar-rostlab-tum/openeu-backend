CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type TEXT NOT NULL,
    message TEXT,
    FOREIGN KEY (user_id) REFERENCES auth.users (id) ON DELETE CASCADE
);
