from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RECORD_PATH = REPO_ROOT / "fixtures" / "sec-sim" / "notices.json"


def _flag(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _optional_float(value: str | None) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...] = ()
    seed_samples: bool = False
    rate_limit_per_minute: int = 30
    photo_workers: int = 1  # one picture at a time keeps memory small on a free host
    # Confidence gate for photo checks (0-100). None = the engine default, which is 95 (gate ON).
    # CONFAM_MIN_WORD_CONFIDENCE=off switches the gate off (confidence_gate_off).
    min_word_confidence: float | None = None
    confidence_gate_off: bool = False
    ip_salt: str = "dev-only-salt-change-me"
    record_path: Path = field(default=DEFAULT_RECORD_PATH)

    @classmethod
    def from_env(cls) -> "Settings":
        origins = tuple(
            o.strip().rstrip("/")
            for o in os.environ.get("CONFAM_CORS_ORIGINS", "http://localhost:3000").split(",")
            if o.strip()
        )
        return cls(
            cors_origins=origins,
            seed_samples=_flag(os.environ.get("CONFAM_SEED_SAMPLES"), False),
            rate_limit_per_minute=int(os.environ.get("CONFAM_RATE_LIMIT_PER_MINUTE", "30")),
            photo_workers=int(os.environ.get("CONFAM_PHOTO_WORKERS", "1")),
            min_word_confidence=_optional_float(os.environ.get("CONFAM_MIN_WORD_CONFIDENCE")),
            confidence_gate_off=(os.environ.get("CONFAM_MIN_WORD_CONFIDENCE") or "").strip().lower() in {"off", "none", "false"},
            ip_salt=os.environ.get("CONFAM_IP_SALT", cls.ip_salt),
            record_path=Path(os.environ.get("CONFAM_RECORD_PATH", str(DEFAULT_RECORD_PATH))),
        )
