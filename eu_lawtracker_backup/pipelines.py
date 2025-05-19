
# eu_law_tracker/pipelines.py
import hashlib, logging, datetime as _dt
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker
)
from eu_lawtracker.models import Base, Topic, Law, topic_laws
from eu_lawtracker.items  import TopicItem, LawItem

log = logging.getLogger(JMK_Law_tracker)

class SQLPipeline:
    def __init__(self, database_url: str):
        self._engine  = create_async_engine(database_url, future=True)
        self._Session = async_sessionmaker(self._engine, expire_on_commit=False)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(database_url=crawler.settings["-------DATABASE_URL---------!!!!"])

    async def open_spider(self, spider):
        # ensure metadata is created (dev convenience – prod uses Alembic)
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def process_item(self, item, spider):
        async with self._Session() as session:
            if isinstance(item, TopicItem):
                await self._upsert_topic(session, item)
            else:
                await self._upsert_law(session, item)
            await session.commit()
        return item

    async def _upsert_topic(self, session, it: TopicItem):
        stmt = insert(Topic).values(**it.__dict__).on_conflict_do_update(
            index_elements=[Topic.code],
            set_={"name": it.name, "url": it.url}
        )
        await session.execute(stmt)

    async def _upsert_law(self, session, it: LawItem):
        hash_ = hashlib.sha256(
            f"{it.title}{it.status}{it.summary}".encode()
        ).hexdigest()
        law_vals = dict(
            procedure_id=it.procedure_id,
            title=it.title, status=it.status, summary=it.summary,
            started=it.started, last_stage_date=it.last_stage_date,
            committees="; ".join(it.committees or []),
            content_hash=hash_, scraped_at=_dt.datetime.utcnow()
        )
        stmt = insert(Law).values(**law_vals).on_conflict_do_update(
            index_elements=[Law.procedure_id],
            set_={k: law_vals[k] for k in law_vals if k != "procedure_id"}
        )
        await session.execute(stmt)
        # keep junctions fresh
        for code in it.topic_codes:
            up = insert(topic_laws).values(
                topic_code=code, law_id=it.procedure_id,
                first_seen=_dt.datetime.utcnow(), last_seen=_dt.datetime.utcnow()
            ).on_conflict_do_update(
                index_elements=["topic_code", "law_id"],
                set_={"last_seen": _dt.datetime.utcnow()}
            )
            await session.execute(up)





