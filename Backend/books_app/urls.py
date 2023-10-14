from django.contrib.auth.views import LoginView
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    VisitorDetailsView,
    VisitorUpdateView,
    MyLogoutView,
    BookListView,
    BookDetailsView,
    BookCreateView,
    BookUpdateView,
    BookDeleteView,
    CommentCreateView,
    RatingCreateView,
    SearchResultsView,
    BookViewSet,
    AuthorViewSet,
)

app_name = "books_app"

router = DefaultRouter()
router.register("books", BookViewSet)
router.register("authors", AuthorViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='books_app/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', MyLogoutView.as_view(), name='logout'),
    path('users/<int:pk>/', VisitorDetailsView.as_view(), name='visitor_details'),
    path('users/<int:pk>/update/', VisitorUpdateView.as_view(), name='visitor_update'),
    path('', BookListView.as_view(), name='books_list'),
    path('<int:pk>/', BookDetailsView.as_view(), name='book_details'),
    path('create/', BookCreateView.as_view(), name='book_add'),
    path('<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('<int:pk>/comments/', CommentCreateView.as_view(), name='comment_create'),
    path('rating/', RatingCreateView.as_view(), name='rating'),
    path('search/', SearchResultsView.as_view(), name='search'),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)