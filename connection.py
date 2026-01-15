import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração para TiDB Cloud (compatível com MySQL)
config = {
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_DATABASE", "oficina_mjp"),
    "port": int(os.getenv("DB_PORT", "4000")),  # TiDB Cloud usa porta 4000 por padrão
    "autocommit": os.getenv("DB_AUTOCOMMIT", "True").lower() == "true",
    "ssl_ca": os.getenv("DB_SSL_CA"),  # Para conexões SSL do TiDB Cloud
    "ssl_verify_cert": os.getenv("DB_SSL_VERIFY", "True").lower() == "true",
    "ssl_verify_identity": os.getenv("DB_SSL_VERIFY_IDENTITY", "True").lower() == "true"
}

# Remover valores None do config
config = {k: v for k, v in config.items() if v is not None}

def get_connection():
    try:
        conn = mysql.connector.connect(**config)
        conn.ping(reconnect=True, attempts=3, delay=2)
        return conn
    except mysql.connector.Error as err:
        print("Erro MySQL/TiDB:", err)
        raise
