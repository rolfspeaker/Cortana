import customtkinter as ctk
from PIL import Image, ImageTk

from customtkinter import CTkCanvas as canvas
from customtkinter import filedialog as dialog

import numpy as np

from pathlib import Path
from modules.core import page_handler

class LoginPage(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app, corner_radius=0)

        self.username = ctk.CTkEntry(
            self, placeholder_text="Username"
        )
        self.username.pack(pady=20)

        self.login_btn = ctk.CTkButton(
            self, text="LOGIN", command=self.login
        )
        self.login_btn.pack()

        #page_handler.pages["login"] = self # The navigation function already handles this

    def login():
        pass
