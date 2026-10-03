# create_account.py
# This module interacts with the SQL database to create new user accounts 
# It's responsible for inserting new user data into the database

from cffi import VerificationError
import customtkinter as ctk
from modules.core import page_handler

from modules.gui import notification as notification_handler
from email_validator import validate_email, EmailNotValidError

from modules.core import database 

import sqlite3
from contextlib import closing
from argon2 import PasswordHasher

# The active account
# None means nobody is logged in
current_account: dict | None = None

password_hasher = PasswordHasher()

def create_account(username: str, email: str, phone: str, password: str, first_name: str, last_name: str) -> tuple[bool, str]:
    # Hash the password before saving it
    password_hash = password_hasher.hash(password)

    try:
        # Open the database and close it when finished
        with closing(database.connect()) as connection:
            # Commit the insert on success or roll it back on failure
            with connection:
                # Save the account using safely supplied values
                connection.execute(
                    """
                    INSERT INTO users (
                        first_name,
                        last_name,
                        email,
                        phone,
                        username,
                        password_hash
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        first_name,
                        last_name,
                        email,
                        phone,
                        username,
                        password_hash,
                    ),
                )

    except sqlite3.IntegrityError:
        # Database constraints prevent duplicate accounts
        return False, "That username or email is already in my records. Maybe try another?"

    except sqlite3.OperationalError:
        # Do not report success when the database could not save
        return False, "I couldn't save your account. That's on me, not you. Please try again."

    return True, "Account created. Welcome! You can log in now."


def log_into_account(username: str, password: str) -> tuple[bool, str]:
    global current_account

    # Load account details without loading the password hash
    with closing(database.connect()) as connection:
        account = connection.execute(
            """
            SELECT id, first_name, last_name, email, phone, username
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    if account is None:
        return False, "I can't find that account. Check the spelling, or create a new one."

    # Remember this account for the current app session
    current_account = dict(account) # Comprises id, first_name, last_name, email, phone, username

    return True, "You're in. Good to see you, {}!".format(current_account["first_name"])


def log_out_of_account():
    global current_account
    current_account = None