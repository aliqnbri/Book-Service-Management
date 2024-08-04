-- schema.sql
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    UNIQUE (title, author, genre)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (book_id) REFERENCES books (id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT unique_user_book_review UNIQUE (book_id, user_id)
);