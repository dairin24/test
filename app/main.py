"""FastAPI アプリケーション。

エンドポイント:
- ``POST /api/generate``  要求ファイル → 要件定義 JSON
- ``POST /api/export``    要件定義 JSON → Markdown / Excel ダウンロード
- ``GET  /``              フロントエンド (静的ファイル)
"""

from __future__ import annotations

import io
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import exporters
from .extractors import UnsupportedFileError, extract
from .generator import generate
from .schema import RequirementsSpec

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="車載ソフトウェア 要件定義 自動生成")


@app.post("/api/generate", response_model=RequirementsSpec)
async def api_generate(file: UploadFile = File(...)) -> RequirementsSpec:
    """要求ファイルを受け取り、要件定義を生成して返す。"""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="ファイルが空です。")

    try:
        extracted = extract(file.filename or "uploaded", data)
    except UnsupportedFileError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        spec = generate(extracted, file.filename or "uploaded")
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return spec


@app.post("/api/export")
async def api_export(spec: RequirementsSpec, format: str = "markdown"):
    """編集後の要件定義を Markdown / Excel でダウンロードする。"""
    fmt = format.lower()
    if fmt in ("markdown", "md"):
        content = exporters.to_markdown(spec).encode("utf-8")
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="requirements.md"'},
        )
    if fmt in ("excel", "xlsx"):
        content = exporters.to_excel(spec)
        return StreamingResponse(
            io.BytesIO(content),
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={"Content-Disposition": 'attachment; filename="requirements.xlsx"'},
        )
    raise HTTPException(
        status_code=400,
        detail="format は 'markdown' または 'excel' を指定してください。",
    )


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# 静的アセット (app.js, style.css など) を配信
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
