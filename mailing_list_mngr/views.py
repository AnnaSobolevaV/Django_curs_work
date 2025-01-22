import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Count, Sum
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from config.settings import EMAIL_HOST_USER
from mailing_list_mngr.forms import MessageForm, RecipientForm, MailingListForm
from mailing_list_mngr.models import MailingList, AttemptToSend, Message, Recipient


class AttemptToSendListView(LoginRequiredMixin, ListView):
    model = AttemptToSend
    success_url = reverse_lazy("mailing_list_mngr:home")

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        user = self.request.user
        if user.is_authenticated:
            if user.has_perm('mailing_list_mngr.view_attempttosend'):
                context_data['total_recipients'] = Recipient.objects.all().aggregate(total=Count('id'))
                context_data['total_mailing_list'] = MailingList.objects.all().aggregate(total=Count('id'))
                context_data['total_mailing_list_started'] = MailingList.objects.filter(status='Запущена').aggregate(
                    total=Count('id'))
                context_data['total_attempts'] = AttemptToSend.objects.all().aggregate(total=Count('id'))

            else:
                context_data['total_recipients'] = Recipient.objects.filter(owner=user).aggregate(total=Count('id'))
                context_data['total_mailing_list'] = MailingList.objects.filter(owner=user).aggregate(total=Count('id'))
                context_data['total_mailing_list_started'] = MailingList.objects.filter(owner=user,
                                                                                        status='Запущена').aggregate(
                    total=Count('id'))
                context_data['total_attempts'] = AttemptToSend.objects.filter(mailing_list__owner=user).aggregate(
                    total=Count('id'))
        return context_data

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated:
            if not user.has_perm('mailing_list_mngr.view_attempttosend'):
                queryset = queryset.filter(mailing_list__owner=user)
        return queryset


class MailingListView(LoginRequiredMixin, ListView):
    model = MailingList
    success_url = reverse_lazy("mailing_list_mngr:mailing_list")

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset()
        user = self.request.user
        started_at = datetime.datetime.now()
        current_date = started_at.strftime("%Y-%m-%d %H:%M:%S")
        if user.is_authenticated:
            if not user.has_perm('mailing_list_mngr.view_mailinglist'):
                queryset = queryset.filter(owner=user)
                mailing_lists = queryset.filter(status__in=("Создана", "Запущена"))
                for mailing_list in mailing_lists:
                    mailing_list_finished_at = mailing_list.finished_at.strftime("%Y-%m-%d %H:%M:%S")
                    if mailing_list_finished_at < current_date:
                        mailing_list.status = "Завершена"
                        mailing_list.save()

        return queryset


def mailing_list_stop(request, id_):
    user = request.user
    if user.is_authenticated and user.has_perm('mailing_list_mngr.can_stop_mailingList'):
        mailing_list_stopped = get_object_or_404(MailingList, id=id_)
        mailing_list_stopped.status = "Завершена"
        mailing_list_stopped.save()
    return redirect(reverse("mailing_list_mngr:mailing_list"))


def mailing_list_sending(request, id_):
    user = request.user
    if user.is_authenticated:
        recipients = MailingList.objects.get(id=id_).recipients.all()
        mailing_list = MailingList.objects.get(id=id_)
        if mailing_list.owner == user or user.has_perm('mailing_list_mngr.can_send_mailingList'):
            started_at = datetime.datetime.now()
            current_date = started_at.strftime("%Y-%m-%d %H:%M:%S")
            mailing_list_started_at = mailing_list.started_at.strftime("%Y-%m-%d %H:%M:%S")
            mailing_list_finished_at = mailing_list.finished_at.strftime("%Y-%m-%d %H:%M:%S")
            if mailing_list_started_at < current_date < mailing_list_finished_at:
                if mailing_list.status == "Создана" or mailing_list.status == "Запущена":
                    for recipient in recipients:
                        try:
                            send_mail(subject=mailing_list.message.name,
                                      message=mailing_list.message.body,
                                      from_email=EMAIL_HOST_USER,
                                      recipient_list=[recipient], )
                            attempt = AttemptToSend(server_response='ok', started_at=started_at,
                                                    status='Успешно', mailing_list=mailing_list, recipient=recipient)
                            attempt.save()
                            mailing_list.status = "Запущена"
                            mailing_list.save()
                        except Exception as ex:
                            print('mailing_list_sending error: ', ex)
                            attempt = AttemptToSend(server_response=ex, started_at=started_at,
                                                    status='Не успешно', mailing_list=mailing_list, recipient=recipient)
                            attempt.save()
            else:
                return HttpResponseBadRequest(
                    f"Нет возможности отправить рассылку. Дата отправки рассылки вне диапазона: {mailing_list_started_at} - {mailing_list_finished_at} ")
    return redirect(reverse("mailing_list_mngr:mailing_list"))


