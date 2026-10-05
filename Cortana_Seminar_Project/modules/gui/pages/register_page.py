import customtkinter as ctk
from PIL import Image, ImageTk

from modules.core import page_handler
from modules.core.backend import registration_handler

class RegisterPage(ctk.CTkFrame):
    def __init__(self):
        super().__init__(master=None, corner_radius=0)

        self.canvas = ctk.CTkCanvas(
            self, highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)

        self._background = None
        self._last_size = None
        self.entries = {}
        self._fields = []
        self._password_toggles = {}

        self.title = self.canvas.create_text(
            0, 0,
            text="Create an Account",
            fill="white",
            font=("Segoe UI", -30, "bold"),
        )
        self.subtitle = self.canvas.create_text(
            0, 0,
            text="Plan your day. Make room for what matters.",
            fill="white",
            font=("Segoe UI", -14),
        )

        definitions = [
            ("first_name", "First name", "Enter your first name", False),
            ("last_name", "Last name", "Enter your last name", False),
            ("email", "Email address", "you@example.com", False),
            ("phone", "Phone number", "Enter your phone number", False),
            ("username", "Username", "Choose a username", False),
            ("password", "Password", "Create a password", True),
            (
                "verify_password",
                "Confirm password",
                "Re-enter your password",
                True,
            ),
        ]

        for name, label, placeholder, secret in definitions:
            label_id = self.canvas.create_text(
                0, 0,
                text=label,
                fill="white",
                anchor="w",
                font=("Segoe UI", -13, "bold"),
            )

            entry = ctk.CTkEntry(
                self.canvas,
                placeholder_text=placeholder,
                height=40,
                corner_radius=8,
                border_width=1,
                border_color="#EDD2F2",
                fg_color="#C770A4",
                bg_color="#C770A4",
                text_color="white",
                placeholder_text_color="#F8EAF7",
                font=ctk.CTkFont(size=14),
                show="*" if secret else "",
            )

            entry.bind("<Return>", lambda event: registration_handler.validate_attempt(self), add="+")
            entry.bind("<MouseWheel>", self._scroll, add="+")

            window_id = self.canvas.create_window(
                0, 0, window=entry, anchor="nw"
            )

            self.entries[name] = entry
            setattr(self, name, entry)
            self._fields.append((label_id, window_id, entry))

            if secret:
                # Match the login page control inside each password bar
                toggle = ctk.CTkButton(
                    entry,
                    text="Show",
                    width=22,
                    height=22,
                    corner_radius=8,
                    fg_color="#C770A4",
                    text_color="#653081",
                    hover_color="#C770A4",
                    bg_color="#C770A4",
                    command=lambda field=name: self._toggle_password(field),
                    font=ctk.CTkFont(
                        family="Consolas",
                        underline=True,
                        size=14,
                    ),
                )
                toggle.place(relx=1, rely=0.5, x=-4, anchor="e")
                toggle.bind("<MouseWheel>", self._scroll, add="+")
                self._password_toggles[name] = toggle


        #def validate_first_name(event):
            #if not self.first_name.get().strip():
                #self.canvas.yview_moveto(0)

        #self.first_name.bind("<FocusIn>", lambda event: self.canvas.yview_moveto(0))

        self.signup_btn = ctk.CTkButton(
            self.canvas,
            text="Sign Up",
            height=44,
            corner_radius=12,
            fg_color="#FFE5F5",
            hover_color="#F7CDEB",
            bg_color="#C770A4",
            text_color="#653081",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: registration_handler.validate_attempt(self),
        )

        self._signup_window = self.canvas.create_window(
            0, 0, window=self.signup_btn, anchor="n"
        )

        self.account_prompt = self.canvas.create_text(
            0, 0,
            text="Already have an account?",
            fill="white",
            font=("Segoe UI", -13),
        )
        self.login_link = self.canvas.create_text(
            0, 0,
            text="Log in",
            fill="white",
            font=("Segoe UI", -13, "underline"),
        )
        self.footer = self.canvas.create_text(
            0, 0,
            text="Your plans. Your pace.",
            fill="white",
            font=("Segoe UI", -12),
        )

        self.canvas.tag_bind(
            self.login_link,
            "<Button-1>",
            lambda event: page_handler.navigate_to_page("login"),
        )
        self.canvas.tag_bind(
            self.login_link,
            "<Enter>",
            lambda event: self.canvas.configure(cursor="hand2"),
        )
        self.canvas.tag_bind(
            self.login_link,
            "<Leave>",
            lambda event: self.canvas.configure(cursor=""),
        )

        self.canvas.bind("<Configure>", self._layout)
        self.canvas.bind("<MouseWheel>", self._scroll)

    def _toggle_password(self, name):
        entry = self.entries[name]
        toggle = self._password_toggles[name]

        # Show the password on one click and hide it on the next
        reveal = entry.cget("show") != ""
        entry.configure(show="" if reveal else "*")
        toggle.configure(text="Hide" if reveal else "Show")

    @staticmethod
    def _color_at(x, width):
        t = max(0, min(1, x / max(1, width - 1)))
        channels = [
            round(a + (b - a) * t)
            for a, b in zip(
                (151, 78, 248),
                (255, 145, 80),
            )
        ]
        return "#" + "".join(
            f"{channel:02x}" for channel in channels
        )

    def _layout(self, event):
        w, h = event.width, event.height

        if w < 2 or h < 2 or self._last_size == (w, h):
            return

        self._last_size = (w, h)

        compact = w < 640
        columns = 1 if compact else 2
        form_width = min(760, max(200, w - 80))
        left = (w - form_width) / 2
        gap = 28
        field_width = (
            form_width - gap * (columns - 1)
        ) / columns

        form_height = 850 if compact else 590
        top = max(30, (h - form_height) / 2 + 30)
        content_height = max(h, form_height)

        c = self.canvas
        c.coords(self.title, w / 2, top)
        c.coords(self.subtitle, w / 2, top + 36)

        fields_top = top + 76

        for index, (label, window, entry) in enumerate(self._fields):
            row, column = divmod(index, columns)

            x = left + column * (field_width + gap)
            y = fields_top + row * 82
            entry_width = field_width

            if entry is self.verify_password:
                x = left
                entry_width = (
                    field_width
                    if compact
                    else 2 * field_width + gap
                )

            c.coords(label, x, y)
            c.coords(window, x, y + 18)

            color = self._color_at(x + entry_width / 2, w)
            entry.configure(fg_color=color, bg_color=color)

            # Blend the control into the password bar when the form resizes
            for name, toggle in self._password_toggles.items():
                if entry is self.entries[name]:
                    toggle.configure(
                        fg_color=color,
                        bg_color=color,
                        hover_color=color,
                    )

            c.itemconfigure(
                window,
                width=entry_width,
                height=40,
            )

        rows = (len(self._fields) + columns - 1) // columns
        button_y = fields_top + rows * 82 + 8

        self.signup_btn.configure(
            bg_color=self._color_at(w / 2, w)
        )
        c.itemconfigure(
            self._signup_window,
            width=min(360, form_width),
            height=44,
        )

        c.coords(self._signup_window, w / 2, button_y)
        c.coords(self.account_prompt, w / 2 - 26, button_y + 70)
        c.coords(self.login_link, w / 2 + 99, button_y + 70)
        c.coords(self.footer, w / 2, button_y + 108)

        content_height = max(content_height, button_y + 140)
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

        