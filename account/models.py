from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model):
    """
        Расширяем модель пользователя
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user/%Y/%m/%d/', blank=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'


class Contact(models.Model):
    """ Модель для связи пользователей
        Промежуточная модель.
    """
    user_from = models.ForeignKey(
        'auth.User',
        related_name='rel_from_set',
        on_delete=models.CASCADE,
        verbose_name='Пользователь который подписался'
    )
    user_to = models.ForeignKey(
        'auth.User',
        related_name='rel_to_set',
        on_delete=models.CASCADE,
        verbose_name='Пользователь на которого  подписались'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Время создания связи'
    )

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


User.add_to_class(  # Динамическое добавление поля following в модель User
    'following',
    models.ManyToManyField(
        'self',  # указываем ссылку на self, чтобы она указывала на текущую модель
        through=Contact,  # использовать заданную явно промежуточную модель
        related_name='followers',
        symmetrical=False)  # не создавать симметричные отношение, (если вы подпишетесь на меня, я не буду
    # автоматически добавлен в список ваших подписчиков)
)
