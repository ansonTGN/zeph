#!/usr/bin/env bash
# Run Telegram E2E scenarios locally.
# All secrets are read from the Zeph age vault — no manual env vars needed.
#
# One-time vault setup:
#   zeph vault set ZEPH_TELEGRAM_TOKEN  '<bot_token>'
#   zeph vault set ZEPH_OPENAI_API_KEY  '<openai_key>'
#   zeph vault set TG_API_ID            '<api_id>'
#   zeph vault set TG_API_HASH          '<api_hash>'
#   zeph vault set TG_BOT_USERNAME      '@YourZephBot'
#   zeph vault set TG_SESSION           '<stringSession>'
#   zeph vault set TG_ACCOUNT_USERNAME  '<telethon_account_username>'
#
# Usage:
#   scripts/telegram-e2e/run-local.sh [--no-reset] [extra telegram_e2e.py flags]

set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."

ZEPH="./target/debug/zeph"

# Patch config and write session file
TG_ACCOUNT_USERNAME=$("$ZEPH" vault get TG_ACCOUNT_USERNAME)
mkdir -p .local/config .local/testing .local/testing/data .local/testing/debug
cp config/telegram-test.toml .local/config/telegram-test.toml
sed -i '' "s|allowed_users = \[\"your_test_username\"\]|allowed_users = [\"$TG_ACCOUNT_USERNAME\"]|" \
  .local/config/telegram-test.toml
"$ZEPH" vault get TG_SESSION > .local/testing/test_session.session

# Start Zeph in background (reads ZEPH_TELEGRAM_TOKEN + ZEPH_OPENAI_API_KEY from age vault directly)
"$ZEPH" --config .local/config/telegram-test.toml \
  >.local/testing/debug/telegram-session.log 2>&1 &
ZEPH_PID=$!
trap 'kill "$ZEPH_PID" 2>/dev/null || true' EXIT

echo "Waiting for bot to connect (12s)..."
sleep 12
tail -10 .local/testing/debug/telegram-session.log || true

TG_API_ID=$("$ZEPH" vault get TG_API_ID) \
TG_API_HASH=$("$ZEPH" vault get TG_API_HASH) \
TG_BOT_USERNAME=$("$ZEPH" vault get TG_BOT_USERNAME) \
TG_SESSION_PATH=".local/testing/test_session.session" \
PYTHONUNBUFFERED=1 \
  python3 scripts/telegram-e2e/telegram_e2e.py "$@"
