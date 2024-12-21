import random
import secrets

from django.contrib.auth.views import LoginView as BaseLoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, FormView

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, MyPasswordResetForm
from users.models import User


class LoginView(BaseLoginView):
    template_name = 'users/login.html'


def new_password_creator():
    random_password = []
    alphabet = [chr(i) for i in range(97, 123)]
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    symbols = ['!', '@', '#', '$', '%']
    random.shuffle(numbers)
    random.shuffle(alphabet)
    random_symbol = random.choice(symbols)
    random_password.extend(alphabet[:4])
    random_password.extend(numbers[:4])
    random_password.extend(random_symbol)
    password_str = ''
    for item in random_password:
        password_str += str(item)
    return password_str.title()


class PasswordResetView(FormView):
    model = User
    form_class = MyPasswordResetForm
    template_name = 'users/password_reset_form.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        form = self.get_form()
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_object_or_404(User, email=email)
            new_password_send(user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


def new_password_send(user):
    new_password_str = new_password_creator()
    user.set_password(new_password_str)
    user.save()
    try:
        send_mail(subject='Восстановление пароля',
                  message=f'Новый пароль: {new_password_str}',
                  from_email=EMAIL_HOST_USER,
                  recipient_list=[user.email], )

    except Exception as ex:
        print('ошибка Восстановления пароля - письмо не отправлено', ex)

    return redirect(reverse("users:login"))


def email_confirm(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class RegistrationView(CreateView):
    model = User
    template_name = 'users/user_register_form.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email_confirm/{token}/'
        try:
            send_mail(subject='Подтверждение почты',
                      message=f'Перейдите по ссылке: {url}',
                      from_email=EMAIL_HOST_USER,
                      recipient_list=[user.email], )
        except Exception as ex:
            print('ошибка ', ex)
        return super().form_valid(form)
