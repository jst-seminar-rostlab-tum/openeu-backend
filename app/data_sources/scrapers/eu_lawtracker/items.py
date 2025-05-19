# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html



# eu_law_tracker/items.py
from __future__ import annotations
import datetime as _dt
from dataclasses import dataclass, field
import scrapy


@dataclass
class TopicItem:
    code: str         # e.g. "16_DOM"
    name: str         # e.g. "Economics"
    url: str
    scraped_at: _dt.datetime = field(default_factory=_dt.datetime.utcnow)

@dataclass
#class EuLawtrackerItem:
class LawItem:

    # define the fields for your item here like:
    # name = scrapy.Field()
    procedure_id: str                   # "2025/0090(COD)"
    title: str
    status: str
    started_dt: str | None
    summary: str | None = None
    last_stage_date: str | None = None  # ISO-date from <time datetime="">
    committees: list[str] | None = None
    topic_codes: list[str] = field(default_factory=list)
    scraped_at: _dt.datetime = field(default_factory=_dt.datetime.utcnow)

