
import os
import re

import mysql.connector
from mysql.connector import Error


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVES_DIR = os.path.join(BASE_DIR, "royal_scrolls")



def connect_database():
    """Connect to the Royal Archives database."""
    try:
        password = os.getenv("MYSQL_PASSWORD")

        if not password:
            print("MySQL password not found.")
            print("Please set the MYSQL_PASSWORD environment variable.")
            return None

        return mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="royal_archives"
        )

    except Error as error:
        print(f"Database connection failed: {error}")
        return None



def log_action(cursor, title, action, details):
    """Record an action in the Maester's Chronicle."""
    cursor.execute(
        """
        INSERT INTO maester_chronicle
        (document_title, action, details)
        VALUES (%s, %s, %s)
        """,
        (title, action, details)
    )


def display_welcome():
    print("\n===================================")
    print("   THE ROYAL ARCHIVES OF WESTEROS")
    print("===================================")
    print("Welcome, Your Grace!")


def make_filename(title):
    """Convert a title into a safe text filename."""
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
    safe_title = safe_title.strip(" .")

    if not safe_title:
        return None

    return safe_title + ".txt"


def replace_whole_words(text, search_word, replacement):
    """Find whole words without case sensitivity."""
    pattern = r"\b" + re.escape(search_word) + r"\b"

    return re.subn(
        pattern,
        lambda match: replacement,
        text,
        flags=re.IGNORECASE
    )


def get_safe_path(file_name):
    """Ensure a document path stays inside royal_scrolls."""
    if os.path.basename(file_name) != file_name:
        raise ValueError("Invalid document filename.")

    return os.path.join(ARCHIVES_DIR, file_name)


def get_document(cursor):
    """Display registered documents and return the selected one."""
    cursor.execute(
        """
        SELECT document_id, document_title, file_name
        FROM royal_documents
        ORDER BY document_id
        """
    )
    documents = cursor.fetchall()

    if not documents:
        print("No documents are registered in the archives.")
        return None

    print("\n--- CONSULT THE ROYAL ARCHIVES ---")

    for document in documents:
        print(f"ID: {document[0]} | {document[1]}")

    try:
        document_id = int(
            input("\nEnter the document ID: ").strip()
        )

        if document_id <= 0:
            raise ValueError

    except ValueError:
        print("Please enter a valid positive numeric document ID.")
        return None

    cursor.execute(
        """
        SELECT document_id, document_title, file_name
        FROM royal_documents
        WHERE document_id = %s
        """,
        (document_id,)
    )

    document = cursor.fetchone()

    if document is None:
        print("No document exists with that ID.")
        return None

    return document


