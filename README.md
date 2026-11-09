Royal Archives of Westeros

Project Overview

Royal Archives of Westeros is a Python-based document management application that combines file handling and MySQL database operations.

The application allows users to create and manage royal documents, retrieve stored records, modify document sections, and maintain an activity history.

It demonstrates the practical use of Python, SQL, file operations, database connectivity, input validation, and error handling in a command-line application.

Key Features

- Issue a Royal Decree: Create a text document and store its details in the database.
- View the Royal Registry: Retrieve and display registered documents.
- Read a Royal Document: Access document content using its database ID.
- Find and Replace Words: Modify the title, issuer, or content of an existing document.
- Maester's Chronicle: Review recorded document activities.
- File and Database Integration: Maintain document content as text files and associated information in MySQL.

Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Database | MySQL |
| Database Client | MySQL Workbench |
| Database Connector | MySQL Connector/Python |
| Development Environment | Visual Studio Code |
| Document Storage | Text Files |

Project Structure

file_handler_project/
│
├── main.py
├── database.sql
├── requirements.txt
├── README.md
├── .gitignore
│
└── decree_vault/
    └── The_Iron_Throne_Proclamation.txt


The 'decree_vault' directory stores document files created by the application. Additional documents are generated as new decrees are issued.

Database Design

The application uses the 'royal_archives' database with two tables.

1. royal_documents

Stores document information, including its ID, title, filename, document type, issuer, and creation timestamp.

2. maester_chronicle

Maintains an activity history containing the document title, action performed, additional details, and timestamp.

The database structure is provided in 'database.sql' so that it can be recreated independently of the development environment.

Setup and Execution

Prerequisites

- Python 3 installed.
- MySQL Server installed and running.
- MySQL Workbench or another MySQL client for database administration.
- Access to a MySQL account with permission to create databases and tables.

1. Obtain the Project

Download or clone the repository and open the extracted project directory in Visual Studio Code or another suitable development environment.

2. Prepare the Database

Execute the SQL statements in 'database.sql' using MySQL Workbench or the MySQL command-line client.

This creates the 'royal_archives' database and the tables required by the application.

3. Configure Database Credentials

The application reads the MySQL password from the 'MYSQL_PASSWORD' environment variable.

Configure this variable using the credentials of the local MySQL account. Do not place database passwords directly in the source code or commit them to the repository.

For Windows PowerShell, the variable can be configured for the current terminal session before launching the application.

4. Install Dependencies

Install the packages listed in 'requirements.txt':

py -m pip install -r requirements.txt


5. Launch the Application

From the project root directory, execute:

py main.py


The command-line menu provides access to the application's document management features.

Application Workflow

The application uses MySQL to store document metadata and activity records, while the actual document content is maintained in text files within 'decree_vault'.

When a document is created, its content is written to a file and its associated information is registered in MySQL. Subsequent operations use the document ID to locate the corresponding database record and file.

Document modifications update the relevant file and database information. Activities are recorded in the Maester's Chronicle.

Important Notes

- MySQL Server must be running before launching the application.
- The database must be initialized using 'database.sql' before application use.
- A valid 'MYSQL_PASSWORD' environment variable is required.
- The application expects the 'decree_vault' directory to be available in the project folder.
- The project does not include a copy of the developer's local MySQL database or credentials.
- Existing document files should be retained when transferring or submitting the project.

Purpose of the Project

This project was developed to demonstrate how a Python application can interact with a relational database while managing external files.

It provides practical experience with SQL operations, Python database connectivity, file handling, data retrieval, record modification, and activity logging.


Author
Salman