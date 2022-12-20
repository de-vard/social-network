import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


def create_action(user, verb, target=None):
    """ Позволяет создавать активность пользователей
        и связывать ее объектом target
    """
    now = timezone.now()  # получаем текущую дату и время
    last_minute = now - datetime.timedelta(seconds=60)  # отнимаем минуту
    similar_actions = Action.objects.filter(  # Получаем активность пользователя за последнею минуту
        user_id=user.id,
        verb=verb,
        created__gte=last_minute
    )
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_ct=target_ct, target_id=target.id)
    if not similar_actions:  # если за последнюю минуту не найдено, создаем новый объект Action
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False  # мы ничего не создаем
