import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self):
        pass

    def create_connection(self, config):
        """Creates a connection to the MySQL database."""
        try:
            connection = mysql.connector.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["db_user"],
                password=config["db_pass"],
                database=config["db_name"]
            )
            return connection
        except Error as e:
            # Try connecting without database to see if we need to create it
             if "Unknown database" in str(e):
                 try:
                    conn_no_db = mysql.connector.connect(
                        host=config["host"],
                        port=int(config["port"]),
                        user=config["db_user"],
                        password=config["db_pass"]
                    )
                    cursor = conn_no_db.cursor()
                    cursor.execute(f"CREATE DATABASE {config['db_name']}")
                    conn_no_db.close()
                    # Retry connection
                    return self.create_connection(config)
                 except Error as e2:
                     raise Exception(f"Could not create database: {str(e2)}")
             
             raise Exception(f"Connection error: {str(e)}")

    def initialize_database(self, config, admin_data):
        """Creates tables and initial SuperAdmin."""
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            
            # 1. Groups Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_groups (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                priority INT DEFAULT 0
            )
            """)

            # 2. Users Table
            # Status: 0 = Not in School, 1 = In School
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('superadmin', 'admin', 'user') DEFAULT 'user',
                status INT DEFAULT 0, 
                group_id INT,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (group_id) REFERENCES user_groups(id) ON DELETE SET NULL
            )
            """)

            # 3. Devices Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                device_id VARCHAR(100) NOT NULL UNIQUE,
                user_id INT,
                name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """)

            # 4. Keywords Table (Stichwörter)
            # location_type: fixed, selectable, none.
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS keywords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                keyword VARCHAR(100) NOT NULL,
                location_type ENUM('fixed', 'selectable', 'none') NOT NULL,
                default_location VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE
            )
            """)

            # 5. Global Settings
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                setting_key VARCHAR(100) PRIMARY KEY,
                setting_value VARCHAR(255)
            )
            """)

            # Insert Setup Name
            cursor.execute("""
            REPLACE INTO settings (setting_key, setting_value) VALUES ('setup_name', %s)
            """, (config["setup_name"],))
            
            # Check if SuperAdmin exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (admin_data["admin_user"],))
            if not cursor.fetchone():
                # TODO: Hash password properly using bcrypt or argon2
                # For now using plain text for demonstration but adding a TODO comment
                # In production this MUST be hashed.
                cursor.execute("""
                INSERT INTO users (username, password_hash, role, is_active)
                VALUES (%s, %s, 'superadmin', TRUE)
                """, (admin_data["admin_user"], admin_data["admin_pass"]))

            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False

    def authenticate_user(self, config, username, password):
        """Verifies user credentials."""
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND is_active = TRUE", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user:
                # TODO: Implement hash check
                if user["password_hash"] == password:
                    return user
            return None
        raise Exception("Database connection failed")
