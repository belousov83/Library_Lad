from django.contrib import admin
from books_app.models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = 'pk', 'surname', 'name', 'year_of_birth', 'description_short'
    list_display_links = 'pk', 'surname'
    search_fields = 'surname', 'name'

    def description_short(self, obj: Author) -> str:
        if len(obj.description) > 100:
            return obj.description[:100] + '...'
        else:
            return obj.description


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'author', 'year', 'description_short'
    list_display_links = 'pk', 'name'
    search_fields = 'name', 'year', 'author__name', 'author__surname'

    def description_short(self, obj: Book) -> str:
        if len(obj.description) > 100:
            return obj.description[:100] + '...'
        else:
            return obj.description