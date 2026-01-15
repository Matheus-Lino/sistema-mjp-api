from flask import Flask, jsonify
from flask_cors import CORS
from database import dashboard_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurar CORS para aceitar requisições do frontend (incluindo Vercel)
# Permitir todas as origens do Vercel temporariamente
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Permitir todas as origens (temporário para debug)
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

app.register_blueprint(dashboard_bp)

# Para Vercel - exportar o app
handler = app

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", "5000"))
    app.run(debug=debug_mode, host="0.0.0.0", port=port)