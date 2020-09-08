from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User

from .models import BookDatabase, BookRatings, MovieDatabase, MovieRatings, \
    DBBook, DBUserAddedBook, DBUserRatedBook
from .forms import AddBookForm, AddMovieForm, DBCommentForm, \
    DBFavoriteSystemForm, DBUserRatedBookForm
from .recommender_models import *
from .utils import ItemViewMixin, ItemAddView, ItemDetailView


class HomeView(View):
    def get(self, request):
        popular_books = self.popular(books_dataset)
        popular_movies = self.popular(movies_dataset)

        ordered_popular_books = []
        for popular_book in popular_books:
            ordered_popular_books.append(BookDatabase.objects.get(pk=popular_book))

        ordered_popular_movies = []
        for popular_movie in popular_movies:
            ordered_popular_movies.append(MovieDatabase.objects.get(id=popular_movie))

        context = {
            "popular_books": ordered_popular_books,
            "popular_movies": ordered_popular_movies
        }
        return render(request, "home.html", context=context)

    def popular(self, dataset):
        c = dataset['vote_average'].mean()
        m = dataset['vote_count'].quantile(0.9)
        trending = dataset.copy().loc[dataset['vote_count'] >= m]

        def weighted_rating(x):
            v = x['vote_count']
            r = x['vote_average']
            return (v / (v + m) * r) + (m / (m + v) * c)

        trending['score'] = trending.apply(weighted_rating, axis=1)
        trend_movies = trending.sort_values('score', ascending=False)
        return trend_movies['id'][:10].tolist()


class ProfileView(View):
    def get(self, request, pk):
        if not request.user.is_authenticated or request.user.id != pk:
            return HttpResponseRedirect(reverse('recommender:index'))

        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        try:
            user_rated_books = BookRatings.objects.filter(user_id=user.id)
        except BookRatings.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        user_rated_books_list = []
        for b in user_rated_books:
            user_rated_books_list.append(b.book_id)

        user_rated_books = BookDatabase.objects.filter(pk__in=user_rated_books_list)
        if len(user_rated_books) >= 5:
            recommend_books = tuple(self.get_user_based_recommend(user.id))
            recommend_books = BookDatabase.objects.filter(pk__in=recommend_books)
        else:
            recommend_books = 0

        try:
            user_rated_movies = MovieRatings.objects.filter(user_id=user.id)
        except MovieRatings.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        user_rated_movies_list = []
        for m in user_rated_movies:
            user_rated_movies_list.append(m.movie_id)

        user_rated_movies = MovieDatabase.objects.filter(id__in=user_rated_movies_list)
        if len(user_rated_movies) >= 5:
            recommend_movies = tuple(self.get_user_based_recommend(user.id, book=False))
            recommend_movies = MovieDatabase.objects.filter(id__in=recommend_movies)
        else:
            recommend_movies = 0

        context = {
            'profile': user,
            'user_rated_books': user_rated_books,
            'user_rated_movies': user_rated_movies,
            'recommend_books': recommend_books,
            'recommend_movies': recommend_movies,
        }
        return render(request, 'profile.html', context)

    def get_user_based_recommend(self, user_id, book=True):
        if book:
            book_rating_pred = []
            user_not_rated = books_ratings[~(books_ratings['user_id'] == user_id)]
            for book_id in user_not_rated["book_id"].unique().tolist():
                pred = user_based_book_algo.predict(user_id, book_id, 3)
                try:
                    book_rating_pred.append((book_id, pred.est))
                except:
                    pass
            book_rating_pred = sorted(book_rating_pred, key=lambda x: x[1], reverse=True)[:10]
            book_indices = [i[0] for i in book_rating_pred]
            return book_indices

        else:
            movie_rating_pred = []
            user_not_rated = movies_ratings[~(movies_ratings['user_id'] == user_id)]
            for movie_id in user_not_rated["movie_id"].unique().tolist():
                pred = user_based_movie_algo.predict(user_id, movie_id, 3)
                try:
                    movie_rating_pred.append((movie_id, pred.est))
                except:
                    pass
            movie_rating_pred = sorted(movie_rating_pred, key=lambda x: x[1], reverse=True)[:10]
            movie_indices = [i[0] for i in movie_rating_pred]
            return movie_indices


class BooksView(ItemViewMixin, View):
    model = BookDatabase
    template = "books.html"
    context_name = "books"


