import pymysql

config = {
    "host": "135.125.201.14",
    "port": 3306,
    "user": "fivem",
    "password": "7658",
    "database": "mysql", # Wir testen erst mal die Standard-DB
    "charset": "utf8mb4"
}

try:
    print(f"Versuche Verbindung als {config['user']}...")
    conn = pymysql.connect(**config)
    print("✅ VERBINDUNG ERFOLGREICH!")
    conn.close()
except Exception as e:
    print(f"❌ FEHLER: {e}")