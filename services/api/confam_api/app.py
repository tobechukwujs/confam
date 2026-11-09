from __future__ import annotations

import json
import re
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from confam_contract.serialize import verdict_to_json
from confam_contract.verdict import Verdict
from confam_engine import OfficialNotice, latest_successor
from confam_engine.ocr import Reader, check_readings
from confam_engine.ocr.imageio import MAX_BYTES, ImageError, load_image, probe_image
from confam_engine.ocr.tesseract import default_readers, tesseract_available

from .jobs import JobManager
from .ratelimit import RateLimiter
from .record import Record, RecordHolder, load_record
from .service import CheckService
from .settings import Settings
from .store import CheckStore

CODE_RE = re.compile(r"^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$")
JOB_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
LANGS = ("en", "pcm", "ha", "yo", "ig")
WRONG_TYPE = "Send a photo or screenshot of the notice (JPG, PNG or WebP)."
TOO_BIG = "That picture is too big. Use one under 5 MB."
NO_PHOTOS = "Photo checks are not available right now. Please paste the text instead."


class CheckRequest(BaseModel):
    """A text check. Photos are sent as a raw image body instead (see create_check)."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(max_length=5000)
    lang: Literal["en", "pcm", "ha", "yo", "ig"] = "en"

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Paste the notice text to check it.")
        return value


ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class SupersededRef(BaseModel):
    id: str
    published: str


class SignatureOut(BaseModel):
    reviewer: str
    role: Literal["first", "second"]
    signed_at: str


class RecordSummary(BaseModel):
    id: str
    title: str
    published: str
    lang: str
    superseded_by: SupersededRef | None


class RecordList(BaseModel):
    record_as_of: str
    notices: list[RecordSummary]


class RecordEntry(RecordSummary):
    url: str
    text: str
    signatures: list[SignatureOut]


def _summary(notice: OfficialNotice, notices: list[OfficialNotice]) -> dict:
    newest = latest_successor(notice, notices)
    return {
        "id": notice.id,
        "title": notice.title,
        "published": notice.published,
        "lang": notice.lang,
        "superseded_by": {"id": newest.id, "published": newest.published} if newest else None,
    }


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _seed_samples(store: CheckStore, settings: Settings) -> None:
    path = settings.record_path.parent / "sample-verdicts.json"
    samples = json.loads(path.read_text(encoding="utf-8"))
    for name, payload in samples.items():
        if name.startswith("_"):
            continue
        store.put(Verdict.model_validate(payload), permanent=True)


def create_app(
    settings: Settings | None = None,
    record: Record | None = None,
    readers: object = "auto",
) -> FastAPI:
    """`readers`: two Reader objects for photo checks, None to turn photo checks off, or "auto"
    (Tesseract if it is installed)."""
    settings = settings or Settings.from_env()
    holder = RecordHolder(record or load_record(settings.record_path))
    store = CheckStore()
    service = CheckService(holder, store)
    limiter = RateLimiter(settings.rate_limit_per_minute, settings.ip_salt)
    if settings.seed_samples:
        _seed_samples(store, settings)

    if readers == "auto":
        readers = default_readers() if tesseract_available() else None
    reading: tuple[Reader, Reader] | None = tuple(readers) if readers else None  # type: ignore[arg-type]

    def process(data: bytes, lang: str, set_stage) -> str:
        """Runs in a worker. The picture exists only here, in memory, and is never stored."""
        assert reading is not None
        set_stage("reading_1")
        image = load_image(data)
        first = reading[0].read(image)
        set_stage("reading_2")
        second = reading[1].read(image)
        set_stage("comparing")
        del image
        rec = holder.record
        verdict = check_readings([first, second], rec.notices, record_as_of=rec.record_as_of, lang=lang)
        store.put(verdict)
        return verdict.code

    jobs = JobManager(process, workers=settings.photo_workers) if reading else None

    app = FastAPI(title="Confam API", version="0.0.0")
    app.state.holder, app.state.store, app.state.service = holder, store, service
    app.state.jobs = jobs

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"status": "ok", "photo_checks": jobs is not None}

    @app.post("/v1/checks")
    async def create_check(request: Request, lang: str = "en") -> JSONResponse:
        """Text: a JSON body {text, lang} returns a verdict. Photo: the raw image as the body
        (Content-Type image/png, image/jpeg or image/webp) with ?lang=, returns 202 {job_id}.
        The photo is read in memory only; a multipart upload is avoided because it can be
        spooled to a temporary file on disk (rule 7)."""
        if not limiter.allow(_client_ip(request)):
            raise HTTPException(status_code=429, detail="Too many checks. Please try again in a minute.")

        ctype = request.headers.get("content-type", "").split(";")[0].strip().lower()
        if ctype in ("", "application/json"):
            try:
                body = CheckRequest.model_validate(await request.json())
            except (ValueError, ValidationError) as exc:
                detail = (
                    [{"loc": e["loc"], "msg": e["msg"]} for e in exc.errors()]
                    if isinstance(exc, ValidationError)
                    else "Send JSON with a text field."
                )
                raise HTTPException(status_code=422, detail=detail) from exc
            return JSONResponse(verdict_to_json(service.check_text(body.text, body.lang)))

        if not ctype.startswith("image/"):
            raise HTTPException(status_code=415, detail=WRONG_TYPE)
        if lang not in LANGS:
            raise HTTPException(status_code=422, detail="Unknown language.")
        if jobs is None:
            raise HTTPException(status_code=503, detail=NO_PHOTOS)

        declared = request.headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > MAX_BYTES:
            raise HTTPException(status_code=413, detail=TOO_BIG)
        data = bytearray()
        async for chunk in request.stream():  # read in memory, stop at the limit
            data += chunk
            if len(data) > MAX_BYTES:
                raise HTTPException(status_code=413, detail=TOO_BIG)
        try:
            probe_image(bytes(data))  # real type, size and pixel count from the header only
        except ImageError as exc:
            status = 413 if exc.kind in ("size", "pixels") else 415
            raise HTTPException(status_code=status, detail=TOO_BIG if status == 413 else WRONG_TYPE) from exc

        return JSONResponse({"job_id": jobs.submit(bytes(data), lang)}, status_code=202)

    @app.get("/v1/checks/{job_id}")
    def get_job(job_id: str) -> JSONResponse:
        job = jobs.get(job_id) if jobs is not None and JOB_RE.match(job_id) else None
        if job is None:
            raise HTTPException(status_code=404, detail="No such check, or it has expired.")
        return JSONResponse(job)
    @app.get("/v1/verdicts/{code}")
    def get_verdict(code: str) -> JSONResponse:
        normal = code.replace("-", "").upper()
        verdict = store.get(normal) if CODE_RE.match(normal) else None
        if verdict is None:
            raise HTTPException(status_code=404, detail="No check with that code.")
        return JSONResponse(verdict_to_json(service.refreshed(verdict)))

    @app.get("/v1/record", response_model=RecordList)
    def list_record() -> dict:
        rec = holder.record
        return {
            "record_as_of": rec.record_as_of.isoformat(),
            "notices": [_summary(n, rec.notices) for n in rec.notices],
        }

    @app.get("/v1/record/{notice_id}", response_model=RecordEntry)
    def get_record_entry(notice_id: str) -> dict:
        rec = holder.record
        notice = rec.get(notice_id) if ID_RE.match(notice_id) else None
        if notice is None:
            raise HTTPException(status_code=404, detail="No such notice in the record.")
        return {
            **_summary(notice, rec.notices),
            "url": notice.url,
            "text": notice.text,  # exact signed text, never reworded
            "signatures": [
                {"reviewer": s.reviewer, "role": s.role, "signed_at": s.signed_at} for s in notice.signatures
            ],
        }

    return app
