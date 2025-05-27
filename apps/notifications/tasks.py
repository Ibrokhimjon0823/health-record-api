from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
)
def send_notification_email(self, notification_id):
    notification = Notification.objects.get(id=notification_id)
    send_mail(
        f"Health Record Notification - {notification.get_notification_type_display()}",
        notification.message,
        settings.DEFAULT_FROM_EMAIL,
        [notification.recipient.email],
    )
