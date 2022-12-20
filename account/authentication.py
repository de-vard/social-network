from django.contrib.auth.models import User


class EmailAuthBackend(object):
    """Выполняет аутентификацию пользователя по e-mail."""

    def authenticate (self, request, username=None, password=None):
        """Пытается получить пользователя"""
        try:
            user = User.objects.get(email=username)
            if user.check_password(
                    password):  # check_password выпол. Шифрование пароля и сравнивает с тем, который в БД
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        """Получает пользователя по ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
