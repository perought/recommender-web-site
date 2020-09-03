from django.urls import path

from .views import Search, OldBookDetail, AddBook, AddMovie, BooksView, \
    BooksDetailView, MovieView, MovieDetailView, ProfileView, HomeView, OldBooksView

app_name = 'recommender'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),

    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),

    path('movies/', MovieView.as_view(), name='movies'),
    path('movies/<int:movie_index>/', MovieDetailView.as_view(), name='movie-recommender'),

    path('books/', BooksView.as_view(), name='books'),
    path('books/<int:pk>', BooksDetailView.as_view(), name='book-recommender'),

    path('add_book/', AddBook.as_view(), name='add-book'),
    path('add_movie/', AddMovie.as_view(), name='add-movie'),
    path('search/', Search.as_view(), name='search'),

    path('old_books/', OldBooksView.as_view(), name='old-books'),
    path('old_books/<str:pk>', OldBookDetail.as_view(), name='old-book-detail'),
]
