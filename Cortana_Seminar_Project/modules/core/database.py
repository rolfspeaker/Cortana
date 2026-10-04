# Import Python's built-in tools for working with SQLite databases
import sqlite3

# Import Path to build and work with file and folder paths
from pathlib import Path
from contextlib import closing

# Store the database file's location
# The opening parenthesis lets this expression continue onto another line
DATABASE_PATH = (
    # __file__ is the location of this Python script
    # Path converts that location into a path object
    # resolve() makes it an absolute path
    # parents[0] is core, parents[1] is modules, parents[2] is Cortana_Seminar_Project
    # The / operators append the data folder and cortana.db filename
    Path(__file__).resolve().parents[2] / "data" / "cortana.db"
    # Finish the expression assigned to DATABASE_PATH
)


# Define a function that opens the database and returns its connection
def connect():
    # DATABASE_PATH.parent is the folder containing the database file
    # mkdir creates that folder
    # parents=True also creates any missing folders above it
    # exist_ok=True prevents an error if the folder already exists
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Open the database file or create it if it does not exist
    # Save the connection object so we can send SQL commands through it
    connection = sqlite3.connect(DATABASE_PATH)

    # Make retrieved rows support column names such as user["username"]
    # Rows can still be accessed by numeric position
    connection.row_factory = sqlite3.Row

    # Enable enforcement of foreign key relationships for this connection
    # Foreign keys connect records across tables such as tasks belonging to users
    connection.execute("PRAGMA foreign_keys = ON")

    # Give the connection back to whichever code called connect()
    return connection


# Define a function that creates the initial database structure
def initialize_database():
# Close the connection when initialization finishes
    with closing(connect()) as connection:
        # Commit changes on success or roll them back on failure
        with connection:
            # Store user accounts
            connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL
                )
            """)

            # Store tasks linked to their owning account
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY NOT NULL,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    task_date TEXT NOT NULL,
                    start_time TEXT NOT NULL DEFAULT '',
                    end_time TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    reminder TEXT NOT NULL,
                    repeat TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                        CHECK (completed IN (0, 1)),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                        ON DELETE CASCADE
                )
            """)
        # CREATE TABLE creates a table named users
        # IF NOT EXISTS leaves an existing users table untouched
        # It does not update an existing table to match this definition
        # The opening parenthesis begins the list of columns

        # id stores a whole number that uniquely identifies each account
        # INTEGER PRIMARY KEY lets SQLite generate an ID when one is omitted

        # first_name stores text and cannot contain SQL NULL
        # NOT NULL does not prevent an empty string so Python must check that

        # last_name stores text and cannot contain SQL NULL

        # email stores text and cannot contain SQL NULL
        # UNIQUE prevents two accounts from having the same stored email value

        # phone stores text to preserve leading zeros
        # Without NOT NULL this column can contain SQL NULL

        # username stores text and cannot contain SQL NULL
        # UNIQUE prevents duplicate stored usernames
        # By default differently capitalized usernames count as different values

        # password_hash stores the encoded password hash rather than the password
        # It cannot contain SQL NULL

        # The SQL closing parenthesis finishes the list of columns
        # The closing triple quotes finish the Python string
        # The final parenthesis finishes the execute() call