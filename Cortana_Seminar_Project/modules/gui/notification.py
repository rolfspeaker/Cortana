from pathlib import Path

import customtkinter as ctk
from PIL import Image

from modules.core import page_handler
from modules.utility import sound_service


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
stunned_ICON_PATH = (
    Path(__file__).resolve().parents[2]
    / "images"
    / "cortana_stunned.png"
)

_active_notifications = {}
# Keep each window's popup identity separate to reject repeated clicks
_active_requests = {}

_active_id: str | None = None

def _show_notification(
    message, duration, success, expression: str = "smile",
    *, prompt=False, on_yes=None, on_no=None, notification_id: str | None = None,
    voiceline: tuple[bool, str] | None = None
):  
    global _active_id
    page = page_handler.pages.get(page_handler.current_page)

    if page is None:
        raise RuntimeError("No active page for the notification.")

    master = page.winfo_toplevel()
    
    request = (message, "prompt" if prompt else "success" if success else "error", expression)
    previous = _active_notifications.get(master)

    if previous is not None:
        same_request = _active_requests.get(master) == request
        same_id = (notification_id is not None and _active_id == notification_id)

        if same_request or same_id:
            return

        previous()

    # Play Cortana voiceline
    try:
        enabled, audio_name = voiceline

        if not audio_name:
            audio_name = "generic_1"

        sound_service.play_voiceline(audio_name)

    except TypeError:
        pass

    _active_id = notification_id

    background = "#FFE5F5"
    accent = "#3984ED" if prompt else "#974EF8" if success else "#FF9150"
    heading = "Confirmation" if prompt else "Notification" if success else "Error"

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

    icon = smile_ICON_PATH if expression == "smile" else worried_ICON_PATH if expression == "worried" else stunned_ICON_PATH

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

    # Prompts wait for a choice while other popups can use a timer
    timer = None
    closed = False

    def dismiss():
        # Allow this function to change the timer variable above
        nonlocal timer, closed
        if closed:
            return
        closed = True

        # Cancel any scheduled dismissal
        if timer is not None:
            notification.after_cancel(timer)
            timer = None

        # Remove this popup from the registry only if it is still the active one
        if _active_notifications.get(master) is dismiss:
            del _active_notifications[master]
            _active_requests.pop(master, None)

        # Remove the popup from the screen
        notification.destroy()

    def choose(accepted):
        # Dismiss before calling the action and ignore any repeated clicks
        if closed:
            return
        dismiss()
        callback = on_yes if accepted else on_no
        if callback is not None:
            callback()

    if prompt:
        buttons = ctk.CTkFrame(text_frame, fg_color=background, corner_radius=0)
        buttons.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        buttons.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            buttons, text="Yes", height=36, corner_radius=12,
            fg_color="transparent", hover=False, text_color="#7135A0",
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            command=lambda: choose(True),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            buttons, text="On second thought...", height=36, corner_radius=12,
            fg_color="transparent", hover=False, text_color="#FF9150",
            font=ctk.CTkFont(size=14, weight="bold", family="Consolas"),
            command=lambda: choose(False),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

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
        # Closing a prompt has the same result as choosing No
        command=(lambda: choose(False)) if prompt else dismiss,
    )
    close_btn.grid(
        row=0,
        column=3,
        sticky="ne",
        padx=(12, 12),
        pady=(12, 0),
    )
    
    # Measure the complete popup before showing it to reduce layout flashes
    notification.update_idletasks()
    notification.place(
        relx=1,
        rely=1,
        x=-24,
        y=-24,
        anchor="se",
    )
    notification.lift()

    _active_notifications[master] = dismiss
    _active_requests[master] = request

    if duration > 0 and not prompt:
        timer = notification.after(duration, dismiss)


def error_notification(message: str, duration: int = 3000, expression: str = "smile",
    request_id: str | None = None, voiceclip: tuple[bool, str] | None = None):
    _show_notification(
        message, duration, success=False, expression=expression, notification_id=request_id,
        voiceline=voiceclip
    )


def success_notification(message: str, duration: int = 3000, expression: str = "smile",
    request_id: str | None = None, voiceclip: tuple[bool, str] | None = None):
    _show_notification(
        message, duration, success=True, expression=expression, notification_id=request_id,
        voiceline=voiceclip
    )
    sound_service.play_sfx("notification", volume=.2)

def prompt_notification(message: str, on_yes, on_no=None, expression: str = "smile",
    request_id: str | None = None, voiceclip: tuple[bool, str] | None = None):
    # Use callbacks because the GUI must keep running while awaiting a choice
    _show_notification(
        message, duration=0, success=False, expression=expression,
        prompt=True, on_yes=on_yes, on_no=on_no, notification_id=request_id,
        voiceline=voiceclip
    )
    
