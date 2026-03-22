#!/usr/bin/env python3
"""Get Telethon StringSession for production Telegram account.

Usage:
    python3 scripts/telegram-e2e/get_session.py --api-id <ID> --api-hash <HASH>
"""
import argparse
import asyncio
import sys

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
except ImportError:
    print("telethon not installed. Run: pip install telethon", file=sys.stderr)
    sys.exit(1)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-id", type=int, required=True)
    parser.add_argument("--api-hash", required=True)
    args = parser.parse_args()

    client = TelegramClient(StringSession(), args.api_id, args.api_hash)

    await client.connect()
    try:
        loop = asyncio.get_event_loop()

        phone = (await loop.run_in_executor(None, lambda: input("Phone number (with +): "))).strip()
        sent = await client.send_code_request(phone)

        code = (await loop.run_in_executor(None, lambda: input("SMS code: "))).strip()
        try:
            await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
        except Exception as e:
            if "SessionPassword" in type(e).__name__:
                pwd = (await loop.run_in_executor(None, lambda: input("2FA password: "))).strip()
                await client.sign_in(password=pwd)
            else:
                raise

        session = client.session.save()
        me = await client.get_me()

        print(f"\nLogged in as: {me.first_name} (@{me.username})")
        print(f"\nTELEGRAM_TEST_ACCOUNT_USERNAME = {me.username}")
        print(f"\n--- TELEGRAM_TEST_SESSION (paste into GitHub secret) ---")
        print(session)
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
