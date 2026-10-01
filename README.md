# WSV 복구봇 + OAuth 웹 — Render와 Supabase 통합 버전

이 저장소는 **Render Web Service(웹)**와 **Render Background Worker(봇)**가 같은 Supabase PostgreSQL을 사용하는 최종 구성입니다.

```text
Render Web Service       ─┐
Render Background Worker ─┼── 같은 DATABASE_URL → Supabase
Discord OAuth 웹          ┘
```

## GitHub 업로드

이 폴더의 파일을 GitHub 저장소 최상위에 그대로 업로드하세요. `database.db`는 사용하지 않습니다.

## Render 서비스 2개

같은 GitHub 저장소로 두 서비스를 만듭니다.

### Web Service

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn web:app --bind 0.0.0.0:$PORT
```

### Background Worker

```text
Build Command: pip install -r requirements.txt
Start Command: python start.py
```

두 서비스 모두 아래 환경변수를 동일하게 입력합니다.

```text
DATABASE_URL=Supabase Session pooler URI
DISCORD_BOT_TOKEN=Discord 봇 토큰
DISCORD_ADMIN_IDS=관리자 Discord ID
DISCORD_CLIENT_ID=Discord Application ID
DISCORD_CLIENT_SECRET=Discord OAuth2 Client Secret
PUBLIC_BASE_URL=https://autha-6r42.onrender.com
DISCORD_API_ENDPOINT=https://discord.com/api/v10
RECOVERY_LOG_WEBHOOKS=
```

## Supabase 연결 문자열

Supabase → Connect → Direct → URI → **Session pooler**에서 복사합니다.

정상 URI 특징:

```text
호스트: pooler.supabase.com
포트: 5432
사용자: postgres.프로젝트ID
```

`db.프로젝트ID.supabase.co` 주소는 Direct Connection이므로 IPv6 오류가 발생할 수 있어 사용하지 않습니다.

## Discord Redirect URL

Discord Developer Portal → OAuth2 → Redirects에 아래 주소를 등록합니다.

```text
https://autha-6r42.onrender.com/callback
```

`PUBLIC_BASE_URL`에는 `/callback`을 붙이지 않습니다.

## 실행 순서

1. Supabase DB 비밀번호를 새로 설정합니다.
2. Session pooler URI를 복사합니다.
3. Web Service와 Background Worker에 같은 `DATABASE_URL`을 입력합니다.
4. 두 서비스를 배포합니다.
5. Discord에서 `/생성` → `/등록` → `/역할` → `/인증` 순서로 실행합니다.

테이블은 첫 DB 연결 때 자동 생성됩니다.

## 보안

실제 토큰, Client Secret, `DATABASE_URL`은 GitHub에 올리지 말고 Render Environment에만 입력하세요. 저장소는 Private을 권장합니다.

## DB 없는 봇 연결값 추가

Render Web Service의 Environment에 아래 값을 추가합니다.

```text
BOT_DB_API_KEY=봇과_공유하는_긴_랜덤_키
```

봇의 `start.py`에도 동일한 키를 입력합니다. 봇은 `REMOTE_DB_URL=https://autha-6r42.onrender.com`으로 Render 웹의 내부 DB API를 호출합니다.

## DB 없는 봇 연결

Render Web Service의 Environment에 다음 값을 추가합니다.

```text
BOT_DB_API_KEY=봇과_공유하는_긴_랜덤_키
```

봇 `start.py`의 `BOT_DB_API_KEY`에도 완전히 같은 값을 입력합니다. 이 키는 봇이 Render의 DB API를 호출할 때 쓰는 인증키이며, Supabase 비밀번호와는 다릅니다.
