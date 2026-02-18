import mysql.connector
from mysql.connector import Error
import json

class DBManager:
    def __init__(self):
        pass

    def create_connection(self, config):
        """Creates a connection to the MySQL database."""
        try:
            connection = mysql.connector.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["user"],
                password=config["password"],
                database=config["database"]
            )
            return connection
        except Error as e:
            # Try connecting without database to see if we need to create it
             if "Unknown database" in str(e):
                 try:
                    conn_no_db = mysql.connector.connect(
                        host=config["host"],
                        port=int(config["port"]),
                        user=config["user"],
                        password=config["password"]
                    )
                    cursor = conn_no_db.cursor()
                    cursor.execute(f"CREATE DATABASE {config['database']}")
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
                selectable_locations TEXT,
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

    def _ensure_keywords_schema(self, conn):
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM keywords LIKE 'selectable_locations'")
        column = cursor.fetchone()
        if not column:
            cursor.execute("ALTER TABLE keywords ADD COLUMN selectable_locations TEXT")
            conn.commit()
        cursor.close()

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

    def get_setup_name(self, config):
        """Loads setup name from settings table if available."""
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_key = %s LIMIT 1",
                ("setup_name",)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return row[0]
            return None
        raise Exception("Database connection failed")

    def get_setting(self, config, key):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_key = %s LIMIT 1",
                (key,)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row[0] if row else None
        raise Exception("Database connection failed")

    def set_setting(self, config, key, value):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "REPLACE INTO settings (setting_key, setting_value) VALUES (%s, %s)",
                (key, value)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def _get_count(self, conn, table_name, where_clause=""):
        cursor = conn.cursor()
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        cursor.execute(query)
        value = cursor.fetchone()[0]
        cursor.close()
        return value

    def get_dashboard_stats(self, config):
        """Returns basic dashboard counters. Fallbacks to zero on errors."""
        default_stats = {
            "users_total": 0,
            "users_active": 0,
            "groups_total": 0,
            "devices_total": 0,
            "keywords_total": 0,
        }

        try:
            conn = self.create_connection(config)
            if conn and conn.is_connected():
                stats = {
                    "users_total": self._get_count(conn, "users"),
                    "users_active": self._get_count(conn, "users", "is_active = TRUE"),
                    "groups_total": self._get_count(conn, "user_groups"),
                    "devices_total": self._get_count(conn, "devices"),
                    "keywords_total": self._get_count(conn, "keywords"),
                }
                conn.close()
                return stats
        except Exception:
            return default_stats

        return default_stats

    def get_groups(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, name, priority
                FROM user_groups
                ORDER BY priority DESC, name ASC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        raise Exception("Database connection failed")

    def get_users(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    u.id,
                    u.username,
                    u.role,
                    u.status,
                    u.group_id,
                    u.is_active,
                    g.name AS group_name
                FROM users u
                LEFT JOIN user_groups g ON g.id = u.group_id
                ORDER BY u.username ASC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        raise Exception("Database connection failed")

    def get_users_basic(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, username
                FROM users
                WHERE is_active = TRUE
                ORDER BY username ASC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        raise Exception("Database connection failed")

    def create_group(self, config, name, priority=0):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_groups (name, priority) VALUES (%s, %s)",
                (name, priority)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def create_user(self, config, username, password, role="user", group_id=None):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role, group_id, status, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                (username, password, role, group_id, 0)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def update_user(self, config, user_id, role=None, group_id=None, set_group=False, is_active=None):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            fields = []
            values = []

            if role is not None:
                fields.append("role = %s")
                values.append(role)
            if set_group:
                fields.append("group_id = %s")
                values.append(group_id)
            if is_active is not None:
                fields.append("is_active = %s")
                values.append(is_active)

            if not fields:
                conn.close()
                return False

            values.append(user_id)
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def get_devices(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.device_id,
                    d.name,
                    d.user_id,
                    d.is_active,
                    u.username
                FROM devices d
                LEFT JOIN users u ON u.id = d.user_id
                ORDER BY d.name ASC, d.device_id ASC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            return rows
        raise Exception("Database connection failed")

    def create_device(self, config, device_id, name, user_id=None):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO devices (device_id, name, user_id, is_active)
                VALUES (%s, %s, %s, TRUE)
                """,
                (device_id, name, user_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def update_device(self, config, device_id, user_id=None, set_user=False, is_active=None, name=None):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            fields = []
            values = []

            if set_user:
                fields.append("user_id = %s")
                values.append(user_id)
            if is_active is not None:
                fields.append("is_active = %s")
                values.append(is_active)
            if name is not None:
                fields.append("name = %s")
                values.append(name)

            if not fields:
                conn.close()
                return False

            values.append(device_id)
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE devices SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def get_keywords(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            self._ensure_keywords_schema(conn)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, keyword, location_type, default_location, selectable_locations, is_active
                FROM keywords
                ORDER BY keyword ASC
                """
            )
            rows = cursor.fetchall()
            for row in rows:
                raw_locations = row.get("selectable_locations")
                if raw_locations:
                    try:
                        row["selectable_locations"] = json.loads(raw_locations)
                    except Exception:
                        row["selectable_locations"] = [part.strip() for part in raw_locations.split(",") if part.strip()]
                else:
                    row["selectable_locations"] = []
            cursor.close()
            conn.close()
            return rows
        raise Exception("Database connection failed")

    def create_keyword(self, config, keyword, location_type, default_location=None, selectable_locations=None):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            self._ensure_keywords_schema(conn)
            selectable_raw = json.dumps(selectable_locations or [])
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO keywords (keyword, location_type, default_location, selectable_locations, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                """,
                (keyword, location_type, default_location, selectable_raw)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def update_keyword(
        self,
        config,
        keyword_id,
        location_type=None,
        default_location=None,
        set_default_location=False,
        selectable_locations=None,
        set_selectable_locations=False,
        is_active=None
    ):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            self._ensure_keywords_schema(conn)
            fields = []
            values = []

            if location_type is not None:
                fields.append("location_type = %s")
                values.append(location_type)
            if set_default_location:
                fields.append("default_location = %s")
                values.append(default_location)
            if set_selectable_locations:
                fields.append("selectable_locations = %s")
                values.append(json.dumps(selectable_locations or []))
            if is_active is not None:
                fields.append("is_active = %s")
                values.append(is_active)

            if not fields:
                conn.close()
                return False

            values.append(keyword_id)
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE keywords SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")
