import time

import pandas as pd
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
from django.utils import timezone
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise import dump

from .models import BookDatabase, BookRatings, MovieDatabase, MovieRatings, \
    DBBook, DBUserAddedBook, DBUserRatedBook
from .forms import AddBookForm, AddMovieForm, DBCommentForm, \
    DBFavoriteSystemForm, DBUserRatedBookForm

books_dataset = pd.read_csv("rcsystem/static/books_dataset.csv")
books_count_vec = CountVectorizer(stop_words='english')
books_count_matrix = books_count_vec.fit_transform(books_dataset['soup'])
books_cosine_sim = cosine_similarity(books_count_matrix, books_count_matrix)

books_ratings = pd.read_csv("rcsystem/static/books_ratings.csv")
_, user_based_book_algo = dump.load("rcsystem/static/user_based_book.dump")

movies_dataset = pd.read_csv("rcsystem/static/movies_dataset.csv")
movies_count_vec = CountVectorizer(stop_words='english')
movies_count_matrix = movies_count_vec.fit_transform(
    movies_dataset['soup'][:10000])
movies_cosine_sim = cosine_similarity(movies_count_matrix, movies_count_matrix)

movies_ratings = pd.read_csv("rcsystem/static/movies_ratings.csv")
_, user_based_movie_algo = dump.load("rcsystem/static/user_based_movie.dump")


class HomeView(View):
    def get(self, request):
        popular_books = self.popular(books_dataset)
        popular_movies = self.popular(movies_dataset)

        ordered_popular_books = []
        for popular_book in popular_books:
            ordered_popular_books.append(
                BookDatabase.objects.get(pk=popular_book))

        ordered_popular_movies = []
        for popular_movie in popular_movies:
            ordered_popular_movies.append(
                MovieDatabase.objects.get(id=popular_movie))

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

        user_rated_books = BookDatabase.objects.filter(
            pk__in=user_rated_books_list)
        if len(user_rated_books) >= 5:
            recommend_books = tuple(self.get_user_based_recommend(user.id))
            recommend_books = BookDatabase.objects.filter(
                pk__in=recommend_books)
        else:
            recommend_books = 0

        try:
            user_rated_movies = MovieRatings.objects.filter(user_id=user.id)
        except MovieRatings.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        user_rated_movies_list = []
        for m in user_rated_movies:
            user_rated_movies_list.append(m.movie_id)

        user_rated_movies = MovieDatabase.objects.filter(
            id__in=user_rated_movies_list)
        if len(user_rated_movies) >= 5:
            recommend_movies = tuple(
                self.get_user_based_recommend(user.id, book=False))
            print("recommend_movies:", recommend_movies)
            recommend_movies = MovieDatabase.objects.filter(
                id__in=recommend_movies)
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
            user_not_rated = books_ratings[
                ~(books_ratings['user_id'] == user_id)]
            for book_id in user_not_rated["book_id"].unique().tolist():
                pred = user_based_book_algo.predict(user_id, book_id, 3)
                try:
                    book_rating_pred.append((book_id, pred.est))
                except:
                    pass
            book_rating_pred = sorted(book_rating_pred, key=lambda x: x[1],
                                      reverse=True)[:10]
            book_indices = [i[0] for i in book_rating_pred]
            return book_indices

        else:
            movie_rating_pred = []
            user_not_rated = movies_ratings[
                ~(movies_ratings['user_id'] == user_id)]
            for movie_id in user_not_rated["movie_id"].unique().tolist():
                pred = user_based_movie_algo.predict(user_id, movie_id, 3)
                try:
                    movie_rating_pred.append((movie_id, pred.est))
                except:
                    pass
            movie_rating_pred = sorted(movie_rating_pred, key=lambda x: x[1],
                                       reverse=True)[:10]
            movie_indices = [i[0] for i in movie_rating_pred]
            return movie_indices


class BooksView(View):
    def get(self, request):
        all_books = BookDatabase.objects.all()[:30]
        book_page_1 = request.GET.get('page', 1)
        paginator = Paginator(all_books, 10)
        try:
            books = paginator.page(book_page_1)
        except PageNotAnInteger:
            books = paginator.page(1)
        except EmptyPage:
            books = paginator.page(paginator.num_pages)
        return render(request, "books.html", context={"books": books})


