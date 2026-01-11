DROP TABLE IF EXISTS sessions;

CREATE TABLE sessions (
  session_id INTEGER PRIMARY KEY AUTOINCREMENT,
  machine_id TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  time_in TEXT NOT NULL,
  status TEXT NOT NULL
);
