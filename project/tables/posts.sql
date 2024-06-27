-- Creating the posts table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    summary TEXT NOT NULL,
    tags TEXT,
    cover_image TEXT,
    publish_date TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creating indexes for retrieving data faster
CREATE INDEX i_user_id ON posts(user_id);
