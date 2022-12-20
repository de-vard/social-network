from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from common.decorators import ajax_required
from actions.utils import create_action

from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile, Contact
from actions.models import Action


# def user_login(request):
#     """Обработчик авторизации"""
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(  # authenticate = сверяет данные в базе данных, если не находит, возвращает None
#                 request,
#                 username=cd['username'],
#                 password=cd['password']
#             )
#             if user is not None:  # Если пользователя есть в БД ...
#                 if user.is_active:  # Если пользователь аутентифицирован
#                     login(request, user)  # авторизуем его на сайте, запоминая его в сессии
#                     return HttpResponse('Authenticated successfully')
#                 else:  # Если пользователь не аутентифицирован
#                     return HttpResponse('Disabled account')
#             else:  # Если пользователя нет в БД ...
#                 return HttpResponse('Invalid login')
#     else:
#         form = LoginForm()
#     return render(request, 'account/login.html', {'form': form})


@login_required  # Проверяет авторизован ли пользователь
def dashboard(request):
    """ Обработчик для отображения стола,
        который пользователь увидит при входе.
        Передает также параметр Next = запрашиваемой страницы
    """
    actions = Action.objects.exclude(user=request.user)  # Действия всех пользователей, кроме текущего
    following_ids = request.user.following.values_list('id', flat=True)  # По умолчанию отображаем последние события
    # всех пользователей системы
    if following_ids:  # Если текущий пользователь подписался на кого-то
        actions = actions.filter(user_id__in=following_ids)  # отображаем только действия этих пользователей
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')[:10]  # prefetch_related
    # И select_related=для оптимизации кода. Показываем 10 записей
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard', 'actions': actions}
        # section = узнаем какой раздел сайта сейчас просматривает пользователь
    )


def register(request):
    """Регистрация"""
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)  # Создаем нового пользователя, но пока не сохраняем в базу данных.
            new_user.set_password(user_form.cleaned_data['password'])  # Задаем пользователю зашифрованный пароль.
            new_user.save()  # Сохраняем пользователя в базе данных.
            Profile.objects.create(user=new_user)  # Связываем пользователя при регистрации с моделью пользователя
            # которую мы создали
            create_action(new_user, 'has created an account')  # используем свою же написанную функцию для
            # создания действия пользователя, что бы отобразить действие в новостной ленте
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required  # Проверяет авторизован ли пользователь
def edit(request):
    """ Редактирование профиля"""
    if request.method == "POST":
        user_form = UserEditForm(
            instance=request.user,  # instance = хранит обрабатываемую запись, для ее редактирования
            data=request.POST,  # data — словарь с данными, занесенными в форму посетителем
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,  # instance = хранит обрабатываемую запись, для ее редактирования
            data=request.POST,  # data — словарь с данными, занесенными в форму посетителем
            files=request.FILES  # files — словарь с файлами, отправленными посетителем из формы
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')  # при удачном сохранении выводим сообщение,
            # используя Django уведомления
        else:  # при не удачном сохранении выводим сообщение, используя Django уведомления
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(
            instance=request.user)  # instance = хранит обрабатываемую запись
        profile_form = ProfileEditForm(instance=request.user.profile)  # instance = хранит обрабатываемую запись
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required  # Проверяет авторизован ли пользователь
def user_list(request):
    """Просмотр всех активных пользователей"""
    users = User.objects.filter(is_active=True)  # Получаем все активных пользователей
    return render(
        request,
        'account/user/list.html',
        {'section': 'people', 'users': users}
    )


@login_required  # Проверяет авторизован ли пользователь
def user_detail(request, username):
    """Промотер пользователя"""
    user = get_object_or_404(User, username=username, is_active=True)  # Получаем пользователя
    return render(
        request,
        'account/user/detail.html',
        {'section': 'people', 'user': user}
    )


@ajax_required  # декоратор проверяет, является ли запрос запросом AJAX
@require_POST  # Принимает только метод POST
@login_required  # Проверяет авторизован ли пользователь
def user_follow(request):
    """ Обработчик, который добавляет и
        удаляет пользователей из подписок
    """
    user_id = request.POST.get('id')  # Получаем из запроса id пользователя
    action = request.POST.get('action')  # Получаем из запроса действие которое он делает
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)  # Получаем пользователя
            if action == "follow":  # Если действие подписка
                Contact.objects.get_or_create(user_from=request.user, user_to=user)  # подписываемся на пользователя
                create_action(request.user, 'is following', user)  # используем свою же написанную функцию для
            # создания действия пользователя, что бы отобразить действие в новостной ленте
            else:  # Если действие отписка
                Contact.objects.filter(user_from=request.user, user_to=user).delete()  # отписываемся от пользователя
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'ok'})
