from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey


class Author(models.Model):
    '''Модель автора книги'''
    class META:
        ordering = ["surname"]

    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    year_of_birth = models.PositiveSmallIntegerField()
    description = models.TextField(null=False, blank=True)

    def __str__(self) -> str:
        full_name = "%s %s" % (self.name, self.surname)
        return full_name.strip()


class Book(models.Model):
    '''Модель книги'''
    class META:
        ordering = ["name"]

    class BookManager(models.Manager):
        '''
        Кастомный менеджер для модели книг
        '''
        def all(self):
            '''
            Список статей (SQL запрос для страницы списка книг)
            '''
            return self.get_queryset().select_related('author').prefetch_related('ratings')

        def detail(self):
            """
            Детализация книги (SQL запрос с фильтрацией для страницы с книгой)
            """
            return self.get_queryset() \
                .select_related('author') \
                .prefetch_related('comments', 'comments__visitor', 'ratings')

    name = models.CharField(max_length=100, verbose_name='Название книги')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    year = models.PositiveSmallIntegerField(verbose_name='Год издания')
    description = models.TextField(null=False, blank=True, verbose_name='Краткое описание')

    custom = BookManager()

    @property
    def book_author(self) -> str:
        return f"{self.author}"

    def __str__(self) -> str:
        return f"{self.name!r}"

    def get_success_url(self):
        return reverse(
            'books_app:book_details',
            kwargs={'pk': self.object.pk}
        )

    def get_sum_rating(self) -> float:
        '''
        Функция, для получения средней велечины рейтинга
        '''
        rate_count = len(self.ratings.all())
        if rate_count != 0:
            return sum([rating.rate for rating in self.ratings.all()]) / rate_count
        return 0


class Visitor(models.Model):
    '''Модель послетителя'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    bio = models.TextField(max_length=500, blank=True)

    def get_success_url(self):
        return reverse('books_app:visitor_details', kwargs={'pk': self.object.pk})

    def __str__(self) -> str:
        full_name = "%s %s" % (self.surname, self.name)
        return full_name.strip()


class BookRate(models.Model):
    '''Модель рейтинка книг'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='visitor_rate')
    rate = models.PositiveSmallIntegerField(choices=[(1, 'один'), (2, 'два'), (3, 'три'), (4, 'четыре'), (5, 'пять')])

    class Meta:
        unique_together = ('book', 'visitor')


class Comment(MPTTModel):
    '''Модель древовидных комментариев книги'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='comments_visitor')
    comment = models.TextField(max_length=500, blank=True)
    published_at = models.DateTimeField(auto_now_add=True)
    parent = TreeForeignKey('self', verbose_name='Родительский комментарий', null=True, blank=True,
                            related_name='children', on_delete=models.CASCADE)

    class MTTMeta:
        order_insertion_by = ('-published_at',)

    def __str__(self):
        return f'{self.visitor}:{self.comment}'


def get_image_filename(instance, filename):
    title = instance.book.name
    slug = slugify(title)
    return "book_images/%s-%s" % (slug, filename)

class Images(models.Model):
    '''Модель изображений книг'''
    book = models.ForeignKey(Book, on_delete=models.CASCADE, default=None)
    image = models.ImageField(
        upload_to=get_image_filename,
        blank=True,
        null=True,
        verbose_name='Изовражение',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )