"""In-memory photo-check jobs.

Rule 7: the uploaded picture lives only inside a Job object, in memory, until the job ends; then
it is dropped. It is never written to disk and never put in the store. Jobs expire after minutes.
TODO(ARCHITECTURE.md): move to Redis + the RQ worker. `JobManager` is the seam: it takes a
`process` function and owns the state, so a queue can replace the thread pool.
"""

from __future__ import annotations

import secrets
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

JOB_TTL_SECONDS = 600

# process(image_bytes, lang, set_stage) -> check code. It reports the real stage it is on.
Process = Callable[[bytes, str, Callable[[str], None]], str]


@dataclass
class Job:
    job_id: str
    lang: str
    created: float
    status: str = "working"  # working | done | failed
    stage: str = "queued"  # queued | reading_1 | reading_2 | comparing | done | failed
    code: str | None = None
    image: bytes | None = None  # dropped as soon as the job ends


class JobManager:
    def __init__(self, process: Process, workers: int = 1, ttl: float = JOB_TTL_SECONDS) -> None:
        self._process = process
        self._ttl = ttl
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="photo-check")

    def submit(self, image: bytes, lang: str) -> str:
        job = Job(job_id=secrets.token_urlsafe(16), lang=lang, created=time.monotonic(), image=image)
        with self._lock:
            self._jobs[job.job_id] = job
        self._pool.submit(self._run, job)
        return job.job_id

    def _set(self, job: Job, stage: str) -> None:
        with self._lock:
            if job.status == "working":
                job.stage = stage

    def _run(self, job: Job) -> None:
        try:
            data = job.image or b""
            code = self._process(data, job.lang, lambda stage: self._set(job, stage))
            with self._lock:
                job.status, job.stage, job.code = "done", "done", code
        except Exception:  # never leak internals; the web shows a plain message
            with self._lock:
                job.status, job.stage, job.code = "failed", "failed", None
        finally:
            with self._lock:
                job.image = None  # rule 7: drop the picture

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            return {"job_id": job.job_id, "status": job.status, "stage": job.stage, "code": job.code}

    def expire_all(self, now: float | None = None) -> int:
        now = time.monotonic() if now is None else now
        with self._lock:
            gone = [j for j, job in self._jobs.items() if now - job.created > self._ttl and job.status != "working"]
            for j in gone:
                del self._jobs[j]
            return len(gone)

    def dump(self) -> list[dict]:
        """What is held, for tests that prove no picture is kept."""
        with self._lock:
            return [
                {"job_id": j.job_id, "status": j.status, "stage": j.stage, "code": j.code, "has_image": j.image is not None}
                for j in self._jobs.values()
            ]
