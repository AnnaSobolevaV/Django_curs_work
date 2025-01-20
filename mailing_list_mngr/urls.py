from mailing_list_mngr.apps import MailingListMngrConfig
from django.urls import path

from mailing_list_mngr.views import MailingListView, MailingListDetailView, MailingListCreateView, \
    MailingListUpdateView, MailingListDeleteView, AttemptToSendListView, MessageListView, MessageDetailView, \
    MessageCreateView, MessageUpdateView, MessageDeleteView, RecipientListView, RecipientDetailView, \
    RecipientCreateView, RecipientUpdateView, RecipientDeleteView, mailing_list_sending, mailing_list_stop

app_name = MailingListMngrConfig.name

urlpatterns = [
    path('', AttemptToSendListView.as_view(), name="home"),
    path('mailing_list/', MailingListView.as_view(), name="mailing_list"),
    path('mailing_list/<int:pk>', MailingListDetailView.as_view(), name='mailing_list_detail'),
    path('mailing_list/create', MailingListCreateView.as_view(), name="mailing_list_create"),
    path('mailing_list/<int:pk>/update/', MailingListUpdateView.as_view(), name="mailing_list_update"),
    path('mailing_list/<int:pk>/delete/', MailingListDeleteView.as_view(), name="mailing_list_delete"),
    path('mailing_list_sending/<int:id_>/', mailing_list_sending, name="mailing_list_sending"),
    path('mailing_list_stop/<int:id_>/', mailing_list_stop, name="mailing_list_stop"),
    path('recipients/', RecipientListView.as_view(), name="recipients"),
    path('recipients/<int:pk>', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/create', RecipientCreateView.as_view(), name="recipient_create"),
    path('recipients/<int:pk>/update/', RecipientUpdateView.as_view(), name="recipient_update"),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name="recipient_delete"),
    path('messages/', MessageListView.as_view(), name="messages"),
    path('messages/<int:pk>', MessageDetailView.as_view(), name='message_detail'),
    path('messages/create', MessageCreateView.as_view(), name="message_create"),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name="message_update"),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name="message_delete"),
]
