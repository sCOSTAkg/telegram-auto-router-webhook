from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
RECIPE_ID = os.environ.get('RECIPE_ID', 'rcp_PXDn1btLCf0u')
COMPOSIO_RECIPE_URL = f"https://backend.composio.dev/api/v3/recipe/{RECIPE_ID}/execute"

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Telegram Auto-Router Webhook Server v3",
        "timestamp": datetime.utcnow().isoformat(),
        "recipe_id": RECIPE_ID,
        "api_version": "v3",
        "has_api_key": bool(COMPOSIO_API_KEY)
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"error": "No update received"}), 400
        
        update_id = update.get('update_id', 'unknown')
        print(f"[{datetime.utcnow().isoformat()}] 📈 Update {update_id}")
        
        if not COMPOSIO_API_KEY:
            print(f"[{datetime.utcnow().isoformat()}] ❌ API key missing!")
            return jsonify({"ok": False, "error": "API key missing"}), 500
        
        headers = {"X-API-KEY": COMPOSIO_API_KEY, "Content-Type": "application/json"}
        payload = {"telegram_update": json.dumps(update)}
        
        print(f"[{datetime.utcnow().isoformat()}] 🚂 Calling v3 recipe...")
        response = requests.post(COMPOSIO_RECIPE_URL, json=payload, headers=headers, timeout=30)
        
        print(f"[{datetime.utcnow().isoformat()}] 📊 Status: {response.status_code}")
        print(f"[{datetime.utcnow().isoformat()}] Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print(f"[{datetime.utcnow().isoformat()}] ✅ Success")
            return jsonify({"ok": True}), 200
        else:
            print(f"[{datetime.utcnow().isoformat()}] ❌ Error: {response.text[:300]}")
            return jsonify({"ok": False, "error": response.text[:200]}), 200
            
    except Exception as e:
        print(f"[{datetime.utcnow().isoformat()}] 💥 Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚂 Starting Telegram Auto-Router v3")
    print(f"   Recipe: {RECIPE_ID}")
    print(f"   API: v3")
    print(f"   Port: {port}")
    app.run(host='0.0.0.0', port=port)
