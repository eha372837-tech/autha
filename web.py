# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, make_response
from flask import session, redirect, url_for, abort, jsonify
from datetime import timedelta

import config as settings
import asyncio
import requests
import datetime
import http
import w
import ipaddress
import datetime as pydatetime
import os

app = Flask(__name__)

def _db_authorized():
    return request.headers.get("X-Bot-DB-Key", "") == settings.BOT_DB_API_KEY and bool(settings.BOT_DB_API_KEY)

@app.post("/internal/db/query")
def internal_db_query():
    """Private SQL bridge used only by the DB-less bot package."""
    if not _db_authorized():
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    sql = str(payload.get("sql", "")).strip()
    params = payload.get("params", [])
    if not sql or not isinstance(params, list):
        return jsonify({"ok": False, "error": "bad_request"}), 400
    try:
        import db
        con, cur = db.connect(), None
        try:
            cur = con.cursor()
            cur.execute(sql, tuple(params))
            rows = cur.fetchall() if sql.lstrip().lower().startswith("select") else []
            con.commit()
        finally:
            con.close()
        return jsonify({"ok": True, "rows": rows})
    except Exception as exc:
        app.logger.exception("bot DB API query failed")
        return jsonify({"ok": False, "error": str(exc)}), 500



@app.get("/")
def home():
    return """<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WSV 인증 사이트</title><style>body{font-family:Arial,sans-serif;background:#f4f6f8;display:grid;place-items:center;min-height:100vh;margin:0;color:#20252b}.card{background:#fff;max-width:560px;margin:24px;padding:40px;border-radius:16px;box-shadow:0 8px 30px #0001;text-align:center}h1{margin-top:0}p{line-height:1.7;color:#667085}.ok{display:inline-block;background:#e8f7ee;color:#18794e;padding:8px 14px;border-radius:999px;font-size:14px}</style></head><body><main class="card"><span class="ok">사이트 정상 작동 중</span><h1>WSV 인증 사이트</h1><p>인증 페이지가 준비되었습니다.<br>Discord OAuth2 연결 후 인증 패널에서 사용할 수 있습니다.</p></main></body></html>""", 200


@app.get("/health")
def health():
    return {"status": "ok"}, 200

def server_check(guild_id):
    headers = {
        'Authorization': f'Bot {settings.token}'
    }

    response = requests.get(f'https://discord.com/api/v10/users/@me/guilds', headers=headers)

    if response.status_code == 200:
        guilds = response.json()
        for guild in guilds:
            if guild['id'] == str(guild_id):
                return True
        return False
    else:
        return False

def get_now():
    return pydatetime.datetime.now()


def get_now_timestamp():
    return round(float(get_now().timestamp()))


def get_kr_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getip():
    # X-Forwarded-For 헤더에서 실제 클라이언트 IP 주소 가져오기
    ip = request.headers.get('X-Forwarded-For')

    # 만약 X-Forwarded-For 헤더가 없으면, REMOTE_ADDR 사용
    if not ip:
        ip = request.remote_addr

    # 여러 IP 주소가 있는 경우, 첫 번째 IP 주소 반환
    ip = ip.split(',')[0].strip()

    return ip


def get_agent():
    return request.user_agent.string


