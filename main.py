
import os
import re
import mysql.connector
from pathlib import Path
from datetime import datetime


# ==========================================
# ROYAL ARCHIVES - CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
SCROLLS_DIR = BASE_DIR / "royal_scrolls"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def connect_database():
    password = os.getenv("MYSQL_PASSWORD")

    if not password:
        print("\nMySQL password is not configured.")
        print("Set the MYSQL_PASSWORD environment variable.")
        return None

    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=password,
            database="royal_archives"
        )

        return connection

    except mysql.connector.Error as error:
        print(f"\nDatabase connection failed: {error}")
        return None


# ==========================================
# DATABASE ACTIVITY LOGGING
# ==========================================

def log_activity(cursor, document_title, action, details):
    query = """
        INSERT INTO maester_chronicle
        (document_title, action, details)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (document_title, action, details)
    )


# ==========================================
# FILE NAME GENERATION
# ==========================================

def generate_filename(title):
    filename = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "",
        title
    )

    filename = filename.strip().rstrip(".")

    if not filename:
        filename = "Untitled Royal Decree"

    return filename + ".txt"


# ==========================================
# ISSUE A ROYAL DECREE
# ==========================================

def issue_royal_decree():
    print("\n--- ISSUE A ROYAL DECREE ---")

    title = input("Enter the document title: ").strip()
    issuer = input("Issued by: ").strip()
    content = input("Enter the document content: ").strip()

    if not title or not issuer or not content:
        print("\nAll fields are required.")
        return

    filename = generate_filename(title)
    file_path = SCROLLS_DIR / filename

    if file_path.exists():
        print("\nA document with this filename already exists.")
        return

    SCROLLS_DIR.mkdir(exist_ok=True)

    document_content = (
        "THE ROYAL ARCHIVES OF WESTEROS\n"
        "===================================\n"
        f"Title: {title}\n"
        f"Issued by: {issuer}\n"
        "===================================\n\n"
        f"{content}\n"
    )

    connection = connect_database()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(document_content)

        query = """
            INSERT INTO royal_documents
            (document_title, file_name, document_type, issued_by)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (title, filename, "Royal Decree", issuer)
        )

        log_activity(
            cursor,
            title,
            "CREATE",
            "A new royal decree was issued."
        )

        connection.commit()

        print("\nRoyal decree successfully issued!")
        print(f"Document ID: {cursor.lastrowid}")
        print(f"File: {filename}")

    except Exception as error:
        connection.rollback()

        if file_path.exists():
            file_path.unlink()

        print(f"\nUnable to issue the decree: {error}")

    finally:
        cursor.close()
        connection.close()


# ==========================================
# VIEW THE ROYAL REGISTRY
# ==========================================

