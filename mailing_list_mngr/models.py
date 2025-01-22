from django.db import models

from users.models import User


class Recipient(models.Model):
    email = models.EmailField(unique=True,
                              verbose_name="Email")
    name = models.CharField(
        max_length=150,
        verbose_name="ФИО получателя письма",
        help_text="",
        blank=True,
        null=True
    )
    comments = models.TextField(
        verbose_name="Комментарий",
        help_text="",
        blank=True,
        null=True
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="",
    )

    class Meta:
        verbose_name = "Получатель письма"
        verbose_name_plural = "Получатели писем"

    def __str__(self):
        return self.email


class Message(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Тема письма",
        help_text=""
    )
    body = models.TextField(
        verbose_name="Текст письма",
        help_text="",
        blank=True,
        null=True
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="",
    )

    class Meta:
        verbose_name = "Письмо"
        verbose_name_plural = "Письма"

    def __str__(self):
        return self.name


class MailingList(models.Model):
    header = models.CharField(
        max_length=50,
        verbose_name="Заголовок",
        help_text=""
    )
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время начала отправки",
        help_text="формат d.m.Y H:M"
    )
    finished_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время окончания отправки",
        help_text="формат d.m.Y H:M"
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Статус рассылки",
        help_text="",
        blank=True,
        null=True
    )
    message = models.ForeignKey(
        Message,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Сообщение рассылки",
        help_text="",
    )
    recipients = models.ManyToManyField(
        Recipient,
        blank=True,
        verbose_name="Получатели рассылки",
        help_text="",
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        help_text="",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [('can_stop_mailingList', 'can stop mailingList'),
                       ('can_send_mailingList', 'can send mailingList'), ]

    def __str__(self):
        return self.header


class AttemptToSend(models.Model):
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ сервера",
        help_text=""
    )
    started_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата и время попытки",
        help_text=""
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Статус попытки рассылки",
        help_text="",
        blank=True,
        null=True
    )
    mailing_list = models.ForeignKey(
        MailingList,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Рассылка",
        help_text=""
    )
    recipient = models.ForeignKey(
        Recipient,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Получатель письма",
        help_text="",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"

    def __str__(self):
        return f'{self.started_at}: {self.mailing_list}'
