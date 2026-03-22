#!/usr/bin/env python3
"""One-time setup: register a Telegram Test DC user account and save the session.

Run once before using telegram_e2e.py. Produces test_session.session (gitignored).

Usage:
    pip install telethon
    python3 scripts/telegram-e2e/setup_tg_test_account.py \\
        --api-id <API_ID> --api-hash <API_HASH> \\
        --dc 2 --phone 9996621234 --session .local/testing/test_session.session

Test DC phone number format (from https://docs.telethon.dev/en/stable/developing/test-servers.html):
    Format: 99966XYYYY where X = DC ID (1-5), YYYY = any 4 digits.
    Example: DC 2, suffix 1234 → phone 9996621234
    OTP code: DC ID repeated 5 times → DC 2 → code 22222

Test DC server:
    IP:   149.154.167.40
    Port: 80 (port 443 is unreliable on test servers)

Second account (for unauthorized-user scenario):
    Run again with a different phone and --session .local/testing/test_session2.session
"""

import argparse
import asyncio
import os
import sys

try:
    from telethon import TelegramClient
    from telethon.errors import PhoneNumberUnoccupiedError
except ImportError:
    print("telethon not installed. Run: pip install telethon", file=sys.stderr)
    sys.exit(1)

TEST_DC_HOST = "149.154.167.40"
TEST_DC_PORT = 443


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create Telegram Test DC session for E2E testing"
    )
    parser.add_argument(
        "--api-id",
        type=int,
        default=int(os.environ.get("TG_API_ID", "0")) or None,
        required=not os.environ.get("TG_API_ID"),
        help="Telegram API ID (use public test credentials: 17349)",
    )
    parser.add_argument(
        "--api-hash",
        default=os.environ.get("TG_API_HASH"),
        required=not os.environ.get("TG_API_HASH"),
        help="Telegram API hash",
    )
    parser.add_argument(
        "--dc",
        type=int,
        default=2,
        choices=[1, 2, 3, 4, 5],
        help="Test DC ID (default: 2). OTP = this digit repeated 5 times.",
    )
    parser.add_argument(
        "--phone",
        required=True,
        help="Test DC phone number without + (format: 99966XYYYY where X=DC ID)",
    )
    parser.add_argument(
        "--session",
        default=os.environ.get("TG_SESSION_PATH", ".local/testing/test_session.session"),
        help="Path to save the session file (default: .local/testing/test_session.session)",
    )
    args = parser.parse_args()

    # Normalize phone: strip leading + if present
    phone = args.phone.lstrip("+")

    expected_prefix = f"99966{args.dc}"
    if not phone.startswith(expected_prefix):
        print(
            f"WARNING: For DC {args.dc}, phone should start with {expected_prefix} (got {phone}).",
            file=sys.stderr,
        )

    otp = str(args.dc) * 5
    print(f"DC {args.dc} | phone: +{phone} | OTP will be: {otp}")

    session_dir = os.path.dirname(args.session)
    if session_dir:
        os.makedirs(session_dir, exist_ok=True)

    # Use None session so Telethon generates a fresh auth key for the test DC.
    # We export to a file manually after sign-in.
    print(f"Connecting to Telegram Test DC ({TEST_DC_HOST}:{TEST_DC_PORT})...")

    client = TelegramClient(None, args.api_id, args.api_hash)
    client.session.set_dc(args.dc, TEST_DC_HOST, TEST_DC_PORT)

    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        print(f"send_code_request response:")
        print(f"  type:       {sent.type}")
        print(f"  next_type:  {sent.next_type}")
        print(f"  timeout:    {sent.timeout}")
        print(f"  hash prefix: {sent.phone_code_hash[:8]}...")

        # Try 5-digit code first (DC_ID × 5), fall back to 6-digit (DC_ID × 6).
        # Telegram has changed test DC code length historically.
        for attempt_code in (otp, str(args.dc) * 6):
            try:
                print(f"Trying code: {attempt_code}")
                await client.sign_in(phone, attempt_code, phone_code_hash=sent.phone_code_hash)
                break
            except PhoneNumberUnoccupiedError:
                print("New test number — registering via sign_up...")
                await client.sign_up(
                    code=attempt_code,
                    first_name="ZephTest",
                    phone_code_hash=sent.phone_code_hash,
                    phone=phone,
                )
                break
            except Exception as e:
                if "PhoneCodeInvalid" in type(e).__name__ and attempt_code == otp:
                    print(f"Code {attempt_code} rejected, trying 6-digit variant...")
                    # refresh code request for next attempt
                    sent = await client.send_code_request(phone)
                    continue
                raise

        me = await client.get_me()
        print(f"\nAuthenticated as: {me.first_name} (@{me.username or 'no username'})")

        # Save session string to file
        session_string = client.session.save()
        session_path = args.session
        os.makedirs(os.path.dirname(session_path) or ".", exist_ok=True)
        with open(session_path, "w") as f:
            f.write(session_string)
        print(f"Session string saved to: {session_path}")
        print(f"\nFor CI secret TELEGRAM_TEST_SESSION, use the contents of that file directly.")
        print("\nNext step: register a bot on Test DC via @BotFather (test server):")
        print("  1. In Telegram app: Settings → switch to test server (tap version 5 times in some clients)")
        print("  2. Start @BotFather → /newbot → copy the token")
        print("  3. Add token to CI secret: ZEPH_TELEGRAM_TEST_TOKEN")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