def view_royal_registry():
    print("\n--- ROYAL REGISTRY ---")

    connection = connect_database()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
            SELECT document_id, document_title,
                   document_type, issued_by, created_at
            FROM royal_documents
            ORDER BY document_id
        """

        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            print("\nNo royal documents found.")
            return

        for record in records:
            print("\n-----------------------------------")
            print(f"ID: {record[0]}")
            print(f"Title: {record[1]}")
            print(f"Type: {record[2]}")
            print(f"Issued by: {record[3]}")
            print(f"Created at: {record[4]}")

        print("\n-----------------------------------")

    except mysql.connector.Error as error:
        print(f"\nUnable to retrieve registry: {error}")

    finally:
        cursor.close()
        connection.close()


# ==========================================
# READ A ROYAL DOCUMENT
# ==========================================

def read_royal_document():
    print("\n--- READ A ROYAL DOCUMENT ---")

    connection = connect_database()

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

        records = cursor.fetchall()

        if not records:
            print("\nNo documents are available.")
            return

        for record in records:
            print(f"ID: {record[0]} | {record[1]}")

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

        document = cursor.fetchone()

        if document is None:
            print("\nDocument not found.")
            return

        title, filename = document
        file_path = SCROLLS_DIR / filename

        if not file_path.exists():
            print("\nThe document file could not be found.")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        print("\n========== ROYAL DOCUMENT ==========")
        print(content)
        print("====================================")

        log_activity(
            cursor,
            title,
            "READ",
            "Royal document viewed."
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print(f"\nUnable to read document: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# FIND AND REPLACE WORDS
# ==========================================

def find_and_replace_words():
    print("\n--- CONSULT THE ROYAL ARCHIVES ---")

    connection = connect_database()

    if connection is None:
        return

    cursor = None
    original_content = None
    file_path = None
    new_file_path = None
    backup_path = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT document_id, document_title
            FROM royal_documents
            ORDER BY document_id
            """
        )

        records = cursor.fetchall()

        if not records:
            print("\nNo documents are available.")
            return

        for record in records:
            print(f"ID: {record[0]} | {record[1]}")

        try:
            document_id = int(
                input("\nEnter the document ID: ")
            )
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

        document = cursor.fetchone()

        if document is None:
            print("\nDocument not found.")
            return

        old_title, filename = document
        file_path = SCROLLS_DIR / filename

        if not file_path.exists():
            print("\nThe document file could not be found.")
            return

        with open(file_path, "r", encoding="utf-8") as file:
            original_content = file.read()

        print("\n--- CHOOSE A SECTION TO MODIFY ---")
        print("1. Title")
        print("2. Issued by")
        print("3. Content")

        section_choice = input(
            "\nChoose a section (1-3): "
        ).strip()

        if section_choice not in ("1", "2", "3"):
            print("\nInvalid section choice.")
            return

        lines = original_content.splitlines()

        title_index = None
        issuer_index = None
        separator_index = None

        # Locate the title and issuer lines.
        for index, line in enumerate(lines):
            stripped_line = line.strip()

            if stripped_line.startswith("Title:"):
                title_index = index

            elif stripped_line.startswith("Issued by:"):
                issuer_index = index

        # Locate the separator after the issuer.
        if issuer_index is not None:
            for index in range(issuer_index + 1, len(lines)):
                if re.fullmatch(r"=+", lines[index].strip()):
                    separator_index = index
                    break

        # Validate the document structure.
        if (
            title_index is None
            or issuer_index is None
            or separator_index is None
        ):
            print(
                "\nThe document section boundaries "
                "could not be identified."
            )
            print("Please check the separator lines in the text file.")
            return

        current_title = lines[title_index].split(":", 1)[1].strip()
        current_issuer = lines[issuer_index].split(":", 1)[1].strip()

        updated_title = current_title
        updated_issuer = current_issuer
        updated_lines = lines.copy()

        # ----------------------------------
        # TITLE REPLACEMENT
        # ----------------------------------

        if section_choice == "1":
            print(f"\nCurrent title: {current_title}")

            find_word = input(
                "Enter the word to find: "
            ).strip()

            replacement = input(
                "Enter the replacement word: "
            ).strip()

            if not find_word:
                print("\nThe search word cannot be empty.")
                return

            updated_title, count = re.subn(
                rf"\b{re.escape(find_word)}\b",
                replacement,
                current_title,
                flags=re.IGNORECASE
            )

            if count == 0:
                print("\nThe specified word was not found in the title.")
                return

            updated_lines[title_index] = f"Title: {updated_title}"

        # ----------------------------------
        # ISSUER REPLACEMENT
        # ----------------------------------

        elif section_choice == "2":
            print(f"\nCurrent issuer: {current_issuer}")

            updated_issuer = input(
                "Enter the new issuer name: "
            ).strip()

            if not updated_issuer:
                print("\nIssuer name cannot be empty.")
                return

            if updated_issuer == current_issuer:
                print("\nThe issuer name has not changed.")
                return

            updated_lines[issuer_index] = (
                f"Issued by: {updated_issuer}"
            )

        # ----------------------------------
        # CONTENT REPLACEMENT
        # ----------------------------------

        elif section_choice == "3":
            content_start = separator_index + 1

            document_content = "\n".join(
                updated_lines[content_start:]
            )

            find_word = input(
                "\nEnter the word to find: "
            ).strip()

            replacement = input(
                "Enter the replacement word: "
            ).strip()

            if not find_word:
                print("\nThe search word cannot be empty.")
                return

            updated_content, count = re.subn(
                rf"\b{re.escape(find_word)}\b",
                replacement,
                document_content,
                flags=re.IGNORECASE
            )

            if count == 0:
                print("\nThe specified word was not found in the content.")
                return

            updated_lines = (
                updated_lines[:content_start]
                + updated_content.split("\n")
            )

        # ----------------------------------
        # PREPARE UPDATED DOCUMENT
        # ----------------------------------

        updated_document = "\n".join(updated_lines)

        if original_content.endswith("\n"):
            updated_document += "\n"

        # Generate a new filename if the title changed.
        new_filename = filename

        if section_choice == "1":
            new_filename = generate_filename(updated_title)

        new_file_path = SCROLLS_DIR / new_filename

        if (
            new_file_path != file_path
            and new_file_path.exists()
        ):
            print(
                "\nA file with the updated title "
                "already exists. Update cancelled."
            )
            return

        # Create a backup before modifying the document.
        backup_path = file_path.with_suffix(
            file_path.suffix + ".bak"
        )

        with open(backup_path, "w", encoding="utf-8") as backup:
            backup.write(original_content)

        # Write the updated document.
        with open(new_file_path, "w", encoding="utf-8") as file:
            file.write(updated_document)

        # Update the database.
        if section_choice == "1":
            cursor.execute(
                """
                UPDATE royal_documents
                SET document_title = %s, file_name = %s
                WHERE document_id = %s
                """,
                (updated_title, new_filename, document_id)
            )

        elif section_choice == "2":
            cursor.execute(
                """
                UPDATE royal_documents
                SET issued_by = %s
                WHERE document_id = %s
                """,
                (updated_issuer, document_id)
            )

        section_names = {
            "1": "Title",
            "2": "Issued by",
            "3": "Content"
        }

        log_activity(
            cursor,
            updated_title,
            "REPLACE",
            f"{section_names[section_choice]} section updated."
        )

        connection.commit()

        # Remove the old file after a successful title update.
        if new_file_path != file_path and file_path.exists():
            file_path.unlink()

        if backup_path.exists():
            backup_path.unlink()

        print("\nDocument updated successfully!")
        print(f"Updated section: {section_names[section_choice]}")

        if section_choice == "1":
            print(f"New title: {updated_title}")

        elif section_choice == "2":
            print(f"New issuer: {updated_issuer}")

    except Exception as error:
        connection.rollback()

        # Restore the original file if an update fails.
        if backup_path and backup_path.exists():
            try:
                if new_file_path and new_file_path != file_path:
                    if new_file_path.exists():
                        new_file_path.unlink()

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(original_content)

                backup_path.unlink()

            except OSError as restore_error:
                print(
                    "\nWarning: Could not restore the original file: "
                    f"{restore_error}"
                )

        print(f"\nUnable to update the document: {error}")

    finally:
        if cursor:
            cursor.close()

        connection.close()


