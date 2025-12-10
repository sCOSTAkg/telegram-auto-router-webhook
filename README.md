# Telegram Auto-Router Webhook Server

Webhook server for Telegram bot that routes incoming messages to Composio recipes.

## Features
- ✅ Receives Telegram webhook updates
- ✅ Routes to Composio recipe execution
- ✅ Production-ready with error handling
- ✅ Railway deployment ready

## Environment Variables

Set these in Railway:

- `COMPOSIO_API_KEY` - Your Composio API key (required)
- `RECIPE_ID` - Recipe ID to execute (default: rcp_PXDn1btLCf0u)
- `PORT` - Server port (auto-set by Railway)

## Deployment to Railway

1. Click "Deploy on Railway" or connect this repo
2. Set environment variables
3. Deploy
4. Copy the Railway URL (e.g., `https://your-app.up.railway.app`)
5. Set Telegram webhook:
   ```bash
   curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -d "url=https://your-app.up.railway.app/webhook"
   ```

## Endpoints

- `GET /` - Health check with server info
- `GET /health` - Simple health check
- `POST /webhook` - Telegram webhook endpoint

## Local Development

```bash
pip install -r requirements.txt
export COMPOSIO_API_KEY=your_key
export RECIPE_ID=rcp_PXDn1btLCf0u
python main.py
```

## Testing

Send a test webhook:
```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"message":{"chat":{"id":123},"text":"test"}}'
```
