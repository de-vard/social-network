from django import forms
from .models import Image
from urllib import request
from django.core.files.base import ContentFile
from django.utils.text import slugify


class ImageCreateForm(forms.ModelForm):
    """Форма изображения """

    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {'url': forms.HiddenInput, }  # заменили виджет по умолчанию, что бы пользователи не видели поле url

    def clean_url(self):
        """Проверка на расширение"""
        url = self.cleaned_data['url']  # получаем значение url из формы
        valid_extensions = ['jpg', 'jpeg']  # допустимые расширения
        extension = url.rsplit('.', 1)[1].lower()  # получаем из url расширение файла
        if extension not in valid_extensions:  # Проверяем допустимое ли расширение
            raise forms.ValidationError('The give URL does not match valid images extensions.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        """Переопределили метод save для сохранения объектов"""
        image = super(ImageCreateForm, self).save(commit=False)
        image_url = self.cleaned_data['url']  # получает URL из атрибута cleaned_data формы
        image_name = f"{slugify(image.title)}.{image_url.rsplit('.', 1)[1].lower()}"  # генерирует название изображения

        response = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(response.read()), save=False)  # Скачиваем изображение по указанному
        # адресу commit=False, чтобы пока не сохранять объект в базу данных
        if commit:  # если commit равен True
            image.save()  # сохраняем
        return image
