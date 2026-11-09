CREATE DATABASE IF NOT EXISTS royal_archives
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE royal_archives;

CREATE TABLE IF NOT EXISTS royal_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    document_title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(100),
    issued_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS maester_chronicle (
    entry_id INT AUTO_INCREMENT PRIMARY KEY,
    document_title VARCHAR(255),
    action VARCHAR(50),
    details TEXT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
