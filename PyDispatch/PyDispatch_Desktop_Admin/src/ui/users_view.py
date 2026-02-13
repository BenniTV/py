import customtkinter as ctk

class UsersView(ctk.CTkFrame):
    def __init__(self, master, config, db_manager):
        super().__init__(master)
        self.config = config
        self.db_manager = db_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_users = self.tab_view.add("Benutzer")
        self.tab_groups = self.tab_view.add("Gruppen")
        
        self._setup_users_tab()
        self._setup_groups_tab()
        
    def _setup_users_tab(self):
        # Tools Frame
        tools_frame = ctk.CTkFrame(self.tab_users)
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(tools_frame, text="Neuer Benutzer", command=self.create_user).pack(side="left", padx=5)
        ctk.CTkButton(tools_frame, text="Aktualisieren", command=self.refresh_users).pack(side="left", padx=5)
        
        # User List (Scrollable Frame)
        self.user_list_frame = ctk.CTkScrollableFrame(self.tab_users)
        self.user_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.user_list_frame, text="Lade Benutzer...").pack()
        
    def _setup_groups_tab(self):
         # Tools Frame
        tools_frame = ctk.CTkFrame(self.tab_groups)
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(tools_frame, text="Neue Gruppe", command=self.create_group).pack(side="left", padx=5)
        
        # Group List
        self.group_list_frame = ctk.CTkScrollableFrame(self.tab_groups)
        self.group_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def create_user(self):
        print("Create user dialog")
        # TODO: Dialog window

    def refresh_users(self):
        print("Refreshing users")
        # TODO: Fetch from DB using db_manager

    def create_group(self):
        print("Create group dialog")
