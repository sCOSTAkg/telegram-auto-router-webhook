from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Получаем переменные окружения
COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
RECIPE_ID = os.environ.get('RECIPE_ID', 'rcp_PXDn1btLCf0u')
COMPOSIO_RECIPE_URL = f"https://backend.composio.dev/api/v3/recipe/{RECIPE_ID}/execute"

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Telegram Auto-Router Webhook Server",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        # Получаем update от Telegram
        update = request.get_json()

        if not update:
            return jsonify({"error": "No update received"}), 400

        print(f"[{datetime.utcnow().isoformat()}] Received update: {json.dumps(update)[:200]}...")

        # Отправляем в рецепт Composio
        headers = {
            "X-API-KEY": COMPOSIO_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "telegram_update": json.dumps(update)
        }

        print(f"[{datetime.utcnow().isoformat()}] Calling Composio recipe {RECIPE_ID}...")

        response = requests.post(
            COMPOSIO_RECIPE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        print(f"[{datetime.utcnow().isoformat()}] Composio response status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"[{datetime.utcnow().isoformat()}] Recipe executed successfully")
            return jsonify({"ok": True, "result": result}), 200
        else:
            error_text = response.text[:500]
            print(f"[{datetime.utcnow().isoformat()}] Recipe error: {error_text}")
            return jsonify({"ok": False, "error": error_text}), 200

    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] Exception: {str(e)}")
        return jsonify({"ok": False, "error": str(e)}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)
