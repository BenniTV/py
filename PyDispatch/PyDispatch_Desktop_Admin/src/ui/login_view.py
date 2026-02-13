import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20)
        
        ctk.CTkLabel(self.login_frame, text="PyDispatch Login", font=("Arial", 24)).pack(pady=(20, 10), padx=40)
        
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Benutzername")
        self.username_entry.pack(pady=10, padx=20)
        
        self.password_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Passwort", show="*")
        self.password_entry.pack(pady=10, padx=20)
        
        self.login_btn = ctk.CTkButton(self.login_frame, text="Anmelden", command=self.attempt_login)
        self.login_btn.pack(pady=20, padx=20)
        
        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.error_label.pack(pady=5)

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
