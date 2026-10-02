# Backend logic for the registration page 
# This module handles the validation of user input and the requesting of new user accounts

import customtkinter as ctk
from modules.core import page_handler

from modules.gui import notification as notification_handler
from email_validator import validate_email, EmailNotValidError

from modules.core import database 
from modules.core.backend import account_creator

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
            "First name cannot be empty."
        )
        return False

    if any(char.isdigit() for char in first_name):
        notification_handler.error_notification(
            "First name cannot contain digits."
        )
        return False
    
    if not last_name:
        notification_handler.error_notification(
            "Last name cannot be empty."
            )
        return False

    if any(char.isdigit() for char in last_name):
        notification_handler.error_notification(
            "Last name cannot contain digits."
            )
        return False

    # Validate email address: must be a valid email format
    if not email:
        notification_handler.error_notification(
            "Email address cannot be empty."
        )
        return False

    # Validate email using the email_validator library
    # check_deliverability is set to False to avoid checking if the email domain can receive emails, which will waste time
    try:
        result = validate_email(email, check_deliverability=False)
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
                "That email address is already registered."
            )
            return False
        
    except EmailNotValidError:
        notification_handler.error_notification(
            "Please enter a valid email address."
        )
        return False
    
    # Validate phone number: must be 10 digits, numeric only
    if not phone:
        notification_handler.error_notification(
            "Phone number cannot be empty."
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
            "Username cannot be empty."
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
            "That username is already taken."
        )
        return False

    # Require a password
    if not password:
        notification_handler.error_notification(
            "Password cannot be empty."
        )
        return False

    # Require at least 8 characters
    if len(password) < 8:
        notification_handler.error_notification(
            "Password must contain at least 8 characters."
        )
        return False

    # Ensure both passwords match
    if password != confirm_password:
        notification_handler.error_notification(
            "The inputted passwords don't match! You'd be wise to double-check them."
        )
        return False
    # Validate inputs, then create the account.

    # Navigate only after the account is successfully saved.

    success, message = account_creator.create_account(
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
        page_handler.navigate_to_page("login", True)
    else:
        notification_handler.error_notification(
            message
        )