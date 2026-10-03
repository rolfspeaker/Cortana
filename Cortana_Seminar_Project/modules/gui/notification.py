from pathlib import Path

import customtkinter as ctk
from PIL import Image

from modules.core import page_handler


smile_ICON_PATH = (
    Path(__file__).resolve().parents[2]
    / "images"
    / "cortana_smile.png"
)
worried_ICON_PATH = (
    Path(__file__).resolve().parents[2]
    / "images"
    / "cortana_worried.png"
)

_active_notifications = {}


def _show_notification(message, duration, success, expression: str = "smile"):
    page = page_handler.pages.get(page_handler.current_page)

    if page is None:
        raise RuntimeError("No active page for the notification.")

    master = page.winfo_toplevel()

    previous = _active_notifications.get(master)
    if previous is not None:
        previous()

    background = "#FFE5F5"
    accent = "#974EF8" if success else "#FF9150"
    heading = "Success" if success else "Error"

    notification = ctk.CTkFrame(
        master,
        corner_radius=0,
        border_width=0,
        fg_color=background,
        bg_color=background,
    )

    notification.grid_columnconfigure(2, weight=1)

    accent_strip = ctk.CTkFrame(
        notification,
        width=6,
        corner_radius=0,
        border_width=0,
        fg_color=accent,
    )
    accent_strip.grid(
        row=0,
        column=0,
        rowspan=2,
        sticky="ns",
    )

    icon = smile_ICON_PATH if expression == "smile" else worried_ICON_PATH

    with Image.open(icon) as source:
        logo = source.convert("RGBA")
        logo.thumbnail((150, 150), Image.Resampling.LANCZOS)

    notification.logo_image = ctk.CTkImage(
        light_image=logo,
        dark_image=logo,
        size=logo.size,
    )

    logo_label = ctk.CTkLabel(
        notification,
        text="",
        image=notification.logo_image,
        width=150,
        height=150,
        fg_color=background,
    )
    logo_label.grid(
        row=0,
        column=1,
        rowspan=2,
        padx=(20, 16),
        pady=20,
    )

    title_label = ctk.CTkLabel(
        notification,
        text=heading,
        text_color="#7135A0",
        fg_color=background,
        font=ctk.CTkFont(
            family="Segoe UI",
            size=17,
            weight="bold",
        ),
        anchor="w",
    )
    title_label.grid(
        row=0,
        column=2,
        sticky="ew",
        pady=(18, 0),
    )

    message_label = ctk.CTkLabel(
        notification,
        text=message,
        width=360,
        wraplength=360,
        justify="left",
        anchor="w",
        text_color="#542D68",
        fg_color=background,
        font=ctk.CTkFont(
            family="Segoe UI",
            size=15,
        ),
    )
    message_label.grid(
        row=1,
        column=2,
        sticky="ew",
        pady=(2, 20),
    )

    timer = None

    def dismiss():
        nonlocal timer

        if timer is not None:
            notification.after_cancel(timer)
            timer = None

        if _active_notifications.get(master) is dismiss:
            del _active_notifications[master]

        notification.destroy()

    close_btn = ctk.CTkButton(
        notification,
        text="×",
        width=28,
        height=28,
        corner_radius=7,
        fg_color=background,
        bg_color=background,
        hover_color="#F4C9E8",
        text_color="#7135A0",
        font=ctk.CTkFont(size=22),
        command=dismiss,
    )
    close_btn.grid(
        row=0,
        column=3,
        sticky="ne",
        padx=(12, 12),
        pady=(12, 0),
    )

    notification.place(
        relx=1,
        rely=1,
        x=-24,
        y=-24,
        anchor="se",
    )
    notification.lift()

    _active_notifications[master] = dismiss

    if duration > 0:
        timer = notification.after(duration, dismiss)


def error_notification(message: str, duration: int = 3000, expression: str = "smile"):
    _show_notification(message, duration, success=False, expression=expression)


def success_notification(message: str, duration: int = 3000, expression: str = "smile"):
    _show_notification(message, duration, success=True, expression=expression)