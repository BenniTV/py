import customtkinter as ctk

from ui.users_view import UsersView

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, config, user_data, db_manager):
        super().__init__(master)
        self.config = config
        self.user_data = user_data
        self.db_manager = db_manager
        
        # Grid layout for sidebar + main content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar()
        self._create_main_content()
        
    def set_db_manager(self, db_manager):
        # Deprecated
        pass
        
    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="PyDispatch Admin", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=20, pady=20)
        
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=lambda: self.show_page("Dashboard"))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_users = ctk.CTkButton(self.sidebar, text="Benutzer", command=lambda: self.show_page("Benutzer"))
        self.btn_users.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_devices = ctk.CTkButton(self.sidebar, text="Geräte", command=lambda: self.show_page("Geräte"))
        self.btn_devices.grid(row=3, column=0, padx=20, pady=10)

        self.btn_keywords = ctk.CTkButton(self.sidebar, text="Stichwörter", command=lambda: self.show_page("Stichwörter"))
        self.btn_keywords.grid(row=4, column=0, padx=20, pady=10)
        
        ctk.CTkLabel(self.sidebar, text=f"User: {self.user_data['username']}").grid(row=6, column=0, padx=20, pady=10)

    def _create_main_content(self):
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.page_label = ctk.CTkLabel(self.content_frame, text="Willkommen im Dashboard", font=("Arial", 24))
        self.page_label.pack(pady=20)
        
    def show_page(self, name):
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if name == "Benutzer":
            view = UsersView(self.content_frame, self.config, self.db_manager)
            view.pack(fill="both", expand=True)
        else:
            self.page_label = ctk.CTkLabel(self.content_frame, text=f"{name} Modul - Work in Progress", font=("Arial", 24))
            self.page_label.pack(pady=20)