# ==========================================
# CONSULT MAESTER'S CHRONICLE
# ==========================================

def consult_maesters_chronicle():
    print("\n--- MAESTER'S CHRONICLE ---")

    connection = connect_database()

    if connection is None:
        return

    try:
        cursor = connection.cursor()

        query = """
            SELECT entry_id, document_title,
                   action, details, action_time
            FROM maester_chronicle
            ORDER BY entry_id DESC
        """

        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            print("\nNo activity records found.")
            return

        for record in records:
            print("\n-----------------------------------")
            print(f"Entry ID: {record[0]}")
            print(f"Document: {record[1]}")
            print(f"Action: {record[2]}")
            print(f"Details: {record[3]}")
            print(f"Time: {record[4]}")

        print("\n-----------------------------------")

    except mysql.connector.Error as error:
        print(f"\nUnable to retrieve Chronicle: {error}")

    finally:
        cursor.close()
        connection.close()


# ==========================================
# MAIN MENU
# ==========================================

def main():
    SCROLLS_DIR.mkdir(exist_ok=True)

    while True:
        print("\n===================================")
        print("   THE ROYAL ARCHIVES OF WESTEROS")
        print("===================================")
        print("Welcome, Your Grace!\n")

        print("1. Issue a Royal Decree")
        print("2. View the Royal Registry")
        print("3. Read a Royal Document")
        print("4. Find and Replace Words")
        print("5. Consult Maester's Chronicle")
        print("6. Leave the Royal Archives")

        choice = input(
            "\nYour command, Your Grace: "
        ).strip()

        if choice == "1":
            issue_royal_decree()

        elif choice == "2":
            view_royal_registry()

        elif choice == "3":
            read_royal_document()

        elif choice == "4":
            find_and_replace_words()

        elif choice == "5":
            consult_maesters_chronicle()

        elif choice == "6":
            print(
                "\nThe Royal Archives are closed. "
                "Until we meet again, Your Grace!"
            )
            break

        else:
            print("\nInvalid command. Please choose between 1 and 6.")


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":
    main()
