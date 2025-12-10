from flask import Flask, request, jsonify
import requests
import logging
import os
from datetime import datetime

app = Flask(__name__)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные
COMPOSIO_API_KEY = os.environ.get('COMPOSIO_API_KEY')
RECIPE_ID = os.environ.get('RECIPE_ID', 'rcp_PXDn1btLCf0u')
COMPOSIO_RECIPE_URL = f"https://backend.composio.dev/api/v3/recipe/{RECIPE_ID}/execute"

if not COMPOSIO_API_KEY:
    raise RuntimeError("Не настроен API ключ (COMPOSIO_API_KEY)")

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Telegram Auto-Router Webhook Server",
        "timestamp": datetime.utcnow().isoformat(),
        "recipe_id": RECIPE_ID,
        "has_api_key": bool(COMPOSIO_API_KEY)
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
            logger.warning("Не получен update")
            return jsonify({"error": "No update received"}), 400

        logger.info(f"Получено обновление: update_id={update.get('update_id')}")

        # Проверяем наличие API ключа
        if not COMPOSIO_API_KEY:
            logger.error("Отсутствует COMPOSIO_API_KEY!")
            return jsonify({"ok": False, "error": "COMPOSIO_API_KEY not configured"}), 503

        # Отправляем данные в Composio
        headers = {
            "X-API-KEY": COMPOSIO_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "telegram_update": update
        }

        response = requests.post(
            COMPOSIO_RECIPE_URL,
            json=payload,
            headers=headers,
            timeout=int(os.environ.get('REQUESTS_TIMEOUT', 30))
        )

        logger.info(f"Ответ Composio: {response.status_code}")
        if response.status_code == 200:
            try:
                return jsonify({"ok": True, "result": response.json()}), 200
            except ValueError:
                logger.error("Ошибка обработки JSON ответа от Composio")
                return jsonify({"ok": True, "result": "processed"}), 200

        logger.error(f"Ошибка Composio: {response.text}")
        return jsonify({"ok": False, "error": response.text[:500]}), 502

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети: {e}")
        return jsonify({"ok": False, "error": "Service unavailable"}), 503
    except Exception as e:
        logger.exception("Исключение при обработке вебхука")
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Запуск сервера на порту {port}")
    app.run(host='0.0.0.0', port=port)
