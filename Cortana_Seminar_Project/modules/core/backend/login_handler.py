# Backend logic for the login page 
# This module handles the validation of user input and the authentication of existing users

import customtkinter as ctk
from contextlib import closing

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from modules.core import database
from modules.gui import notification as notification_handler

from modules.core.backend import account_handler
from modules.core import page_handler

password_hasher = PasswordHasher()

def validate_attempt(page: type[ctk.CTkFrame]) -> bool:
    username = page.username.get().strip()
    password = page.password.get()

    # Require both fields
    if not username:
        notification_handler.error_notification(
            "What, you lost your username on the way here? I need it to log you in.",
            expression="worried"
        )
        return False

    if not password:
        notification_handler.error_notification(
            "I can't let you in without your password. Security concerns, y'know?",
        )
        return False

    # Retrieve the account and close the connection afterward
    with closing(database.connect()) as connection:
        user = connection.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    # Reject an unknown username
    if user is None:
        notification_handler.error_notification(
            "That username isn't in my records. Check the spelling, or create a new account."
        )
        return False

    # Check the entered password against the stored hash
    try:
        password_hasher.verify(user["password_hash"], password)

    except (VerifyMismatchError, VerificationError):
        notification_handler.error_notification(
            "That's not the right password! You didn't forget it, did you?",
            expression="worried"
        )
        return False

    success, message = account_handler.log_into_account(username, password)
    if success:
        notification_handler.success_notification(message); page_handler.navigate_to_page("home")
    else:
        notification_handler.error_notification(message, expression="worried")
