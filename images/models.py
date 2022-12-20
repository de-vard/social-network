from django.db import models
from django.conf import settings
# from django.utils.text import slugify  # не подходит для кириллицы
from django.urls import reverse
from pytils.translit import slugify  # импортируем для русского языка


class Image(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='images_created',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField()
    image = models.ImageField(upload_to='images/%Y/%m/%d')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True, db_index=True)
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='images_liked',
        blank=True
    )
    total_likes = models.PositiveIntegerField(db_index=True, default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ Переопределяем метод save() для того
            чтобы автоматически формировать слаг
        """
        if not self.slug:  # если при сохранении изображения нету слага...
            self.slug = slugify(self.title)  # формируем его из title
        super(Image, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('images:detail', args=[self.id, self.slug])
