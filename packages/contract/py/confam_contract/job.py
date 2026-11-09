# GENERATED from packages/contract/job.schema.json by `pnpm contract:gen`. DO NOT EDIT.

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Status(Enum):
    working = 'working'
    done = 'done'
    failed = 'failed'


class Stage(Enum):
    queued = 'queued'
    reading_1 = 'reading_1'
    reading_2 = 'reading_2'
    comparing = 'comparing'
    done = 'done'
    failed = 'failed'


class Job(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    job_id: str = Field(..., pattern='^[A-Za-z0-9_-]{16,64}$')
    status: Status
    stage: Stage
    code: str | None = Field(
        ...,
        description='The check code (8 characters, no hyphen). Present only when status is done.',
        pattern='^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$',
    )
