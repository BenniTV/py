import json
import mysql.connector
from mysql.connector import Error


class DBManager:
    def create_connection(self, config):
        try:
            connection = mysql.connector.connect(
                host=config["host"],
                port=int(config["port"]),
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )
            return connection
        except Error as e:
            raise Exception(f"Connection error: {str(e)}")

    def ensure_runtime_schema(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    setting_key VARCHAR(100) PRIMARY KEY,
                    setting_value VARCHAR(255)
                )
                """
            )
            cursor.execute("SHOW COLUMNS FROM keywords LIKE 'selectable_locations'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE keywords ADD COLUMN selectable_locations TEXT")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS alarms (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    keyword_id INT,
                    keyword_name VARCHAR(120) NOT NULL,
                    location_text VARCHAR(255),
                    fallback_used BOOLEAN DEFAULT FALSE,
                    alerted_user_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
            cursor.close()
            conn.close()

    def get_setting(self, config, key):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_key = %s LIMIT 1",
                (key,),
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
                (key, value),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def validate_leitstelle_id(self, config, leitstelle_id):
        self.ensure_runtime_schema(config)
        saved_id = self.get_setting(config, "leitstelle_id")

        if saved_id is None:
            self.set_setting(config, "leitstelle_id", leitstelle_id)
            return True, "Leitstellen-ID wurde initial hinterlegt"

        if saved_id != leitstelle_id:
            return False, "Leitstellen-ID ungültig"

        return True, "Leitstellen-ID gültig"

    def get_active_group(self, config):
        active_group_id = self.get_setting(config, "active_group_id")
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)

            if active_group_id:
                cursor.execute(
                    "SELECT id, name, priority FROM user_groups WHERE id = %s LIMIT 1",
                    (active_group_id,),
                )
                row = cursor.fetchone()
                if row:
                    cursor.close()
                    conn.close()
                    return row

            cursor.execute(
                """
                SELECT id, name, priority
                FROM user_groups
                ORDER BY priority DESC, name ASC
                LIMIT 1
                """
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            return row
        raise Exception("Database connection failed")

    def get_available_sanitaeter_count(self, config):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM users
                WHERE is_active = TRUE AND status = 1
                """
            )
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        raise Exception("Database connection failed")

    def get_dashboard_data(self, config):
        self.ensure_runtime_schema(config)
        active_group = self.get_active_group(config)
        available_count = self.get_available_sanitaeter_count(config)
        return {
            "active_group": active_group,
            "available_count": available_count,
        }

    def get_keywords(self, config):
        self.ensure_runtime_schema(config)
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, keyword, location_type, default_location, selectable_locations, is_active
                FROM keywords
                WHERE is_active = TRUE
                ORDER BY keyword ASC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            for row in rows:
                raw_locations = row.get("selectable_locations")
                if raw_locations:
                    try:
                        row["selectable_locations"] = json.loads(raw_locations)
                    except Exception:
                        row["selectable_locations"] = [part.strip() for part in raw_locations.split(",") if part.strip()]
                else:
                    row["selectable_locations"] = []
            return rows
        raise Exception("Database connection failed")

    def get_alert_recipients(self, config):
        active_group = self.get_active_group(config)
        group_id = active_group["id"] if active_group else None

        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            primary_users = []
            if group_id:
                cursor.execute(
                    """
                    SELECT id, username
                    FROM users
                    WHERE is_active = TRUE AND status = 1 AND group_id = %s
                    ORDER BY username ASC
                    """,
                    (group_id,),
                )
                primary_users = cursor.fetchall()

            if primary_users:
                cursor.close()
                conn.close()
                return primary_users, False

            cursor.execute(
                """
                SELECT id, username
                FROM users
                WHERE is_active = TRUE
                ORDER BY username ASC
                """
            )
            fallback_users = cursor.fetchall()
            cursor.close()
            conn.close()
            return fallback_users, True
        raise Exception("Database connection failed")

    def create_alarm(self, config, keyword_id, keyword_name, location_text, alerted_users, fallback_used):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO alarms (keyword_id, keyword_name, location_text, fallback_used, alerted_user_ids)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    keyword_id,
                    keyword_name,
                    location_text,
                    fallback_used,
                    json.dumps([user["id"] for user in alerted_users]),
                ),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        raise Exception("Database connection failed")

    def get_recent_alarms(self, config, limit=5):
        conn = self.create_connection(config)
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id, keyword_name, location_text, fallback_used, alerted_user_ids, created_at
                FROM alarms
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            for row in rows:
                raw_ids = row.get("alerted_user_ids")
                if raw_ids:
                    try:
                        ids = json.loads(raw_ids)
                        row["recipient_count"] = len(ids)
                    except Exception:
                        row["recipient_count"] = 0
                else:
                    row["recipient_count"] = 0
            return rows
        raise Exception("Database connection failed")
