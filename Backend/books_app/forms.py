from django import forms
from books_app.models import Author, Visitor, Book, Comment


class MultipleFileInput(forms.ClearableFileInput):
    '''Класс, добавляющий возможность подгружать несколько файлов за один раз'''
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    '''Класс поля, добавляющий несколько файлов за один раз'''
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class BookWithFileForm(forms.Form):
    ''' Класс формы, для добавления книги с несколькими изображениями'''
    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    name = forms.CharField(label='Название книги', max_length=100)
    author = forms.ModelChoiceField(queryset=Author.objects.all(), label='Автор')
    description = forms.CharField(
        label='Описание книги',
        widget=forms.Textarea(),
    )
    year = forms.DecimalField(label='Год издания', min_value=1, max_value=2050)
    images = MultipleFileField(label='Обложка и фото', required=False)


class BookUpdateForm(forms.ModelForm):
    """
    Форма обновления книги на сайте
    """
    class Meta:
        model = Book
        fields = ['name', 'author', 'year', 'description',]

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

class VisitorUpdateForm(forms.ModelForm):
    """
    Форма обновления данных пользователя
    """
    class Meta:
        model = Visitor
        fields = ('name', 'surname', 'bio')

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы обновления
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })


class CommentCreateForm(forms.ModelForm):
    """
    Форма добавления комментариев к книге
    """
    parent = forms.IntegerField(widget=forms.HiddenInput, required=False)
    comment = forms.CharField(label='', widget=forms.Textarea(attrs={'cols': 30, 'rows': 5, 'placeholder': 'Комментарий', 'class': 'form-control'}))

    class Meta:
        model = Comment
        fields = ('comment',)