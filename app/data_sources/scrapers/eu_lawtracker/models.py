

# eu_law_tracker/models.py
from __future__ import annotations
import datetime as _dt
from sqlalchemy import (
    Column, String, Text, Date, DateTime,
    ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

topic_laws = Table(
    "topic_laws", Base.metadata,
    Column("topic_code", String, ForeignKey("topics.code"), primary_key=True),
    Column("law_id",     String, ForeignKey("laws.procedure_id"), primary_key=True),
    Column("first_seen", DateTime, default=_dt.datetime.utcnow, nullable=False),
    Column("last_seen",  DateTime, default=_dt.datetime.utcnow, nullable=False),
)

class Topic(Base):
    __tablename__ = "topics"
    code = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url  = Column(Text,   nullable=False)
    laws = relationship("Law", secondary=topic_laws, back_populates="topics")

class Law(Base):
    __tablename__ = "laws"
    procedure_id    = Column(String, primary_key=True)  # 2025/0090(COD)
    title           = Column(Text, nullable=False)
    status          = Column(String, nullable=False)
    started_date    = Column(Date)
    summary         = Column(Text)
    last_stage_date = Column(Date)
    committees      = Column(Text)
    content_hash    = Column(String, nullable=False)
    scraped_at      = Column(DateTime, default=_dt.datetime.utcnow, nullable=False)
    topics          = relationship("Topic", secondary=topic_laws, back_populates="laws")
    __table_args__  = (UniqueConstraint("procedure_id", name="uq_laws_procedure"),)






