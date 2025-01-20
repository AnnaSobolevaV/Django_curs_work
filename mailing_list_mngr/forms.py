from django import forms
from django.forms import ModelForm

from mailing_list_mngr.models import MailingList, AttemptToSend, Message, Recipient

STATUSES = {
    "Завершена": "Завершена",
    "Создана": "Создана",
    "Запущена": "Запущена",
}


class AttemptToSendForm(ModelForm):
    class Meta:
        model = AttemptToSend
        fields = '__all__'


class MailingListForm(ModelForm):
    status = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect,
        choices=STATUSES,
    )

    started_at = forms.DateTimeField(
        widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M'),
        input_formats=('%d.%m.%Y %H:%M',)
    )

    finished_at = forms.DateTimeField(
        widget=forms.DateTimeInput(format='%d.%m.%Y %H:%M'),
        input_formats=('%d.%m.%Y %H:%M',)
    )

    class Meta:
        model = MailingList
        fields = '__all__'
        exclude = ("owner",)


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ("owner",)


class RecipientForm(ModelForm):
    class Meta:
        model = Recipient
        fields = '__all__'
        exclude = ("owner",)