class MailingListDetailView(LoginRequiredMixin, DetailView):
    model = MailingList
    form_class = MailingListForm
    success_url = reverse_lazy("mailing_list_mngr:mailing_list")

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['start_date_ok'] = False
        user = self.request.user
        if user.is_authenticated:
            mailing_list = context_data['object']
            recipients = mailing_list.recipients.all()
            context_data['recipients'] = recipients
            started_at = datetime.datetime.now()
            current_date = started_at.strftime("%Y-%m-%d %H:%M:%S")
            mailing_list_started_at = mailing_list.started_at.strftime("%Y-%m-%d %H:%M:%S")
            mailing_list_finished_at = mailing_list.finished_at.strftime("%Y-%m-%d %H:%M:%S")
            if mailing_list_started_at < current_date:
                if current_date < mailing_list_finished_at:
                    context_data['start_date_ok'] = True
                else:
                    if mailing_list.status == "Создана" or mailing_list.status == "Запущена":
                        mailing_list.status = "Завершена"
                        mailing_list.save()
        return context_data


class MailingListCreateView(LoginRequiredMixin, CreateView):
    model = MailingList
    form_class = MailingListForm
    success_url = reverse_lazy("mailing_list_mngr:mailing_list")

    def form_valid(self, form):
        context_data = self.get_context_data()
        if form.is_valid():
            self.object = form.save()
            user = self.request.user
            self.object.owner = user
            return super().form_valid(form)
        else:
            return self.render_to_response(context_data)


class MailingListUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingList
    form_class = MailingListForm
    success_url = reverse_lazy("mailing_list_mngr:mailing_list")


class MailingListDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingList
    success_url = reverse_lazy("mailing_list_mngr:mailing_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    success_url = reverse_lazy("mailing_list_mngr:home")

    def get_queryset(self, *args, **kwargs):
        queryset = cache.get('message_list_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('message_list_queryset', queryset, 60 * 15)  # Кешируем данные на 15 минут
        user = self.request.user
        if user.is_authenticated:
            if not user.has_perm('mailing_list_mngr.view_message'):
                queryset = queryset.filter(owner=user)
        return queryset


@method_decorator(cache_page(60 * 15), name='dispatch')
class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing_list_mngr:messages")


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing_list_mngr:messages")

    def form_valid(self, form):
        context_data = self.get_context_data()
        if form.is_valid():
            self.object = form.save()
            user = self.request.user
            self.object.owner = user
            return super().form_valid(form)
        else:
            return self.render_to_response(context_data)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing_list_mngr:messages")


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailing_list_mngr:messages")


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    success_url = reverse_lazy("mailing_list_mngr:home")

    def get_queryset(self, *args, **kwargs):
        queryset = cache.get('recipient_list_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('recipient_list_queryset', queryset, 60 * 15)  # Кешируем данные на 15 минут
        user = self.request.user
        if user.is_authenticated:
            if not user.has_perm('mailing_list_mngr.view_recipient'):
                queryset = queryset.filter(owner=user)
        return queryset


@method_decorator(cache_page(60 * 15), name='dispatch')
class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing_list_mngr:recipients")


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing_list_mngr:recipients")

    def form_valid(self, form):
        context_data = self.get_context_data()
        if form.is_valid():
            self.object = form.save()
            user = self.request.user
            self.object.owner = user
            return super().form_valid(form)
        else:
            return self.render_to_response(context_data)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing_list_mngr:recipients")


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    success_url = reverse_lazy("mailing_list_mngr:recipients")