def is_expired(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
    if (ExpireTime - ServerTime).total_seconds() > 0:
        return False
    else:
        return True


def get_expiretime(time):
    ServerTime = datetime.datetime.now()
    ExpireTime = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
    if (ExpireTime - ServerTime).total_seconds() > 0:
        how_long = ExpireTime - ServerTime
        days = how_long.days
        hours = how_long.seconds // 3600
        minutes = how_long.seconds // 60 - hours * 60
        return (
            str(round(days))
            + "일 "
            + str(round(hours))
            + "시간 "
            + str(round(minutes))
            + "분"
        )
    else:
        return False


def make_expiretime(days):
    ServerTime = datetime.datetime.now()
    ExpireTime_STR = (ServerTime + timedelta(days=days)
                      ).strftime("%Y-%m-%d %H:%M")
    return ExpireTime_STR


def add_time(now_days, add_days):
    ExpireTime = datetime.datetime.strptime(now_days, "%Y-%m-%d %H:%M")
    ExpireTime_STR = (ExpireTime + timedelta(days=add_days)
                      ).strftime("%Y-%m-%d %H:%M")
    return ExpireTime_STR



async def exchange_code(code, redirect_url):
    data = {
        "client_id": settings.client_id,
        "client_secret": settings.client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_url,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    while True:
        r = requests.post(
            f"{settings.api_endpoint}/oauth2/token", data=data, headers=headers
        )
        if r.status_code != 429:
            break

        limitinfo = r.json()
        await asyncio.sleep(limitinfo["retry_after"] + 2)
    return False if "error" in r.json() else r.json()

def getguild(id):
    header = {
        "Authorization" : f"Bot {settings.token}"
    }
    r = requests.get(f'https://discord.com/api/v9/guilds/{id}',headers=header)
    rr = r.json()
    #print(rr['approximate_member_count'])
    return r.json()
async def get_user_profile2(token):
    header = {
        "Authorization": "Bearer " + token}  # Bot은 Authorization : Bot TOKEN, 유저 Access Token은 Bearer Token으로 명시함 이 경우는 oauth2 access token인 경우에만 해당
    res = requests.get("https://discordapp.com/api/v8/users/@me", headers=header)  # 여긴 그냥 헤더에 토큰쳐넣으면 user정보 반환하는거임
    print(res.json())
    if (res.status_code != 200):
        return False
    else:
        return res.json()

async def get_user_profile(token):
    header = {"Authorization": token}
    res = requests.get("https://discord.com/api/v10/users/@me", headers=header)
    print(res.json())
    if res.status_code != 200:
        return False
    else:
        return res.json()
def start_db():
    con = db.connect()
    cur = con.cursor()
    return con, cur

def is_guild(id):
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    res = cur.fetchone()
    con.close()
    if res == None:
        return False
    else:
        return True


def is_guild_valid(id):
    if not (str(id).isdigit()):
        return False
    if not is_guild(id):
        return False
    con, cur = start_db()
    cur.execute("SELECT * FROM guilds WHERE id == ?;", (id,))
    guild_info = cur.fetchone()
    expire_date = guild_info[3]
    con.close()
    if is_expired(expire_date):
        return False
    return True

def get_role_info(role_id):
    headers = {
        'Authorization': f'Bot {settings.token}'
    }
    url = f'{settings.api_endpoint}/roles/{role_id}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        role_info = response.json()
        role_name = role_info['name']
        print(f"Role name: {role_name}")
        return role_info
    elif response.status_code == 404:
        print("Role not found. Please provide a valid role ID.")
    else:
        print(f"Failed to fetch role info. Status code: {response.status_code}")
        print(response.text)

def give_role_to_member(server_id, member_id, role_id):
    if not role_id or str(role_id) == "0":
        return False, "역할이 아직 설정되지 않았습니다. Discord에서 /역할 명령어를 먼저 실행하세요."
    headers = {
        'Authorization': f'Bot {settings.token}',
        'Content-Type': 'application/json'
    }
    url = f'{settings.api_endpoint}/guilds/{server_id}/members/{member_id}/roles/{role_id}'
    response = requests.put(url, headers=headers, timeout=20)
    if response.status_code == 204:
        print("Role successfully given to member!")
        return True, ""
    detail = f"Discord API {response.status_code}: {response.text[:300]}"
    print(f"Failed to give role to member. {detail}")
    return False, detail

@app.route("/callback", methods=["GET"])
async def callback():
    """Discord OAuth callback with defensive validation and friendly errors."""
    try:
        state = request.args.get("state")
        code = request.args.get("code")
        if not state or not code:
            return render_template("error.html", title="인증 실패", ERROR_MSG="인증 코드가 없거나 만료되었습니다. Discord에서 인증을 다시 시작해주세요."), 400

        try:
            guild_id = int(state)
        except (TypeError, ValueError):
            return render_template("error.html", title="인증 실패", ERROR_MSG="잘못된 서버 인증 요청입니다."), 400

        exchange_res = await exchange_code(code, f"{settings.base_url}/callback")
        if not isinstance(exchange_res, dict) or not exchange_res.get("access_token"):
            return render_template("error.html", title="인증 실패", ERROR_MSG="Discord 인증 코드가 만료되었거나 이미 사용되었습니다. 다시 인증해주세요."), 400

        access_token = exchange_res["access_token"]
        user_info = await get_user_profile("Bearer " + access_token)
        if not isinstance(user_info, dict) or not user_info.get("id"):
            return render_template("error.html", title="인증 실패", ERROR_MSG="Discord 사용자 정보를 가져오지 못했습니다."), 400

        guild = server_check(guild_id)
        if guild is False:
            return render_template("error.html", title="인증 실패", ERROR_MSG="서버에 봇이 참여되어 있지 않습니다."), 400

        email = user_info.get("email")
        if not email:
            return render_template("error.html", title="인증 실패", ERROR_MSG="Discord 계정의 이메일 인증 후 다시 시도해주세요."), 400
        if "police" in email:
            return render_template("error.html", title="인증 실패", ERROR_MSG="제한된 사용자입니다."), 400

        # Store the user and read role/webhook in one DB connection.
        con, cur = start_db()
        try:
            cur.execute("INSERT INTO users VALUES(?, ?, ?);", (str(user_info["id"]), exchange_res.get("refresh_token", ""), guild_id))
            cur.execute("SELECT * FROM guilds WHERE id == ?", (guild_id,))
            guild_row = cur.fetchone()
            con.commit()
        finally:
            con.close()

        if not guild_row:
            return render_template("error.html", title="인증 실패", ERROR_MSG="이 서버에 등록된 라이센스 정보를 찾지 못했습니다."), 400

        role_id = guild_row[1]
        webhook = str(guild_row[4]) if len(guild_row) > 4 else "no"
        guild_name = guild.get("name", str(guild_id)) if isinstance(guild, dict) else str(guild_id)
        user_id = user_info["id"]
        username = user_info.get("username", "알 수 없음")
        discriminator = user_info.get("discriminator", "0")

        try:
            role_ok, role_error = give_role_to_member(guild_id, user_id, role_id)
        except Exception:
            app.logger.exception("role assignment failed")
            role_ok, role_error = False, "Render에서 Discord 역할 API 호출에 실패했습니다."
        if not role_ok:
            return render_template("error.html", title="인증 실패", ERROR_MSG=f"{guild_name} 서버에서 역할 지급에 실패했습니다.\n{role_error}"), 400

        # External IP lookup is optional; authentication must not fail if it is unavailable.
        ip = getip()
        isp = city = country = "확인 불가"
        if webhook != "no":
            try:
                w.send(webhook, "인증 성공", f"<@{user_id}>님이 인증을 완료하였습니다.\n유저 닉네임: {username}\n유저 아이디: {user_id}\n인증한 서버: {guild_name} ({guild_id})", "")
            except Exception:
                app.logger.exception("verification webhook failed")

        return render_template("success.html", title="인증 성공", id=str(user_id), name=username, tag=discriminator, ip=ip)
    except Exception:
        app.logger.exception("OAuth callback failed")
        return render_template("error.html", title="인증 실패", ERROR_MSG="인증 처리 중 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요."), 500

if __name__ == "__main__":
    try:
        # Hosting providers inject PORT; local execution defaults to 8080.
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
    except Exception as e:
        print(e)