def issue_royal_decree():
    """Create a decree file and register it in MySQL."""
    connection = None
    cursor = None
    file_path = None

    try:
        os.makedirs(ARCHIVES_DIR, exist_ok=True)

        title = input("\nEnter the decree title: ").strip()

        if not title:
            print("The decree title cannot be empty.")
            return

        contents = input("Enter the decree contents: ").strip()
        issuer = input("Issued by: ").strip() or "King"

        file_name = make_filename(title)

        if file_name is None:
            print("Please enter a valid title.")
            return

        file_path = get_safe_path(file_name)

        if os.path.exists(file_path):
            print("A scroll with this filename already exists.")
            return

        connection = connect_database()

        if connection is None:
            return

        cursor = connection.cursor()

        cursor.execute(
            "SELECT document_id FROM royal_documents WHERE file_name = %s",
            (file_name,)
        )

        if cursor.fetchone():
            print("This filename is already registered.")
            return

        with open(file_path, "x", encoding="utf-8") as file:
            file.write("THE ROYAL ARCHIVES OF WESTEROS\n")
            file.write("=" * 35 + "\n")
            file.write(f"Title: {title}\n")
            file.write(f"Issued by: {issuer}\n")
            file.write("=" * 35 + "\n\n")
            file.write(contents + "\n")
            file.write("=" * 35 + "\n")

        try:
            cursor.execute(
                """
                INSERT INTO royal_documents
                (document_title, file_name, document_type, issued_by)
                VALUES (%s, %s, %s, %s)
                """,
                (title, file_name, "Royal Decree", issuer)
            )

            log_action(
                cursor,
                title,
                "CREATE",
                "A new royal decree was issued."
            )

            connection.commit()

            print("\nThe royal decree has been issued successfully!")

        except Exception:
            connection.rollback()

            if os.path.exists(file_path):
                os.remove(file_path)

            raise

    except (OSError, Error) as error:
        print(f"Unable to issue the decree: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def view_royal_registry():
    """Display all registered royal documents."""
    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT document_id, document_title,
                   document_type, issued_by, created_at
            FROM royal_documents
            ORDER BY document_id
            """
        )

        documents = cursor.fetchall()

        print("\n--- ROYAL REGISTRY ---")

        if not documents:
            print("The royal archives are currently empty.")
            return

        for document in documents:
            print(
                f"ID: {document[0]} | {document[1]} | "
                f"Type: {document[2]} | Issued by: {document[3]} | "
                f"Created: {document[4]}"
            )

    except Error as error:
        print(f"Unable to access the registry: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def read_royal_document():
    """Read and display a registered document."""
    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return

        cursor = connection.cursor()
        document = get_document(cursor)

        if document is None:
            return

        _, title, file_name = document
        file_path = get_safe_path(file_name)

        with open(file_path, "r", encoding="utf-8") as file:
            contents = file.read()

        print("\n========== ROYAL DECREE ==========")
        print(f"Title: {title}")
        print("-----------------------------------")
        print(contents)
        print("===================================")

        log_action(
            cursor,
            title,
            "READ",
            "Document contents were viewed."
        )
        connection.commit()

    except FileNotFoundError:
        print("The document file could not be found.")

    except PermissionError:
        print("Permission denied while reading the document.")

    except (OSError, ValueError, Error) as error:
        print(f"Unable to read the document: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def find_and_replace_words():
    """Modify the selected section of a royal document."""
    connection = None
    cursor = None

    temp_path = None
    backup_path = None
    original_path = None
    current_path = None
    backup_created = False
    file_installed = False

    try:
        connection = connect_database()

        if connection is None:
            return

        cursor = connection.cursor()
        document = get_document(cursor)

        if document is None:
            return

        document_id, title, file_name = document
        original_path = get_safe_path(file_name)
        current_path = original_path

        print("\n--- CHOOSE A SECTION TO MODIFY ---")
        print("1. Title")
        print("2. Issued by")
        print("3. Content")

        choice = input("\nChoose a section (1-3): ").strip()

        if choice not in ("1", "2", "3"):
            print("Invalid choice. Please select 1, 2, or 3.")
            return

        with open(original_path, "r", encoding="utf-8") as file:
            original_text = file.read()

        lines = original_text.splitlines(keepends=True)

        title_index = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("Title: ")
            ),
            None
        )

        issuer_index = next(
            (
                i for i, line in enumerate(lines)
                if line.startswith("Issued by: ")
            ),
            None
        )

        if title_index is None or issuer_index is None:
            print("The document header has an unexpected format.")
            return

        separator_index = None

        for i in range(issuer_index + 1, len(lines)):
            stripped = lines[i].strip()

            if stripped and set(stripped) == {"="}:
                separator_index = i
                break

        if separator_index is None:
            print("The document section boundaries could not be identified.")
            return

        footer_index = None

        for i in range(len(lines) - 1, separator_index, -1):
            stripped = lines[i].strip()

            if stripped and set(stripped) == {"="}:
                footer_index = i
                break

        if footer_index is None:
            print("The document section boundaries could not be identified.")
            return

        updated_title = title
        updated_file_name = file_name
        details = ""
        count = 0

        if choice == "1":
            
            current_title = lines[title_index][
                len("Title: "):
            ].rstrip("\r\n")

            search_word = input("Enter the word to find in the title: ")

            if not search_word or search_word.isspace():
                print("The search word cannot be empty.")
                return

            replacement = input("Enter the replacement word: ")

            new_title, count = replace_whole_words(
                current_title,
                search_word,
                replacement
            )

            if count == 0:
                print(f"No whole-word matches found for '{search_word}'.")
                print("The document was not changed.")
                return

            new_title = new_title.strip()

            if not new_title:
                print("The title cannot be empty.")
                return

            updated_file_name = make_filename(new_title)

            if updated_file_name is None:
                print("The updated title is not a valid filename.")
                return

            updated_title = new_title
            new_path = get_safe_path(updated_file_name)

            if os.path.normcase(new_path) != os.path.normcase(original_path):
                if os.path.exists(new_path):
                    print("A file with the new title already exists.")
                    return

                cursor.execute(
                    """
                    SELECT document_id
                    FROM royal_documents
                    WHERE file_name = %s AND document_id <> %s
                    """,
                    (updated_file_name, document_id)
                )

                if cursor.fetchone():
                    print("That filename is already registered.")
                    return

            lines[title_index] = "Title: " + new_title + "\n"

            details = (
                f"Title changed from '{title}' to '{new_title}'. "
                f"Whole-word replacements: {count}."
            )

        elif choice == "2":
            
            new_issuer = input(
                "Enter the complete new issuer name: "
            ).strip()

            if not new_issuer:
                print("The issuer name cannot be empty.")
                return

            old_issuer = lines[issuer_index][
                len("Issued by: "):
            ].rstrip("\r\n")

            if new_issuer == old_issuer:
                print("The new issuer is the same as the current issuer.")
                return

            lines[issuer_index] = "Issued by: " + new_issuer + "\n"

            details = (
                f"Issuer changed from '{old_issuer}' to '{new_issuer}'."
            )

        else:
            
            search_word = input("Enter the word to find in the content: ")

            if not search_word or search_word.isspace():
                print("The search word cannot be empty.")
                return

            replacement = input("Enter the replacement word: ")

            body = "".join(lines[separator_index + 1:footer_index])

            new_body, count = replace_whole_words(
                body,
                search_word,
                replacement
            )

            if count == 0:
                print(f"No whole-word matches found for '{search_word}'.")
                print("The document was not changed.")
                return

            lines[separator_index + 1:footer_index] = [new_body]

            details = (
                f"Content: replaced '{search_word}' with '{replacement}' "
                f"({count} occurrence(s))."
            )

        updated_text = "".join(lines)

        temp_path = original_path + ".tmp"
        backup_path = original_path + ".bak"

        if os.path.exists(temp_path) or os.path.exists(backup_path):
            print("A temporary or backup file already exists.")
            print("Inspect it before trying again.")
            return

        with open(
            temp_path,
            "w",
            encoding="utf-8",
            newline=""
        ) as file:
            file.write(updated_text)

        try:
            
            os.replace(original_path, backup_path)
            backup_created = True

            if choice == "1":
                current_path = get_safe_path(updated_file_name)
            else:
                current_path = original_path

            os.replace(temp_path, current_path)
            file_installed = True

            if choice == "1":
                cursor.execute(
                    """
                    UPDATE royal_documents
                    SET document_title = %s, file_name = %s
                    WHERE document_id = %s
                    """,
                    (updated_title, updated_file_name, document_id)
                )

            elif choice == "2":
                cursor.execute(
                    """
                    UPDATE royal_documents
                    SET issued_by = %s
                    WHERE document_id = %s
                    """,
                    (
                        new_issuer,
                        document_id
                    )
                )

            log_action(
                cursor,
                updated_title,
                "REPLACE",
                details
            )

            connection.commit()

        except Exception:
            connection.rollback()

            if backup_created:
                if file_installed and os.path.exists(current_path):
                    os.remove(current_path)

                os.replace(backup_path, original_path)
                backup_created = False

            raise

        print("\nThe royal document has been updated successfully!")
        print(
            "Section modified: "
            f"{('Title', 'Issued by', 'Content')[int(choice) - 1]}"
        )

        if choice == "1":
            print(f"Updated title: {updated_title}")
            print(f"New filename: {updated_file_name}")

        elif choice == "2":
            print("The issuer name has been updated.")

        if choice in ("1", "3"):
            print(f"Whole-word replacements: {count}")

        
        try:
            if backup_created and os.path.exists(backup_path):
                os.remove(backup_path)
                backup_created = False

        except OSError:
            print(
                "Warning: The update succeeded, "
                "but the backup file remains."
            )

    except FileNotFoundError:
        print("The document file could not be found.")

    except PermissionError:
        print("Permission denied while accessing the document.")

    except (OSError, ValueError, Error) as error:
        print(f"Unable to update the document: {error}")

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def view_maesters_chronicle():
    """Display the history of actions in the Royal Archives."""
    connection = None
    cursor = None

    try:
        connection = connect_database()

        if connection is None:
            return

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT entry_id, document_title, action, details, action_time
            FROM maester_chronicle
            ORDER BY entry_id DESC
            """
        )

        entries = cursor.fetchall()

        print("\n===================================")
        print("       MAESTER'S CHRONICLE")
        print("===================================")

        if not entries:
            print("No actions have been recorded yet.")
            return

        for entry in entries:
            entry_id, title, action, details, action_time = entry

            print(f"\nEntry ID: {entry_id}")
            print(f"Document: {title}")
            print(f"Action: {action}")
            print(f"Details: {details}")
            print(f"Time: {action_time}")
            print("-----------------------------------")

    except Error as error:
        print(f"Unable to consult the Chronicle: {error}")

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


def main():
    while True:
        display_welcome()

        print("\n1. Issue a Royal Decree")
        print("2. View the Royal Registry")
        print("3. Read a Royal Document")
        print("4. Find and Replace Words")
        print("5. Consult Maester's Chronicle")
        print("6. Leave the Royal Archives")

        command = input("\nYour command, Your Grace: ").strip()

        if command == "1":
            issue_royal_decree()

        elif command == "2":
            view_royal_registry()

        elif command == "3":
            read_royal_document()

        elif command == "4":
            find_and_replace_words()

        elif command == "5":
            view_maesters_chronicle()

        elif command == "6":
            print("\nThe archives await your next command, Your Grace.")
            break

        else:
            print("Invalid command. Choose a number from 1 to 6.")


if __name__ == "__main__":
    main()
