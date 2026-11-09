
import os
import re
import mysql.connector
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "decree_vault"


def open_database():
    password = os.getenv("MYSQL_PASSWORD")

    if not password:
        print("\nMySQL password is not configured.")
        print("Set the MYSQL_PASSWORD environment variable.")
        return None

    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="royal_archives"
        )
    except mysql.connector.Error as error:
        print(f"\nDatabase connection failed: {error}")
        return None


def record_activity(cursor, title, action, details):
    query = """
        INSERT INTO maester_chronicle
        (document_title, action, details)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (title, action, details))


def create_safe_filename(title):
    cleaned_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
    cleaned_title = cleaned_title.strip().rstrip(".")

    if not cleaned_title:
        cleaned_title = "Untitled Decree"

    return cleaned_title + ".txt"


def issue_decree():
    print("\n--- CREATE A NEW DECREE ---")

    title = input("Enter the document title: ").strip()
    issuer = input("Issued by: ").strip()
    content = input("Enter the document content: ").strip()

    if not title or not issuer or not content:
        print("\nAll fields are required.")
        return

    filename = create_safe_filename(title)
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    file_path = DOCUMENTS_DIR / filename

    if file_path.exists():
        print("\nA document with this filename already exists.")
        return

    document_text = (
        "THE ROYAL ARCHIVES OF WESTEROS\n"
        "===================================\n"
        f"Title: {title}\n"
        f"Issued by: {issuer}\n"
        "===================================\n\n"
        f"{content}\n"
    )

    connection = open_database()

    if connection is None:
        return

    cursor = None
    file_created = False

    try:
        cursor = connection.cursor()

        with open(file_path, "w", encoding="utf-8") as document_file:
            document_file.write(document_text)

        file_created = True

        query = """
            INSERT INTO royal_documents
            (document_title, file_name, document_type, issued_by)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (title, filename, "Royal Decree", issuer)
        )

        record_activity(
            cursor,
            title,
            "CREATE",
            "A new decree was created."
        )

        connection.commit()

        print("\nDecree created successfully.")
        print(f"Document ID: {cursor.lastrowid}")
        print(f"File: {filename}")

    except Exception as error:
        connection.rollback()

        if file_created and file_path.exists():
            file_path.unlink()

        print(f"\nUnable to create the decree: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


def display_registry():
    print("\n--- DOCUMENT REGISTRY ---")

    connection = open_database()

    if connection is None:
        return

    cursor = None

    try:
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

        if not documents:
            print("\nNo documents are available.")
            return

        for document in documents:
            print("\n-----------------------------------")
            print(f"ID: {document[0]}")
            print(f"Title: {document[1]}")
            print(f"Type: {document[2]}")
            print(f"Issued by: {document[3]}")
            print(f"Created at: {document[4]}")

        print("\n-----------------------------------")

    except mysql.connector.Error as error:
        print(f"\nUnable to retrieve the registry: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


def open_decree():
    print("\n--- OPEN A DOCUMENT ---")

    connection = open_database()

    if connection is None:
        return

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT document_id, document_title, file_name
            FROM royal_documents
            ORDER BY document_id
            """
        )

        documents = cursor.fetchall()

        if not documents:
            print("\nNo documents are available.")
            return

        for document in documents:
            print(f"ID: {document[0]} | {document[1]}")

        try:
            document_id = int(input("\nEnter the document ID: "))
        except ValueError:
            print("\nPlease enter a valid document ID.")
            return

        cursor.execute(
            """
            SELECT document_title, file_name
            FROM royal_documents
            WHERE document_id = %s
            """,
            (document_id,)
        )

        selected_document = cursor.fetchone()

        if selected_document is None:
            print("\nDocument not found.")
            return

        title, filename = selected_document
        file_path = DOCUMENTS_DIR / filename

        if not file_path.is_file():
            print("\nThe document file could not be found.")
            return

        with open(file_path, "r", encoding="utf-8") as document_file:
            document_text = document_file.read()

        print("\n========== DOCUMENT ==========")
        print(document_text)
        print("==============================")

        record_activity(
            cursor,
            title,
            "READ",
            "The document was opened."
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print(f"\nUnable to open the document: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


def locate_document_sections(document_lines):
    title_position = None
    issuer_position = None
    body_separator_position = None

    for position, line in enumerate(document_lines):
        current_line = line.strip()

        if current_line.startswith("Title:"):
            title_position = position

        elif current_line.startswith("Issued by:"):
            issuer_position = position

    if issuer_position is not None:
        for position in range(issuer_position + 1, len(document_lines)):
            if re.fullmatch(r"=+", document_lines[position].strip()):
                body_separator_position = position
                break

    return title_position, issuer_position, body_separator_position


def replace_document_text():
    print("\n--- MODIFY A DOCUMENT ---")

    connection = open_database()

    if connection is None:
        return

    cursor = None
    source_path = None
    destination_path = None
    backup_path = None
    original_text = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT document_id, document_title
            FROM royal_documents
            ORDER BY document_id
            """
        )

        documents = cursor.fetchall()

        if not documents:
            print("\nNo documents are available.")
            return

        for document in documents:
            print(f"ID: {document[0]} | {document[1]}")

        try:
            document_id = int(input("\nEnter the document ID: "))
        except ValueError:
            print("\nPlease enter a valid document ID.")
            return

        cursor.execute(
            """
            SELECT document_title, file_name
            FROM royal_documents
            WHERE document_id = %s
            """,
            (document_id,)
        )

        selected_document = cursor.fetchone()

        if selected_document is None:
            print("\nDocument not found.")
            return

        old_title, filename = selected_document
        source_path = DOCUMENTS_DIR / filename

        if not source_path.is_file():
            print("\nThe document file could not be found.")
            return

        with open(source_path, "r", encoding="utf-8") as document_file:
            original_text = document_file.read()

        document_lines = original_text.splitlines()

        title_position, issuer_position, separator_position = (
            locate_document_sections(document_lines)
        )

        if (
            title_position is None
            or issuer_position is None
            or separator_position is None
        ):
            print("\nThe document structure is not recognised.")
            print("Check that the title, issuer and separator lines exist.")
            return

        print("\nSelect the section to modify:")
        print("1. Document title")
        print("2. Issued by")
        print("3. Document content")

        section_choice = input("\nEnter your choice (1-3): ").strip()

        if section_choice not in ("1", "2", "3"):
            print("\nInvalid selection.")
            return

        current_title = document_lines[title_position].split(":", 1)[1].strip()
        current_issuer = document_lines[issuer_position].split(":", 1)[1].strip()

        revised_title = current_title
        revised_issuer = current_issuer
        revised_lines = document_lines.copy()

        if section_choice == "1":
            print(f"\nCurrent title: {current_title}")

            search_text = input("Word to find: ").strip()
            replacement_text = input("Replace with: ").strip()

            if not search_text:
                print("\nThe search text cannot be empty.")
                return

            revised_title, replacements = re.subn(
                rf"\b{re.escape(search_text)}\b",
                lambda match: replacement_text,
                current_title,
                flags=re.IGNORECASE
            )

            if replacements == 0:
                print("\nThe specified word was not found in the title.")
                return

            revised_lines[title_position] = f"Title: {revised_title}"

        elif section_choice == "2":
            print(f"\nCurrent issuer: {current_issuer}")

            revised_issuer = input("Enter the new issuer name: ").strip()

            if not revised_issuer:
                print("\nThe issuer name cannot be empty.")
                return

            if revised_issuer == current_issuer:
                print("\nThe issuer name has not changed.")
                return

            revised_lines[issuer_position] = f"Issued by: {revised_issuer}"

        else:
            content_start = separator_position + 1
            current_content = "\n".join(revised_lines[content_start:])

            search_text = input("\nWord to find in the content: ").strip()
            replacement_text = input("Replace with: ").strip()

            if not search_text:
                print("\nThe search text cannot be empty.")
                return

            revised_content, replacements = re.subn(
                rf"\b{re.escape(search_text)}\b",
                lambda match: replacement_text,
                current_content,
                flags=re.IGNORECASE
            )

            if replacements == 0:
                print("\nThe specified word was not found in the content.")
                return

            revised_lines = (
                revised_lines[:content_start] + revised_content.split("\n")
            )

        revised_text = "\n".join(revised_lines)

        if original_text.endswith("\n"):
            revised_text += "\n"

        new_filename = filename

        if section_choice == "1":
            new_filename = create_safe_filename(revised_title)

        destination_path = DOCUMENTS_DIR / new_filename

        if destination_path != source_path and destination_path.exists():
            print("\nA file with the revised title already exists.")
            print("The update has been cancelled.")
            return

        backup_path = source_path.with_suffix(source_path.suffix + ".bak")

        with open(backup_path, "w", encoding="utf-8") as backup_file:
            backup_file.write(original_text)

        with open(destination_path, "w", encoding="utf-8") as document_file:
            document_file.write(revised_text)

        if section_choice == "1":
            cursor.execute(
                """
                UPDATE royal_documents
                SET document_title = %s, file_name = %s
                WHERE document_id = %s
                """,
                (revised_title, new_filename, document_id)
            )

        elif section_choice == "2":
            cursor.execute(
                """
                UPDATE royal_documents
                SET issued_by = %s
                WHERE document_id = %s
                """,
                (revised_issuer, document_id)
            )

        section_labels = {
            "1": "Title",
            "2": "Issuer",
            "3": "Content"
        }

        record_activity(
            cursor,
            revised_title,
            "REPLACE",
            f"{section_labels[section_choice]} section modified."
        )

        connection.commit()

        if destination_path != source_path and source_path.exists():
            source_path.unlink()

        if backup_path.exists():
            backup_path.unlink()

        print("\nDocument updated successfully.")
        print(f"Updated section: {section_labels[section_choice]}")

        if section_choice == "1":
            print(f"New title: {revised_title}")

        elif section_choice == "2":
            print(f"New issuer: {revised_issuer}")

    except Exception as error:
        connection.rollback()

        if backup_path and backup_path.exists() and source_path:
            try:
                if destination_path and destination_path != source_path:
                    if destination_path.exists():
                        destination_path.unlink()

                with open(source_path, "w", encoding="utf-8") as document_file:
                    document_file.write(original_text)

                backup_path.unlink()

            except OSError as restore_error:
                print(f"\nWarning: file recovery failed: {restore_error}")

        print(f"\nUnable to update the document: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


def show_activity_history():
    print("\n--- ACTIVITY HISTORY ---")

    connection = open_database()

    if connection is None:
        return

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT entry_id, document_title, action, details, action_time
            FROM maester_chronicle
            ORDER BY entry_id DESC
            """
        )

        entries = cursor.fetchall()

        if not entries:
            print("\nNo activity records were found.")
            return

        for entry in entries:
            print("\n-----------------------------------")
            print(f"Entry ID: {entry[0]}")
            print(f"Document: {entry[1]}")
            print(f"Action: {entry[2]}")
            print(f"Details: {entry[3]}")
            print(f"Time: {entry[4]}")

        print("\n-----------------------------------")

    except mysql.connector.Error as error:
        print(f"\nUnable to retrieve activity history: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


def run_archive_console():
    DOCUMENTS_DIR.mkdir(exist_ok=True)

    while True:
        print("\n===================================")
        print("       THE ROYAL ARCHIVES")
        print("===================================")
        print("1. Create a new decree")
        print("2. Display document registry")
        print("3. Open a document")
        print("4. Find and replace text")
        print("5. View activity history")
        print("6. Exit")

        choice = input("\nSelect an option (1-6): ").strip()

        if choice == "1":
            issue_decree()

        elif choice == "2":
            display_registry()

        elif choice == "3":
            open_decree()

        elif choice == "4":
            replace_document_text()

        elif choice == "5":
            show_activity_history()

        elif choice == "6":
            print("\nThe archive session has ended.")
            break

        else:
            print("\nInvalid selection. Choose a number from 1 to 6.")


if __name__ == "__main__":
    run_archive_console()
