-- Creating a table for follow transactions
CREATE TABLE follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    follower_id INTEGER NOT NULL,
    following_id INTEGER NOT NULL,
    follow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (follower_id) REFERENCES users(id),
    FOREIGN KEY (following_id) REFERENCES users(id)
);

-- Creating indexes for retrieving data faster
CREATE INDEX i_follower_id ON follows (follower_id);
CREATE INDEX i_following_id ON follows (following_id);
