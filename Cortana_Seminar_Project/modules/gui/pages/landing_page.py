from pathlib import Path
import customtkinter as ctk

from PIL import Image, ImageTk
from customtkinter import CTkCanvas as canvas

from customtkinter import filedialog as dialog
import numpy as np

from pathlib import Path
from modules.core import page_handler

GRADIENT_TOP = (151, 78, 248)
GRADIENT_BOTTOM = (255, 145, 80)


def create_gradient(width, height, color_top, color_bottom):
    top = np.array(color_top, dtype=float)
    bottom = np.array(color_bottom, dtype=float)

    t = np.linspace(0, 1, width).reshape(1, width, 1)
    gradient = top + (bottom - top) * t
    gradient = np.tile(gradient, (height, 1, 1)).astype(np.uint8)

    return Image.fromarray(gradient)


def lerp_color(t, color_top, color_bottom):
    top = np.array(color_top, dtype=float)
    bottom = np.array(color_bottom, dtype=float)
    r, g, b = (top + (bottom - top) * t).astype(int)
    return f"#{r:02x}{g:02x}{b:02x}"


def build_landing_page(app):
    bg_label = canvas(app, highlightthickness=0, bd=0)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    last_size = [None, None]

    logo_path = Path(__file__).resolve().parents[3] / "images" / "image_logo.png"
    with Image.open(logo_path) as logo_source:
        logo_image = logo_source.convert("RGBA")

    logo_image.thumbnail((180, 180), Image.Resampling.LANCZOS)
    bg_label.logo_image = ImageTk.PhotoImage(logo_image, master=bg_label)

    logo = bg_label.create_image(0, 0, image=bg_label.logo_image, anchor="center")

    title = bg_label.create_text(
        0, 0, text="Smart Daily Planner",
        font=("Segoe UI", 34, "bold"), fill="white",
    )
    subtitle = bg_label.create_text(
        0, 0, text="& Personal Productivity Assistant",
        font=("Segoe UI", 16), fill="white",
    )
    welcome = bg_label.create_text(
        0, 0, text="Welcome!",
        font=("Segoe UI", 28), fill="white",
    )

    button_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold", underline=True)

    # Buttons are centered at x = w/2, the horizontal midpoint of a
    # left-to-right gradient, so their background is a single fixed color
    # rather than something recalculated per-resize. This is also what
    # fixes the white/cream borders: CTkButton's default transparent
    # bg_color falls back to the theme panel color on a raw Canvas parent,
    # instead of blending into the gradient behind it.
    button_bg = lerp_color(0.5, GRADIENT_TOP, GRADIENT_BOTTOM)

    def handle_login():
        from modules.core.page_handler import navigate_to_page
        navigate_to_page("login")
        
    def handle_signup():
        pass

    login_btn = ctk.CTkButton(
        bg_label, text="LOGIN", font=button_font,
        text_color="white", fg_color="#E4ADF0", hover_color="#D89AE6",
        bg_color=button_bg,
        border_width=2, border_color="#25202B", corner_radius=21,
        width=236, height=42,
        command=lambda: handle_login(),
    )
    signup_btn = ctk.CTkButton(
        bg_label, text="SIGN UP", font=button_font,
        text_color="white", fg_color="#E4ADF0", hover_color="#D89AE6",
        bg_color=button_bg,
        border_width=2, border_color="#25202B", corner_radius=21,
        width=236, height=42,
        command=lambda: handle_signup(),
    )

    # Embed the buttons directly into the canvas so they share the exact
    # same coordinate system as the text/logo items. Using .place() on a
    # CTkButton applies CTk's own DPI scaling to the x/y values, which the
    # raw canvas items don't get -- that mismatch is what was causing the
    # buttons to drift out of alignment with the text above them.
    login_window = bg_label.create_window(0, 0, window=login_btn, anchor="center")
    signup_window = bg_label.create_window(0, 0, window=signup_btn, anchor="center")

    def redraw_background(event=None):
        w, h = bg_label.winfo_width(), bg_label.winfo_height()
        if w <= 1 or h <= 1:
            return
        if (w, h) == tuple(last_size):
            return

        gradient_img = create_gradient(w, h, GRADIENT_TOP, GRADIENT_BOTTOM)
        bg_image = ImageTk.PhotoImage(gradient_img, master=bg_label)

        bg_label.delete("gradient")
        bg_label.create_image(0, 0, anchor="nw", image=bg_image, tags="gradient")
        bg_label.image = bg_image
        bg_label.tag_lower("gradient")

        x = w / 2
        y = max(220, h / 2 - 40)

        bg_label.coords(logo, x, y - 125)
        bg_label.coords(title, x, y)
        bg_label.coords(subtitle, x, y + 44)
        bg_label.coords(welcome, x, y + 122)

        bg_label.coords(login_window, x, y + 204)
        bg_label.coords(signup_window, x, y + 272)

        last_size[0], last_size[1] = w, h

    bg_label.bind("<Configure>", redraw_background)
    bg_label.after_idle(redraw_background)


class LandingPage(ctk.CTkFrame):
    def __init__(self):
        super().__init__(master=None, corner_radius=0)
        build_landing_page(self)