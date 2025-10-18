#!/bin/bash
# Start the GitHub webhook listener

set -e

echo "🎣 Starting GitHub Webhook Listener..."

# Navigate to project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
else
    echo "⚠️  Warning: .env file not found, using defaults"
fi

# Check for required environment variable
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not set in .env"
    exit 1
fi

# Start the webhook server
echo "📡 Webhook server starting on port ${PORT:-8001}..."
echo "🔗 Endpoint: http://localhost:${PORT:-8001}/gh-webhook"
echo "❤️  Health check: http://localhost:${PORT:-8001}/health"
echo "🛑 Press Ctrl+C to stop"
echo ""

uv run adws/adw_triggers/trigger_webhook.py
