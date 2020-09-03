from django.forms import ModelForm
from .models import DBBook, DBBookComment, DBUserRatedBook, BookDatabase, MovieDatabase


class AddBookForm(ModelForm):
    class Meta:
        model = BookDatabase
        fields = '__all__'
        # exclude = ('book_user_favorite', 'book_overall_favorite', 'book_favorites_count')


class AddMovieForm(ModelForm):
    class Meta:
        model = MovieDatabase
        fields = '__all__'
        # exclude = ('book_user_favorite', 'book_overall_favorite', 'book_favorites_count')


class DBAddBookForm(ModelForm):
    class Meta:
        model = DBBook
        fields = '__all__'
        exclude = ('book_user_favorite', 'book_overall_favorite', 'book_favorites_count')


class DBCommentForm(ModelForm):
    class Meta:
        model = DBBookComment
        fields = ('text',)


class DBFavoriteSystemForm(ModelForm):
    class Meta:
        model = DBBook
        fields = ['book_user_favorite']


class DBUserRatedBookForm(ModelForm):
    class Meta:
        model = DBUserRatedBook
        fields = ['user_rated']
