-- Creating users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    hash TEXT NOT NULL,
    profile_image TEXT,
    join_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    bio TEXT
);

-- Creating indexes for retrieving data faster
CREATE INDEX i_username ON users(username);
