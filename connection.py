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
    "port": int(os.getenv("DB_PORT", "4000")),
    "autocommit": os.getenv("DB_AUTOCOMMIT", "True").lower() == "true",
    "ssl_disabled": False,
    "ssl_verify_cert": False,
    "ssl_verify_identity": False,
    "connect_timeout": 30,
    "pool_size": 1,
    "pool_reset_session": False
}

# Remover valores None do config
config = {k: v for k, v in config.items() if v is not None}

def get_connection():
    try:
        print(f"Tentando conectar ao banco: {config.get('host')}:{config.get('port')}")
        print(f"Database: {config.get('database')}, User: {config.get('user')}")
        
        conn = mysql.connector.connect(**config)
        conn.ping(reconnect=True, attempts=3, delay=2)
        print("Conexão estabelecida com sucesso!")
        return conn
    except mysql.connector.Error as err:
        print(f"Erro MySQL/TiDB: {err}")
        print(f"Config usado: {config}")
        raise Exception(f"Erro ao conectar ao banco de dados: {str(err)}")
    except Exception as e:
        print(f"Erro geral: {e}")
        raise
