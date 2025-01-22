from django.contrib.auth.views import LogoutView
from django.urls import path

from users.apps import UsersConfig
from users.views import LoginView, RegistrationView, email_confirm, PasswordResetView, UserListView, user_is_active_chng

app_name = UsersConfig.name

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('email_confirm/<str:token>/', email_confirm, name='email_confirm'),
    path('user_is_active_chng/<str:id_>', user_is_active_chng, name='user_is_active_chng'),
    path('users/', UserListView.as_view(), name="users"),

]
