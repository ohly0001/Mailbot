CREATE DATABASE IF NOT EXISTS Mailbot;
USE Mailbot;

CREATE TABLE emails(
    email_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_line VARCHAR(255),
    body_text TEXT,
    sent_on DATETIME,
    read_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE correspondent_whitelist(
    correspondent_id INT AUTO_INCREMENT PRIMARY KEY,
    preferred_name VARCHAR(100),
    email_address VARCHAR(254) UNIQUE NOT NULL
);

CREATE TABLE email_correspondents(
    correspondent_id INT NOT NULL,
    email_id INT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES emails(email_id) ON DELETE CASCADE,
    FOREIGN KEY (correspondent_id) REFERENCES correspondent_whitelist(correspondent_id) ON DELETE CASCADE
);