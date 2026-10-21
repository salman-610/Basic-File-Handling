
# Royal Archives of Westeros 🐉

A Python-based file handling system inspired by the world of Game of Thrones. The application manages royal documents using text files and MySQL database integration.

## Features

- Create and issue royal decrees.
- View the royal document registry.
- Read documents using their unique IDs.
- Find and replace whole words in document titles and contents.
- Update the issuer of a document.
- Record document activities in Maester's Chronicle.
- Handle invalid inputs, missing files, and database errors.

## Technologies Used

- Python
- MySQL
- MySQL Connector for Python
- Regular Expressions
- File Handling (TXT files)

## Project Structure

    file_handler_project/
    ├── main.py
    ├── database.sql
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    └── royal_scrolls/

## Prerequisites

- Python 3
- MySQL Server
- MySQL Workbench (recommended)
- Git (for version control)

## Setup Instructions

### 1. Clone the repository

    git clone YOUR_GITHUB_REPOSITORY_URL
    cd file_handler_project

Replace `YOUR_GITHUB_REPOSITORY_URL` with your repository's URL.

### 2. Install dependencies

    py -m pip install -r requirements.txt

### 3. Set up the database

Open `database.sql` in MySQL Workbench and execute the script.

### 4. Configure your MySQL password

In Windows Command Prompt, enter:

    set MYSQL_PASSWORD=your_actual_mysql_password

Replace the placeholder with your own MySQL password. Never publish your password.

### 5. Run the application

    py main.py

## Learning Objectives

This project demonstrates Python file input/output, string manipulation, regular expressions, exception handling, and database integration.

## Author

Salman A
