from django.contrib.auth.models import User


def create_test_user():
    user = User.objects.create_user(
        email='cory@madden.com',
        username='cory@madden.com',
        password='password',
        first_name='Cory',
        last_name='Madden'
    )


def login_test_user(client):
    client.login(username='cory@madden.com', password='password')
