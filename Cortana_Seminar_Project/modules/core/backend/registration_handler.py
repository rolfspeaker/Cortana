# Backend logic for the registration page 
# This module handles the validation of user input and the requesting of new user accounts

import customtkinter as ctk
from modules.core import page_handler

from modules.gui import notification as notification_handler
from email_validator import validate_email, EmailNotValidError

from modules.core import database 
from modules.core.backend import account_handler

def validate_attempt(page: ctk.CTkFrame) -> bool:
    first_name: str = page.first_name.get().strip()
    last_name: str = page.last_name.get().strip()

    email: str = page.email.get().strip()
    phone: str = page.phone.get().strip()

    username: str = page.username.get().strip()
    password: str = page.password.get()

    confirm_password: str = page.verify_password.get()

    if not first_name:
        notification_handler.error_notification(
            "I need your first name to go on. You can't leave it blank.",
            expression="worried"
        )
        return False

    if any(char.isdigit() for char in first_name):
        notification_handler.error_notification(
            "Ever seen a first name with numbers in it? Me neither. Please remove any digits."
        )
        return False
    
    if not last_name:
        notification_handler.error_notification(
            "Your last name's just as important as your first. Maybe even more so!"
            )
        return False

    if any(char.isdigit() for char in last_name):
        notification_handler.error_notification(
            "I'd be hard pressed to find a last name with numbers in it. Letters only, please."
            )
        return False

    # Validate email address: must be a valid email format
    if not email:
        notification_handler.error_notification(
            "I need your email address to go on. You can't leave it blank.",
            expression="worried"
        )
        return False

    # Validate email using the email_validator library
    # check_deliverability is set to False to avoid checking if the email domain can receive emails, which can waste time if unnecessary
    # In our case, I set it to True to ensure the email is deliverable, which is important for account verification and communication
    try:
        result = validate_email(email, check_deliverability=True)
        email = result.normalized

        with database.connect() as connection:
        # Find an account with this username
            existing_email = connection.execute(
                # Retrieve its ID if a match exists
                "SELECT id FROM users WHERE email = ?",
                # Safely supply the email as a one-item tuple
                (email,),
            # Return the first match or None
            ).fetchone()

        if existing_email is not None:
            notification_handler.error_notification(
                "I already have that email on file. Unless you made an account with it, you might want to try another.",
                expression="worried"
            )
            return False
        
    except EmailNotValidError:
        notification_handler.error_notification(
            "That email doesn't look quite right. Mind checking it for me?",
            expression="worried"
        )
        return False
    
    # Validate phone number: must be 10 digits, numeric only
    if not phone:
        notification_handler.error_notification(
            "A number where I can reach you, please. I promise I only call when it matters."
        )
        return False
    
    # "isascii()" checks if all characters in the string are ASCII characters
    # ASCII characters basically include the standard English letters, digits, and some special characters
    # "isdigit()" checks if all characters in the string are valid digits (0-9)
    # len(phone) == 10 checks if the length of the phone number is exactly 10 characters

    if not (phone.isascii() and phone.isdigit() and len(phone) == 10):
        notification_handler.error_notification(
            "Enter a 10-digit phone number using numbers only."
        )
        return False

    if not username:
        notification_handler.error_notification(
            "I'll need a username from you to create an account."
        )
        return False

    # Open a database connection
    with database.connect() as connection:
        # Find an account with this username
        existing_user = connection.execute(
            # Retrieve its ID if a match exists
            "SELECT id FROM users WHERE username = ?",
            # Safely supply the username as a one-item tuple
            (username,),
        # Return the first match or None
        ).fetchone()

    # If the username already exists
    if existing_user is not None:
        notification_handler.error_notification(
            "Someone beat you to that username. Pick another, and make it yours."
        )
        return False

    # Require a password
    if not password:
        notification_handler.error_notification(
            "I need a password to secure your account! You can't leave it blank."
        )
        return False

    # Require at least 8 characters
    if len(password) < 8:
        notification_handler.error_notification(
            "Eight characters minimum. A stronger lock keeps your account safer!",
        )
        return False

    # Ensure both passwords match
    if password != confirm_password:
        notification_handler.error_notification(
            "Those passwords don't match! I promise I won't tell anyone about the typo.",
        )
        return False
    # Validate inputs, then create the account.

    # Navigate only after the account is successfully saved.

    success, message = account_handler.create_account(
        username=username,
        email=email,

        phone=phone,
        password=password,

        first_name=first_name,
        last_name=last_name
    )

    if success:
        notification_handler.success_notification(
            message
        )
        page_handler.navigate_to_page("login")
    else:
        notification_handler.error_notification(
            message
        )