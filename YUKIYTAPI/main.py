"""
========================================================================
  ʏᴜᴋɪ ʏᴛ ᴀᴘɪ - ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴇᴅɪᴀ ꜱᴛʀᴇᴀᴍɪɴɢ ᴇɴɢɪɴᴇ
========================================================================
  © 2026 ᴋᴀɪᴛᴏ | ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ. ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ.

  ᴡᴀʀɴɪɴɢ: ᴅᴏ ɴᴏᴛ ᴇᴅɪᴛ, ᴍᴏᴅɪꜰʏ, ᴏʀ ʀᴇᴍᴏᴠᴇ ᴛʜɪꜱ ʜᴇᴀᴅᴇʀ.
  ᴛʜɪꜱ ᴄᴏᴅᴇʙᴀꜱᴇ ɪꜱ ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴀɴᴛɪ-ᴛᴀᴍᴘᴇʀ ᴍᴇᴄʜᴀɴɪꜱᴍ.
  ʀᴇᴍᴏᴠɪɴɢ ᴛʜɪꜱ ᴄᴏᴘʏʀɪɢʜᴛ ɴᴏᴛɪᴄᴇ ᴡɪʟʟ ᴛʀɪɢɢᴇʀ ᴀ ꜱʏꜱᴛᴇᴍ-ʟᴇᴠᴇʟ
  ꜰᴀᴛᴀʟ ᴇʀʀᴏʀ ᴀɴᴅ ᴘᴇʀᴍᴀɴᴇɴᴛʟʏ ᴘʀᴇᴠᴇɴᴛ ᴛʜᴇ ᴀᴘɪ ꜰʀᴏᴍ ʀᴜɴɴɪɴɢ.
========================================================================
"""

import sys

if (
    __doc__ is None
    or "© 2026 ᴋᴀɪᴛᴏ | ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ. ᴀʟʟ ʀɪɢʜᴛꜱ ʀᴇꜱᴇʀᴠᴇᴅ."
    not in __doc__
):
    print("\n[!] ꜰᴀᴛᴀʟ ᴇʀʀᴏʀ: ᴄᴏᴘʏʀɪɢʜᴛ ᴛᴀᴍᴘᴇʀɪɴɢ ᴅᴇᴛᴇᴄᴛᴇᴅ.")
    print("[!] ᴛʜᴇ ʜᴇʟʟꜰɪʀᴇᴅᴇᴠꜱ ᴄᴏᴘʏʀɪɢʜᴛ ʜᴇᴀᴅᴇʀ ʜᴀꜱ ʙᴇᴇɴ ᴍᴏᴅɪꜰɪᴇᴅ ᴏʀ ʀᴇᴍᴏᴠᴇᴅ.")
    print("[!] ᴀᴘɪ ᴇxᴇᴄᴜᴛɪᴏɴ ʙʟᴏᴄᴋᴇᴅ. ꜱʏꜱᴛᴇᴍ ᴇxɪᴛɪɴɢ...\n")
    sys.exit(1)

import os
import time
import uuid
import asyncio
import json

from fastapi import (
    FastAPI,
    BackgroundTasks,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import FileResponse, JSONResponse

from YUKIYTAPI.database.stats import (
    init_db,
    add_download,
    get_stats,
)

app = FastAPI(
    title="YUKI YT API",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CACHE_DIR = os.path.join(
    BASE_DIR,
    "YUKIYTAPI",
    "saved",
)

COOKIES_FILE = os.path.join(
    BASE_DIR,
    "cookies.txt",
)

os.makedirs(CACHE_DIR, exist_ok=True)

init_db()

TOKENS = {}
START_TIME = time.time()


# ═══════════════════════════════════════════════════════════════════════
# BACKGROUND: temp → cache
# ═══════════════════════════════════════════════════════════════════════

def _move_to_cache(tmp_path: str, cache_path: str) -> None:
    try:
        if (
            os.path.exists(tmp_path)
            and os.path.getsize(tmp_path) > 0
        ):
            os.replace(tmp_path, cache_path)

    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════

@app.get("/")
async def home(request: Request):

    uptime = round(
        time.time() - START_TIME,
        2
    )

    return JSONResponse({
        "status": "Running...",
        "owner": "YUKIMUSIC",
        "uptime": f"{uptime}s",
        "message": "Welcome to YUKI API",
    })


# ═══════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════

@app.get("/search")
async def search_songs(
    request: Request,
    q: str,
    limit: int = 10,
):

    # Empty query protection
    if not q or not q.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query is required",
        )

    # Keep limit between 1 and 20
    limit = max(1, min(limit, 20))

    search_query = q.strip()

    cmd = [
        "yt-dlp",

        "--flat-playlist",
        "--dump-single-json",

        "--no-warnings",
        "--skip-download",

        f"ytsearch{limit}:{search_query}",
    ]

    try:

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:

            error_text = stderr.decode(
                errors="ignore"
            ).strip()

            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {error_text[:500]}",
            )

        if not stdout:
            raise HTTPException(
                status_code=500,
                detail="Search returned empty response",
            )

        data = json.loads(
            stdout.decode(
                errors="ignore"
            )
        )

        results = []

        for item in data.get("entries", []):

            if not item:
                continue

            video_id = item.get("id")

            if not video_id:
                continue

            results.append({
                "title": item.get("title"),
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "duration": item.get("duration"),
                "channel": (
                    item.get("channel")
                    or item.get("uploader")
                ),
                "thumbnail": item.get("thumbnail"),
            })

        return JSONResponse({
            "status": "success",
            "query": search_query,
            "count": len(results),
            "results": results,
        })

    except HTTPException:
        raise

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Invalid response received from yt-dlp",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}",
        )


