from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserEditForm(forms.ModelForm):
    """ Редактирование полей пользователя,
        которые есть по умолчанию в Django
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    """ Редактирование полей пользователя,
        которые мы добавили пользователю
    """
    class Meta:
        model = Profile
        fields = ('date_of_birth', 'photo')


class LoginForm(forms.Form):
    """
        Форма входа
        Не использую
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)  # Параметр widget позволяет задать виджет, который будет
    # использоваться для генерации разметки html


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)  # Параметр widget позволяет задать
    # виджет, который будет использоваться для генерации разметки html, label — псевдоним приложения в виде строки
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)  # Параметр widget позволяет задать

    # виджет, который будет использоваться для генерации разметки html, label — псевдоним приложения в виде строки

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        """Проверка на совпадения пароля"""
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords do\'t match.')
        return cd['password2']
