#!/usr/bin/env python3
"""Discord bot entrypoint. Render Worker command: python start.py"""
import os
import runpy
from pathlib import Path

# Render Environment Variables override these fallback placeholders.
os.environ.setdefault("DISCORD_BOT_TOKEN", "여기에_봇_토큰_입력")
os.environ.setdefault("DISCORD_ADMIN_IDS", "여기에_관리자_ID_입력")
os.environ.setdefault("DISCORD_CLIENT_ID", "여기에_Application_ID_입력")
os.environ.setdefault("DISCORD_CLIENT_SECRET", "여기에_Client_Secret_입력")
os.environ.setdefault("PUBLIC_BASE_URL", "https://autha-6r42.onrender.com")
os.environ.setdefault("DATABASE_URL", "여기에_Supabase_Session_Pooler_URI_입력")
os.environ.setdefault("DISCORD_API_ENDPOINT", "https://discord.com/api/v10")
os.environ.setdefault("RECOVERY_LOG_WEBHOOKS", "")

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)

if __name__ == "__main__":
    runpy.run_path(str(ROOT / "new.py"), run_name="__main__")
