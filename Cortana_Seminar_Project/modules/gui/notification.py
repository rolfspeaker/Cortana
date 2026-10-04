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
_current_message: str | None = None

def _show_notification(message, duration, success, expression: str = "smile"):
    global _current_message
    page = page_handler.pages.get(page_handler.current_page)

    if page is None:
        raise RuntimeError("No active page for the notification.")

    master = page.winfo_toplevel()
    
    previous = _active_notifications.get(master)
    if previous is not None:
        # If the requested notification bears the same message as the active notification, reject the request
        if _current_message == message: 
            return
        # If the requested notification has a different message, then delete the active notification in favor of the incoming notification
        else: 
            previous()
    
    
    _current_message = message

    background = "#FFE5F5"
    accent = "#974EF8" if success else "#FF9150"
    heading = "Notification" if success else "Error"

    notification = ctk.CTkFrame(
        master,
        corner_radius=15,
        border_width=0,
        fg_color=background,
        bg_color="#FF9150",
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
        sticky="ns",
    )

    icon = smile_ICON_PATH if expression == "smile" else worried_ICON_PATH

    with Image.open(icon) as source:
        cortana_icon = source.convert("RGBA")
        cortana_icon.thumbnail((150, 150), Image.Resampling.LANCZOS)

    notification.cortana_image = ctk.CTkImage(
        light_image=cortana_icon,
        dark_image=cortana_icon,
        size=cortana_icon.size,
    )

    notif_label = ctk.CTkLabel(
        notification,
        text="",
        image=notification.cortana_image,
        width=150,
        height=150,
        fg_color=background,
    )
    notif_label.grid(
        row=0,
        column=1,
        sticky="n",
        padx=(20, 16),
        pady=20,
    )

    # Keep the text rows independent of the image height
    text_frame = ctk.CTkFrame(
        notification,
        corner_radius=0,
        fg_color=background,
    )
    text_frame.grid(
        row=0,
        column=2,
        sticky="new",
        pady=(20, 20),
    )
    text_frame.grid_columnconfigure(0, weight=1)

    title_label = ctk.CTkLabel(
        text_frame,
        text=heading,
        text_color="#7135A0",
        fg_color=background,
        font=ctk.CTkFont(
            family="Segoe UI",
            size=24,
            weight="bold",
        ),
        anchor="w",
    )
    title_label.grid(
        row=0,
        column=0,
        sticky="ew",
    )

    subtitle_label = ctk.CTkLabel(
        text_frame,
        text="Cortana says:",
        text_color="#7135A0",
        fg_color=background,
        font=ctk.CTkFont(
            family="Calibri",
            size=16,
            weight="bold",
        ),
        anchor="w",
    )
    subtitle_label.grid(
        row=1,
        column=0,
        sticky="ew",
        pady=(2, 0),
    )

    message_label = ctk.CTkLabel(
        text_frame,
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
            weight="normal",
        ),
    )
    message_label.grid(
        row=2,
        column=0,
        sticky="ew",
        pady=(40, 0),
    )

        # No automatic dismissal has been scheduled yet
    timer = None

    def dismiss():
        # Allow this function to change the timer variable above
        nonlocal timer

        # Cancel any scheduled dismissal
        if timer is not None:
            notification.after_cancel(timer)
            timer = None

        # Remove this popup from the registry only if it is still the active one
        if _active_notifications.get(master) is dismiss:
            del _active_notifications[master]

        # Remove the popup from the screen
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
    _show_notification(
        message, duration, success=False, expression=expression
    )


def success_notification(message: str, duration: int = 3000, expression: str = "smile"):
    _show_notification(
        message, duration, success=True, expression=expression
    )