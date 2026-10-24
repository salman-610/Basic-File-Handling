Basic File Handling

Theme - Royal Archives of Westeros

Royal Archives of Westeros is a Python-based document management application inspired by the world of Game of Thrones. It combines text-file operations with MySQL database integration to create, store, organize, and retrieve royal documents.

Features

- Issue Royal Decrees: Create new royal documents and save their contents as text files.
- Royal Registry: View registered documents and their details from the MySQL database.
- Read Documents: Retrieve and read documents using their unique document IDs.
- Document Editing: Find and replace whole words in document titles and contents.
- Issuer Management: Update the person or authority responsible for issuing a document.
- Activity Tracking: Record document operations in Maester's Chronicle.
- Error Handling: Handle invalid inputs, missing files, duplicate filenames, and database connection errors.

Technologies Used

- Python 3
- MySQL
- MySQL Connector/Python
- Regular Expressions (`re`)
- File Handling (`os`)
- Git and GitHub

Project Structure


file_handler_project/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── royal_scrolls/
    └── [Royal document text files]


*Note: The structure above represents the main project files. Add `database.sql` if you create and maintain a database setup script.*

Prerequisites

Before running the application, ensure you have:

- Python 3 installed
- MySQL Server installed and running
- MySQL Workbench (recommended for database management)
- Git installed
- A MySQL account with permission to access the project database

Installation and Setup

1. Clone the Repository:


git clone https://github.com/salman-610/Basic-File-Handling.git
cd Basic-File-Handling


2. Install Dependencies:

Install the required Python packages:


py -m pip install -r requirements.txt


3. Configure the MySQL Database:

Create a database named `royal_archives` and configure the required tables:

- `royal_documents` — stores document details and filenames.
- `maester_chronicle` — stores a history of document activities.

Ensure the table definitions match those expected by `main.py`. If you maintain a `database.sql` file, you can use it to create the database structure.

4. Configure the MySQL Password:

The application reads the MySQL password from an environment variable named `MYSQL_PASSWORD`.

In Windows Command Prompt, run:

cmd
set MYSQL_PASSWORD=your_actual_mysql_password


Replace the example value with your own MySQL password. Keep your password private and never commit it to GitHub.

This command applies to the current Command Prompt session.

5. Run the Application:

From the project directory, execute:


py main.py
```

Follow the on-screen menu to manage royal documents.

Learning Objectives:

This project provides practical experience with:

- Reading and writing text files in Python
- Organizing files and managing filenames
- Using regular expressions for text replacement
- Connecting Python applications to MySQL
- Executing SQL queries and managing database records
- Handling exceptions and validating user input
- Tracking application activities
- Using Git and GitHub for version control

Author:

Salman A

