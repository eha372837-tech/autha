# -*- coding: utf-8 -*-
"""Render web settings.

You may enter values directly below. Environment variables override these
values when present. Never commit real secrets to a public GitHub repository.
"""
import os

# ============================================================
# Render 웹사이트 설정 — 여기에 직접 입력할 수 있습니다.
# ============================================================
DATABASE_URL = "여기에_Supabase_연결문자열_입력"
DISCORD_BOT_TOKEN = ""
DISCORD_ADMIN_IDS = ""
DISCORD_CLIENT_ID = ""
DISCORD_CLIENT_SECRET = ""
PUBLIC_BASE_URL = "https://autha-6r42.onrender.com"
RECOVERY_LOG_WEBHOOKS = ""
BOT_DB_API_KEY = "여기에_봇_DB_API_키_입력"
DISCORD_API_ENDPOINT = "https://discord.com/api/v10"


def _value(env_name: str, direct_value: str) -> str:
    return os.getenv(env_name, "").strip() or direct_value.strip()


def _int_list(value: str) -> list[int]:
    if not value:
        return []
    try:
        return [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise RuntimeError("DISCORD_ADMIN_IDS는 숫자 ID를 쉼표로 구분해야 합니다.") from exc


봇_토큰 = _value("DISCORD_BOT_TOKEN", DISCORD_BOT_TOKEN)
관리자아이디 = _int_list(_value("DISCORD_ADMIN_IDS", DISCORD_ADMIN_IDS))
API_엔드포인트 = _value("DISCORD_API_ENDPOINT", DISCORD_API_ENDPOINT)
클라이언트_아이디 = _value("DISCORD_CLIENT_ID", DISCORD_CLIENT_ID)
클라이언트_시크릿 = _value("DISCORD_CLIENT_SECRET", DISCORD_CLIENT_SECRET)
도메인 = _value("PUBLIC_BASE_URL", PUBLIC_BASE_URL).rstrip("/")
복구로그웹훅 = [
    item.strip() for item in _value("RECOVERY_LOG_WEBHOOKS", RECOVERY_LOG_WEBHOOKS).split(",") if item.strip()
]

token = 봇_토큰
admin_id = 관리자아이디
api_endpoint = API_엔드포인트
client_id = 클라이언트_아이디
client_secret = 클라이언트_시크릿
base_url = 도메인
bokweb = 복구로그웹훅

# 봇이 Render DB API를 호출할 때 사용하는 비밀키
BOT_DB_API_KEY = 봇_DB_API_키
