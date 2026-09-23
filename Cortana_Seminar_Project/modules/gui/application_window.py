import os
import sys

from sys import exception
import time

import customtkinter as ctk
from PIL import Image, ImageTk

from customtkinter import CTkCanvas as canvas

from modules.gui.pages import landing_page as lp
import threading

def initialize():
    app = ctk.CTk()
    app.title("Cortana")

    app.geometry("800x600")
    lp.LandingPage(app)

    app.mainloop()
    return app