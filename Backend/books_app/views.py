from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, ListView, DeleteView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from books_app.forms import BookWithFileForm, VisitorUpdateForm, BookUpdateForm, CommentCreateForm
from books_app.models import Author, Book, Visitor, Images, Comment, BookRate
from books_app.serializers import AuthorSerializer, BookSerializer
from extra_views import UpdateWithInlinesView, InlineFormSetFactory
from django.db.models import Q


class RegisterView(CreateView):
    '''
    Класс для регистрации пользователей с автозаходом на сайт
    '''
    form_class = UserCreationForm
    template_name = 'books_app/register.html'
    success_url = reverse_lazy('books_app:books_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        Visitor.objects.create(user=self.object)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


class VisitorDetailsView(DetailView):
    '''
    Класс для детальной информации о пользователе
    '''
    template_name = 'books_app/visitor_details.html'
    model = Visitor
    context_object_name = 'visitor'
    queryset = model.objects.all().select_related('user')


class VisitorUpdateView(UserPassesTestMixin, UpdateView):
    '''
    Класс для изменения информации пользователя
    '''
    def test_func(self):
        return self.request.user == self.get_object().user

    model = Visitor
    form_class = VisitorUpdateForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'books_app:visitor_details',
            kwargs={'pk': self.object.pk}
        )


class MyLogoutView(LogoutView):
    next_page = reverse_lazy('books_app:login')


class BookDetailsView(DetailView):
    '''
    Класс для детальной информации о книге
    '''
    model = Book
    template_name = 'books_app/book_details.html'
    context_object_name = 'book'
    queryset = model.custom.detail()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = Images.objects.filter(book=self.object.pk)
        context['form'] = CommentCreateForm
        return context


class BookListView(ListView):
    '''
    Класс для вывода списка книг по 3шт на странице
    '''
    template_name = 'books_app/books_list.html'
    context_object_name = 'object_list'
    model = Book
    queryset = Book.custom.all()
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        return context


class BookCreateView(LoginRequiredMixin, View):
    '''
    Класс для создания книги
    '''
    def get(self, request: HttpRequest) -> HttpResponse:
        form = BookWithFileForm()
        context = {"form": form}
        return render(request, 'books_app/book_add.html', context=context)

    def post(self, request: HttpRequest):
        form = BookWithFileForm(request.POST, request.FILES)
        if form.is_valid():
            author = Author.objects.get(pk=request.POST["author"])
            book = Book.custom.create(
                name=request.POST["name"],
                author=author,
                description=request.POST["description"],
                year=request.POST["year"],
            )
            book.save()

            images = request.FILES.getlist("images")
            for image in images:
                added_photo = Images.objects.create(image=image, book=book)
                added_photo.save()

            url = reverse('books_app:books_list')
            return redirect(url)


class ImageInline(InlineFormSetFactory):
    '''
    Класс, для создания экземпляра изображения, для присоединения к экземпляру книги
    '''
    model = Images
    fields = ['image',]
    factory_kwargs = {"extra": 1, 'can_delete': False}

class BookUpdateView(LoginRequiredMixin, UpdateWithInlinesView):
    '''
    Класс для редактирования данных о книге
    '''
    model = Book
    form_class = BookUpdateForm
    inlines = [ImageInline]
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'books_app:book_details',
            kwargs={'pk': self.object.pk}
        )


class BookDeleteView(LoginRequiredMixin, DeleteView):
    '''
    Класс для удаления книги
    '''
    model = Book
    success_url = reverse_lazy('books_app:books_list')
    context_object_name = 'book'
    template_name = 'books_app/book_delete.html'


class CommentCreateView(LoginRequiredMixin, CreateView):
    '''
    Класс, для создания древовидный коментариев
    '''
    model = Comment
    form_class = CommentCreateForm

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_invalid(self, form):
        if self.is_ajax():
            return JsonResponse({'error': form.errors}, status=400)
        return super().form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.book_id = self.kwargs.get('pk')
        comment.visitor = Visitor.objects.get(user_id=self.request.user.id)
        comment.parent_id = form.cleaned_data.get('parent')
        comment.save()

        if self.is_ajax():
            return JsonResponse({
                'is_child': comment.is_child_node(),
                'id': comment.id,
                'visitor': comment.visitor.name,
                'parent_id': comment.parent_id,
                'published_at': comment.published_at.strftime('%Y-%b-%d %H:%M:%S'),
                'comment': comment.comment,
            }, status=200)

        return redirect(comment.book.get_success_url())

    def handle_no_permission(self):
        return JsonResponse({'error': 'Необходимо авторизоваться для добавления комментариев'}, status=400)


class RatingCreateView(LoginRequiredMixin, View):
    '''
    Класс для выставления оценки для книги, с отрисовкой результата на странице.
    Если повторно выбрать эту оценку - она удалится, если выбрать другую - она изменится на новое значение.
    '''
    model = BookRate
    def post(self, request, *args, **kwargs):
        book_id = request.POST.get('book_id')
        rate = int(request.POST.get('rate'))
        visitor = Visitor.objects.get(user_id=self.request.user.id)

        rating, created = self.model.objects.get_or_create(
            book_id=book_id,
            visitor=visitor,
            defaults={'rate': rate},
        )

        if not created:
            if rating.rate == rate:
                rating.delete()
                return JsonResponse({'status': 'deleted',
                                     'rating_sum': rating.book.get_sum_rating(),
                                     })
            else:
                rating.rate = rate
                rating.visitor = visitor
                rating.save()
                return JsonResponse({'status': 'updated',
                                     'rating_sum': rating.book.get_sum_rating(),
                                     })
        return JsonResponse({'status': 'created',
                             'rating_sum': rating.book.get_sum_rating(),
                             })


class SearchResultsView(ListView):
    '''
    Класс для поиска экземпляров книг по полям "Название" и "Автор"
    '''
    model = Book
    template_name = 'books_app/books_list.html'

    def get_queryset(self):
        query = self.request.GET.get('do')
        object_list = Book.custom.filter(
            Q(name__icontains=query) |
            Q(author__name__icontains=query) |
            Q(author__surname__icontains=query)
        )
        return object_list


class BookViewSet(ModelViewSet):
    '''
    Класс для создания API по книгам с различными фильтрами и поисками
    '''
    serializer_class = BookSerializer
    queryset = Book.custom.all()

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["name", "author__name", "author__surname", "year", "description"]
    filterset_fields = ["name", "author", "year", "description"]
    ordering_fields = ["name", "author__name", "author__surname", "year"]

class AuthorViewSet(ModelViewSet):
    '''
    Класс для создания API по авторам с различными фильтрами и поисками
    '''
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]
    search_fields = ["name", "surname", "year_of_birth", "description"]
    filterset_fields = ["name", "surname", "year_of_birth", "description"]
    ordering_fields = ["name", "surname", "year_of_birth"]