class BooksDetailView(ItemDetailView, View):
    model = BookDatabase
    model_ratings = BookRatings
    template = "book_recommend.html"
    item_name = "books"
    item_name_singular = "book"
    dataset = books_dataset
    cosine_sim = books_cosine_sim


class MoviesView(ItemViewMixin, View):
    model = MovieDatabase
    template = "movies.html"
    context_name = "movies"


class MoviesDetailView(ItemDetailView, View):
    model = MovieDatabase
    model_ratings = MovieRatings
    template = "movie_recommend.html"
    item_name = "movies"
    item_name_singular = "movie"
    dataset = movies_dataset
    cosine_sim = movies_cosine_sim


class Search(View):
    def get(self, request):
        search_term = request.GET.get('search')

        if request.GET.get('submit') == 'Search books':
            searched_for = BookDatabase.objects.filter(title__icontains=search_term)[:50]
            search_type = "books"
        elif request.GET.get('submit') == 'Search movies':
            searched_for = MovieDatabase.objects.filter(title__icontains=search_term)[:50]
            search_type = "movies"
        else:
            return HttpResponseRedirect(reverse('recommender:index'))

        search_page_1 = request.GET.get('page', 1)
        paginator = Paginator(searched_for, 10)
        try:
            searched_for = paginator.page(search_page_1)
        except PageNotAnInteger:
            searched_for = paginator.page(1)
        except EmptyPage:
            searched_for = paginator.page(paginator.num_pages)

        context = {'searched': searched_for, "search_type": search_type}
        return render(request, 'search.html', context=context)


class AddBook(ItemAddView, View):
    Form = AddBookForm
    item_name = "books"


class AddMovie(ItemAddView, View):
    Form = AddMovieForm
    item_name = "movies"


class OldBooksView(View):
    def get(self, request):
        all_books = DBBook.objects.all()[:30]
        book_page_1 = request.GET.get('page', 1)
        paginator = Paginator(all_books, 10)
        try:
            books = paginator.page(book_page_1)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        return render(request, "old_books.html", context={"books": books})

    def post(self, request):
        for query in request.POST:
            if 'add-to-your-book-' in query:
                book_isbn = query[len('add-to-your-book-'):]
                book = DBBook.objects.get(pk=book_isbn)
                if request.user.is_authenticated:
                    entity = DBUserAddedBook(
                        user=User.objects.get(username=request.user).id,
                        user_book=book)
                    entity.save()

                return HttpResponseRedirect(self.request.path_info)


class OldBookDetail(View):
    def get(self, request, pk):
        form = DBCommentForm(request.POST)
        favorite = DBFavoriteSystemForm(request.POST)
        user_rating = DBUserRatedBookForm(request.POST)
        try:
            book = DBBook.objects.get(pk=pk)
        except DBBook.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))
        is_rated = 0
        if request.user.is_authenticated:
            try:
                is_rated = DBUserRatedBook.objects.get(
                    user=User.objects.get(username=request.user).id, book=book)
                is_rated = is_rated.user_rated
            except DBUserRatedBook.DoesNotExist:
                is_rated = 0

        context = {
            'book': book,
            'form': form,
            'favorite': user_rating,
            'user_rated': is_rated,
        }
        return render(request, 'old_book_detail.html', context=context)

    def post(self, request, pk):
        book = get_object_or_404(DBBook, pk=pk)
        form = DBCommentForm(request.POST)
        favorite = DBFavoriteSystemForm(request.POST)
        user_rating = DBUserRatedBookForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.book = book
            comment.author = User.objects.get(username=request.user)
            comment.save()
            return redirect('recommender:old-book-detail', pk=book.pk)
        else:
            form = DBCommentForm()
        if user_rating.is_valid():
            user_rated = user_rating.cleaned_data['user_rated']
            count = book.book_favorites_count
            average = book.book_overall_favorite
            total_point = average * count
            count += 1
            overall = (total_point + user_rated) / count
            DBBook.objects.filter(pk=book.pk).update(
                book_favorites_count=count,
                book_overall_favorite=overall
            )

            rated = user_rating.save(commit=False)
            rated.user = User.objects.get(username=request.user)
            rated.book = book
            rated.save()

            return redirect('recommender:old-book-detail', pk=book.pk)
        else:
            favorite = DBFavoriteSystemForm()

        context = {'form': form, 'favorite': user_rating}
        return render(request, 'old_book_detail.html', context=context)
