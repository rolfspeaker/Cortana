import os
import sys

from sys import exception
import time

import customtkinter as ctk
from PIL import Image, ImageTk

from customtkinter import CTkCanvas as canvas
from modules.core import page_handler

from modules.gui.pages import landing_page as lp
import threading

def initialize():
    app = ctk.CTk()
    app.title("Cortana")

    app.geometry("800x600")
    
    page_handler.initialize_pages()
    page_handler.navigate_to_page("landing")

    app.mainloop()
    return app