class BooksDetailView(View):
    def get(self, request, pk):
        try:
            book = BookDatabase.objects.get(pk=pk)
        except BookDatabase.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        is_rated = 0
        if request.user.is_authenticated:
            try:
                is_rated = BookRatings.objects.get(user_id=request.user.id,
                                                   book_id=pk).rating
            except BookRatings.DoesNotExist:
                pass

        recommend_books = tuple(self.get_recommendations(book.title))
        recommend_books = BookDatabase.objects.filter(pk__in=recommend_books)

        context = {
            'book': book,
            'recommend_books': recommend_books,
            'is_rated': is_rated,
            'user': request.user
        }
        return render(request, 'book_recommend.html', context=context)

    def get_index_from_title(self, title):
        return books_dataset[books_dataset["title"] == title]["id"].values[0]

    def get_recommendations(self, title):
        idx = int(self.get_index_from_title(title))
        sim_scores = list(enumerate(books_cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]
        book_indices = [i[0] for i in sim_scores]
        return books_dataset['title'].iloc[book_indices].index.tolist()

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))

        rated = int(request.POST["rating"])
        rating = BookRatings(rating=rated, book_id=pk, user_id=request.user.id)
        rating.save()

        with open("rcsystem/static/books_ratings.csv", "a") as f:
            append = str(pk) + "," + str(request.user.id) + "," + request.POST[
                "rating"] + "\n"
            f.write(append)

        return HttpResponseRedirect(self.request.path_info)


class MovieView(View):
    def get(self, request):
        all_movies = MovieDatabase.objects.all()[:30]
        movies_page_1 = request.GET.get('page', 1)
        paginator = Paginator(all_movies, 10)
        try:
            movies = paginator.page(movies_page_1)
        except PageNotAnInteger:
            movies = paginator.page(1)
        except EmptyPage:
            movies = paginator.page(paginator.num_pages)
        return render(request, "movies.html", context={"movies": movies})


class MovieDetailView(View):
    def get(self, request, movie_index):
        try:
            movie = MovieDatabase.objects.get(movie_index=movie_index)
        except MovieDatabase.DoesNotExist:
            return HttpResponseRedirect(reverse('recommender:index'))

        is_rated = 0
        if request.user.is_authenticated:
            try:
                actual = MovieDatabase.objects.get(movie_index=movie_index).id
                is_rated = MovieRatings.objects.get(user_id=request.user.id,
                                                    movie_id=actual).rating

            except MovieRatings.DoesNotExist:
                pass

        if movie_index >= 10000:
            context = {
                'movie': movie,
                'recommend_movies': "recommend_movies",
                'is_rated': is_rated,
                'user': request.user
            }
            return render(request, 'movie_recommend.html', context=context)

        recommend_movies = tuple(self.get_recommendations(movie.title))
        recommend_movies = MovieDatabase.objects.filter(
            movie_index__in=recommend_movies)

        context = {
            'movie': movie,
            'recommend_movies': recommend_movies,
            'is_rated': is_rated
        }
        return render(request, 'movie_recommend.html', context=context)

    def get_index_from_title(self, title):
        return movies_dataset[movies_dataset["title"] == title].index[0]

    def get_recommendations(self, title):
        movie_index = int(self.get_index_from_title(title))
        similar_movies = list(enumerate(movies_cosine_sim[movie_index]))
        sortedmovies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
        sim_scores = sortedmovies[1:11]
        movie_indices = [i[0] for i in sim_scores]
        return movies_dataset['title'].iloc[movie_indices].index.tolist()

    def post(self, request, movie_index):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))

        rated = float(request.POST["rating"])
        date = str(timezone.now())

        actual = MovieDatabase.objects.get(movie_index=movie_index).id

        rating = MovieRatings(user_id=request.user.id, rating=rated,
                              movie_id=actual, timestamp=date)
        rating.save()

        with open("rcsystem/static/movies_ratings.csv", "a") as f:
            append = str(request.user.id) + "," + str(actual) + "," + \
                     str(rated) + "," + str(int(time.time())) + "\n"
            f.write(append)

        return HttpResponseRedirect(self.request.path_info)


class Search(View):
    def get(self, request):
        search_term = request.GET.get('search')

        if request.GET.get('submit') == 'Search books':
            searched_for = BookDatabase.objects.all().filter(
                title__icontains=search_term)[:50]
            search_type = "books"
        elif request.GET.get('submit') == 'Search movies':
            searched_for = MovieDatabase.objects.all().filter(
                title__icontains=search_term)[:50]
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


class AddBook(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))
        form = AddBookForm()
        return render(request, "add_item.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))
        form = AddBookForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recommender:index'))
        else:
            form = AddBookForm()

        return render(request, "add_item.html", {"form": form})


class AddMovie(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))
        form = AddMovieForm()
        return render(request, "add_item.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse('recommender:index'))
        form = AddMovieForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recommender:index'))
        else:
            form = AddMovieForm()

        return render(request, "add_item.html", {"form": form})


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
