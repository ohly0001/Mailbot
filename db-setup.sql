CREATE DATABASE IF NOT EXISTS Mailbot;
USE Mailbot;

CREATE TABLE correspondent_whitelist(
    correspondent_id INT AUTO_INCREMENT,
    preferred_name VARCHAR(100),
    email_address VARCHAR(254) UNIQUE NOT NULL,
    added_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (correspondent_id)
);

CREATE TABLE emails(
    email_id INT AUTO_INCREMENT,
    correspondent_id INT NOT NULL,
    subject_line VARCHAR(256),
    body_text MEDIUMTEXT,
    sent_on DATETIME,
    read_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_uid INT UNSIGNED UNIQUE;
    PRIMARY KEY (email_id),
    FOREIGN KEY (correspondent_id) 
    REFERENCES correspondent_whitelist(correspondent_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- fallback default
INSERT INTO correspondent_whitelist(preferred_name, email_address)
VALUES ('UNKNOWN', '?');