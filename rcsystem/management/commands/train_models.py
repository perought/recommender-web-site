from django.core.management.base import BaseCommand

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise.model_selection import KFold
from surprise import Reader, Dataset, SVD, accuracy, dump

import rcsystem.recommender_models as rec_models


class Command(BaseCommand):
    help = 'Train models after changing datasets'

    def add_arguments(self, parser):
        parser.add_argument('--which', default="books")

    def handle(self, *args, **options):
        if options["which"] == "books":
            rec_models.books_dataset = pd.read_csv("rcsystem/static/books_dataset.csv")
            rec_models.books_count_vec = CountVectorizer(stop_words='english')
            rec_models.books_count_matrix = rec_models.books_count_vec.fit_transform(rec_models.books_dataset['soup'])
            rec_models.books_cosine_sim = cosine_similarity(rec_models.books_count_matrix, rec_models.books_count_matrix)
            self.stdout.write(self.style.SUCCESS('books updated'))

        if options["which"] == "books_rated":
            rec_models.books_ratings = pd.read_csv("rcsystem/static/books_ratings.csv")
            reader = Reader()
            data = Dataset.load_from_df(rec_models.books_ratings[['user_id', 'book_id', 'rating']], reader)
            kf = KFold(n_splits=5)
            svd = SVD()

            for trainset, testset in kf.split(data):
                svd.fit(trainset)
                predictions = svd.test(testset)
                accuracy.rmse(predictions, verbose=True)

            trainset = data.build_full_trainset()
            svd.fit(trainset)

            dump.dump("rcsystem/static/user_based_book.dump", algo=svd)
            rec_models.user_based_book_algo = svd

            self.stdout.write(self.style.SUCCESS('user_based_book_algo updated'))

        if options["which"] == "movies":
            rec_models.movies_dataset = pd.read_csv("rcsystem/static/movies_dataset.csv")
            rec_models.movies_count_vec = CountVectorizer(stop_words='english')
            rec_models.movies_count_matrix = rec_models.movies_count_vec.fit_transform(rec_models.movies_dataset['soup'][:10000])
            rec_models.movies_cosine_sim = cosine_similarity(rec_models.movies_count_matrix, rec_models.movies_count_matrix)
            self.stdout.write(self.style.SUCCESS('movies updated'))

        if options["which"] == "movies_rated":
            rec_models.books_ratings = pd.read_csv("rcsystem/static/movies_ratings.csv")
            reader = Reader()
            data = Dataset.load_from_df(rec_models.books_ratings[['user_id', 'movie_id', 'rating']], reader)
            kf = KFold(n_splits=5)
            svd = SVD()

            for trainset, testset in kf.split(data):
                svd.fit(trainset)
                predictions = svd.test(testset)
                accuracy.rmse(predictions, verbose=True)

            trainset = data.build_full_trainset()
            svd.fit(trainset)

            dump.dump("rcsystem/static/user_based_movie.dump", algo=svd)
            rec_models.user_based_movie_algo = svd

            self.stdout.write(self.style.SUCCESS('user_based_movie_algo updated'))
