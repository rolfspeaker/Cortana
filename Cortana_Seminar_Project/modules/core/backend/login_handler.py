# Backend logic for the login page 
# This module handles the validation of user input and the authentication of existing users

import sqlite3
import customtkinter as ctk
from contextlib import closing

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

from modules.core import database
from modules.gui import notification as notification_handler

from modules.core.backend import account_handler
from modules.core import page_handler

import random
password_hasher = PasswordHasher()

def validate_attempt(page: type[ctk.CTkFrame]) -> bool:
    # Remove extra username spaces but preserve the exact password
    username = page.username.get().strip()
    password = page.password.get()

    # Require both fields
    if not username:
        notification_handler.error_notification(
            "What, you lost your username on the way here? I need it to log you in.",
            expression="worried",
            #voiceclip=(True, "i_dont_think_so"), 
        )
        return False
    
    # Retrieve the account and close the connection afterward
    with closing(database.connect()) as connection:
        user = connection.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    # Reject an unknown username
    rng: int = random.randint(1,3)

    if user is None:
        return notification_handler.error_notification(
            "{} Check the spelling, or create an account.".format(
                "That user isn't in my records, and I'd remember a handle that interesting."
                if rng == 1 else
                "No such username. I'd remember, trust me."
                if rng == 2 else
                "Nothing under that name, and I never miss a name."
            ),
            request_id="username_error",
            voiceclip=(True, "use_my_help"),
        )
    
    if not password:
        notification_handler.error_notification(
            "I can't let you in without your password. Security concerns, y'know?",
            voiceclip=(True, "with_all_due_respect"), 
        )
        return False

    
       

    # Check the entered password against the stored hash
    try:
        password_hasher.verify(user["password_hash"], password)

    except (VerifyMismatchError, VerificationError):
        return notification_handler.error_notification(
            "That's not the right password. You didn't forget it, did you?",
            expression="worried",
            #voiceclip=(True, "with_all_due_respect"),
        )

    # Establish the signed-in account after the password has been verified
    success, message = account_handler.log_into_account(username, password)
    if not success:
        notification_handler.error_notification(message, expression="worried", voiceclip=(True, "apologize"))
        return False

    # Load this account's tasks before displaying the home page
    try:
        page_handler.pages["home"].load_tasks()
    except (sqlite3.Error, ValueError):
        # Clear the session if its task data could not be loaded
        account_handler.log_out_of_account()

        notification_handler.error_notification(
            "I couldn't load your tasks. Please try logging in again.",
            expression="worried",
            voiceclip=(True, "apologize"),
        )
        return False

    # Show the home page only after login and task loading succeed
    page_handler.navigate_to_page("home")
    notification_handler.success_notification(message, voiceclip=(True, "miss_me"))
    return True
