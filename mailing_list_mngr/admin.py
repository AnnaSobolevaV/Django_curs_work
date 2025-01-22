from mailing_list_mngr.models import MailingList, Message, Recipient
from django.contrib import admin


@admin.register(MailingList)
class MailingListAdmin(admin.ModelAdmin):
    list_display = ('header', 'started_at', 'finished_at', 'status', 'message', 'owner')
    list_filter = ('owner',)
    search_fields = ('header', 'message')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner')
    list_filter = ('name', 'owner')
    search_fields = ('name',)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'comments', 'owner')
    list_filter = ('name',)
    search_fields = ('name', 'phone',)
