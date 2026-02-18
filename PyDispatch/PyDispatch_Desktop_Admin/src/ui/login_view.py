import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=28, pady=28)
        self.container.grid_columnconfigure(0, weight=1)

        self.login_frame = ctk.CTkFrame(self.container, corner_radius=18)
        self.login_frame.grid(row=0, column=0, pady=30)

        ctk.CTkLabel(self.login_frame, text="PyDispatch Admin", font=("Arial", 34, "bold")).pack(pady=(26, 4), padx=44)
        ctk.CTkLabel(self.login_frame, text="Melde dich mit deinem Admin-Konto an", font=("Arial", 14)).pack(pady=(0, 20), padx=44)

        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Benutzername",
            width=420,
            height=42,
            corner_radius=10,
            font=("Arial", 14)
        )
        self.username_entry.pack(pady=(0, 12), padx=30)
        
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Passwort",
            show="*",
            width=420,
            height=42,
            corner_radius=10,
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=(0, 14), padx=30)
        
        self.login_btn = ctk.CTkButton(
            self.login_frame,
            text="Anmelden",
            command=self.attempt_login,
            width=420,
            height=44,
            corner_radius=10,
            font=("Arial", 15, "bold")
        )
        self.login_btn.pack(pady=(0, 14), padx=30)
        
        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="#d9534f", font=("Arial", 13))
        self.error_label.pack(pady=(0, 18), padx=24)

        self.username_entry.bind("<Return>", lambda event: self.attempt_login())
        self.password_entry.bind("<Return>", lambda event: self.attempt_login())

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Bitte Felder ausfüllen")
            return
            
        # Trigger callback
        self.on_login_success(username, password, self.error_callback)

    def error_callback(self, message):
        self.error_label.configure(text=message)
