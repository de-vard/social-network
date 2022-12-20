from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
import redis
from django.conf import settings

from .models import Image
from .forms import ImageCreateForm

# создаем постоянное соединение с Redis, чтобы использовать его в обработчиках, а не открывать каждый раз
r = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)  # передаем данные в форму
        if form.is_valid():
            cd = form.cleaned_data

            new_item = form.save(commit=False)  # создаем объект, но не сохраняем

            new_item.user = request.user  # привязывает текущего пользователя к картинке
            new_item.save()  # сохраняем
            create_action(request.user, 'bookmarked image', new_item)  # используем свою же написанную функцию для
            # создания действия пользователя, что бы отобразить действие в новостной ленте
            messages.success(request, 'Image added successfiully')  # создаем уведомление

            return redirect(new_item.get_absolute_url())  # перенаправляет пользователя на url новой картинки
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html', {'section': 'images', 'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr(f'image:{image.id}:views')  # Увеличиваем количество просмотров картинки на 1.
    r.zincrby('image_ranking', image.id, 1)  # Увеличиваем рейтинг картинки на 1.
    return render(
        request,
        'images/image/detail.html',
        {'section': 'images', 'image': image, 'total_views': total_views}
    )


@ajax_required  # написанный нами декоратор если не ajax запрос генерит ошибку 400
@login_required  # проверка авторизован ли пользователь
@require_POST  # возвращает ответ 405, если запрос отправлен не методом POST
def image_like(request):
    """Функция для обработки лайков"""
    image_id = request.POST.get('id')  # получаем ID изображение
    action = request.POST.get('action')  # строковое действие которое хочет использовать пользователь (like или unlike)
    if image_id and action:  # если есть id и изображение ...
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)  # добавление лайков, что бы не создавался дубликат user_like.add
                create_action(request.user, 'likes', image)  # используем свою же написанную функцию для
            # создания действия пользователя, что бы отобразить действие в новостной ленте
            else:
                image.users_like.remove(request.user)  # удаление лайков
            return JsonResponse({'status': 'ok'})  # преобразовывает ответ в Json
        except:
            pass
    return JsonResponse({'status': 'ok'})  # преобразовывает ответ в Json


def is_ajax(request):
    """Пре определил метод так как он устарел"""
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
def image_list(request):
    """ Пост граничная навигация
        При прокрутке до конца списка
         будут проявляться еще 8 фото
    """
    images = Image.objects.all()
    paginator = Paginator(images, 8)  # показываем 8 записей за раз
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:  # Если страницы не существует ...
        if is_ajax(request):
            return HttpResponse('')  # Отправляем в ajax пустую строку, что бы остановить пагинацию
        images = paginator.page(paginator.num_pages)
    if is_ajax(request=request):
        return render(request, 'images/image/list_ajax.html', {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html', {'section': 'images', 'images': images})


@login_required
def image_ranking(request):
    """ Обработчик, который добавит на сайт блок
        с самыми просматриваемыми картинками
     """
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]  # используем метод zrange() для доступа к

    # нескольким элементам сортированного списка.
    image_ranking_ids = [int(id) for id in image_ranking]  # сохраняем идентификаторы нужных картинок в списке
    # image_ranking_ids
    most_viewed = list(Image.objects.filter(
        id__in=image_ranking_ids))  # Получаем картинки, в списке
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))  # Сортируем

    return render(
        request,
        'images/image/ranking.html',
        {'section': 'images', 'most_viewed': most_viewed}

    )
