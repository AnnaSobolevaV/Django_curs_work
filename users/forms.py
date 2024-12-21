from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.forms import BooleanField, ModelForm
from django.shortcuts import get_object_or_404
from django import forms

from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2",)


class MyPasswordResetForm(StyleFormMixin, PasswordResetForm):
    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data['email']
        try:
            get_object_or_404(User, email=email)
        except Exception as ex:
            raise forms.ValidationError(f'этот email не зарегистрирован: {email}')
        return email