# ═══════════════════════════════════════════════════════════════════════
# STATS
# ═══════════════════════════════════════════════════════════════════════

@app.get("/stats")
async def api_stats(request: Request):

    total_dl, cache_mb = get_stats()

    return JSONResponse({
        "status": "success",
        "total_song_downloads": total_dl,
        "total_cache_size_mb": cache_mb,
        "active_tokens": len(TOKENS),
    })


# ═══════════════════════════════════════════════════════════════════════
# TOKEN GENERATE
# ═══════════════════════════════════════════════════════════════════════

@app.get("/download")
async def generate_token(
    request: Request,
    url: str,
    type: str = "audio",
):

    video_id = (
        url.split("v=")[-1].split("&")[0]
        if "v=" in url
        else url
    )

    yuki_token = (
        f"YUKIMusic"
        f"{uuid.uuid4().hex[:16]}"
        f"YukiBots"
    )

    TOKENS[yuki_token] = {
        "video_id": video_id,
        "type": type,
        "expires": time.time() + 60,
    }

    return JSONResponse({
        "status": "success",
        "video_id": video_id,
        "download_token": yuki_token,
        "usage": "Use token parameter in /stream endpoint",
    })


# ═══════════════════════════════════════════════════════════════════════
# STREAM
# ═══════════════════════════════════════════════════════════════════════

@app.get("/stream/{video_id}")
async def stream_music(
    request: Request,
    video_id: str,
    background_tasks: BackgroundTasks,
    type: str = "audio",
    token: str = None,
    x_download_token: str = Header(None),
):

    # ───────────────────────────────────────────────────────────────────
    # AUTH
    # ───────────────────────────────────────────────────────────────────

    actual_token = (
        token
        or x_download_token
    )

    if (
        not actual_token
        or actual_token not in TOKENS
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Token Access Denied",
        )

    token_data = TOKENS[actual_token]

    if (
        time.time() > token_data["expires"]
        or token_data["video_id"] != video_id
    ):
        TOKENS.pop(
            actual_token,
            None,
        )

        raise HTTPException(
            status_code=401,
            detail="Token Expired",
        )

    # Token is one-time use
    del TOKENS[actual_token]

    # ───────────────────────────────────────────────────────────────────
    # CACHE
    # ───────────────────────────────────────────────────────────────────

    ext = (
        "m4a"
        if type == "audio"
        else "mp4"
    )

    cache_path = os.path.join(
        CACHE_DIR,
        f"{video_id}.{ext}",
    )

    if (
        os.path.exists(cache_path)
        and os.path.getsize(cache_path) > 0
    ):

        add_download()

        return FileResponse(
            cache_path,
            media_type=(
                "audio/mp4"
                if type == "audio"
                else "video/mp4"
            ),
        )

    # ───────────────────────────────────────────────────────────────────
    # DOWNLOAD
    # ───────────────────────────────────────────────────────────────────

    tmp_path = os.path.join(
        CACHE_DIR,
        f"{video_id}.tmp.{ext}",
    )

    outtmpl = os.path.join(
        CACHE_DIR,
        f"{video_id}.tmp.%(ext)s",
    )

    if type == "audio":

        cmd = [
            "yt-dlp",

            "--cookies",
            COOKIES_FILE,

            "--js-runtimes",
            "node",

            "--remote-components",
            "ejs:github",

            "-f",
            "bestaudio[ext=m4a]/"
            "bestaudio[ext=opus]/"
            "bestaudio/best",

            "-o",
            outtmpl,

            "--quiet",

            video_id,
        ]

    else:

        cmd = [
            "yt-dlp",

            "--cookies",
            COOKIES_FILE,

            "--js-runtimes",
            "node",

            "--remote-components",
            "ejs:github",

            "-f",
            "(bestvideo[ext=mp4]+"
            "bestaudio[ext=m4a])/best[ext=mp4]/best",

            "-o",
            outtmpl,

            "--quiet",

            video_id,
        ]

    try:

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        _, stderr = await process.communicate()

        if process.returncode != 0:

            raise HTTPException(
                status_code=500,
                detail=(
                    "yt-dlp error: "
                    + stderr.decode(
                        errors="ignore"
                    )[:500]
                ),
            )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    # ───────────────────────────────────────────────────────────────────
    # FIND DOWNLOADED FILE
    # ───────────────────────────────────────────────────────────────────

    actual_tmp = None

    for fname in os.listdir(CACHE_DIR):

        if (
            fname.startswith(
                f"{video_id}.tmp."
            )
            and not fname.endswith(".tmp")
        ):
            actual_tmp = os.path.join(
                CACHE_DIR,
                fname,
            )
            break

    if (
        not actual_tmp
        or not os.path.exists(actual_tmp)
    ):

        raise HTTPException(
            status_code=500,
            detail="Download failed — file not found",
        )

    actual_ext = actual_tmp.rsplit(
        ".",
        1
    )[-1]

    final_cache = os.path.join(
        CACHE_DIR,
        f"{video_id}.{actual_ext}",
    )

    add_download()

    # ───────────────────────────────────────────────────────────────────
    # BACKGROUND CACHE
    # ───────────────────────────────────────────────────────────────────

    background_tasks.add_task(
        _move_to_cache,
        actual_tmp,
        final_cache,
    )

    return FileResponse(
        actual_tmp,
        media_type=(
            "audio/mp4"
            if type == "audio"
            else "video/mp4"
        ),
    )
