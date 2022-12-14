from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.


def default_urls():
    return {
        'hhru': '',
        'superjob': ''
    }


class City(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название города')
    slug = models.SlugField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Название города'
        verbose_name_plural = 'Названия городов'

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Язык программирования')
    slug = models.SlugField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Язык программирования'
        verbose_name_plural = 'Языки программирования'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    title = models.CharField(max_length=250, verbose_name='Заголовок вакансии')
    url = models.URLField(unique=True)
    company = models.CharField(max_length=250, verbose_name='Компания')
    description = RichTextField(verbose_name='Описание вакансии')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name='Язык программирования')
    timestamp = models.DateField(auto_now_add=True)
    published_at = models.DateField(blank=True, null=True)
    from_recurse = models.CharField(max_length=50, verbose_name='Ресурс', blank=True, null=True)
    salary = models.JSONField(default=None, null=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-timestamp']

    def __str__(self):
        return self.title


class Error(models.Model):
    timestamp = models.DateField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return str(self.timestamp)

    class Meta:
        verbose_name = 'Ошибка'
        verbose_name_plural = 'Ошибки'


class Url(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, verbose_name='Язык программирования')
    url_data = models.JSONField(default=default_urls)

    class Meta:
        # уникальная совокупность полей (не может быть создано 2 экземпляра с одинаковыми указанными полями)
        unique_together = ('city', 'language')

