import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from .models import Application

logger = logging.getLogger(__name__)


def fine_tuning_job():
    """
    Timed fine-tuning
    :return:
    """
    applications = Application.objects.filter(is_deleted=False, timed_fine_tuning=True)
    for application in applications:
        # TODO: Timed fine-tuning
        pass


@util.close_old_connections
def delete_old_job_executions(max_age=30 * 24 * 60 * 60):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


def parse_cron_expression(cron_expr):
    parts = cron_expr.split()
    if len(parts) != 5:
        raise ValueError("Invalid cron expression. Must have 5 fields.")
    return CronTrigger(minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4])


def run_scheduler():
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        fine_tuning_job,
        trigger=parse_cron_expression("0 0 * * *"),
        id="fine_tuning_job",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'run_fine_tuning_job'.")
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
            day_of_week="mon", hour="00", minute="00"
        ),  # Midnight on Monday, before start of the next work week.
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: 'delete_old_job_executions'.")
    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")
