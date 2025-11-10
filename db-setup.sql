IF DB_ID('Mailbot') IS NULL CREATE DATABASE Mailbot;
GO
USE Mailbot;
GO

CREATE TABLE emails(
    email_id INT IDENTITY PRIMARY KEY,
    subject_line NVARCHAR(255),
    body_text NVARCHAR(MAX),
    sent_on DATETIME2,
    read_on DATETIME2 DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE correspondent_whitelist(
    correspondent_id INT IDENTITY PRIMARY KEY,
    preferred_name NVARCHAR(100),
    email_address NVARCHAR(254) UNIQUE NOT NULL
);

CREATE TABLE email_correspondents(
    correspondent_id INT FOREIGN KEY 
    REFERENCES correspondent_whitelist(correspondent_id) 
    ON DELETE CASCADE,
    email_id INT FOREIGN KEY (email_id) 
    REFERENCES emails(email_id) 
    ON DELETE CASCADE
);