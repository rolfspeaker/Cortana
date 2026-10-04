import customtkinter as ctk
from PIL import Image, ImageTk

from pathlib import Path

from modules.core import page_handler
from modules.core.backend import login_handler

class LoginPage(ctk.CTkFrame):
    def __init__(self):
        super().__init__(master=None, corner_radius=0)

        self.canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self._background = None
        self._last_size = None

        self.title = self.canvas.create_text(
            0, 0,
            text="Login",
            fill="white",
            anchor="w",
            font=("Segoe UI", -30, "bold"),
        )
        self.username_label = self.canvas.create_text(
            0, 0,
            text="Username",
            fill="white",
            anchor="w",
            font=("Segoe UI", -13, "bold"),
        )
        self.password_label = self.canvas.create_text(
            0, 0,
            text="Password",
            fill="white",
            anchor="w",
            font=("Segoe UI", -13, "bold"),
        )

        self.username = ctk.CTkEntry(
            self.canvas,
            height=42,
            corner_radius=8,
            border_width=1,
            border_color="#EDD2F2",
            fg_color="#C770A4",
            bg_color="#C770A4",
            text_color="white",
                font=ctk.CTkFont(
                family="Segoe UI",
                size=14
            ),
        )
        self.password = ctk.CTkEntry(
            self.canvas,
            height=42,
            corner_radius=8,
            border_width=1,
            border_color="#EDD2F2",
            fg_color="#C770A4",
            bg_color="#C770A4",
            text_color="white",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14
            ),
            show="*",
        )

        

        self._username_window = self.canvas.create_window(
            0, 0, window=self.username, anchor="nw"
        )
        self._password_window = self.canvas.create_window(
            0, 0, window=self.password, anchor="nw"
        )
        self.toggle_btn = ctk.CTkButton(
            self.password,
            text="Show",
            width=22,
            height=22,
            corner_radius=8,
            fg_color="#C770A4",
            text_color="#653081",
            hover_color="#C770A4",
            bg_color="#C770A4",
            command=self._toggle_password_visibility,
            font=ctk.CTkFont(
                family="Consolas",
                underline=True,
                size=14
            ),
        )

        self.toggle_btn.place(
            relx=1,
            rely=0.5,
            x=-4,
            anchor="e",
        )
        
        self.login_btn = ctk.CTkButton(
            self.canvas,
            text="Login",
            height=44,
            corner_radius=18,
            fg_color="#FFE5F5",
            hover_color="#F7CDEB",
            bg_color="#C770A4",
            text_color="#653081",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: login_handler.validate_attempt(self),
        )
        self._login_window = self.canvas.create_window(
            0, 0, window=self.login_btn, anchor="nw"
        )

        self.account_prompt = self.canvas.create_text(
            0, 0,
            text="Don’t have an account?",
            fill="white",
            font=("Segoe UI", -14),
        )
        self.signup_link = self.canvas.create_text(
            0, 0,
            text="Sign up.",
            fill="white",
            font=("Segoe UI", -14, "underline"),
        )

        self.canvas.tag_bind(
            self.signup_link,
            "<Button-1>",
            lambda event: page_handler.navigate_to_page("register"),
        )
        self.canvas.tag_bind(
            self.signup_link,
            "<Enter>",
            lambda event: self.canvas.configure(cursor="hand2"),
        )
        self.canvas.tag_bind(
            self.signup_link,
            "<Leave>",
            lambda event: self.canvas.configure(cursor=""),
        )

        for entry in (self.username, self.password):
            entry.bind("<Return>", lambda event: self.login())
            entry.bind("<MouseWheel>", self._scroll, add="+")

        self.canvas.bind("<Configure>", self._layout)
        self.canvas.bind("<MouseWheel>", self._scroll)

    def _toggle_password_visibility(self):
        if self.password.cget("show") == "*":
            self.password.configure(show=""); self.toggle_btn.configure(text="Hide")
        else:
            self.password.configure(show="*"); self.toggle_btn.configure(text="Show")

    def _layout(self, event):
        w, h = event.width, event.height

        if w < 2 or h < 2 or self._last_size == (w, h):
            return

        self._last_size = (w, h)

        form_width = min(460, max(180, w - 64))
        left = (w - form_width) / 2
        center = w / 2
        top = max(36, (h - 440) / 2)
        content_height = max(h, top + 440)

        c = self.canvas

        c.coords(self.title, left, top)
        c.coords(self.username_label, left, top + 64)
        c.coords(self._username_window, left, top + 82)
        c.coords(self.password_label, left, top + 146)
        c.coords(self._password_window, left, top + 164)
        c.coords(self._login_window, left, top + 280)
        c.coords(self.account_prompt, center, top + 356)
        c.coords(self.signup_link, center, top + 386)

        for window in (
            self._username_window,
            self._password_window,
        ):
            c.itemconfigure(
                window, width=form_width, height=42
            )

        c.itemconfigure(
            self._login_window,
            width=form_width,
            height=44,
        )
        c.configure(scrollregion=(0, 0, w, content_height))

        gradient = Image.new("RGB", (256, 1))
        gradient.putdata([
            tuple(
                round(a + (b - a) * x / 255)
                for a, b in zip(
                    (151, 78, 248),
                    (255, 145, 80),
                )
            )
            for x in range(256)
        ])
        gradient = gradient.resize(
            (w, int(content_height)),
            Image.Resampling.BILINEAR,
        )

        self._background = ImageTk.PhotoImage(
            gradient, master=c
        )

        c.delete("gradient")
        c.create_image(
            0, 0,
            image=self._background,
            anchor="nw",
            tags="gradient",
        )
        c.tag_lower("gradient")

        if content_height <= h:
            c.yview_moveto(0)

    def _scroll(self, event):
        bounds = self.canvas.cget("scrollregion").split()

        if bounds and float(bounds[3]) > self.canvas.winfo_height():
            self.canvas.yview_scroll(
                -int(event.delta / 120), "units"
            )
            return "break"

    def login(self):
        pass