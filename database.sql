
CREATE DATABASE IF NOT EXISTS royal_archives;

USE royal_archives;

CREATE TABLE IF NOT EXISTS royal_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    document_title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL UNIQUE,
    document_type VARCHAR(100),
    issued_by VARCHAR(100) DEFAULT 'King',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS maester_chronicle (
    entry_id INT AUTO_INCREMENT PRIMARY KEY,
    document_title VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details VARCHAR(500),
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
