import datetime

from django.core.mail import send_mail
from django.core.management import BaseCommand

from config.settings import EMAIL_HOST_USER
from mailing_list_mngr.models import MailingList, AttemptToSend


class Command(BaseCommand):

    def handle(self, *args, **options):

        mailing_list = MailingList.objects.filter(status__in=("Запущена", "Создана"))
        for mail in mailing_list:
            started_at = datetime.datetime.now()
            if mail.started_at.strftime("%Y-%m-%d %H:%M:%S") < started_at.strftime(
                    "%Y-%m-%d %H:%M:%S") < mail.finished_at.strftime("%Y-%m-%d %H:%M:%S"):
                recipients = mail.recipients.all()
                for recipient in recipients:
                    try:
                        send_mail(subject=mail.message.name,
                                  message=mail.message.body,
                                  from_email=EMAIL_HOST_USER,
                                  recipient_list=[recipient], )
                        attempt = AttemptToSend(server_response='ok', started_at=started_at,
                                                status='Успешно', mailing_list=mail,
                                                recipient=recipient)
                        attempt.save()
                        mail.status = "Запущена"
                        mail.save()
                    except Exception as ex:
                        print('error: ', ex)
                        attempt = AttemptToSend(server_response=ex, started_at=started_at,
                                                status='Не успешно', mailing_list=mail,
                                                recipient=recipient)
                        attempt.save()
