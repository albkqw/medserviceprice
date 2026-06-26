import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.scheduler.jobs import run_parser

logger = logging.getLogger(__name__)

# Singleton — imported and started in main.py lifespan
scheduler = AsyncIOScheduler(timezone="Asia/Almaty")

# (source_slug, hour, minute)
_JOBS = [
    ("kdl",     2, 0),
    ("invitro", 3, 0),
    ("doq",     4, 0),
]


def setup_scheduler() -> None:
    for slug, hour, minute in _JOBS:
        scheduler.add_job(
            run_parser,
            trigger=CronTrigger(hour=hour, minute=minute, timezone="Asia/Almaty"),
            args=[slug],
            id=f"parse_{slug}",
            name=f"Parse {slug}",
            replace_existing=True,
            misfire_grace_time=3600,  # run even if up to 1h late
        )
        logger.info("Scheduled parser '%s' at %02d:%02d Asia/Almaty", slug, hour, minute)
