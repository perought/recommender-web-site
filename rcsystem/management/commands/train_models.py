from django.core.management.base import BaseCommand

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from surprise.model_selection import KFold
from surprise import Reader, Dataset, SVD, accuracy, dump
from fastai.collab import CollabDataLoaders, collab_learner

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
            # surprise model
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

            # fastai model
            rec_models.books_ratings_title = pd.read_csv("rcsystem/static/books_ratings_with_title.csv")
            rec_models.books_dls = CollabDataLoaders.from_df(rec_models.books_ratings, item_name='title', seed=1)
            rec_models.books_collab_filtering = collab_learner(rec_models.books_dls, y_range=(0.5, 5.5))
            rec_models.books_collab_filtering.model_dir = "."
            rec_models.books_collab_filtering.fine_tune(1, wd=0.1)  # could be more epochs
            rec_models.books_collab_filtering.save("rcsystem/static/books_collab_filtering")

            self.stdout.write(self.style.SUCCESS('books collaborative filtering updated'))

        if options["which"] == "movies":
            rec_models.movies_dataset = pd.read_csv("rcsystem/static/movies_dataset.csv")
            rec_models.movies_count_vec = CountVectorizer(stop_words='english')
            rec_models.movies_count_matrix = rec_models.movies_count_vec.fit_transform(rec_models.movies_dataset['soup'][:10000])
            rec_models.movies_cosine_sim = cosine_similarity(rec_models.movies_count_matrix, rec_models.movies_count_matrix)
            self.stdout.write(self.style.SUCCESS('movies updated'))

        if options["which"] == "movies_rated":
            # surprise model
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

            # fastai model
            rec_models.movies_ratings_title = pd.read_csv("rcsystem/static/movies_ratings_with_title.csv")
            rec_models.movies_dls = CollabDataLoaders.from_df(rec_models.movies_ratings, item_name='title', seed=1)
            rec_models.movies_collab_filtering = collab_learner(rec_models.movies_dls, y_range=(0.5, 5.5))
            rec_models.movies_collab_filtering.model_dir = "."
            rec_models.movies_collab_filtering.fine_tune(1, wd=0.1)  # could be more epochs
            rec_models.movies_collab_filtering.save("rcsystem/static/movies_collab_filtering")

            self.stdout.write(self.style.SUCCESS('movies collaborative filtering updated'))
