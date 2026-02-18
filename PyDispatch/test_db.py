from sqlalchemy import create_engine, text

# Der Connection-String im FiveM-Stil
# Format: mysql+pymysql://NUTZER:PASSWORT@IP:PORT/DATENBANK
connection_string = "mysql+pymysql://fivem:7658@135.125.201.14:3306/pydispatch"

try:
    # Engine erstellen (jetzt ohne den Tippfehler)
    engine = create_engine(connection_string)
    
    # Verbindung testen
    with engine.connect() as connection:
        # Wir senden ein einfaches SELECT an die DB
        result = connection.execute(text("SELECT 'Verbindung steht!'"))
        for row in result:
            print(f"Server sagt: {row[0]}")
            
except Exception as e:
    print(f"Fehler: {e}")