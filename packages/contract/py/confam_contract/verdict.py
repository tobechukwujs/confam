# GENERATED from packages/contract/verdict.schema.json by `pnpm contract:gen`. DO NOT EDIT.

from __future__ import annotations

from datetime import date as date_aliased
from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel


class Verdict1(Enum):
    confirmed = 'confirmed'
    altered = 'altered'
    not_official = 'not_official'
    partial = 'partial'
    cannot_confirm = 'cannot_confirm'


class Reason(Enum):
    unclear = 'unclear'
    not_in_record = 'not_in_record'
    no_fact = 'no_fact'
    line_missing = 'line_missing'
    NoneType_None = None


class Lang(Enum):
    en = 'en'
    pcm = 'pcm'
    ha = 'ha'
    yo = 'yo'
    ig = 'ig'


class Notice(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    published: date_aliased
    url: str = Field(..., min_length=1)


class Op(Enum):
    replace = 'replace'
    insert = 'insert'
    delete = 'delete'


class Kind(Enum):
    date = 'date'
    time = 'time'
    weekday = 'weekday'
    number = 'number'
    money = 'money'
    link = 'link'
    phone = 'phone'
    negation = 'negation'
    text = 'text'


class RecordChange(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    op: Op
    kind: Kind
    official: str | None
    copy_: str | None = Field(..., alias='copy')


class Placement(Enum):
    before_notice = 'before_notice'
    after_notice = 'after_notice'


class BoxItem(RootModel[float]):
    root: float = Field(..., ge=0.0, le=1.0)


class Change(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    op: Op
    kind: Kind
    official: str | None = Field(
        ...,
        description='The official wording. Null for insert (nothing in the record), a string otherwise.',
    )
    copy_: str | None = Field(
        ...,
        alias='copy',
        description="The forwarded copy's wording. Null for delete (nothing in the copy), a string otherwise.",
    )
    placement: Placement | None = Field(
        None,
        description='Only on an insert. Set when the added words sit OUTSIDE the notice itself: after it (a link, amount or phone number added below a genuine notice) or before it. Absent when the change is inside the notice body.',
    )
    box: list[BoxItem] | None = Field(
        None,
        description='Optional position on a photo from OCR: x, y, width, height, each 0 to 1. Absent for pasted text.',
        max_length=4,
        min_length=4,
    )


class Kind2(Enum):
    date = 'date'
    link = 'link'
    money = 'money'


class Conflict(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    kind: Kind2
    copy_: str = Field(..., alias='copy')
    official: str
    quote: str


class SupersededBy(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: str = Field(..., min_length=1)
    published: date_aliased
    url: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    changes: list[RecordChange] = Field(
        ...,
        description='Old notice versus the replacing notice. May be empty when the differences cannot be expressed as facts. No box: these come from record text, not a photo.',
    )


class Verdict(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    code: str = Field(
        ...,
        description='Check code: 8 characters from the alphabet 23456789ABCDEFGHJKMNPQRSTUVWXYZ (no 0, O, 1, I, L). Stored and sent as 8 characters; presentation inserts a hyphen as XXXX-XXXX.',
        pattern='^[23456789ABCDEFGHJKMNPQRSTUVWXYZ]{8}$',
    )
    verdict: Verdict1
    reason: Reason | None = Field(
        ...,
        description='Why the engine cannot confirm. Non-null only when verdict is cannot_confirm, and required then.',
    )
    lang: Lang
    checked_at: AwareDatetime
    record_as_of: AwareDatetime
    notice: Notice | None = Field(
        ...,
        description='The official notice the check was made against. Null only when verdict is cannot_confirm and reason is not_in_record or no_fact, or unclear because OCR read no usable text from a photo (the engine uses unclear with a null notice only then). Otherwise required.',
    )
    superseded_by: SupersededBy | None = Field(
        ...,
        description='Set when the matched notice has been replaced. Only on confirmed; null otherwise.',
    )
    changes: list[Change]
    conflicts: list[Conflict] = Field(
        ...,
        description='Official facts the copy contradicts. Non-empty exactly when verdict is not_official; empty for every other verdict.',
    )
