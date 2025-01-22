from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin_curs6@mail.pro',
            first_name='Admin',
            last_name='curs6_work',
            is_staff=True,
            is_active=True,
            is_superuser=True
        )

        user.set_password('superuser_pass')
        user.save()
